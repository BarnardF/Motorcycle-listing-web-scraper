from urllib.parse import quote_plus
from trackers.baseTracker import fetch_page, create_listing
from utils.relevant_match import is_relevant_match
from utils.search_variation_generator import generate_search_variations
from logger.logger import logger
from config.config import GUMTREE_BASE_URL, MATCH_THRESHOLDS

SOURCE = "Gumtree"


def scrape_gumtree(search_term):
    """
    Scrape Gumtree for a specific search term
    Tries multiple search variations to maximize results
    """
    if not search_term or not search_term.strip():
        logger.warning(f"[{SOURCE}] Skipping empty search term")
        return {}
    
    listings = {}
    seen_ids = set()
    
    # Generate search variations
    search_variations = generate_search_variations(search_term)
    if len(search_variations) > 1:
        logger.info(f"[{SOURCE}] Trying {len(search_variations)} variation(s) for {search_term}")
    
    for variation in search_variations:
        encoded_term = quote_plus(variation)
        url = f"{GUMTREE_BASE_URL}?q={encoded_term}"

        logger.debug(f"[{SOURCE}] Searching variation: {variation}")
        logger.debug(f"[{SOURCE}] URL: {url}")

        soup = fetch_page(url)
        if not soup:
            logger.debug(f"[{SOURCE}] Failed to fetch page for variation: {variation}")
            continue
        
        # Find real listings (not filter UI elements)
        listing_selectors = [
            "span.related-item",
            "div.related-item",
        ]
        
        listing_elements = []
        for selector in listing_selectors:
            elements = soup.select(selector)
            # Filter out false positives - must have data-adid
            listing_elements = [el for el in elements if el.get("data-adid")]
            if listing_elements:
                logger.debug(f"[{SOURCE}] Found {len(listing_elements)} listings for variation: {variation}")
                break

        if not listing_elements:
            logger.debug(f"[{SOURCE}] No listings found for variation: {variation}")
            continue
        
        skipped = 0

        for idx, listing_elem in enumerate(listing_elements, 1):
            try:
                # Extract title
                title_elem = listing_elem.select_one("a.related-ad-title span")
                title = title_elem.get_text(strip=True) if title_elem else None

                if not title or title == "undefined":
                    logger.debug(f"[{SOURCE}] Skipping: no title")
                    skipped += 1
                    continue

                # Extract price
                price_elem = listing_elem.select_one("span.ad-price")
                price = price_elem.get_text(strip=True) if price_elem else None  

                if not price or "contact" in price.lower():
                    logger.debug(f"[{SOURCE}] Skipping: no valid price")
                    skipped += 1
                    continue

                # Extract kilometers
                kilometers = "N/A"
                chiplets = listing_elem.select("div.chiplets-container span")
                if chiplets and len(chiplets) >= 2:
                    km_text = chiplets[1].get_text(strip=True)
                    if 'km' in km_text.lower():
                        kilometers = km_text
                
                if kilometers == "N/A":
                    property_labels = listing_elem.select(".property-label")
                    if len(property_labels) >= 2:
                        km_text = property_labels[1].get_text(strip=True)
                        if km_text and km_text != "2024":
                            kilometers = km_text

                # Extract location
                location = "N/A"
                loc_elem = listing_elem.select_one(".location span")
                if loc_elem:
                    location = loc_elem.get_text(strip=True)

                # Extract URL
                link_elem = listing_elem.select_one("a.related-ad-title")
                href = link_elem.get("href", "") if link_elem else ""

                if not href:
                    logger.debug(f"[{SOURCE}] Skipping: no URL")
                    skipped += 1
                    continue

                # Extract listing ID
                listing_id = listing_elem.get("data-adid", "")
                if not listing_id:
                    logger.debug(f"[{SOURCE}] Skipping: no ID")
                    skipped += 1
                    continue

                listing_id = f"gt_{listing_id}"

                # Check for duplicates across all variations
                if listing_id in seen_ids:
                    logger.debug(f"[{SOURCE}] Skipping duplicate: {listing_id}")
                    skipped += 1
                    continue

                seen_ids.add(listing_id)

                # Validate match with fuzzy matching against ORIGINAL search term
                if not is_relevant_match(search_term, title, min_match_ratio=MATCH_THRESHOLDS["gumtree"]):
                    logger.debug(f"[{SOURCE}] Skipping irrelevant: '{title}'")
                    skipped += 1
                    continue

                full_url = f"https://www.gumtree.co.za{href}"

                listings[listing_id] = create_listing(
                    listing_id=listing_id,
                    title=title,
                    price=price,
                    url=full_url,
                    search_term=search_term,  # original search term
                    source=SOURCE
                )

                listings[listing_id]['kilometers'] = kilometers
                listings[listing_id]['location'] = location
                
                logger.debug(f"[{SOURCE}] Added listing: {title}")
      
            except AttributeError as e:
                logger.warning(f"[{SOURCE}] Skipping malformed listing: {e}")  
                skipped += 1
                continue
            except Exception as e:
                logger.error(f"[{SOURCE}] Error processing listing: {e}") 
                skipped += 1
                continue

        if listing_elements:
            logger.info(f"[{SOURCE}] Found {len([e for e in listing_elements if not (e.get('data-adid') in seen_ids)])} new listing(s) for variation '{variation}'" + 
                        (f" ({skipped} skipped)" if skipped > 0 else ""))

    logger.info(f"[{SOURCE}] Total: {len(listings)} listing(s) for {search_term}")
    return listings

