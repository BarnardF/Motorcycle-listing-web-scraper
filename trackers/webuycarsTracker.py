from urllib.parse import quote_plus
from trackers.baseTracker import fetch_page, create_listing
from utils.relevant_match import is_relevant_match
from utils.search_variation_generator import generate_search_variations
from logger.logger import logger
from config.config import WEBUYCARS_BASE_URL

SOURCE = "WeBuyCars"

def scrape_webuycars(search_term):
    """
    ***DISABLED***
    
    Reason: Their search API is unreliable and returns inconsistent results.
    
    Better alternative: Scrape their motorcycle category page directly.
    This bypasses the search API entirely and handles name variations
    automatically without needing manual configuration.
    
    TODO (Roadmap): Implement category page scraper
    - Get all bikes from: webuycars.co.za/motorcycles or similar
    - Parse paginated results
    - Extract all bike data automatically
    - No search term matching needed
    """

    if not search_term or not search_term.strip():
        logger.error(f"[{SOURCE}] Skipping empty search term.")
        return {}
    
    listings = {}
    seen_ids = set()
    
    # Get search variations
    search_variations = generate_search_variations(search_term)
    logger.info(f"[{SOURCE}] Trying {len(search_variations)} search variation(s) for {search_term}")
    
    # Try each variation
    for variation in search_variations:
        encoded_term = quote_plus(f'"{variation}"')
        url = f"{WEBUYCARS_BASE_URL}?q={encoded_term}&activeTypeSearch=[\"Motorbike\"]"

        logger.debug(f"[{SOURCE}] Trying variation: {variation}")
        
        soup = fetch_page(url)
        if not soup:
            logger.debug(f"[{SOURCE}] Failed to fetch page for variation: {variation}")
            continue
        
        listing_elements = soup.select("div.list-grid-item")
        if not listing_elements:
            logger.debug(f"[{SOURCE}] No listings found for variation: {variation}")
            continue
        
        logger.debug(f"[{SOURCE}] Found {len(listing_elements)} potential listings for variation: {variation}")    
        
        skipped = 0

        for idx, listing_elem in enumerate(listing_elements, 1):
            try:
                # Extract stock number first for duplicate check
                fav_btn = listing_elem.select_one("button[data-stocknumber]")
                if not fav_btn:
                    logger.debug(f"[{SOURCE}] Skipping listing {idx}: no stock number")
                    skipped += 1
                    continue
                    
                listing_id = fav_btn.get("data-stocknumber")
                if not listing_id:
                    skipped += 1
                    continue
                    
                listing_id = f"wbc_{listing_id}"

                # Check for duplicates early
                if listing_id in seen_ids:
                    logger.debug(f"[{SOURCE}] Skipping duplicate listing: {listing_id}")
                    skipped += 1
                    continue
                    
                seen_ids.add(listing_id)

                # Extract title from description
                desc_elem = listing_elem.select_one(".grid-card-body .description")
                if not desc_elem:
                    logger.debug(f"[{SOURCE}] Skipping listing {idx}: no description")
                    skipped += 1
                    continue
                    
                title = desc_elem.get_text(" ", strip=True)
                
                if not title or title == "undefined":
                    skipped += 1
                    continue

                # Validate relevance to search term
                if not is_relevant_match(title, search_term, min_match_ratio=0.3):
                    logger.debug(f"[{SOURCE}] Skipping irrelevant match: {title}")
                    skipped += 1
                    continue

                # Extract price - look for .price-text span
                price_elem = listing_elem.select_one(".price-text span")
                price = price_elem.get_text(strip=True) if price_elem else "N/A"
                
                if not price or price == "N/A":
                    logger.debug(f"[{SOURCE}] Skipping listing {idx}: no price")
                    skipped += 1
                    continue

                # Extract kilometers from chip-text spans
                kilometers = "N/A"
                chip_spans = listing_elem.select(".chip-text span")
                for chip in chip_spans:
                    chip_text = chip.get_text(strip=True)
                    if 'km' in chip_text.lower():
                        kilometers = chip_text
                        break

                # Extract location - look for map marker icon parent
                location = "N/A"
                loc_chip = listing_elem.select_one(".chip-text:has(i.fa-map-marker-alt)")
                if loc_chip:
                    # Get text after the icon
                    location_text = loc_chip.get_text(strip=True)
                    # Remove the icon placeholder
                    location = location_text.replace("📍", "").strip()

                # Construct URL using stock number
                full_url = f"https://www.webuycars.co.za/stock-details/{listing_id.replace('wbc_', '')}" 

                listings[listing_id] = create_listing(
                    listing_id=listing_id,
                    title=title,
                    price=price,
                    url=full_url,
                    search_term=search_term,
                    source=SOURCE
                )

                listings[listing_id]['kilometers'] = kilometers
                listings[listing_id]['location'] = location
                
                logger.debug(f"[{SOURCE}] Added listing: {title} - {price}")

            except Exception as e:
                logger.error(f"[{SOURCE}] Error processing listing {idx}: {e}")
                skipped += 1
                continue

        logger.info(f"[{SOURCE}] Found {len(listings)} listing(s) for variation '{variation}'" +
                    (f" ({skipped} skipped)" if skipped > 0 else ""))

    logger.info(f"[{SOURCE}] Total: {len(listings)} listing(s) for {search_term}")
    return listings