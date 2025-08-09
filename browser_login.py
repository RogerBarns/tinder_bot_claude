# browser_login.py
"""
Manual browser login for Tinder with better error handling
"""
import sys
import os
import subprocess

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_chrome_version():
    """Check installed Chrome version"""
    try:
        # Try to get Chrome version
        import winreg
        try:
            # Check Chrome version in registry
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version = winreg.QueryValueEx(key, "version")[0]
            print(f"✅ Chrome version: {version}")
            return version
        except:
            pass

        # Alternative method
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path):
            result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True)
            if result.stdout:
                version = result.stdout.strip().split()[-1]
                print(f"✅ Chrome version: {version}")
                return version
    except:
        print("⚠️ Could not detect Chrome version")
    return None


def manual_login():
    """Open browser for manual Tinder login"""
    print("🌐 Setting up browser for Tinder login...")

    # Check Chrome version first
    chrome_version = check_chrome_version()

    print("Installing/updating ChromeDriver...")
    try:
        # Update undetected-chromedriver
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "undetected-chromedriver"], check=True)
        print("✅ ChromeDriver updated")
    except:
        print("⚠️ Failed to update ChromeDriver")

    print("-" * 50)

    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        # Create Chrome options
        options = uc.ChromeOptions()

        # Create profile directory
        profile_dir = os.path.join(os.path.dirname(__file__), "data", "chrome_profile")
        os.makedirs(profile_dir, exist_ok=True)
        options.add_argument(f'--user-data-dir={profile_dir}')

        # Other options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--window-size=1366,768')

        print("🚀 Starting Chrome browser...")

        # Let undetected-chromedriver handle version automatically
        driver = uc.Chrome(options=options, version_main=None)
        wait = WebDriverWait(driver, 20)

        print("✅ Browser started successfully!")
        print("📍 Navigating to Tinder...")

        driver.get("https://tinder.com")

        print("\n" + "=" * 50)
        print("👤 MANUAL LOGIN REQUIRED")
        print("=" * 50)
        print("1. Complete the login process in the browser")
        print("2. Once you see your matches/swipe cards, login is complete")
        print("3. The browser will close automatically")
        print("4. Your session will be saved for future use")
        print("=" * 50)

        # Wait for login (check every 2 seconds for 2 minutes)
        logged_in = False
        for i in range(60):  # 2 minutes total
            try:
                # Check if logged in by looking for app elements
                if (driver.find_elements(By.CSS_SELECTOR, "[data-testid='gamepad']") or
                        driver.find_elements(By.CSS_SELECTOR, ".recsCardboard") or
                        driver.find_elements(By.CSS_SELECTOR, "[href='/app/recs']") or
                        "app/recs" in driver.current_url or
                        "app/matches" in driver.current_url):
                    logged_in = True
                    break
            except:
                pass

            if i % 10 == 0:
                remaining = 300 - (i * 2)
                print(f"⏳ Waiting for login... ({remaining} seconds remaining)")

            import time
            time.sleep(2)

        if logged_in:
            print("\n✅ Login successful! Session saved.")
            print("✅ You can now run the bot normally with run.bat")
            time.sleep(3)  # Let user see the success message
        else:
            print("\n❌ Login timeout - please try again")

        driver.quit()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Chrome is installed")
        print("2. Update Chrome to the latest version")
        print("3. Run: pip install --upgrade undetected-chromedriver")


if __name__ == "__main__":
    check_chrome_version()
    manual_login()