"""
AutoTrader Scraper with search variations
Tries multiple search variations to handle different model name formats
AI(Claude) assisted implementation
"""

import time

from urllib.parse import quote
from trackers.baseTracker import fetch_page
from utils.search_variation_generator import generate_search_variations
from utils.relevant_match import is_relevant_autotrader_match
from utils.listing_builder import build_listing
from logger.logger import logger
from config.config import AUTOTRADER_BASE_URL

SOURCE = "AutoTrader"


def scrape_autotrader(search_term):
    """
    Scrape AutoTrader for a specific search term
    Tries formatting variations to handle different model name formats
    
    Args:
        search_term: Search term in format "Brand Model" (e.g., "Honda CB500X")
        
    Returns:
        Dictionary of listings with listing_id as key
    """
    # Skip empty search terms
    if not search_term or not search_term.strip():
        logger.warning(f"[{SOURCE}] Skipping empty search term")
        return {}
    
    # Parse brand and validate format
    parts = search_term.split(maxsplit=1)
    if len(parts) < 2:
        logger.warning(f"[{SOURCE}] Invalid format: '{search_term}' (use 'Brand Model')")
        return {}
    
    brand = parts[0].lower()
    listings = {}
    seen_ids = set()
    
    # Generate search variations
    search_variations = generate_search_variations(search_term)
    if len(search_variations) > 1:
        logger.debug(f"[{SOURCE}] Trying {len(search_variations)} variation(s) for {search_term}")
    
    for variation in search_variations:
        model_parts = variation.split(maxsplit=1)
        model = model_parts[1]
        encoded_model = quote(model, safe="")
        url = f"{AUTOTRADER_BASE_URL}/{brand}/{encoded_model}"

        logger.debug(f"[{SOURCE}] Trying variation: {variation}")
        logger.debug(f"[{SOURCE}] URL: {url}")

        soup = fetch_page(url)
        time.sleep(2)  # Add a 2-second delay between requests to be polite
        if not soup:
            logger.debug(f"[{SOURCE}] Failed to fetch: {variation}")
            continue

        listing_elements = soup.find_all("a", class_="b-result-tile__nUiUiFtR93FVbMOF")

        if not listing_elements:
            logger.debug(f"[{SOURCE}] No listings for variation: {variation}")
            continue
        
        logger.debug(f"[{SOURCE}] Found {len(listing_elements)} potential listings for {variation}")
        skipped = 0

        for idx, listing_elem in enumerate(listing_elements, 1):
            try:
                # Extract title
                title = listing_elem.select_one("span.e-make-model-title__yWb_LfShP7iz22PX")
                title = title.get_text(strip=True) if title else None

                # Validate title
                if not title or title == "undefined":
                    skipped += 1
                    continue

                # Validate relevance against ORIGINAL search term
                if not is_relevant_autotrader_match(title, search_term):
                    logger.debug(f"[{SOURCE}] Skipping irrelevant: {title}")
                    skipped += 1
                    continue

                # Extract price
                price = listing_elem.select_one("h2.e-price__IA1Hxg4LkKwwRqMB")
                price = price.get_text(strip=True) if price else None

                if not price:
                    skipped += 1
                    continue

                # Extract specifications
                spec_container = listing_elem.select_one(".b-vehicle-specifications__G33kWAOWZs0tmFIT")
                condition = "N/A"
                kilometers = "N/A"

                if spec_container:
                    spec_tags = spec_container.select(".e-text__XJ7raWOpNHUkT6ZU")
                    for tag in spec_tags:
                        text = tag.get_text(strip=True)
                        text_lower = text.lower()
                        if "km" in text_lower:
                            kilometers = text.replace("\xa0", " ")
                        elif text_lower in ["used", "new", "demo"]:
                            condition = text

                # Extract location
                location_elem = listing_elem.select_one("span.e-suburb__eiCxIOrnXW9SrLIq")
                location = location_elem.get_text(strip=True) if location_elem else "N/A"

                # Extract URL
                href = listing_elem.get("href", "")
                if not href:
                    skipped += 1
                    continue

                # Extract listing ID
                listing_id = href.split("/")[-1].split("?")[0]
                listing_id = f"{SOURCE.lower()}_{listing_id}"

                # Check for duplicates across all variations
                if listing_id in seen_ids:
                    logger.debug(f"[{SOURCE}] Skipping duplicate: {listing_id}")
                    skipped += 1
                    continue

                seen_ids.add(listing_id)
                full_url = f"https://www.autotrader.co.za{href}"

                listings[listing_id] = build_listing(
                    listing_id=listing_id,
                    title=title,
                    price=price,
                    url=full_url,
                    search_term=search_term,
                    source=SOURCE
                )

                listings[listing_id]["kilometers"] = kilometers
                listings[listing_id]["condition"] = condition
                listings[listing_id]["location"] = location

            except AttributeError as e:
                logger.warning(f"[{SOURCE}] Skipping malformed listing: {e}")
                skipped += 1
                continue
            except Exception as e:
                logger.error(f"[{SOURCE}] Error processing listing: {e}")
                skipped += 1
                continue
        
        if listing_elements:
            logger.debug(f"[{SOURCE}] Variation '{variation}': {len(listing_elements)} found, {skipped} skipped")
    
    logger.info(f"[{SOURCE}] Found {len(listings)} listing(s) for {search_term}")
    return listings