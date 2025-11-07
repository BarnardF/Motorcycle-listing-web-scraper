from urllib.parse import quote_plus
from trackers.baseTracker import fetch_page, create_listing, is_relevant_match
from logger.logger import logger
from config.config import GUMTREE_BASE_URL


SOURCE = "Gumtree"

def scrape_gumtree(search_term):
    """Scrape Gumtree for a specific search term"""
    # Skip empty search terms
    if not search_term or not search_term.strip():
        logger.warning(f"[{SOURCE}] Skipping empty search term")
        return {}
    
    encoded_term = quote_plus(search_term)
    url = f"{GUMTREE_BASE_URL}?q={encoded_term}" #https://www.gumtree.co.za/s-motorcycles-scooters/v1c9027p1?q=triumph

    # print(f"Gumtree: {search_term}")
    logger.info(f"[{SOURCE}] Searching: {search_term}")
    logger.debug(f"[{SOURCE}] URL: {url}")

    soup = fetch_page(url)
    if not soup:
        return {}
    
    listing_elements = soup.find_all("span", class_="related-item")

    if not listing_elements:
        logger.info(f"[{SOURCE}] No listings found for {search_term}")
        return {}
    
    listings = {}
    seen_ids = set()
    skipped = 0

    for idx,listing_elem in enumerate(listing_elements, 1):
        try:
            # Extract title
            title_elem = listing_elem.select_one("a.related-ad-title span")
            title = title_elem.get_text(strip=True) if title_elem else None

            # Extract price
            price_elem = listing_elem.select_one("span.ad-price")
            price = price_elem.get_text(strip=True) if price_elem else None  

            # Extract kilometers
            km_elem = listing_elem.select_one("div.chiplets-container span:nth-of-type(2)")  # second span usually holds km
            kilometers = km_elem.get_text(strip=True) if km_elem else "N/A"

            # Extract location  
            location_elem = listing_elem.select_one(".bottom-container .location span")
            location = location_elem.get_text(strip=True) if location_elem else "N/A"

            # Extract URL
            link_elem = listing_elem.select_one("a.related-ad-title")   
            href = link_elem.get("href", "") if link_elem else ""

            # Extract listing ID
            listing_id = listing_elem.get("data-adid", "")
            if not listing_id:
                continue

            listing_id = f"gt_{listing_id}" #"gt_" for gumtree

            # Validate required fields
            if not href or not title or not price or title == "undefined":
                logger.debug(f"[{SOURCE}] Skipping listing {idx}: missing required fields")
                skipped += 1
                continue

            # Check for duplicates
            if listing_id in seen_ids:
                logger.debug(f"[{SOURCE}] Skipping duplicate listing: {listing_id}")
                skipped += 1
                continue

            seen_ids.add(listing_id)
            full_url = f"https://www.gumtree.co.za{href}"

            #validate match
            if not is_relevant_match(title, search_term, min_match_ratio=0.5):
                logger.debug(f"[{SOURCE}] Skipping irrelevant match: {title}")
                skipped += 1
                continue

            listings[listing_id] = create_listing(
                listing_id=listing_id,
                title=title,
                price=price,
                url=full_url,
                search_term=search_term,
                source=SOURCE
            )

            # Add extra info separately
            listings[listing_id]['kilometers'] = kilometers
            listings[listing_id]['location'] = location
  
        except AttributeError as e:
            logger.warning(f"[{SOURCE}] Skipping malformed listing {idx}: {e}")  
            continue
        except Exception as e:
            logger.error(f"[{SOURCE}] Error processing listing {idx}: {e}") 
            continue

        # listings.append(listing_data)
    logger.info(f"[{SOURCE}] Found {len(listings)} listing(s) for {search_term}" + 
                (f" ({skipped} skipped)" if skipped > 0 else ""))
    
    return listings