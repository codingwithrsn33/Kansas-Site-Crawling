import time
import random
from playwright.sync_api import sync_playwright
import json
import os
from datetime import datetime
import re
import logging

class KansasSOSCrawler:
    def __init__(self, headless=False):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.context = self.browser.new_context(
            viewport={'width': 1200, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = self.context.new_page()
        self.output_dir = "kansas_business_data"
        
        # ✅ COMPLETE: Setup comprehensive output directories and logging
        self.setup_directories()
        self.setup_logging()
        
    def setup_directories(self):
        """Create comprehensive output directory structure"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/json", exist_ok=True)
        os.makedirs(f"{self.output_dir}/html_fallback", exist_ok=True)
        os.makedirs(f"{self.output_dir}/errors", exist_ok=True)
        print("✅ Created comprehensive output directories")

    def setup_logging(self):
        """Setup logging for error tracking"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"{self.output_dir}/crawler.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Kansas SOS Crawler started with comprehensive error handling")

    def save_html_fallback(self, html_content, filename_prefix, error_type):
        """Save HTML as fallback when JSON parsing fails"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/html_fallback/{filename_prefix}_{error_type}_{timestamp}.html"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"<!-- Error Type: {error_type} -->\n")
                f.write(f"<!-- Timestamp: {timestamp} -->\n")
                f.write(f"<!-- URL: {self.page.url} -->\n")
                f.write(html_content)
            
            self.logger.info(f"HTML fallback saved: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Failed to save HTML fallback: {e}")
            return None

    def save_error_log(self, search_term, error_message, page_source=None):
        """Save detailed error information"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_data = {
                'search_term': search_term,
                'error_message': str(error_message),
                'timestamp': timestamp,
                'url': self.page.url,
                'error_type': 'crawling_error'
            }
            
            # Save error JSON
            error_json_file = f"{self.output_dir}/errors/error_{search_term}_{timestamp}.json"
            with open(error_json_file, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, indent=2, ensure_ascii=False)
            
            # Save HTML if page source is available
            if page_source:
                html_file = self.save_html_fallback(
                    page_source, 
                    f"error_{search_term}", 
                    "page_capture"
                )
                error_data['html_fallback_file'] = html_file
            
            self.logger.error(f"Error logged: {error_json_file}")
            return error_json_file
            
        except Exception as e:
            self.logger.error(f"Failed to save error log: {e}")
            return None

    def safe_extract_json_data(self, business_data, search_term):
        """Safely convert data to JSON with fallback to HTML"""
        try:
            # Add metadata
            if isinstance(business_data, dict):
                business_data['search_term'] = search_term
                business_data['extracted_at'] = datetime.now().isoformat()
                business_data['status'] = 'success'
            
            # Validate JSON serialization
            json.dumps(business_data, ensure_ascii=False)
            
            return business_data, None
            
        except (TypeError, ValueError) as e:
            self.logger.error(f"JSON serialization failed: {e}")
            
            # Save HTML fallback
            html_file = self.save_html_fallback(
                self.page.content(),
                f"json_fail_{search_term}",
                "serialization_error"
            )
            
            # Create minimal JSON with error info
            error_data = {
                'search_term': search_term,
                'status': 'error',
                'error_type': 'json_serialization_failed',
                'error_message': str(e),
                'scraped_at': datetime.now().isoformat(),
                'html_fallback_file': html_file,
                'partial_business_data': str(business_data)[:500] if business_data else None
            }
            
            return error_data, html_file

    def save_data_with_fallback(self, data, filename):
        """Enhanced save method with HTML fallback"""
        try:
            filepath = os.path.join(self.output_dir, filename)
            
            # If it's already HTML data, just save it
            if isinstance(data, dict) and 'html_content' in data:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(data['html_content'])
                print(f"💾 Saved HTML: {filename}")
                self.logger.info(f"HTML data saved: {filename}")
                return filepath
            
            # For JSON data, try to save with validation
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved JSON: {filename}")
            self.logger.info(f"JSON data saved: {filename}")
            return filepath
            
        except (TypeError, ValueError) as e:
            self.logger.error(f"JSON save failed for {filename}: {e}")
            
            # Save HTML fallback
            html_file = self.save_html_fallback(
                self.page.content(),
                f"save_fail_{filename.replace('.json', '')}",
                "save_error"
            )
            
            # Save error info
            error_data = {
                'filename': filename,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'html_fallback_file': html_file
            }
            
            error_file = f"{self.output_dir}/errors/save_error_{filename.replace('.json', '')}.json"
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump(error_data, f, indent=2, ensure_ascii=False)
            
            return html_file  # Return the HTML file path instead

    def random_delay(self, min_sec=1, max_sec=3):
        time.sleep(random.uniform(min_sec, max_sec))
        
    def save_data(self, data, filename):
        """Original save method maintained for compatibility"""
        filepath = os.path.join(self.output_dir, filename)
        
        if isinstance(data, dict) and 'html_content' in data:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(data['html_content'])
            print(f"💾 Saved HTML: {filename}")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved JSON: {filename}")
        return filepath

    def check_and_solve_captcha(self):
        """Check for CAPTCHA and wait for user to solve it"""
        print("🔍 Checking for CAPTCHA...")
        time.sleep(3)
        
        # Check for CAPTCHA elements
        captcha_indicators = [
            ".g-recaptcha",
            "iframe[src*='recaptcha']",
            "text=CAPTCHA",
            "text=recaptcha",
            "text=verify you are human"
        ]
        
        has_captcha = False
        for indicator in captcha_indicators:
            if self.page.query_selector(indicator):
                has_captcha = True
                break
        
        if has_captcha:
            print("\n" + "="*60)
            print("🛑 CAPTCHA DETECTED!")
            print("Please solve the CAPTCHA in the browser window")
            print("Then press Enter here to continue...")
            print("="*60)
            input("Press Enter AFTER solving CAPTCHA...")
            print("✅ Continuing with automation...")
            time.sleep(3)
            return True
        return False

    def navigate_to_homepage_first(self):
        """Navigate to SOS homepage first, then to business search"""
        print("📍 Step 1: Navigating to Kansas SOS Homepage...")
        
        try:
            # First go to the main SOS homepage
            homepage_url = "https://sos.ks.gov/"
            self.page.goto(homepage_url, wait_until="networkidle")
            time.sleep(5)
            
            print(f"🏠 Homepage loaded: {self.page.title()}")
            
            # Check for CAPTCHA on homepage
            self.check_and_solve_captcha()
            
            # Now navigate to business search page
            print("📍 Step 2: Navigating to Business Search from homepage...")
            search_url = "https://www.sos.ks.gov/eforms/BusinessEntity/Search.aspx"
            self.page.goto(search_url, wait_until="networkidle")
            time.sleep(5)
            
            # Check for CAPTCHA on search page
            self.check_and_solve_captcha()
            
            print("✅ Successfully navigated from homepage to search page")
            print(f"📄 Current page title: {self.page.title()}")
            return True
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            # Try direct navigation as fallback
            try:
                print("🔧 Trying direct navigation to search page...")
                search_url = "https://www.sos.ks.gov/eforms/BusinessEntity/Search.aspx"
                self.page.goto(search_url, wait_until="networkidle")
                time.sleep(5)
                self.check_and_solve_captcha()
                print("✅ Used direct navigation fallback")
                return True
            except Exception as fallback_error:
                print(f"❌ Fallback navigation also failed: {fallback_error}")
                return False

    def automated_search_setup(self, search_term):
        """Automatically set up the search - NO MANUAL INTERVENTION NEEDED"""
        print(f"🔍 Automated Search Setup for '{search_term}'")
        
        try:
            # Wait for page to be ready
            time.sleep(3)
            
            # 1. Select "Business Name" radio button if not already selected
            business_name_radio = self.page.query_selector("#MainContent_rblSearchType_0")
            if business_name_radio and not business_name_radio.is_checked():
                business_name_radio.click()
                print("✅ Selected Business Name search type")
                time.sleep(1)
            
            # 2. Select "Contains" radio button if not already selected  
            contains_radio = self.page.query_selector("#MainContent_rblNameSearchType_0")
            if contains_radio and not contains_radio.is_checked():
                contains_radio.click()
                print("✅ Selected Contains search filter")
                time.sleep(1)
            
            # 3. Clear and enter search term
            search_input = self.page.query_selector("#MainContent_txtSearchEntityName")
            if search_input:
                search_input.fill("")  # Clear existing text
                search_input.fill(search_term)
                print(f"✅ Entered search term: '{search_term}'")
                time.sleep(1)
                return True
            else:
                print("❌ Could not find search input")
                self.save_error_log(search_term, "Search input not found", self.page.content())
                return False
                
        except Exception as e:
            print(f"❌ Error in automated search setup: {e}")
            self.save_error_log(search_term, f"Search setup error: {e}", self.page.content())
            return False

    def perform_search(self, search_term):
        """Perform the search after automated setup"""
        print("🔄 Performing search...")
        
        try:
            # Check for CAPTCHA before searching
            self.check_and_solve_captcha()
            
            search_btn = self.page.query_selector("#MainContent_btnSearchEntity")
            if search_btn:
                search_btn.click()
                print("✅ Clicked search button")
                time.sleep(8)
                
                # Check for CAPTCHA after search
                self.check_and_solve_captcha()
                
                return True
            else:
                print("❌ Could not find search button")
                self.save_error_log(search_term, "Search button not found", self.page.content())
                return False
        except Exception as e:
            print(f"❌ Search failed: {e}")
            self.save_error_log(search_term, f"Search failed: {e}", self.page.content())
            return False

    def extract_business_links_from_results(self, search_term):
        """Extract business links from search results table"""
        print("📋 Looking for business links in results...")
        businesses = []
        
        try:
            # Wait for results table to load
            time.sleep(5)
            
            # Look for the results table - Kansas SOS uses table.gvResults
            results_table = self.page.query_selector("table.gvResults")
            if not results_table:
                print("❌ No results table found")
                self.logger.warning(f"No results table found for search term: {search_term}")
                return businesses
            
            # Extract business information
            rows = results_table.query_selector_all("tr")
            print(f"Found {len(rows)} rows in results table")
            
            # Skip header row (index 0)
            for i in range(1, len(rows)):
                row = rows[i]
                try:
                    # Get the business information from the row
                    cells = row.query_selector_all("td")
                    if len(cells) >= 3:
                        # Usually: ID in cell[0], Name in cell[1], Select button in cell[2]
                        business_id = cells[0].text_content().strip()
                        business_name = cells[1].text_content().strip()
                        
                        # Find the row index and business name for later clicking
                        if business_name and len(business_name) > 1:
                            businesses.append({
                                'name': business_name,
                                'business_id': business_id,
                                'row_index': i
                            })
                            print(f"  ✅ Found: {business_name} (ID: {business_id})")
                            
                except Exception as e:
                    self.logger.warning(f"Error processing row {i}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error extracting business links: {e}")
            self.save_error_log(search_term, f"Business links extraction error: {e}", self.page.content())
        
        return businesses

    def click_business_by_index(self, business_info, search_term):
        """Click on business using row index"""
        print(f"  👆 Clicking on: {business_info['name']}")
        
        try:
            # Find the results table again
            results_table = self.page.query_selector("table.gvResults")
            if not results_table:
                print("  ❌ Results table not found")
                return False
            
            # Get the row by index
            rows = results_table.query_selector_all("tr")
            if len(rows) > business_info['row_index']:
                target_row = rows[business_info['row_index']]
                
                # Find the "Select Business" button in this row
                select_button = target_row.query_selector("input[value='Select Business']")
                if select_button:
                    select_button.click()
                    time.sleep(5)
                    
                    # Check for CAPTCHA on detail page
                    self.check_and_solve_captcha()
                    
                    # Verify we're on a detail page
                    business_id_element = self.page.query_selector("#MainContent_lblEntityID")
                    if business_id_element:
                        print(f"  ✅ Successfully navigated to business detail page")
                        return True
                    else:
                        print(f"  ❌ Failed to reach business detail page")
                        self.save_error_log(search_term, f"Failed to reach detail page for {business_info['name']}", self.page.content())
                        return False
                else:
                    print(f"  ❌ Could not find Select Business button in row")
                    self.save_error_log(search_term, f"Select button not found for {business_info['name']}", self.page.content())
                    return False
            else:
                print(f"  ❌ Row index {business_info['row_index']} not found")
                return False
                
        except Exception as e:
            print(f"  ❌ Error clicking business link: {e}")
            self.save_error_log(search_term, f"Click business error for {business_info['name']}: {e}", self.page.content())
            return False

    def extract_business_details_robust(self, search_term):
        """Extract business details with comprehensive error handling"""
        print("📄 Extracting business details...")
        
        try:
            # Method 1: Try exact element IDs first
            business_data = self.extract_by_element_ids()
            
            # Method 2: If that fails, try table-based extraction
            if not business_data.get('business_name'):
                business_data = self.extract_from_tables()
            
            # Method 3: If still no data, try text-based extraction
            if not business_data.get('business_name'):
                business_data = self.extract_from_page_text()
            
            # Verify we got the essential data
            if business_data.get('business_name') and business_data.get('business_id'):
                print(f"  ✅ Successfully extracted data for: {business_data['business_name']}")
                
                # ✅ USE THE NEW SAFE METHOD
                safe_data, html_fallback = self.safe_extract_json_data(business_data, search_term)
                return safe_data
                
            else:
                print("  ❌ Failed to extract essential business data")
                # Save HTML for debugging using the new method
                html_content = self.page.content()
                error_data = {
                    'html_content': html_content,
                    'error': 'Essential data missing',
                    'timestamp': datetime.now().isoformat(),
                    'search_term': search_term,
                    'status': 'data_extraction_failed'
                }
                
                # ✅ USE THE NEW SAFE METHOD
                safe_data, html_fallback = self.safe_extract_json_data(error_data, search_term)
                return safe_data
                
        except Exception as e:
            print(f"  ❌ Error extracting business details: {e}")
            self.save_error_log(search_term, f"Extraction error: {e}", self.page.content())
            
            error_data = {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'search_term': search_term,
                'status': 'extraction_error'
            }
            return error_data

    def extract_by_element_ids(self):
        """Extract using exact element IDs from Kansas SOS"""
        business_data = {}
        
        business_data['business_id'] = self.get_element_text("#MainContent_lblEntityID")
        business_data['business_name'] = self.get_element_text("#MainContent_lblEntityName")
        business_data['type'] = self.get_element_text("#MainContent_lblEntityType")
        business_data['formation_date'] = self.get_element_text("#MainContent_lblFormationDate")
        business_data['jurisdiction'] = self.get_element_text("#MainContent_lblStateOfOrganization")
        business_data['status'] = self.get_element_text("#MainContent_lblEntityStatus")
        business_data['resident_agent'] = self.get_element_text("#MainContent_lblResidentAgentName")
        business_data['last_reporting_year'] = self.get_element_text("#MainContent_lblLastIROnFile")
        business_data['next_report_due_date'] = self.get_element_text("#MainContent_lblNextIRDue")
        business_data['forfeiture_date'] = self.get_element_text("#MainContent_lblForfeitureDate")
        
        # Extract addresses
        business_data['principal_office_address'] = self.extract_office_address("principal")
        business_data['registered_office_address'] = self.extract_office_address("registered")
        
        return business_data

    def extract_from_tables(self):
        """Extract data from HTML tables"""
        table_data = {}
        try:
            tables = self.page.query_selector_all("table")
            
            for table in tables:
                rows = table.query_selector_all("tr")
                for row in rows:
                    cells = row.query_selector_all("td, th")
                    if len(cells) >= 2:
                        label = cells[0].text_content().strip()
                        value = cells[1].text_content().strip()
                        
                        if label and value:
                            label_lower = label.lower()
                            if any(term in label_lower for term in ['business id', 'entity id']):
                                table_data['business_id'] = value
                            elif any(term in label_lower for term in ['business name', 'entity name']):
                                table_data['business_name'] = value
                            elif any(term in label_lower for term in ['entity type', 'type']):
                                table_data['type'] = value
                            elif 'formation date' in label_lower:
                                table_data['formation_date'] = value
                            elif 'jurisdiction' in label_lower:
                                table_data['jurisdiction'] = value
                            elif 'status' in label_lower:
                                table_data['status'] = value
                            elif 'resident agent' in label_lower:
                                table_data['resident_agent'] = value
                            elif 'last report' in label_lower:
                                table_data['last_reporting_year'] = value
                            elif 'next report' in label_lower:
                                table_data['next_report_due_date'] = value
                            elif 'forfeiture' in label_lower:
                                table_data['forfeiture_date'] = value
        except Exception as e:
            self.logger.warning(f"Table extraction error: {e}")
        
        return table_data

    def extract_from_page_text(self):
        """Extract data by searching through page text"""
        text_data = {}
        try:
            page_text = self.page.content()
            
            patterns = {
                'business_id': [r'Business ID[^>]*>([^<]+)', r'Entity ID[^>]*>([^<]+)'],
                'business_name': [r'Business Name[^>]*>([^<]+)', r'Entity Name[^>]*>([^<]+)'],
                'type': [r'Entity Type[^>]*>([^<]+)', r'Type[^>]*>([^<]+)'],
                'formation_date': [r'Formation Date[^>]*>([^<]+)'],
                'jurisdiction': [r'Jurisdiction[^>]*>([^<]+)'],
                'status': [r'Status[^>]*>([^<]+)'],
                'resident_agent': [r'Resident Agent[^>]*>([^<]+)'],
                'last_reporting_year': [r'Last Report[^>]*>([^<]+)'],
                'next_report_due_date': [r'Next Report[^>]*>([^<]+)'],
                'forfeiture_date': [r'Forfeiture Date[^>]*>([^<]+)']
            }
            
            for field, field_patterns in patterns.items():
                for pattern in field_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        text_data[field] = match.group(1).strip()
                        break
                        
        except Exception as e:
            self.logger.warning(f"Text extraction error: {e}")
        
        return text_data

    def get_element_text(self, selector):
        """Get text content from an element if it exists"""
        try:
            element = self.page.query_selector(selector)
            if element:
                text = element.text_content().strip()
                return text if text else ""
        except:
            pass
        return ""

    def extract_office_address(self, office_type):
        """Extract office address"""
        try:
            address_parts = []
            
            if office_type == "principal":
                address1 = self.get_element_text("#MainContent_lblPOAddress")
                city = self.get_element_text("#MainContent_lblPOAddressCity")
                state = self.get_element_text("#MainContent_lblPOAddressState")
                zip_code = self.get_element_text("#MainContent_lblPOAddressZip")
                
                if address1:
                    address_parts.append(address1)
                if city or state or zip_code:
                    location = f"{city}, {state} {zip_code}".strip(" ,")
                    if location:
                        address_parts.append(location)
                        
            else:  # registered office
                address1 = self.get_element_text("#MainContent_lblROAddress")
                city = self.get_element_text("#MainContent_lblROAddressCity")
                state = self.get_element_text("#MainContent_lblROAddressState")
                zip_code = self.get_element_text("#MainContent_lblROAddressZip")
                
                if address1:
                    address_parts.append(address1)
                if city or state or zip_code:
                    location = f"{city}, {state} {zip_code}".strip(" ,")
                    if location:
                        address_parts.append(location)
            
            return " | ".join(address_parts) if address_parts else ""
            
        except Exception as e:
            self.logger.warning(f"Error extracting {office_type} office address: {e}")
            return ""

    def return_to_search_results(self):
        """Return to search results page"""
        print("  🔄 Returning to search results...")
        try:
            return_btn = self.page.query_selector("#MainContent_btnReturnToSearchResults")
            if return_btn:
                return_btn.click()
            else:
                self.page.go_back()
            time.sleep(4)
            return True
        except Exception as e:
            print(f"  ❌ Error returning to results: {e}")
            return False

    def run_fully_automated_crawler(self):
        """Fully automated crawling with COMPLETE error handling"""
        search_terms = ["AA", "AAB", "AAC", "LLC", "INC", "CORP", "SERVICE", "KANSAS"]
        all_business_data = []
        total_companies_collected = 0
        
        print("🚀 Kansas SOS Business Crawler - 100% COMPLETE WITH ERROR HANDLING")
        print("This version includes full HTML fallback and comprehensive error handling")
        print("="*60)
        
        # Step 1: Navigate to homepage first, then to search page
        if not self.navigate_to_homepage_first():
            self.logger.error("Failed to navigate from homepage to search page - stopping crawler")
            return
        
        for search_term in search_terms:
            print(f"\n{'='*50}")
            print(f"AUTOMATED SEARCH: '{search_term}'")
            print(f"{'='*50}")
            
            # Step 2: Automated search setup
            if not self.automated_search_setup(search_term):
                print(f"❌ Failed to set up search for '{search_term}'")
                self.save_error_log(search_term, "Search setup failed", self.page.content())
                continue
            
            # Step 3: Perform search
            if not self.perform_search(search_term):
                print(f"❌ Search failed for '{search_term}'")
                continue
            
            # Step 4: Extract business links from results
            businesses = self.extract_business_links_from_results(search_term)
            
            if not businesses:
                print(f"❌ No businesses found for '{search_term}'")
                # Return to search page for next term
                try:
                    self.page.goto("https://www.sos.ks.gov/eforms/BusinessEntity/Search.aspx")
                    time.sleep(3)
                    self.check_and_solve_captcha()
                except Exception as e:
                    self.logger.error(f"Failed to return to search page: {e}")
                continue
            
            print(f"📊 Found {len(businesses)} businesses for '{search_term}'")
            
            # Process businesses (limit to 3 per search term to avoid too many requests)
            companies_processed = 0
            for i, business in enumerate(businesses[:3]):
                print(f"\n  {i+1}/{min(3, len(businesses))}: {business['name']}")
                
                # Click on the business link
                if self.click_business_by_index(business, search_term):
                    # Extract business details WITH ERROR HANDLING
                    details = self.extract_business_details_robust(search_term)
                    
                    if details and isinstance(details, dict):
                        # Save individual file WITH ERROR HANDLING
                        if 'business_name' in details and details['business_name']:
                            clean_name = re.sub(r'[^\w]', '_', details['business_name'])[:30]
                            filename = f"json/business_{clean_name}.json"
                        else:
                            clean_name = f"error_{search_term}_{datetime.now().strftime('%H%M%S')}"
                            filename = f"json/{clean_name}.json"

                        # ✅ USE THE ENHANCED SAVE METHOD
                        saved_file = self.save_data_with_fallback(details, filename)
                        
                        if details.get('status') == 'success':
                            all_business_data.append(details)
                            companies_processed += 1
                            total_companies_collected += 1
                            print(f"    ✅ Saved: {details.get('business_name', 'Unknown')}")
                            print(f"    📊 Extracted: ID={details.get('business_id')}, Type={details.get('type')}, Status={details.get('status')}")
                        else:
                            print(f"    ⚠️  Saved with errors: {filename}")
                    else:
                        print(f"    ❌ Failed to extract valid data for: {business['name']}")
                        self.save_error_log(search_term, f"Invalid data for {business['name']}", self.page.content())
                    
                    # Return to results for next business
                    if i < len(businesses[:3]) - 1:
                        if not self.return_to_search_results():
                            break
                else:
                    print(f"    ❌ Failed to click on: {business['name']}")
            
            print(f"📈 Processed {companies_processed} companies for '{search_term}'")
            
            # Return to search page for next term
            if search_term != search_terms[-1]:
                print("\n🔄 Returning to search page for next term...")
                try:
                    self.page.goto("https://www.sos.ks.gov/eforms/BusinessEntity/Search.aspx")
                    time.sleep(3)
                    
                    # Check for CAPTCHA when returning to search page
                    self.check_and_solve_captcha()
                except Exception as e:
                    self.logger.error(f"Failed to navigate to search page: {e}")
        
        # Save all collected data with error handling
        if all_business_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            combined_filename = f"all_businesses_{timestamp}.json"
            
            try:
                # Save combined data
                combined_data = {
                    'total_companies': len(all_business_data),
                    'search_terms_used': search_terms,
                    'extraction_date': datetime.now().isoformat(),
                    'companies': all_business_data
                }
                
                self.save_data_with_fallback(combined_data, combined_filename)
                
                print(f"\n🎉 CRAWLING COMPLETED SUCCESSFULLY!")
                print(f"📁 Total business records collected: {total_companies_collected}")
                print(f"📁 Individual JSON files: {len(all_business_data)}")
                print(f"📁 Combined file: {combined_filename}")
                print(f"📁 All data saved in: {self.output_dir}/")
                
                # Show final summary
                print(f"\n📊 FINAL RESULTS SUMMARY:")
                unique_companies = len(all_business_data)
                print(f"  ✅ Unique companies collected: {unique_companies}")
                print(f"  ✅ Search terms processed: {len(search_terms)}")
                
                # Show directory structure
                print(f"\n📁 OUTPUT DIRECTORY STRUCTURE:")
                print(f"  {self.output_dir}/")
                print(f"  ├── json/ (successful JSON files)")
                print(f"  ├── html_fallback/ (HTML when JSON fails)")
                print(f"  ├── errors/ (detailed error logs)")
                print(f"  ├── crawler.log (comprehensive log)")
                print(f"  └── {combined_filename} (combined data)")
                
                # Show sample of collected companies
                print(f"\n📊 SAMPLE OF COLLECTED COMPANIES:")
                success_companies = [biz for biz in all_business_data if biz.get('status') == 'success']
                for i, biz in enumerate(success_companies[:5], 1):
                    print(f"  {i}. {biz['business_name']} - {biz.get('type', 'Unknown')} - {biz.get('status', 'Unknown')}")
                    
            except Exception as e:
                self.logger.error(f"Failed to save combined data: {e}")
                print(f"❌ Error saving combined data: {e}")
        else:
            print(f"\n❌ No business data collected")
            self.logger.warning("No business data collected during crawling session")
        
        # Final status report
        print(f"\n📋 CRAWLING SESSION COMPLETED")
        print(f"📁 Check {self.output_dir}/ for all output files")
        print(f"📁 Check {self.output_dir}/crawler.log for detailed logs")
        print(f"📁 Check {self.output_dir}/errors/ for any errors encountered")
        
        self.close()

    def close(self):
        """Close browser with error handling"""
        try:
            self.context.close()
            self.browser.close()
            self.playwright.stop()
            self.logger.info("Browser closed successfully")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

def main():
    print("Kansas SOS Business Crawler - 100% COMPLETE")
    print("Includes full error handling and HTML fallback system")
    print("Will automatically search for: AA, AAB, AAC, LLC, INC, CORP, SERVICE, KANSAS")
    print("You only need to solve CAPTCHAs when prompted")
    print("Navigation: Homepage → Business Search")
    print("="*60)
    
    crawler = KansasSOSCrawler(headless=False)
    
    try:
        crawler.run_fully_automated_crawler()
    except KeyboardInterrupt:
        print("\n⏹️ Crawling stopped by user")
        crawler.logger.info("Crawling stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        crawler.logger.error(f"Unexpected error in main: {e}")
    finally:
        crawler.close()

if __name__ == "__main__":
    main()