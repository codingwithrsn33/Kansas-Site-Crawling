from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def explore_sos_website():
    print("🔍 Exploring Kansas SOS website structure...")
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Go to the main SOS page
        driver.get("https://sos.ks.gov/")
        time.sleep(3)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Take initial screenshot
        driver.save_screenshot("sos_homepage.png")
        print("📸 Screenshot saved as 'sos_homepage.png'")
        
        # Look for business-related sections
        print("\n🔎 Looking for business services...")
        
        # Strategy 1: Look for navigation menus
        nav_links = driver.find_elements(By.CSS_SELECTOR, "nav a, .menu a, .navigation a, ul li a")
        business_links = []
        
        for link in nav_links:
            try:
                text = link.text.strip()
                href = link.get_attribute("href")
                if text and ("business" in text.lower() or "entity" in text.lower() or "corporation" in text.lower()):
                    business_links.append((text, href))
                    print(f"🏢 Found in navigation: {text} -> {href}")
            except:
                continue
        
        # Strategy 2: Look for buttons or sections with business text
        business_elements = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'BUSINESS', 'business'), 'business')]")
        for element in business_elements:
            try:
                text = element.text.strip()
                if text and len(text) < 100:  # Reasonable length for clickable elements
                    # Try to get link if it's a clickable element
                    parent_link = element.find_element(By.XPATH, "./ancestor::a")
                    href = parent_link.get_attribute("href")
                    if href:
                        business_links.append((text, href))
                        print(f"🔘 Found business element: {text} -> {href}")
            except:
                # If no link, just note the text
                if text and text not in [link[0] for link in business_links]:
                    print(f"📝 Business text found: {text}")
        
        # Strategy 3: Look for search functionality
        search_forms = driver.find_elements(By.TAG_NAME, "form")
        search_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='search'], input[type='text']")
        
        print(f"\n🔍 Found {len(search_forms)} forms and {len(search_inputs)} input fields")
        
        # Save page source for analysis
        with open("sos_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Page source saved as 'sos_page_source.html'")
        
        # If we found business links, explore the first one
        if business_links:
            print(f"\n🎯 Found {len(business_links)} business-related links")
            first_business = business_links[0]
            print(f"🖱️ Clicking on: {first_business[0]}")
            
            driver.get(first_business[1])
            time.sleep(3)
            
            print(f"📄 New page title: {driver.title}")
            print(f"🔗 New URL: {driver.current_url}")
            
            # Save this page too
            driver.save_screenshot("business_section.png")
            with open("business_section.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("📸 Screenshot and source saved for business section")
            
            return driver.current_url
        else:
            print("❌ No clear business links found in navigation")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    business_url = explore_sos_website()
    if business_url:
        print(f"\n✅ Business section found at: {business_url}")
    else:
        print("\n❌ Could not find business section automatically")