"""
ZABikers Cache Generator
Fetches ALL motorcycle listings from zabikers.co.za and stores them locally.
Uses Playwright to render Vue.js content before scraping.
Run this once daily/weekly, then zabikerstracker.py searches the cache.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from logger.logger import logger

SOURCE = "ZABikers"
ZABIKERS_CACHE_FILE = "data/zabikers_cache.json"
BASE_URL = "https://www.zabikers.co.za/bikes-for-sale/"


def fetch_all_listings():
    """
    Fetch ALL ZABikers motorcycle listings using Playwright.
    Waits for Vue.js to render the content before scraping.
    """
    logger.info(f"[{SOURCE}] Starting cache refresh...")
    logger.info(f"[{SOURCE}] Using Playwright to render Vue.js content")
    
    all_listings = {}
    page_num = 1
    max_pages = 100  # Safety limit
    consecutive_no_new = 0  # Track pages that add no new listings
    
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True, args=["--no-sandbox"])
        
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-ZA",
        )
        page = context.new_page()
        
        try:
            # First page - navigate to URL
            logger.info(f"[{SOURCE}] Fetching page {page_num}...")
            page.goto(BASE_URL, wait_until="domcontentloaded", timeout=15000)
            
            # Wait for Vue.js to render the listings
            try:
                page.wait_for_selector('.listing-tile', timeout=10000)
            except Exception:
                logger.warning(f"[{SOURCE}] Timeout waiting for listings on page {page_num}")
            
            while page_num <= max_pages:
                try:
                    # For page 1, we already navigated. For others, click Next button
                    if page_num > 1:
                        logger.info(f"[{SOURCE}] Clicking to page {page_num}...")
                        
                        # Click the "Next" button
                        next_button = page.query_selector('.next-page')
                        if not next_button:
                            logger.info(f"[{SOURCE}] No more pages available")
                            break
                        
                        next_button.click()
                        
                        # Wait for new listings to load
                        try:
                            page.wait_for_selector('.listing-tile', timeout=10000)
                        except Exception:
                            logger.warning(f"[{SOURCE}] Timeout waiting for listings on page {page_num}")
                            consecutive_no_new += 1
                            if consecutive_no_new >= 2:
                                break
                            page_num += 1
                            time.sleep(1)
                            continue
                        
                        time.sleep(1)  # Give Vue.js time to update
                    
                    logger.info(f"[{SOURCE}] Scraping page {page_num}...")
                    
                    # Get the rendered HTML
                    content = page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Find all listing tiles
                    listing_elements = soup.find_all('div', class_='listing-tile')
                    
                    if not listing_elements:
                        consecutive_no_new += 1
                        logger.debug(f"[{SOURCE}] Page {page_num}: No listings found")
                        
                        if consecutive_no_new >= 2:
                            logger.info(f"[{SOURCE}] Stopping: {consecutive_no_new} consecutive pages with no new listings")
                            break
                        
                        page_num += 1
                        time.sleep(1)
                        continue
                    
                    page_new_count = 0  # Count only truly NEW listings this page
                    
                    logger.info(f"[{SOURCE}] Page {page_num}: Found {len(listing_elements)} listings")
                    
                    for element in listing_elements:
                        try:
                            # Extract URL
                            url_elem = element.find('a', href=True)
                            if not url_elem:
                                continue
                            listing_url = url_elem.get('href', '')
                            if not listing_url:
                                continue
                            
                            # Extract title
                            title_elem = element.find('h4', class_='listing-tile__listing__price')
                            title = title_elem.get_text(strip=True) if title_elem else "Unknown"
                            
                            # Extract price
                            price_elem = element.find('h4', class_='listing-tile__listing-make-model')
                            price = price_elem.get_text(strip=True) if price_elem else "N/A"
                            
                            # Extract metadata (year, mileage, dealer)
                            meta_spans = element.find_all('span', class_='listing-tile__listing-meta__mileage')
                            year = "N/A"
                            kilometers = "N/A"
                            
                            if len(meta_spans) >= 1:
                                year_text = meta_spans[0].get_text(strip=True)
                                year = year_text.replace('Year:', '').strip() if 'Year:' in year_text else "N/A"
                            
                            if len(meta_spans) >= 2:
                                km_text = meta_spans[1].get_text(strip=True)
                                kilometers = km_text.replace('Mileage:', '').strip() if 'Mileage:' in km_text else "N/A"
                            
                            # Extract dealer
                            dealer_elem = element.find('span', class_='listing-tile__listing-meta__dealer')
                            dealer = "N/A"
                            if dealer_elem:
                                dealer_link = dealer_elem.find('a')
                                dealer = dealer_link.get_text(strip=True) if dealer_link else "N/A"
                            
                            # Create unique listing ID from URL slug
                            listing_id = f"{SOURCE.lower()}_{listing_url.split('/')[-2]}"
                            
                            # Only count as new if we haven't seen this ID before
                            if listing_id not in all_listings:
                                listing_data = {
                                    'id': listing_id,
                                    'title': title,
                                    'price': price,
                                    'url': listing_url,
                                    'year': year,
                                    'kilometers': kilometers,
                                    'location': dealer,
                                    'source': SOURCE
                                }
                                all_listings[listing_id] = listing_data
                                page_new_count += 1
                            
                        except Exception as e:
                            logger.debug(f"[{SOURCE}] Error parsing listing: {e}")
                            continue
                    
                    logger.info(f"[{SOURCE}] Page {page_num}: +{page_new_count} new listings (total: {len(all_listings)})")
                    
                    # Stop if this page added no new listings - we've looped back to the last page
                    if page_new_count == 0:
                        consecutive_no_new += 1
                        logger.info(f"[{SOURCE}] Page {page_num}: No new listings added ({consecutive_no_new} consecutive)")
                        if consecutive_no_new >= 2:
                            logger.info(f"[{SOURCE}] Stopping: reached end of listings after {page_num} pages")
                            break
                    else:
                        consecutive_no_new = 0  # Reset counter when we find new listings
                    
                    page_num += 1
                    
                except Exception as e:
                    logger.warning(f"[{SOURCE}] Error on page {page_num}: {e}")
                    consecutive_no_new += 1
                    
                    if consecutive_no_new >= 2:
                        logger.info(f"[{SOURCE}] Stopping after {consecutive_no_new} consecutive errors/empty pages")
                        break
                    
                    page_num += 1
                    time.sleep(1)
        
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
        with open(ZABIKERS_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[{SOURCE}] Cache saved: {ZABIKERS_CACHE_FILE}")
        logger.info(f"[{SOURCE}] Total listings cached: {len(listings)}")
        return True
    except Exception as e:
        logger.error(f"[{SOURCE}] Failed to save cache: {e}")
        return False


def load_cache():
    """Load existing cache for comparison"""
    try:
        if Path(ZABIKERS_CACHE_FILE).exists():
            with open(ZABIKERS_CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('listings', {})
    except Exception as e:
        logger.error(f"[{SOURCE}] Failed to load existing cache: {e}")
    return {}


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("ZABIKERS CACHE REFRESH")
    logger.info("=" * 60)
    
    # Load previous cache
    previous_listings = load_cache()
    previous_count = len(previous_listings)
    
    # Fetch all listings
    new_listings = fetch_all_listings()
    
    if not new_listings:
        logger.error(f"[{SOURCE}] Failed to fetch any listings. Cache not updated.")
        return False
    
    # Save cache
    success = save_cache(new_listings)
    
    if success:
        logger.info("=" * 60)
        logger.info(f"CACHE REFRESH COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Previous listings: {previous_count}")
        logger.info(f"Current listings:  {len(new_listings)}")
        logger.info(f"Difference: {len(new_listings) - previous_count:+d}")
        return True
    
    return False


if __name__ == "__main__":
    main()