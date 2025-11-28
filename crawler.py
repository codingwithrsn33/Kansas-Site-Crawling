import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
import json
import re

class KansasSOSCrawler:
    def __init__(self):
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        
    def navigate_to_search(self):
        """Navigate to search page"""
        try:
            logging.info("🌐 Navigating to search page...")
            self.driver.get("https://www.sos.ks.gov/eforms/BusinessEntity/Search.aspx")
            time.sleep(5)
            
            if self.has_captcha():
                print("🛑 CAPTCHA detected. Please solve it in the browser.")
                input("Press Enter after solving CAPTCHA...")
                time.sleep(3)
            
            return True
        except Exception as e:
            logging.error(f"Navigation failed: {e}")
            return False
    
    def has_captcha(self):
        """Check if CAPTCHA is present"""
        return 'recaptcha' in self.driver.page_source.lower()
    
    def perform_search(self, keyword):
        """Perform search"""
        try:
            logging.info(f"🔍 Searching for: '{keyword}'")
            
            # Handle CAPTCHA
            if self.has_captcha():
                print(f"🛑 CAPTCHA detected for '{keyword}'. Please solve it.")
                input("Press Enter after solving CAPTCHA...")
                time.sleep(3)
            
            # Select Business Name
            biz_radio = self.driver.find_element(By.ID, "BusinessName")
            if not biz_radio.is_selected():
                biz_radio.click()
            
            # Enter keyword
            search_input = self.driver.find_element(By.ID, "SearchString")
            search_input.clear()
            search_input.send_keys(keyword)
            
            # Select Starts With
            starts_radio = self.driver.find_element(By.ID, "StartsWith")
            if not starts_radio.is_selected():
                starts_radio.click()
            
            # Search
            search_btn = self.driver.find_element(By.ID, "SearchButton")
            search_btn.click()
            time.sleep(8)
            
            # Handle CAPTCHA after search
            if self.has_captcha():
                print(f"🛑 CAPTCHA detected after search. Please solve it.")
                input("Press Enter after solving CAPTCHA...")
                time.sleep(3)
            
            return True
        except Exception as e:
            logging.error(f"Search failed: {e}")
            return False
    
    def extract_business_links(self):
        """Extract business links from search results"""
        try:
            businesses = []
            
            # Look for business links in tables
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            for table in tables:
                rows = table.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    links = row.find_elements(By.TAG_NAME, "a")
                    for link in links:
                        text = link.text.strip()
                        href = link.get_attribute("href")
                        if text and href and ("business" in href.lower() or "detail" in href.lower()):
                            # Get business ID from nearby cells
                            business_id = ""
                            cells = row.find_elements(By.TAG_NAME, "td")
                            for cell in cells:
                                cell_text = cell.text.strip()
                                if cell_text and cell_text.isdigit() and len(cell_text) > 3:
                                    business_id = cell_text
                                    break
                            
                            businesses.append({
                                'name': text,
                                'url': href,
                                'business_id': business_id
                            })
            
            return businesses
        except Exception as e:
            logging.error(f"Link extraction failed: {e}")
            return []
    
    def extract_detailed_business_data(self, detail_url):
        """Extract detailed business data from detail page"""
        try:
            logging.info(f"📄 Extracting details from: {detail_url}")
            self.driver.get(detail_url)
            time.sleep(5)
            
            # Handle CAPTCHA on detail page
            if self.has_captcha():
                print("🛑 CAPTCHA on detail page. Please solve it.")
                input("Press Enter after solving CAPTCHA...")
                time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Initialize with empty values
            business_data = {
                "business_id": "",
                "business_name": "",
                "type": "",
                "formation_date": "",
                "jurisdiction": "",
                "status": "",
                "principal_office_address": "",
                "registered_office_address": "",
                "resident_agent_name": "",
                "last_reporting_year": "",
                "next_report_due_date": "",
                "forfeiture_date": ""
            }
            
            # Extract using multiple strategies
            
            # Strategy 1: Look for label-value pairs in tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text().strip().lower()
                        value = cells[1].get_text().strip()
                        
                        # Map labels to fields
                        if any(term in label for term in ['business id', 'id', 'filing number']):
                            business_data['business_id'] = value
                        elif any(term in label for term in ['business name', 'entity name', 'name']):
                            business_data['business_name'] = value
                        elif any(term in label for term in ['entity type', 'type']):
                            business_data['type'] = value
                        elif any(term in label for term in ['formation date', 'filing date']):
                            business_data['formation_date'] = value
                        elif 'jurisdiction' in label:
                            business_data['jurisdiction'] = value
                        elif 'status' in label:
                            business_data['status'] = value
                        elif 'principal office' in label:
                            business_data['principal_office_address'] = value
                        elif 'registered office' in label:
                            business_data['registered_office_address'] = value
                        elif 'resident agent' in label:
                            business_data['resident_agent_name'] = value
                        elif 'last report' in label:
                            business_data['last_reporting_year'] = value
                        elif 'next report' in label:
                            business_data['next_report_due_date'] = value
                        elif 'forfeiture' in label:
                            business_data['forfeiture_date'] = value
            
            # Strategy 2: Look for specific text patterns
            page_text = soup.get_text()
            
            # Extract Business ID
            if not business_data['business_id']:
                id_match = re.search(r'Business ID[:\s]*([^\s<]+)', page_text, re.IGNORECASE)
                if id_match:
                    business_data['business_id'] = id_match.group(1).strip()
            
            # Extract Business Name
            if not business_data['business_name']:
                name_match = re.search(r'Business Name[:\s]*([^\n<]+)', page_text, re.IGNORECASE)
                if name_match:
                    business_data['business_name'] = name_match.group(1).strip()
            
            # Extract Formation Date
            if not business_data['formation_date']:
                date_match = re.search(r'Formation Date[:\s]*([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})', page_text, re.IGNORECASE)
                if date_match:
                    business_data['formation_date'] = date_match.group(1).strip()
            
            # Extract Status
            if not business_data['status']:
                status_match = re.search(r'Status[:\s]*([^\n<]+)', page_text, re.IGNORECASE)
                if status_match:
                    business_data['status'] = status_match.group(1).strip()
            
            # Clean up - remove empty fields
            business_data = {k: v for k, v in business_data.items() if v}
            
            return business_data
            
        except Exception as e:
            logging.error(f"Detail extraction failed: {e}")
            return None
    
    def save_business_data(self, data, filename):
        """Save business data as JSON"""
        os.makedirs('data/json', exist_ok=True)
        path = f'data/json/{filename}.json'
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"💾 Saved: {path}")
        return path
    
    def run(self):
        """Main crawler execution"""
        try:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
            
            print("🚀 Starting Kansas SOS Business Crawler...")
            print("This crawler will extract detailed business information.")
            print("You may need to solve CAPTCHAs manually when prompted.\n")
            
            if not self.navigate_to_search():
                return False
            
            keywords = ['A', 'AA', 'Test', 'LLC']
            all_businesses = []
            
            for keyword in keywords:
                print(f"\n{'='*50}")
                print(f"🔍 PROCESSING: '{keyword}'")
                print('='*50)
                
                if self.perform_search(keyword):
                    businesses = self.extract_business_links()
                    
                    if businesses:
                        print(f"✅ Found {len(businesses)} businesses")
                        
                        # Process first business only (to avoid too many requests)
                        first_business = businesses[0]
                        print(f"📄 Getting details for: {first_business['name']}")
                        
                        detailed_data = self.extract_detailed_business_data(first_business['url'])
                        
                        if detailed_data and any(detailed_data.values()):
                            # Use the business ID for filename
                            biz_id = detailed_data.get('business_id', first_business.get('business_id', 'unknown'))
                            filename = f"{biz_id}_{keyword}"
                            
                            self.save_business_data(detailed_data, filename)
                            all_businesses.append(detailed_data)
                            
                            print(f"✅ Successfully extracted detailed data:")
                            for key, value in detailed_data.items():
                                if value:
                                    print(f"   {key}: {value}")
                        else:
                            print("❌ Could not extract detailed data")
                            # Save the page HTML for debugging
                            os.makedirs('data/html', exist_ok=True)
                            with open(f"data/html/{keyword}_detail.html", "w", encoding="utf-8") as f:
                                f.write(self.driver.page_source)
                    else:
                        print("❌ No businesses found in search results")
                else:
                    print("❌ Search failed")
            
            # Save all collected data
            if all_businesses:
                self.save_business_data(all_businesses, "all_businesses_collected")
                print(f"\n🎉 CRAWLING COMPLETED!")
                print(f"📊 Total detailed business records: {len(all_businesses)}")
            else:
                print("\n❌ No business data was collected")
            
            return True
            
        except Exception as e:
            logging.error(f"Crawler error: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                print("\n🔚 Browser closed")

if __name__ == "__main__":
    crawler = KansasSOSCrawler()
    success = crawler.run()
    
    if success:
        print("\n✅ Crawling completed successfully!")
        print("📁 Check 'data/json' folder for business data files")
    else:
        print("\n❌ Crawling failed")