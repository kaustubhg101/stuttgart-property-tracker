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

    # 1. Get API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("❌ No GEMINI_API_KEY found! Make sure it is set in GitHub Secrets.")
        exit(1)

    # 2. Configure Gemini
    genai.configure(api_key=api_key)
        
    tools = [{'google_search': {}}] 
    
    model = "gemini-3-pro-preview"

     
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(        
        tools=tools,
        response_mime_type="application/json",
    )
    

    # 3. Define the Agent Prompt
    # We ask for a specific JSON structure to ensure the frontend can read it.
    prompt = """
    You are a Real Estate Data Extraction Agent.
    
    Task:
    1. Search the web for currently available real estate listings for sale ("Immobilien kaufen") in: 
       Stuttgart, Böblingen, Sindelfingen, Ludwigsburg, Filderstadt.
    2. Focus strictly on these banking portals: 
       - Kreissparkasse Böblingen (kskbb.de)
       - Volksbank Stuttgart (vbs.immo)
       - BW Bank / Sparkasse Stuttgart (bw-bank.de)
       - LBS Südwest (lbs.de)
    3. Criteria: Price €200k - €900k, Area > 60 m².
    4. Find 12-15 unique, recent listings. Do not include sold properties.

    Format the output as a strict valid JSON object with a single key "properties".
    Schema:
    {
      "properties": [
        {
          "title": "String (German title)",
          "price": Number (integer, no symbols),
          "area": Number (float, no symbols),
          "rooms": Number,
          "location": "String",
          "source": "sparkasse" | "volksbank" | "lbs",
          "daysOnMarket": Number (estimate, default 2),
          "yearBuilt": Number (use 2000 if unknown),
          "heatingType": "String",
          "features": ["String", "String"],
          "url": "String (must be a valid URL)",
          "scrapedAt": "ISO Date String"
        }
      ]
    }
    
    IMPORTANT: 
    - Return ONLY the JSON. 
    - Do NOT invent data. If a field like yearBuilt is missing, use null.
    - Ensure 'price' and 'area' are numbers, not strings.
    - Do not use markdown formatting (no ```json code blocks).
    """
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]

    # 4. Run the Search & Generation
    try:
        logger.info("🤖 Asking Gemini to search and structure data...")
        
        # Explicitly request JSON response mimetype if supported, otherwise rely on prompt
        response = model.generate_content(prompt)
        
        # 5. Clean and Parse JSON
        raw_text = response.text
        
        # Clean up any potential Markdown formatting Gemini might still add
        clean_json = raw_text.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json.replace("```json", "", 1)
        if clean_json.startswith("```"):
            clean_json = clean_json.replace("```", "", 1)
        if clean_json.endswith("```"):
            clean_json = clean_json.replace("```", "", 1)
            
        clean_json = clean_json.strip()
        
        data = json.loads(clean_json)
        properties = data.get("properties", [])
        
        if not properties:
            logger.warning("⚠️ Gemini returned valid JSON but no properties list.")
            exit(1)

        # Add timestamp if missing
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

    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse JSON from Gemini: {e}")
        logger.error(f"Raw response: {raw_text[:500]}...") # Log start of response for debug
        exit(1)
    except Exception as e:
        logger.error(f"❌ Gemini Agent failed: {e}")
        exit(1)

if __name__ == '__main__':
    main()
