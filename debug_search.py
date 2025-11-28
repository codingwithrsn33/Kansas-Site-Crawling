from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json

def debug_search_page():
    print("🔍 Debugging search page structure...")
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate directly to search page
        print("🌐 Navigating to search page...")
        driver.get("https://www.sos.ks.gov/eforms/BusinessEntity/Search.aspx")
        time.sleep(5)
        
        print(f"📄 Page title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Check for CAPTCHA
        page_source = driver.page_source.lower()
        if any(word in page_source for word in ['recaptcha', 'captcha']):
            print("🎯 CAPTCHA detected - please solve it manually in the browser")
            input("Press Enter after solving CAPTCHA...")
        
        # Take screenshot
        driver.save_screenshot("search_page.png")
        print("📸 Screenshot saved: 'search_page.png'")
        
        # Find all form elements
        print("\n🔍 FORM ELEMENTS:")
        
        # Find all input fields
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(inputs)} input fields:")
        
        for i, input_field in enumerate(inputs):
            try:
                input_type = input_field.get_attribute("type") or "no type"
                input_name = input_field.get_attribute("name") or "no name"
                input_id = input_field.get_attribute("id") or "no id"
                input_value = input_field.get_attribute("value") or "no value"
                placeholder = input_field.get_attribute("placeholder") or "no placeholder"
                
                print(f"  {i+1}. Type: {input_type}, Name: {input_name}, ID: {input_id}")
                print(f"      Value: '{input_value}', Placeholder: '{placeholder}'")
                print(f"      Displayed: {input_field.is_displayed()}, Enabled: {input_field.is_enabled()}")
                
            except Exception as e:
                print(f"  {i+1}. Error: {e}")
        
        # Find all radio buttons specifically
        print("\n🎯 RADIO BUTTONS:")
        radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        for radio in radio_buttons:
            try:
                radio_id = radio.get_attribute("id") or "no id"
                radio_name = radio.get_attribute("name") or "no name"
                radio_value = radio.get_attribute("value") or "no value"
                is_checked = radio.is_selected()
                print(f"  Radio: ID={radio_id}, Name={radio_name}, Value={radio_value}, Checked={is_checked}")
            except:
                pass
        
        # Find the search button
        print("\n🔘 BUTTONS:")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        submit_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
        
        all_buttons = buttons + submit_inputs
        for btn in all_buttons:
            try:
                btn_type = btn.get_attribute("type") or "no type"
                btn_value = btn.get_attribute("value") or "no value"
                btn_text = btn.text or "no text"
                btn_id = btn.get_attribute("id") or "no id"
                print(f"  Button: Type={btn_type}, ID={btn_id}, Value='{btn_value}', Text='{btn_text}'")
            except:
                pass
        
        # Test a search manually
        print("\n🧪 TESTING SEARCH MANUALLY...")
        
        # Select "Business Name" radio
        try:
            biz_name_radio = driver.find_element(By.ID, "BusinessName")
            if not biz_name_radio.is_selected():
                biz_name_radio.click()
                print("✅ Selected Business Name radio")
        except:
            print("❌ Could not find BusinessName radio")
        
        # Enter search term
        try:
            search_input = driver.find_element(By.ID, "SearchString")
            search_input.clear()
            search_input.send_keys("Test")
            print("✅ Entered search term: 'Test'")
        except:
            print("❌ Could not find SearchString input")
        
        # Select "Starts With" radio
        try:
            starts_with_radio = driver.find_element(By.ID, "StartsWith")
            if not starts_with_radio.is_selected():
                starts_with_radio.click()
                print("✅ Selected Starts With radio")
        except:
            print("❌ Could not find StartsWith radio")
        
        # Click search
        try:
            search_btn = driver.find_element(By.ID, "SearchButton")
            search_btn.click()
            print("✅ Clicked Search button")
        except:
            print("❌ Could not find SearchButton")
        
        # Wait for results
        time.sleep(7)
        
        # Check what we got
        print(f"\n📊 AFTER SEARCH:")
        print(f"URL: {driver.current_url}")
        print(f"Title: {driver.title}")
        
        # Look for results table
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} tables after search")
        
        for i, table in enumerate(tables):
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"  Table {i+1}: {len(rows)} rows")
            
            # Show first few rows
            for j, row in enumerate(rows[:3]):
                cells = row.find_elements(By.TAG_NAME, "td")
                cell_texts = [cell.text for cell in cells]
                print(f"    Row {j}: {cell_texts}")
        
        # Save the page source
        with open("search_results_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("💾 Page source saved: 'search_results_debug.html'")
        
        # Take screenshot of results
        driver.save_screenshot("search_results.png")
        print("📸 Results screenshot: 'search_results.png'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_search_page()