from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def debug_current_page():
    print("🔍 Debugging the current page structure...")
    
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to SOS and click business link (same as before)
        driver.get("https://sos.ks.gov/")
        time.sleep(3)
        
        # Click the business link
        business_link = driver.find_element(By.XPATH, "//a[contains(translate(., 'BUSINESS', 'business'), 'business')]")
        business_link.click()
        time.sleep(5)
        
        print(f"📄 Current Page Title: {driver.title}")
        print(f"🔗 Current URL: {driver.current_url}")
        
        # Take screenshot
        driver.save_screenshot("current_page.png")
        print("📸 Screenshot saved as 'current_page.png'")
        
        # Find ALL input fields on the page
        print("\n🔎 Searching for ALL input fields:")
        all_inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(all_inputs)} input fields:")
        
        for i, input_field in enumerate(all_inputs):
            try:
                input_type = input_field.get_attribute("type") or "no type"
                input_name = input_field.get_attribute("name") or "no name"
                input_id = input_field.get_attribute("id") or "no id"
                input_placeholder = input_field.get_attribute("placeholder") or "no placeholder"
                input_class = input_field.get_attribute("class") or "no class"
                
                print(f"  {i+1}. Type: {input_type}, Name: {input_name}, ID: {input_id}")
                print(f"     Placeholder: {input_placeholder}, Class: {input_class}")
                
            except Exception as e:
                print(f"  {i+1}. Error reading input: {e}")
        
        # Find ALL forms on the page
        print("\n🔎 Searching for ALL forms:")
        all_forms = driver.find_elements(By.TAG_NAME, "form")
        print(f"Found {len(all_forms)} forms:")
        
        for i, form in enumerate(all_forms):
            try:
                form_id = form.get_attribute("id") or "no id"
                form_class = form.get_attribute("class") or "no class"
                form_action = form.get_attribute("action") or "no action"
                print(f"  {i+1}. ID: {form_id}, Class: {form_class}, Action: {form_action}")
            except Exception as e:
                print(f"  {i+1}. Error reading form: {e}")
        
        # Find ALL buttons
        print("\n🔎 Searching for ALL buttons:")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(all_buttons)} buttons:")
        
        for i, button in enumerate(all_buttons):
            try:
                button_text = button.text.strip() or "no text"
                button_type = button.get_attribute("type") or "no type"
                print(f"  {i+1}. Text: '{button_text}', Type: {button_type}")
            except Exception as e:
                print(f"  {i+1}. Error reading button: {e}")
        
        # Save the complete page source
        with open("debug_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\n💾 Full page source saved as 'debug_page_source.html'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_current_page()