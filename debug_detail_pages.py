from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json

def debug_detail_pages():
    print("🔍 Debugging business detail pages...")
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to search page
        print("🌐 Going to search page...")
        driver.get("https://www.sos.ks.gov/eforms/BusinessEntity/Search.aspx")
        time.sleep(5)
        
        # Handle CAPTCHA if present
        if 'recaptcha' in driver.page_source.lower():
            print("🛑 CAPTCHA detected - please solve it in browser")
            input("Press Enter after solving CAPTCHA...")
            time.sleep(3)
        
        # Perform a search that we know returns results
        print("🔍 Performing search for 'Test'...")
        
        # Select Business Name radio
        biz_radio = driver.find_element(By.ID, "BusinessName")
        if not biz_radio.is_selected():
            biz_radio.click()
        
        # Enter search term
        search_input = driver.find_element(By.ID, "SearchString")
        search_input.clear()
        search_input.send_keys("Test")
        
        # Select Starts With radio  
        starts_radio = driver.find_element(By.ID, "StartsWith")
        if not starts_radio.is_selected():
            starts_radio.click()
        
        # Click search
        search_btn = driver.find_element(By.ID, "SearchButton")
        search_btn.click()
        time.sleep(8)
        
        # Handle CAPTCHA again if needed
        if 'recaptcha' in driver.page_source.lower():
            print("🛑 CAPTCHA detected - please solve it in browser")
            input("Press Enter after solving CAPTCHA...")
            time.sleep(3)
        
        # Find and click the first business link
        print("🔍 Looking for business links...")
        
        # Try different selectors for business links
        business_links = []
        
        # Look for clickable business names in tables
        tables = driver.find_elements(By.TAG_NAME, "table")
        for table in tables:
            links = table.find_elements(By.TAG_NAME, "a")
            for link in links:
                text = link.text.strip()
                href = link.get_attribute("href")
                if text and href and ("business" in href.lower() or "detail" in href.lower()):
                    business_links.append((text, href))
                    print(f"✅ Found business link: {text} -> {href}")
        
        if not business_links:
            print("❌ No business links found. Looking for any clickable links...")
            all_links = driver.find_elements(By.TAG_NAME, "a")
            for link in all_links:
                text = link.text.strip()
                if text and len(text) > 2:
                    print(f"Possible link: '{text}'")
        
        # Click the first business link if found
        if business_links:
            first_business = business_links[0]
            print(f"🖱️ Clicking on: {first_business[0]}")
            driver.get(first_business[1])
            time.sleep(5)
            
            # Now we're on the detail page - let's analyze it
            print(f"📄 Detail page title: {driver.title}")
            print(f"🔗 Detail page URL: {driver.current_url}")
            
            # Save the detail page
            with open("business_detail_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("💾 Detail page saved: 'business_detail_page.html'")
            
            # Take screenshot
            driver.save_screenshot("business_detail_page.png")
            print("📸 Screenshot saved: 'business_detail_page.png'")
            
            # Analyze the page structure
            print("\n🔍 ANALYZING DETAIL PAGE STRUCTURE:")
            
            # Look for common data patterns
            page_text = driver.page_source
            
            # Look for Business ID
            import re
            id_patterns = [
                r'Business ID[^>]*>([^<]+)',
                r'Business ID[:\s]*([^\s<]+)',
                r'ID[^>]*>([^<]+)',
            ]
            
            for pattern in id_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    print(f"✅ Business ID found: {match.group(1)}")
                    break
            
            # Look for Business Name
            name_patterns = [
                r'Business Name[^>]*>([^<]+)',
                r'Entity Name[^>]*>([^<]+)',
                r'Name[^>]*>([^<]+)',
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    print(f"✅ Business Name found: {match.group(1)}")
                    break
            
            # Look for tables with data
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"📊 Found {len(tables)} tables on detail page")
            
            for i, table in enumerate(tables):
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"  Table {i+1}: {len(rows)} rows")
                
                # Show first few rows
                for j, row in enumerate(rows[:5]):
                    cells = row.find_elements(By.TAG_NAME, ["td", "th"])
                    cell_texts = [cell.text for cell in cells]
                    if any(cell_texts):  # Only show non-empty rows
                        print(f"    Row {j}: {cell_texts}")
            
            # Look for specific data fields
            print("\n🎯 LOOKING FOR SPECIFIC FIELDS:")
            field_patterns = {
                'Business ID': ['business id', 'id', 'filing number'],
                'Business Name': ['business name', 'entity name', 'name'],
                'Entity Type': ['entity type', 'type'],
                'Formation Date': ['formation date', 'filing date', 'date'],
                'Status': ['status'],
                'Jurisdiction': ['jurisdiction'],
                'Principal Office': ['principal office'],
                'Registered Office': ['registered office'],
                'Resident Agent': ['resident agent'],
                'Last Report': ['last report'],
                'Next Report': ['next report'],
                'Forfeiture': ['forfeiture']
            }
            
            for field_name, patterns in field_patterns.items():
                for pattern in patterns:
                    if pattern in page_text.lower():
                        print(f"  ✅ {field_name} field detected")
                        break
            
            return True
        else:
            print("❌ No business links to click")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_detail_pages()