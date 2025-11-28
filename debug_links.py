from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_business_links():
    print("🔍 Debugging business links on the page...")
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to SOS homepage
        driver.get("https://sos.ks.gov/")
        time.sleep(3)
        
        # Click the main Business link
        print("🌐 Clicking main Business link...")
        business_link = driver.find_element(By.XPATH, "//a[contains(translate(., 'BUSINESS', 'business'), 'business')]")
        business_link.click()
        time.sleep(3)
        
        # Take screenshot of the business page
        driver.save_screenshot("business_menu_page.png")
        print("📸 Screenshot saved: 'business_menu_page.png'")
        
        # Find ALL links on the page
        print("\n🔍 Finding ALL links on the business page:")
        all_links = driver.find_elements(By.TAG_NAME, "a")
        print(f"Found {len(all_links)} total links")
        
        # Show all links with their text and href
        for i, link in enumerate(all_links):
            try:
                text = link.text.strip()
                href = link.get_attribute("href")
                if text:  # Only show links with text
                    print(f"{i+1:2d}. Text: '{text}'")
                    print(f"     URL: {href}")
                    print(f"     Displayed: {link.is_displayed()}, Enabled: {link.is_enabled()}")
                    print()
            except Exception as e:
                print(f"{i+1:2d}. Error reading link: {e}")
        
        # Specifically look for search-related links
        print("\n🎯 Looking for search-related links:")
        search_keywords = ['search', 'Search', 'SEARCH', 'business search', 'Business Search']
        
        for keyword in search_keywords:
            print(f"\nLooking for links containing: '{keyword}'")
            try:
                # By partial text
                links_by_text = driver.find_elements(By.PARTIAL_LINK_TEXT, keyword)
                for link in links_by_text:
                    text = link.text.strip()
                    href = link.get_attribute("href")
                    print(f"  Found by partial text: '{text}' -> {href}")
            except:
                pass
            
            try:
                # By XPath contains text
                links_by_xpath = driver.find_elements(By.XPATH, f"//a[contains(., '{keyword}')]")
                for link in links_by_xpath:
                    text = link.text.strip()
                    href = link.get_attribute("href")
                    print(f"  Found by XPATH: '{text}' -> {href}")
            except:
                pass
        
        # Save the page source for analysis
        with open("business_menu_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\n💾 Page source saved: 'business_menu_source.html'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_business_links()