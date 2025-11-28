from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_chromedriver():
    print("🧪 Testing ChromeDriver...")
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    try:
        # Try to start Chrome
        driver = webdriver.Chrome(options=chrome_options)
        
        # Test by opening Google
        print("🌐 Opening Google...")
        driver.get("https://www.google.com")
        time.sleep(2)
        
        print("✅ SUCCESS: ChromeDriver is working!")
        print(f"✅ Page title: {driver.title}")
        
        driver.quit()
        print("🚪 Browser closed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure Chrome browser is installed")
        print("2. Try closing all Chrome windows and run again")
        print("3. Make sure chromedriver.exe is in the same folder as your Python files")
        return False

if __name__ == "__main__":
    test_chromedriver()