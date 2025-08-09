"""
Session management for Tinder API interactions
"""
import time
import uuid
import random
import requests
from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime, timedelta

from config import CLIENT_VARIATIONS, TINDER_AUTH_TOKEN
from utils.logger import get_logger
from mobile_requests import get_mobile_local_ip, SourceIPAdapter

logger = get_logger(__name__)


@dataclass
class TinderSession:
    """Represents a Tinder client session with fingerprinting"""
    
    account_id: str
    auth_token: str = field(default="")
    app_session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    advertising_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tinder_version: str = field(default="")
    user_agent: str = field(default="")
    os_version: str = field(default="")
    platform: str = field(default="")
    login_timestamp: float = field(default_factory=time.time)
    last_rotation: float = field(default_factory=time.time)
    session: requests.Session = field(default_factory=requests.Session)
    _mobile_bound: bool = field(default=False)
    
    def __post_init__(self):
        """Initialize session with random fingerprint"""
        if not self.tinder_version:
            self.tinder_version = random.choice(CLIENT_VARIATIONS["versions"])
        if not self.user_agent:
            self.user_agent = random.choice(CLIENT_VARIATIONS["user_agents"])
        if not self.os_version:
            self.os_version = random.choice(CLIENT_VARIATIONS["os_versions"])
        if not self.platform:
            self.platform = random.choice(CLIENT_VARIATIONS["platforms"])
        if not self.auth_token and TINDER_AUTH_TOKEN:
            self.auth_token = TINDER_AUTH_TOKEN
    
    def elapsed_seconds(self) -> int:
        """Get seconds elapsed since login"""
        return int(time.time() - self.login_timestamp)
    
    def should_rotate_fingerprint(self) -> bool:
        """Check if fingerprint should be rotated (adds randomness)"""
        hours_elapsed = (time.time() - self.last_rotation) / 3600
        # Rotate randomly between 1-3 hours with increasing probability
        return random.random() < (hours_elapsed / 3.0)
    
    def rotate_fingerprint(self):
        """Rotate some fingerprint elements to appear more human"""
        if random.random() < 0.7:  # 70% chance to change version
            old_version = self.tinder_version
            self.tinder_version = random.choice(CLIENT_VARIATIONS["versions"])
            logger.info(f"Rotated Tinder version: {old_version} -> {self.tinder_version}")
        
        if random.random() < 0.3:  # 30% chance to change user agent
            self.user_agent = random.choice(CLIENT_VARIATIONS["user_agents"])
            logger.info("Rotated user agent")
        
        self.last_rotation = time.time()
    
    def bind_mobile_interface(self):
        """Bind session to mobile network interface if available"""
        if self._mobile_bound:
            return
        
        mobile_ip = get_mobile_local_ip()
        if not mobile_ip:
            logger.warning("No mobile interface found, using default routing")
            return
        
        try:
            adapter = SourceIPAdapter(source_ip=mobile_ip)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            self._mobile_bound = True
            
            # Verify binding
            resp = self.session.get("https://api.ipify.org", timeout=5)
            if resp.ok:
                logger.info(f"Mobile session bound, external IP: {resp.text.strip()}")
        except Exception as e:
            logger.error(f"Failed to bind mobile interface: {e}")
    
    def get_headers(self) -> Dict[str, str]:
        """Generate request headers with current session state"""
        # Maybe rotate fingerprint
        if self.should_rotate_fingerprint():
            self.rotate_fingerprint()
        
        elapsed = self.elapsed_seconds()
        
        return {
            "X-Auth-Token": self.auth_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "app-session-id": self.app_session_id,
            "user-session-id": self.user_session_id,
            "persistent-device-id": self.device_id,
            "advertising-id": self.advertising_id,
            "tinder-version": self.tinder_version,
            "User-Agent": self.user_agent,
            "platform": self.platform,
            "os-version": self.os_version,
            "app-session-time-elapsed": str(elapsed),
            "user-session-time-elapsed": str(elapsed),
        }
    
    def make_request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with session"""
        headers = kwargs.pop("headers", {})
        headers.update(self.get_headers())
        kwargs["headers"] = headers
        
        try:
            return self.session.request(method, url, **kwargs)
        except Exception as e:
            logger.error(f"Request failed: {method} {url} - {e}")
            return None


class SessionManager:
    """Manages multiple Tinder sessions"""
    
    def __init__(self):
        self._sessions: Dict[str, TinderSession] = {}
        self._default_account = "main"
    
    def get_session(self, account_id: Optional[str] = None) -> TinderSession:
        """Get or create session for account"""
        if account_id is None:
            account_id = self._default_account
        
        if account_id not in self._sessions:
            session = TinderSession(account_id=account_id)
            session.bind_mobile_interface()
            self._sessions[account_id] = session
            logger.info(f"Created new session for account: {account_id}")
        
        return self._sessions[account_id]
    
    def rotate_all_sessions(self):
        """Rotate fingerprints for all sessions"""
        for session in self._sessions.values():
            if session.should_rotate_fingerprint():
                session.rotate_fingerprint()


# Global session manager
session_manager = SessionManager()
