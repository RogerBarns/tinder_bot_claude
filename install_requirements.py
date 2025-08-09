"""
Quick installer for Tinder Bot dependencies
Run this script to install all required packages
"""

import subprocess
import sys


def install_package(package):
    """Install a single package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Install all required packages"""
    print("=" * 50)
    print("🔧 Installing Tinder Bot Dependencies")
    print("=" * 50)

    packages = [
        "flask",
        "flask-socketio",
        "python-socketio[client]",
        "apscheduler",
        "python-dotenv",
        "requests",
        "selenium",
        "anthropic",
        "pytz",
        "colorlog"
    ]

    failed = []

    for package in packages:
        print(f"\n📦 Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
        else:
            print(f"❌ Failed to install {package}")
            failed.append(package)

    print("\n" + "=" * 50)

    if failed:
        print("⚠️ Some packages failed to install:")
        for pkg in failed:
            print(f"  - {pkg}")
        print("\nTry installing them manually with:")
        print(f"  pip install {' '.join(failed)}")
    else:
        print("✅ All packages installed successfully!")
        print("\n🚀 You can now run the bot with:")
        print("  python main.py")

    print("=" * 50)

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()