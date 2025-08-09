# test_deps.py
try:
    import undetected_chromedriver as uc

    print("✅ undetected_chromedriver imported successfully")

    import selenium

    print("✅ selenium imported successfully")

    # Test basic functionality
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    print("✅ Chrome options created successfully")

    print("🎉 All browser dependencies are working!")

except Exception as e:
    print(f"❌ Error: {e}")
    print("Run: pip install undetected-chromedriver selenium")