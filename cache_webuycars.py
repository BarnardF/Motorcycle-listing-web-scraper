"""
WeBuyCars Cache Generator (Playwright API Interception)
Fetches ALL motorcycle listings from WeBuyCars API and stores them locally.
Uses Playwright to intercept API responses - much faster and more reliable than DOM scraping.
Used ai(Claude) to help write this code after many, many, many hours of strugling to figure this shit out.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright
from logger.logger import logger
from config.config import WEBUYCARS_CACHE_FILE, WEBUYCARS_BASE_URL, API_KEYWORDS

SOURCE = "WeBuyCars"


def fetch_all_listings():
    """
    Fetch all WeBuyCars motorcycle listings by intercepting API responses.
    Uses Playwright to handle pagination and capture JSON data directly.
    """
    logger.info(f"[{SOURCE}] Starting cache refresh...")
    logger.info(f"[{SOURCE}] Using Playwright to intercept API responses")
    
    all_listings = {}
    page_num = 1
    max_pages = 100  # Safety limit
    
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True, args=["--no-sandbox"])
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 OPR/123.0.0.0",
            viewport={"width": 1920, "height": 1080},
            locale="en-ZA",
        )
        page = context.new_page()
        
        # Track API responses for each page
        page_listings = {}
        api_response_count = 0
        
        def handle_response(response):
            """Capture and process API responses"""
            nonlocal api_response_count
            
            if API_KEYWORDS in response.url:
                api_response_count += 1
                logger.debug(f"[{SOURCE}] API Response #{api_response_count}: status={response.status}")
                
                # Only process 200 responses with valid data
                if response.status != 200:
                    logger.debug(f"[{SOURCE}] Skipping non-200 response (status: {response.status})")
                    return
                
                try:
                    json_resp = response.json()
                except Exception as json_err:
                    logger.debug(f"[{SOURCE}] Could not parse JSON: {json_err}")
                    return
                
                data = json_resp.get("data", [])
                
                if not data:
                    logger.debug(f"[{SOURCE}] API returned empty data array")
                    return
                
                logger.info(f"[{SOURCE}] API Response: Found {len(data)} listing(s)")
                
                for item in data:
                    try:
                        make = item.get("Make", "Unknown")
                        model = item.get("Model", "Unknown")
                        vehicle_id = item.get("StockNumber", "N/A")
                        
                        # Skip if no stock number
                        if vehicle_id == "N/A":
                            continue
                        
                        price = item.get("Price", item.get("BuyNowPrice", "N/A"))
                        km = item.get("Mileage", "N/A")
                        location = item.get("DealerKey", "N/A")
                        description = item.get("OnlineDescription", "N/A")
                        
                        # Construct reliable URL
                        url = f"https://www.webuycars.co.za/buy-a-car/{make}/{model}/{vehicle_id}"
                        
                        # Use StockNumber as unique ID
                        listing_id = f"{SOURCE.lower()}_{vehicle_id}"
                        
                        # Store in both all_listings and page_listings
                        listing_data = {
                            'vehicle_id': vehicle_id,
                            'title': description,
                            'price': price,
                            'url': url,
                            'make': make,
                            'model': model,
                            'source': SOURCE,
                            'kilometers': km,
                            'location': location
                        }
                        
                        all_listings[listing_id] = listing_data
                        page_listings[listing_id] = listing_data
                        
                    except Exception as e:
                        logger.debug(f"[{SOURCE}] Error processing listing: {e}")
                        continue
        
        page.on("response", handle_response)
        
        # Fetch all pages
        try:
            consecutive_empty_pages = 0
            
            while page_num <= max_pages:
                page_url = f'{WEBUYCARS_BASE_URL}&page={page_num}'
                logger.info(f"[{SOURCE}] Fetching page {page_num}...")
                
                # Reset page listings tracker
                page_listings.clear()
                api_response_count = 0
                
                try:
                    page.goto(page_url, wait_until="domcontentloaded", timeout=15000)
                except Exception as goto_err:
                    logger.warning(f"[{SOURCE}] Page {page_num} navigation error: {goto_err}")
                
                # Wait for API responses (give it time to be intercepted)
                # Skip the first error response (status 400), wait for the real one (status 200)
                max_wait = 0
                while max_wait < 8 and api_response_count < 2:  # Wait for 2 responses (400 + 200)
                    page.wait_for_timeout(500)
                    max_wait += 0.5
                
                # Check if we got listings on this page
                if not page_listings:
                    consecutive_empty_pages += 1
                    logger.info(f"[{SOURCE}] Page {page_num}: No listings (empty page {consecutive_empty_pages})")
                    
                    # Stop after 2 consecutive empty pages
                    if consecutive_empty_pages >= 2:
                        logger.info(f"[{SOURCE}] Stopping: {consecutive_empty_pages} consecutive empty pages")
                        break
                else:
                    consecutive_empty_pages = 0
                    logger.info(f"[{SOURCE}] Page {page_num}: +{len(page_listings)} listings (total: {len(all_listings)})")
                
                page_num += 1
                time.sleep(1)  # Respectful delay between requests
        
        except Exception as e:
            logger.warning(f"[{SOURCE}] Error during pagination: {e}")
        
        finally:
            browser.close()
            logger.info(f"[{SOURCE}] Browser closed")
    
    return all_listings

def save_cache(listings):
    """Save listings to cache file with timestamp"""
    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'date_formatted': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'total_listings': len(listings),
        'listings': listings
    }
    
    try:
        with open(WEBUYCARS_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[{SOURCE}] Cache saved: {WEBUYCARS_CACHE_FILE}")
        logger.info(f"[{SOURCE}] Total listings cached: {len(listings)}")
        return True
    except Exception as e:
        logger.error(f"[{SOURCE}] Failed to save cache: {e}")
        return False

def load_cache():
    """Load existing cache for comparison"""
    try:
        if Path(WEBUYCARS_CACHE_FILE).exists():
            with open(WEBUYCARS_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('listings', {})
    except Exception as e:
        logger.error(f"[{SOURCE}] Failed to load existing cache: {e}")
    return {}

def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("🏍️  WEBUYCARS CACHE REFRESH")
    logger.info("=" * 60)
    
    # Load previous cache
    previous_listings = load_cache()
    previous_count = len(previous_listings)
    
    # Fetch all listings via API interception
    new_listings = fetch_all_listings()
    
    if not new_listings:
        logger.error(f"[{SOURCE}] Failed to fetch any listings. Cache not updated.")
        return False
    
    # Save cache
    success = save_cache(new_listings)
    
    if success:
        logger.info("=" * 60)
        logger.info(f"✅ CACHE REFRESH COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Previous listings: {previous_count}")
        logger.info(f"Current listings:  {len(new_listings)}")
        logger.info(f"Difference: {len(new_listings) - previous_count:+d}")
        return True
    
    return False

if __name__ == "__main__":
    main()