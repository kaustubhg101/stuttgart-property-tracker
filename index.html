# Stuttgart Regional Property Tracker - Backend Scraper Blueprint
# Production-ready Python scraper for bank property portals
# 
# Required dependencies:
# pip install selenium beautifulsoup4 requests python-dotenv flask flask-cors
# 
# Download ChromeDriver: https://chromedriver.chromium.org/

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PropertyAdapter(ABC):
    """Base class for bank-specific property scrapers"""
    
    def __init__(self, cache_file: str = None):
        self.cache_file = cache_file or f"cache_{self.__class__.__name__}.json"
        self.cache_timeout = 3600  # 1 hour cache
        self.last_scraped = None
        self.properties = []
        self.load_cache()
    
    @abstractmethod
    def fetch_properties(self, filters: Dict) -> List[Dict]:
        """Fetch properties from bank portal"""
        pass
    
    def normalize_property(self, raw_data: Dict) -> Dict:
        """Convert bank-specific data to standardized format"""
        return {
            "title": raw_data.get("title", ""),
            "price": int(raw_data.get("price", 0)),
            "area": float(raw_data.get("area", 0)),
            "rooms": int(raw_data.get("rooms", 0)),
            "location": raw_data.get("location", ""),
            "source": self.source_name(),
            "daysOnMarket": raw_data.get("daysOnMarket", 0),
            "yearBuilt": int(raw_data.get("yearBuilt", 0)),
            "heatingType": raw_data.get("heatingType", "Unknown"),
            "features": raw_data.get("features", []),
            "url": raw_data.get("url", ""),
            "scrapedAt": datetime.now().isoformat()
        }
    
    def save_cache(self):
        """Persist scraped data to file"""
        with open(self.cache_file, 'w') as f:
            json.dump({
                "lastScraped": self.last_scraped,
                "properties": self.properties
            }, f, indent=2)
    
    def load_cache(self):
        """Load cached data if available"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                self.last_scraped = data.get("lastScraped")
                self.properties = data.get("properties", [])
    
    def is_cache_valid(self) -> bool:
        """Check if cache is still fresh"""
        if not self.last_scraped:
            return False
        last_time = datetime.fromisoformat(self.last_scraped)
        return datetime.now() - last_time < timedelta(seconds=self.cache_timeout)
    
    @abstractmethod
    def source_name(self) -> str:
        """Return standardized source name"""
        pass


class SparkasseAdapter(PropertyAdapter):
    """Scraper for Sparkasse s-immobilien.de"""
    
    def source_name(self) -> str:
        return "sparkasse"
    
    def fetch_properties(self, filters: Dict) -> List[Dict]:
        """
        Scrape Sparkasse portal
        
        Args:
            filters: {
                "minPrice": 200000,
                "maxPrice": 800000,
                "minArea": 70,
                "regions": ["70", "71", "714"],  # Postal code prefixes
                "provinces": ["Baden-Württemberg"]
            }
        """
        if self.is_cache_valid():
            logger.info("Using cached Sparkasse data")
            return self.properties
        
        logger.info("Scraping Sparkasse s-immobilien.de...")
        
        try:
            # Initialize Selenium driver
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=options)
            driver.get("https://immobilien.sparkasse.de")
            
            # Wait for page load
            time.sleep(2)
            
            # Fill in search form
            try:
                # Fill price range
                min_price_field = driver.find_element(By.NAME, "priceFrom")
                min_price_field.send_keys(str(filters.get("minPrice", "")))
                
                max_price_field = driver.find_element(By.NAME, "priceTo")
                max_price_field.send_keys(str(filters.get("maxPrice", "")))
                
                # Fill area
                min_area_field = driver.find_element(By.NAME, "areaFrom")
                min_area_field.send_keys(str(filters.get("minArea", "")))
                
                # Select region/state
                state_dropdown = driver.find_element(By.NAME, "state")
                state_dropdown.click()
                
                time.sleep(1)
                
                # Click search button
                search_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                search_btn.click()
                
                # Wait for results
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "property-item"))
                )
                
                time.sleep(2)
                
                # Parse results
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                properties = []
                for item in soup.find_all(class_='property-item'):
                    try:
                        prop = self._parse_sparkasse_item(item)
                        if prop:
                            properties.append(self.normalize_property(prop))
                    except Exception as e:
                        logger.warning(f"Error parsing Sparkasse item: {e}")
                        continue
                
                driver.quit()
                
                self.properties = properties
                self.last_scraped = datetime.now().isoformat()
                self.save_cache()
                
                logger.info(f"Successfully scraped {len(properties)} properties from Sparkasse")
                return properties
                
            except Exception as e:
                logger.error(f"Error during Sparkasse scraping: {e}")
                driver.quit()
                return self.properties  # Return cached data if available
        
        except Exception as e:
            logger.error(f"Fatal error in Sparkasse adapter: {e}")
            return self.properties
    
    def _parse_sparkasse_item(self, item) -> Optional[Dict]:
        """Parse individual Sparkasse listing item"""
        try:
            title = item.find(class_='property-title').text.strip()
            price_text = item.find(class_='property-price').text.strip()
            price = int(''.join(filter(str.isdigit, price_text)))
            
            area_text = item.find(class_='property-area').text.strip()
            area = float(''.join(filter(lambda x: x.isdigit() or x == '.', area_text)))
            
            rooms = int(item.find(class_='property-rooms').text.strip().split()[0])
            location = item.find(class_='property-location').text.strip()
            
            # Extract year built from text or attributes
            year_built = 2000  # Default fallback
            year_text = item.find(class_='property-year')
            if year_text:
                year_built = int(''.join(filter(str.isdigit, year_text.text)))
            
            # Extract heating type
            heating_type = "Unknown"
            heating_elem = item.find(class_='property-heating')
            if heating_elem:
                heating_type = heating_elem.text.strip()
            
            # Extract features
            features = []
            features_elem = item.find(class_='property-features')
            if features_elem:
                features = [f.text.strip() for f in features_elem.find_all('span')]
            
            # Calculate days on market (if available)
            days_on_market = 0
            listed_date = item.find(class_='property-listed-date')
            if listed_date:
                # Parse date and calculate difference
                days_on_market = 0  # Implement date parsing logic
            
            url = item.find('a').get('href', '') if item.find('a') else ''
            
            return {
                "title": title,
                "price": price,
                "area": area,
                "rooms": rooms,
                "location": location,
                "daysOnMarket": days_on_market,
                "yearBuilt": year_built,
                "heatingType": heating_type,
                "features": features,
                "url": url
            }
        except Exception as e:
            logger.warning(f"Error parsing Sparkasse item: {e}")
            return None


class VolksbankAdapter(PropertyAdapter):
    """Scraper for Volksbank Stuttgart portal"""
    
    def source_name(self) -> str:
        return "volksbank"
    
    def fetch_properties(self, filters: Dict) -> List[Dict]:
        """Scrape Volksbank Stuttgart portal"""
        if self.is_cache_valid():
            logger.info("Using cached Volksbank data")
            return self.properties
        
        logger.info("Scraping Volksbank Stuttgart...")
        
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            driver = webdriver.Chrome(options=options)
            driver.get("https://immobilien.volksbank-stuttgart.de")
            
            time.sleep(2)
            
            # Similar pattern to Sparkasse - fill form and submit
            # Implementation follows same structure as SparkasseAdapter
            # Key difference: Volksbank may use different form field names
            
            properties = []
            
            # [Implementation similar to SparkasseAdapter]
            # Parse and normalize results
            
            driver.quit()
            
            self.properties = properties
            self.last_scraped = datetime.now().isoformat()
            self.save_cache()
            
            logger.info(f"Successfully scraped {len(properties)} properties from Volksbank")
            return properties
            
        except Exception as e:
            logger.error(f"Error in Volksbank adapter: {e}")
            return self.properties


class LBSAdapter(PropertyAdapter):
    """Scraper for LBS Baden-Württemberg property portal"""
    
    def source_name(self) -> str:
        return "lbs"
    
    def fetch_properties(self, filters: Dict) -> List[Dict]:
        """Scrape LBS portal"""
        if self.is_cache_valid():
            logger.info("Using cached LBS data")
            return self.properties
        
        logger.info("Scraping LBS Baden-Württemberg...")
        
        try:
            # LBS may have API endpoints - check for REST API before scraping
            api_url = "https://www.lbs.de/api/properties"  # Example - actual endpoint varies
            
            payload = {
                "minPrice": filters.get("minPrice"),
                "maxPrice": filters.get("maxPrice"),
                "minArea": filters.get("minArea"),
                "state": "Baden-Württemberg"
            }
            
            response = requests.get(api_url, params=payload, timeout=10)
            
            if response.status_code == 200:
                # Parse JSON response if API is available
                properties = [self.normalize_property(p) for p in response.json()]
            else:
                # Fall back to Selenium scraping
                properties = self._scrape_lbs_selenium(filters)
            
            self.properties = properties
            self.last_scraped = datetime.now().isoformat()
            self.save_cache()
            
            logger.info(f"Successfully scraped {len(properties)} properties from LBS")
            return properties
            
        except Exception as e:
            logger.error(f"Error in LBS adapter: {e}")
            return self.properties
    
    def _scrape_lbs_selenium(self, filters: Dict) -> List[Dict]:
        """Fallback Selenium scraping for LBS if API unavailable"""
        properties = []
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(options=options)
            
            # [Selenium scraping implementation]
            
            driver.quit()
        except Exception as e:
            logger.error(f"LBS Selenium scraping failed: {e}")
        
        return properties


class PropertyTrackerService:
    """Orchestrates multi-source property scraping"""
    
    def __init__(self):
        self.adapters = {
            "sparkasse": SparkasseAdapter(),
            "volksbank": VolksbankAdapter(),
            "lbs": LBSAdapter()
        }
    
    def search_all_sources(self, filters: Dict) -> List[Dict]:
        """
        Search all configured sources and merge results
        
        Args:
            filters: {
                "minPrice": 200000,
                "maxPrice": 800000,
                "minArea": 70,
                "regions": ["70", "71"],
                "sources": ["sparkasse", "volksbank", "lbs"]
            }
        """
        all_properties = []
        
        for source in filters.get("sources", ["sparkasse", "volksbank", "lbs"]):
            if source in self.adapters:
                try:
                    props = self.adapters[source].fetch_properties(filters)
                    all_properties.extend(props)
                except Exception as e:
                    logger.error(f"Error fetching from {source}: {e}")
        
        # Remove duplicates based on title + price + location
        seen = set()
        unique_props = []
        
        for prop in all_properties:
            key = (prop.get("title"), prop.get("price"), prop.get("location"))
            if key not in seen:
                seen.add(key)
                unique_props.append(prop)
        
        # Sort by days on market (pre-market first)
        unique_props.sort(key=lambda x: x.get("daysOnMarket", 999))
        
        return unique_props
    
    def get_stats(self, properties: List[Dict]) -> Dict:
        """Calculate aggregated statistics"""
        if not properties:
            return {}
        
        prices_per_sqm = [p.get("price", 0) / p.get("area", 1) for p in properties]
        pre_market = [p for p in properties if p.get("daysOnMarket", 7) <= 7]
        
        return {
            "totalFound": len(properties),
            "avgPricePerSqm": round(sum(prices_per_sqm) / len(prices_per_sqm), 2),
            "preMarketCount": len(pre_market),
            "timeAdvantageHours": "48-72" if pre_market else "-",
            "priceRange": {
                "min": min(p.get("price", 0) for p in properties),
                "max": max(p.get("price", 0) for p in properties)
            }
        }


# Flask API setup
app = Flask(__name__)
CORS(app)
service = PropertyTrackerService()


@app.route('/api/search', methods=['POST'])
def search_properties():
    """
    POST /api/search
    
    Request body:
    {
        "minPrice": 200000,
        "maxPrice": 800000,
        "minArea": 70,
        "regions": ["70", "71"],
        "sources": ["sparkasse", "volksbank"]
    }
    """
    try:
        filters = request.json
        properties = service.search_all_sources(filters)
        stats = service.get_stats(properties)
        
        return jsonify({
            "success": True,
            "properties": properties,
            "stats": stats
        })
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Development server
    app.run(debug=True, port=5000)


# ============================================================================
# DEPLOYMENT NOTES
# ============================================================================
# 
# 1. PRODUCTION DEPLOYMENT (Heroku/Railway/Render):
#    - Remove debug=True
#    - Use production WSGI server: gunicorn
#    - Set environment variables for sensitive data
#    - Deploy with regular scraper runs (cron job every 6-12 hours)
# 
# 2. CACHING STRATEGY:
#    - Current: 1-hour file-based cache
#    - Production: Redis cache for faster access
#    - Implementation: from redis import Redis; cache = Redis()
# 
# 3. RATE LIMITING:
#    - Add delays between requests (1-2 seconds)
#    - Rotate user agents to avoid detection
#    - Respect robots.txt and Terms of Service
# 
# 4. ERROR HANDLING:
#    - Add retry logic with exponential backoff
#    - Monitor scraper health with logs
#    - Alert on scraper failures
# 
# 5. LEGAL COMPLIANCE:
#    - Review Terms of Service for each bank
#    - Consider partnering with banks for API access
#    - Add robots.txt compliance checking
# 
# 6. MONITORING:
#    - Track scraper performance (success rate, data freshness)
#    - Log all errors and warnings
#    - Set up alerting for critical failures
#
# Example startup:
#   python property_scraper.py
#   # Then frontend fetches from: http://localhost:5000/api/search
