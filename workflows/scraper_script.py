# Stuttgart Property Scraper - Lightweight Version
# Runs on GitHub Actions every 6 hours, saves results to JSON
# NO Selenium required - uses requests + BeautifulSoup (fast & lightweight)

import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This is MOCK data - in production, would scrape real sites
# For now, we're using demo data to avoid blocking issues
MOCK_PROPERTIES = [
    {
        "title": "Renovierte 3-Zimmer Wohnung, Süd-West Lage",
        "price": 520000,
        "area": 85,
        "rooms": 3,
        "location": "Stuttgart-Feuerbach, 70469",
        "source": "sparkasse",
        "daysOnMarket": 3,
        "yearBuilt": 1995,
        "heatingType": "Gasheizung",
        "features": ["Balkon", "Parkett", "Renoviert 2023"],
        "url": "https://s-immobilien.de/property/123",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "4-Zimmer Einfamilienhaus mit Garten",
        "price": 675000,
        "area": 140,
        "rooms": 4,
        "location": "Stuttgart-Vaihingen, 70186",
        "source": "volksbank",
        "daysOnMarket": 1,
        "yearBuilt": 2015,
        "heatingType": "Wärmepumpe",
        "features": ["Garten 280m²", "Garage", "Neubau-Standard"],
        "url": "https://vbs.immo/property/456",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Kapitalanlage: 2er Maisonette, zentral",
        "price": 395000,
        "area": 72,
        "rooms": 2,
        "location": "Stuttgart-Mitte, 70173",
        "source": "lbs",
        "daysOnMarket": 5,
        "yearBuilt": 1920,
        "heatingType": "Fernwärme",
        "features": ["Rendite 4,2%", "Denkmalschutz", "Makler"],
        "url": "https://www.lbs.de/property/789",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Villa mit Pool, Hang-Lage",
        "price": 950000,
        "area": 280,
        "rooms": 6,
        "location": "Stuttgart-Zauffenhausen, 70437",
        "source": "sparkasse",
        "daysOnMarket": 2,
        "yearBuilt": 2008,
        "heatingType": "Wärmepumpe",
        "features": ["Pool", "Sauna", "Moderne Smart-Home Technik"],
        "url": "https://s-immobilien.de/property/321",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Wohnung in beliebter Innenstadtlage",
        "price": 445000,
        "area": 68,
        "rooms": 2,
        "location": "Stuttgart-West, 70176",
        "source": "volksbank",
        "daysOnMarket": 4,
        "yearBuilt": 1975,
        "heatingType": "Gasheizung",
        "features": ["Dachterrasse", "High-Speed Internet", "Grüne Umgebung"],
        "url": "https://vbs.immo/property/654",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Reihenhaus modern ausgebaut",
        "price": 580000,
        "area": 110,
        "rooms": 4,
        "location": "Stuttgart-Möhringen, 70435",
        "source": "lbs",
        "daysOnMarket": 6,
        "yearBuilt": 2005,
        "heatingType": "Wärmepumpe",
        "features": ["Doppelgarage", "Keller", "Wärmepumpe"],
        "url": "https://www.lbs.de/property/987",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Modernes Einfamilienhaus in Sindelfingen",
        "price": 625000,
        "area": 135,
        "rooms": 4,
        "location": "Sindelfingen, 71063",
        "source": "sparkasse",
        "daysOnMarket": 2,
        "yearBuilt": 2018,
        "heatingType": "Wärmepumpe",
        "features": ["Energieeffizient KfW 55", "Terrasse", "Carport"],
        "url": "https://kskbb.de/property/201",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Wohnung in Böblingen-Zentrum",
        "price": 485000,
        "area": 92,
        "rooms": 3,
        "location": "Böblingen, 71034",
        "source": "sparkasse",
        "daysOnMarket": 4,
        "yearBuilt": 1985,
        "heatingType": "Gasheizung",
        "features": ["Balkon", "Parklatz", "Treppenhaus renoviert"],
        "url": "https://kskbb.de/property/202",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Einfamilienhaus in Ludwigsburg",
        "price": 720000,
        "area": 165,
        "rooms": 5,
        "location": "Ludwigsburg, 71638",
        "source": "volksbank",
        "daysOnMarket": 1,
        "yearBuilt": 2010,
        "heatingType": "Fernwärme",
        "features": ["Großer Garten", "Doppelgarage", "Kamin"],
        "url": "https://ksklb.de/property/301",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Kapitalanlage Wohnung in Ludwigsburg",
        "price": 350000,
        "area": 65,
        "rooms": 2,
        "location": "Ludwigsburg, 71638",
        "source": "lbs",
        "daysOnMarket": 3,
        "yearBuilt": 1970,
        "heatingType": "Gasheizung",
        "features": ["Rendite 4,8%", "Vermietet", "Sanierungspotential"],
        "url": "https://www.lbs.de/property/302",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Villa Waiblingen, Rems-Murr-Kreis",
        "price": 890000,
        "area": 250,
        "rooms": 6,
        "location": "Waiblingen, 71356",
        "source": "sparkasse",
        "daysOnMarket": 2,
        "yearBuilt": 2003,
        "heatingType": "Wärmepumpe",
        "features": ["Panoramablick", "Pool", "Wellness-Bereich"],
        "url": "https://kskwm.de/property/401",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Doppelhaushälfte Schorndorf",
        "price": 550000,
        "area": 120,
        "rooms": 4,
        "location": "Schorndorf, 73614",
        "source": "volksbank",
        "daysOnMarket": 5,
        "yearBuilt": 2000,
        "heatingType": "Gasheizung",
        "features": ["Garten 200m²", "Terrasse", "Nebengebäude"],
        "url": "https://vrs.immo/property/402",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Moderne Wohnung in Filderstadt",
        "price": 420000,
        "area": 78,
        "rooms": 2,
        "location": "Filderstadt, 70374",
        "source": "volksbank",
        "daysOnMarket": 1,
        "yearBuilt": 2020,
        "heatingType": "Wärmepumpe",
        "features": ["Smart Home", "Balkon Süd", "Tiefgarage"],
        "url": "https://volksbank-filder.de/property/501",
        "scrapedAt": datetime.now().isoformat()
    },
    {
        "title": "Haus zum Mitnehmen in Filderstadt",
        "price": 680000,
        "area": 155,
        "rooms": 5,
        "location": "Filderstadt-Bernhausen, 70374",
        "source": "sparkasse",
        "daysOnMarket": 3,
        "yearBuilt": 1995,
        "heatingType": "Ölheizung",
        "features": ["Sanierungsbedürftig", "Großes Potential", "Ausbaugarten"],
        "url": "https://kskbb.de/property/502",
        "scrapedAt": datetime.now().isoformat()
    }
]


def scrape_sparkasse():
    """Lightweight scraper for Sparkasse - uses requests, not Selenium"""
    try:
        logger.info("Scraping Sparkasse...")
        
        # In production, would use requests + BeautifulSoup:
        # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        # response = requests.get('https://immobilien.sparkasse.de', headers=headers, timeout=10)
        # soup = BeautifulSoup(response.content, 'html.parser')
        # Parse and return properties
        
        # For MVP: return mock data
        return [p for p in MOCK_PROPERTIES if p['source'] == 'sparkasse']
    
    except Exception as e:
        logger.error(f"Sparkasse scraping failed: {e}")
        return []


def scrape_volksbank():
    """Lightweight scraper for Volksbank"""
    try:
        logger.info("Scraping Volksbank...")
        return [p for p in MOCK_PROPERTIES if p['source'] == 'volksbank']
    except Exception as e:
        logger.error(f"Volksbank scraping failed: {e}")
        return []


def scrape_lbs():
    """Lightweight scraper for LBS"""
    try:
        logger.info("Scraping LBS...")
        return [p for p in MOCK_PROPERTIES if p['source'] == 'lbs']
    except Exception as e:
        logger.error(f"LBS scraping failed: {e}")
        return []


def main():
    """Main scraping function - runs on schedule"""
    logger.info("Starting property scraper...")
    
    all_properties = []
    
    # Scrape all sources
    all_properties.extend(scrape_sparkasse())
    all_properties.extend(scrape_volksbank())
    all_properties.extend(scrape_lbs())
    
    # Remove duplicates
    seen = set()
    unique_properties = []
    for prop in all_properties:
        key = (prop.get('title'), prop.get('price'), prop.get('location'))
        if key not in seen:
            seen.add(key)
            unique_properties.append(prop)
    
    logger.info(f"Scraped {len(unique_properties)} unique properties")
    
    # Save to JSON file
    output_file = 'properties_cache.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'properties': unique_properties,
            'lastUpdated': datetime.now().isoformat(),
            'totalCount': len(unique_properties)
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved to {output_file}")
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
