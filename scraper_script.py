# Stuttgart Property Scraper - Gemini AI Implementation
# Uses Google Gemini with Search Grounding to find and structure property data

import os
import json
import logging
import google.generativeai as genai
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("🚀 Starting Gemini Property Agent...")

    # 1. Get API Key from Environment Variable (Safe for Public Repos)
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        logger.error("❌ No GEMINI_API_KEY found! Make sure it is set in GitHub Secrets.")
        return # Exit gracefully

    # 2. Configure Gemini
    genai.configure(api_key=api_key)
    
    # Use the model that supports Google Search grounding
    # Note: 'gemini-2.0-flash-exp' is current experimental, falling back to 1.5-pro or flash if needed
    model = genai.GenerativeModel(
        'gemini-2.0-flash-exp', 
        tools='google_search_retrieval'
    )

    # 3. Define the Agent Prompt
    prompt = """
    You are a Real Estate Data Extraction Agent.
    
    Task:
    1. Search the web for current real estate listings for sale ("Immobilien kaufen") in: Stuttgart, Böblingen, Sindelfingen, Ludwigsburg, Filderstadt.
    2. Focus strictly on these banking portals: 
       - Kreissparkasse Böblingen (kskbb.de)
       - Volksbank Stuttgart (vbs.immo)
       - BW Bank / Sparkasse Stuttgart (bw-bank.de)
       - LBS Südwest (lbs.de)
    3. Criteria: Price €200k - €900k, Area > 60 m².
    4. Find 10-15 unique, recent listings.

    Format the output as a strict valid JSON object with a single key "properties":
    {
      "properties": [
        {
          "title": "String",
          "price": Number (no symbols),
          "area": Number (no symbols),
          "rooms": Number,
          "location": "String",
          "source": "sparkasse" | "volksbank" | "lbs",
          "daysOnMarket": Number (estimate based on listing date, default 3),
          "yearBuilt": Number (use 2000 if unknown),
          "heatingType": "String",
          "features": ["String", "String"],
          "url": "String",
          "scrapedAt": "ISO Date String"
        }
      ]
    }
    
    IMPORTANT: Return ONLY the JSON. No markdown formatting.
    """

    # 4. Run the Search & Generation
    try:
        logger.info("🤖 Asking Gemini to search and structure data...")
        response = model.generate_content(prompt)
        
        # 5. Clean and Parse JSON
        raw_text = response.text
        # Remove markdown code blocks if Gemini adds them
        clean_json = raw_text.replace("```json", "").replace("```", "").strip()
        
        data = json.loads(clean_json)
        properties = data.get("properties", [])
        
        # Add timestamp if missing (Gemini usually adds it, but just in case)
        for p in properties:
            if "scrapedAt" not in p:
                p["scrapedAt"] = datetime.now().isoformat()
        
        logger.info(f"✅ Gemini found {len(properties)} properties.")

        # 6. Save to Cache File
        output_file = 'properties_cache.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'properties': properties,
                'lastUpdated': datetime.now().isoformat(),
                'totalCount': len(properties)
            }, f, ensure_ascii=False, indent=2)
            
        logger.info(f"💾 Saved to {output_file}")

    except Exception as e:
        logger.error(f"❌ Gemini Agent failed: {e}")
        # We do NOT save an empty file here to preserve old data if the API fails
        exit(1)

if __name__ == '__main__':
    main()
