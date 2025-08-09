"""
Mobile network interface stub - Windows 11 compatible
Falls back to home IP if no mobile adapter found
"""
import requests
import socket
import psutil
from typing import Optional
from requests.adapters import HTTPAdapter

# Global session that mimics mobile behavior
mobile_session = requests.Session()
mobile_session.headers.update({
    'User-Agent': 'Tinder/13.21.0 (Android; Android 13; Pixel 6 Pro)',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'application/json',
    'Connection': 'keep-alive'
})


class SourceIPAdapter(HTTPAdapter):
    """
    HTTPAdapter that binds to a specific source IP
    """
    def __init__(self, source_ip: str, *args, **kwargs):
        self.source_ip = source_ip
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        kwargs["source_address"] = (self.source_ip, 0)
        return super().init_poolmanager(*args, **kwargs)


def get_mobile_local_ip(target_desc: str = "mobile") -> Optional[str]:
    """
    Try to find a mobile/tethered network interface on Windows
    Falls back to primary network interface if no mobile found
    """
    try:
        # IPs to skip (virtual/local adapters)
        skip_ips = ['127.', '169.254.']  # Removed 192.168.56. to allow home networks
        virtual_keywords = ['virtualbox', 'vmware', 'vbox', 'docker', 'wsl']

        # Windows mobile tethering interface names
        mobile_keywords = [
            'mobile', 'cellular', 'broadband', 'modem',
            'remote ndis', 'rndis', 'ethernet 2', 'ethernet 3',
            'usb', 'tether', 'hotspot', 'samsung', 'android'
        ]

        # First, try to find mobile interface
        for interface, addrs in psutil.net_if_addrs().items():
            interface_lower = interface.lower()

            # Skip virtual adapters
            if any(vm in interface_lower for vm in virtual_keywords):
                continue

            # Check if this might be a mobile interface
            if any(keyword in interface_lower for keyword in mobile_keywords):
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        # Skip problematic IPs
                        if any(addr.address.startswith(skip) for skip in skip_ips):
                            continue

                        # Check if interface is up
                        stats = psutil.net_if_stats().get(interface)
                        if stats and stats.isup:
                            # Additional check: can it reach the internet?
                            if can_reach_internet(addr.address):
                                print(f"📱 Found mobile interface: {interface} -> {addr.address}")
                                return addr.address

        # If no mobile interface found, fall back to primary network interface
        print("📶 No mobile interface found, looking for home network...")

        # Find the default gateway interface (usually your home network)
        primary_ip = get_primary_network_ip()
        if primary_ip:
            print(f"🏠 Using home network: {primary_ip}")
            return primary_ip

        # Last resort: find any working interface
        for interface, addrs in psutil.net_if_addrs().items():
            interface_lower = interface.lower()

            # Skip virtual and loopback
            if any(skip in interface_lower for skip in virtual_keywords):
                continue

            for addr in addrs:
                if addr.family == socket.AF_INET:
                    if any(addr.address.startswith(skip) for skip in skip_ips):
                        continue

                    stats = psutil.net_if_stats().get(interface)
                    if stats and stats.isup:
                        if can_reach_internet(addr.address):
                            print(f"🌐 Using available network: {interface} -> {addr.address}")
                            return addr.address

        print("⚠️ No suitable network interface found")
        return None

    except Exception as e:
        print(f"❌ Error finding network interface: {e}")
        return None


def get_primary_network_ip() -> Optional[str]:
    """
    Get the IP address of the primary network interface (one that can reach internet)
    """
    try:
        # Create a socket and connect to a public DNS server
        # This doesn't actually send data, just determines which interface would be used
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return None


def can_reach_internet(source_ip: str) -> bool:
    """
    Check if the given IP can reach the internet
    """
    try:
        # Try to connect to a reliable public service
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(2)
        test_socket.bind((source_ip, 0))
        test_socket.connect(("8.8.8.8", 53))
        test_socket.close()
        return True
    except Exception:
        return False


def bind_to_mobile_interface(session: requests.Session) -> bool:
    """
    Attempt to bind a requests session to mobile interface or home network
    """
    network_ip = get_mobile_local_ip()
    if not network_ip:
        print("⚠️ No network interface found, using default routing")
        return False

    try:
        # Skip binding for problematic virtual IPs
        if network_ip.startswith('192.168.56.'):
            print(f"⚠️ Skipping VirtualBox adapter {network_ip}, using default routing")
            return False

        adapter = SourceIPAdapter(network_ip)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        print(f"✅ Session bound to network interface: {network_ip}")

        # Test the connection
        try:
            resp = session.get("https://api.ipify.org", timeout=5)
            if resp.ok:
                external_ip = resp.text.strip()
                print(f"🌍 External IP: {external_ip}")
                return True
        except Exception as e:
            print(f"⚠️ Network test failed: {e}")
            print("🔄 Falling back to default routing")
            # Remove the adapter if it doesn't work
            session.mount("http://", requests.adapters.HTTPAdapter())
            session.mount("https://", requests.adapters.HTTPAdapter())
            return False

    except Exception as e:
        print(f"❌ Failed to bind to network interface: {e}")
        return False


# Auto-bind the global session if possible
bind_to_mobile_interface(mobile_session)