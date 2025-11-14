"""
WeBuyCars Cached Scraper
Searches locally cached WeBuyCars listings (from API interception).
Uses fuzzy matching to find relevant bikes without relying on their search API.
"""

import json
from pathlib import Path
from datetime import datetime
from logger.logger import logger
from config.config import WEBUYCARS_CACHE_FILE, MATCH_THRESHOLDS
from utils.relevant_match import is_relevant_match
from utils.search_variation_generator import generate_search_variations
from utils.listing_builder import build_listing

SOURCE = "WeBuyCars"


def load_cache():
    """Load WeBuyCars cache from file"""
    try:
        if not Path(WEBUYCARS_CACHE_FILE).exists():
            logger.warning(f"[{SOURCE}] Cache file not found: {WEBUYCARS_CACHE_FILE}")
            logger.warning(f"[{SOURCE}] Run 'python cache_webuycars.py' to create cache first")
            return {}
        
        with open(WEBUYCARS_CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        listings = data.get('listings', {})
        cached_date = data.get('date_formatted', 'Unknown')
        
        logger.info(f"[{SOURCE}] Loaded cache ({len(listings)} listings, last updated: {cached_date})")
        return listings
    
    except Exception as e:
        logger.error(f"[{SOURCE}] Error loading cache: {e}")
        return {}

def is_relevant_listing(title, make, model, search_term):
    """
    Check if listing is relevant to search term.
    Uses fuzzy matching on title, make, and model.
    """
    threshold = MATCH_THRESHOLDS["webuycars"]
    
    # First, extract key identifiers from search term
    search_parts = search_term.lower().split()
    
    # Build a comparison string from make + model
    full_name = f"{make} {model}".strip().lower()
    
    # Check if ALL major search term words appear in the listing
    # This prevents "BMW G 310" from matching "BMW C G 310"
    matching_parts = sum(1 for part in search_parts if part in full_name)
    
    # reject if less than 60% of search parts match
    if len(search_parts) > 0 and matching_parts / len(search_parts) < 0.6:
        return False
    
    # Try matching against full title first
    if is_relevant_match(title, search_term, threshold):
        return True
    
    # Try matching against make + model
    # full_name = f"{make} {model}".strip()
    # if is_relevant_match(full_name, search_term, threshold):
    #     return True
    
    return False

def format_price(price):
    """Format price string for display"""
    try:
        if isinstance(price, (int, float)):
            return f"R {price:,.0f}"
        if isinstance(price, str) and price != "N/A":
            return f"R {price}"
    except:
        pass
    return price

def format_kilometers(km):
    """Format kilometers for display"""
    try:
        if isinstance(km, (int, float)):
            return f"{km:,.0f} km"
        if isinstance(km, str) and km != "N/A":
            return f"{km} km"
    except:
        pass
    return km

def scrape_webuycars_cached(search_term):
    """
    Search WeBuyCars cache for listings matching search_term.
    Tries multiple search variations to handle different bike name formats.
    
    Returns dict of relevant listings in standard format.
    """
    if not search_term or not search_term.strip():
        logger.warning(f"[{SOURCE}] Skipping empty search term")
        return {}
    
    search_term = search_term.strip()
    logger.info(f"[{SOURCE}] Searching cache: {search_term}")
    
    # Load cache
    cached_listings = load_cache()
    if not cached_listings:
        logger.warning(f"[{SOURCE}] Cache is empty or unavailable")
        return {}
    
    # Generate search variations to try
    search_variations = generate_search_variations(search_term)
    if len(search_variations) > 1:
        logger.debug(f"[{SOURCE}] Trying {len(search_variations)} variation(s) for {search_term}")
    
    # Search cache for relevant listings
    relevant_listings = {}
    seen_ids = set()  # Track duplicates across variations
    
    for variation in search_variations:
        for listing_id, listing in cached_listings.items():
            # Skip if we've already added this listing
            if listing_id in seen_ids:
                continue
            
            try:
                title = listing.get('title', '')
                make = listing.get('make', '')
                model = listing.get('model', '')

            
                # Check if this listing matches the search term
                if is_relevant_listing(title, make, model, variation):
                    seen_ids.add(listing_id)

                    # Use the ORIGINAL search_term (not variation) for grouping
                    relevant_listings[listing_id] = build_listing(
                        listing_id=listing_id,
                        title=title,
                        price=format_price(listing.get('price', 'N/A')),
                        url=listing.get('url', ''),
                        search_term=search_term,
                        source=SOURCE,
                        kilometers=format_kilometers(listing.get('kilometers', 'N/A')),
                        location=listing.get('location', 'N/A')
                    )
            
            except Exception as e:
                logger.debug(f"[{SOURCE}] Error processing listing {listing_id}: {e}")
                continue
    
    logger.info(f"[{SOURCE}] Found {len(relevant_listings)} listing(s) matching '{search_term}'")
    return relevant_listings

# For compatibility with main.py
def scrape_webuycars(search_term):
    """Wrapper for main.py compatibility"""
    return scrape_webuycars_cached(search_term)