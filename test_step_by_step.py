from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def test_website_access():
    print("🧪 Testing website access...")
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Test accessing the Kansas business site
        test_url = "https://www.kansas.gov/sos/business/search.html"
        print(f"🌐 Trying to access: {test_url}")
        
        driver.get(test_url)
        time.sleep(5)
        
        print(f"✅ Successfully loaded page")
        print(f"📄 Page title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Check if page contains expected elements
        page_source = driver.page_source.lower()
        if "business" in page_source or "search" in page_source:
            print("✅ Page contains expected content")
        else:
            print("⚠️  Page content may not be as expected")
            
        # Take screenshot for verification
        driver.save_screenshot("website_test.png")
        print("📸 Screenshot saved as 'website_test.png'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing website: {e}")
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    test_website_access()