# Stuttgart Property Scraper - Selenium Agent Implementation
# Runs on GitHub Actions, uses Headless Chrome to interact with bank portals

import json
import time
import logging
import random
import os
import re
from datetime import datetime
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PropertyAgent:
    def __init__(self):
        self.driver = self._setup_driver()
        
    def _setup_driver(self):
        """Setup headless Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run invisible
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Use webdriver_manager to automatically install the correct driver
        driver_path = ChromeDriverManager().install()
        
        # FIX: webdriver_manager 4.x sometimes returns the wrong file (THIRD_PARTY_NOTICES)
        # We manually correct it to point to the actual binary 'chromedriver' in the same directory
        if "THIRD_PARTY_NOTICES" in driver_path:
            logger.info(f"⚠️ WebDriverManager returned invalid path: {driver_path}")
            driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver")
            logger.info(f"🔧 Corrected driver path to: {driver_path}")
            
            # Ensure it is executable
            try:
                st = os.stat(driver_path)
                os.chmod(driver_path, st.st_mode | 0o111)
            except Exception as e:
                logger.warning(f"Could not chmod driver: {e}")

        service = Service(driver_path)
        return webdriver.Chrome(service=service, options=chrome_options)

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

    def handle_cookie_banner(self):
        """Try to click 'Accept' or 'Decline' on cookie banners"""
        try:
            # Common selectors for cookie buttons on Sparkasse/Bank sites
            cookie_selectors = [
                "button[id*='cookie']", 
                "button[class*='cookie']",
                "a[class*='cookie']",
                "button[title*='Zustimmen']",
                "button:contains('Akzeptieren')",
                "cc-button"
            ]
            
            for selector in cookie_selectors:
                try:
                    element = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    element.click()
                    logger.info("🍪 Cookie banner handled.")
                    time.sleep(1)
                    return
                except:
                    continue
        except Exception as e:
            logger.warning(f"⚠️ Could not handle cookie banner (might not exist): {e}")

    def search_ksk_boeblingen(self, min_price=None, min_area=None):
        """Agent behavior for KSK Böblingen"""
        url = "https://www.kskbb.de/de/home/privatkunden/immobilien/immobilie-kaufen.html"
        logger.info(f"🕵️ Agent opening: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(3) # Wait for initial load
            self.handle_cookie_banner()
            
            # 1. Input Parameters (Example interaction - placeholder for future)
            if min_price:
                pass 
                
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "expose")) # 'expose' is common wrapper class
            )
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"⚠️ Navigation/Interaction issue: {e}")
        
        # 2. Extract Data
        return self.extract_page_source("kskbb")

    def extract_page_source(self, source_name):
        """Parse the rendered HTML with BeautifulSoup"""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        results = []
        
        # Generic scraper for typical property card structures
        cards = soup.find_all('div', class_=lambda x: x and ('expose' in x or 'property' in x or 'objekt' in x))
        
        for card in cards:
            try:
                title_elem = card.find(['h2', 'h3', 'h4'])
                if not title_elem: continue
                
                title = title_elem.get_text(strip=True)
                
                # Extract Price
                price = 0
                price_text = card.find(string=lambda s: s and '€' in s)
                if price_text:
                    clean_price = ''.join(filter(str.isdigit, price_text))
                    if clean_price: price = int(clean_price)
                
                # Extract Area
                area = 0
                area_text = card.find(string=lambda s: s and 'm²' in s)
                if area_text:
                    clean_area = area_text.replace('.', '').replace(',', '.')
                    match = re.search(r'(\d+)', clean_area)
                    if match: area = float(match.group(1))

                link_elem = card.find('a')
                link = link_elem['href'] if link_elem else ""
                if link and not link.startswith('http'):
                    link = "https://www.kskbb.de" + link

                results.append({
                    "title": title,
                    "price": price,
                    "area": area,
                    "location": "Böblingen District", # Placeholder
                    "source": source_name,
                    "url": link,
                    "scrapedAt": datetime.now().isoformat()
                })
            except Exception as e:
                continue
                
        logger.info(f"✅ Extracted {len(results)} properties from {source_name}")
        return results

def main():
    agent = PropertyAgent()
    all_properties = []
    
    try:
        # Run KSK Böblingen Search
        ksk_props = agent.search_ksk_boeblingen(min_price=200000)
        all_properties.extend(ksk_props)
        
        # Future banks can be added here
        
    except Exception as e:
        logger.error(f"❌ Scraper Agent failed: {e}")
        
    finally:
        agent.close()

    # Save Results - NO FALLBACKS
    output_file = 'properties_cache.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'properties': all_properties,
                'lastUpdated': datetime.now().isoformat(),
                'totalCount': len(all_properties)
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Saved {len(all_properties)} properties")
    except Exception as e:
        logger.error(f"Failed to write output file: {e}")

if __name__ == '__main__':
    main()
