from urllib.parse import quote
from trackers.baseTracker import fetch_page, create_listing, validate_search_term
from logger.logger import logger
from config.config import AUTOTRADER_BASE_URL

SOURCE = "AutoTrader"



def scrape_autotrader(search_term):
    """
    Scrape AutoTrader for a specific search term
    
    Args:
        search_term: Search term in format "Brand Model" (e.g., "Honda CB500X")
        
    Returns:
        Dictionary of listings with listing_id as key
    """
    # Skip empty search terms
    if not search_term or not search_term.strip():
        logger.warning(f"[{SOURCE}] Skipping empty search term")
        return {}
    
    # Validate search term format
    is_valid, error_msg = validate_search_term(search_term, requried_format="Brand Model")
    if not is_valid:
        logger.warning(f"[{SOURCE}] {error_msg}")
        return {}
    
    # Parse brand and model
    parts = search_term.split(maxsplit=1)
    brand, model = parts[0].lower(), parts[1]
    encoded_model = quote(model, safe="")
    url = f"{AUTOTRADER_BASE_URL}/{brand}/{encoded_model}"

    logger.info(f"[{SOURCE}] Searching: {search_term}")
    logger.debug(f"[{SOURCE}] URL: {url}")

    soup = fetch_page(url)
    if not soup:
        logger.warning(f"[{SOURCE}] Failed to fetch page for {search_term}")
        return {}

    listing_elements = soup.find_all("a", class_="b-result-tile__nUiUiFtR93FVbMOF")
    # print(f"\nFound {len(listing_elements)} listing elements")

    if not listing_elements:
        logger.info(f"[{SOURCE}] No listings found for {search_term}")
        return {}
    
    logger.debug(f"[{SOURCE}] Found {len(listing_elements)} potential listings")
    
    listings = {}
    seen_ids = set()
    skipped = 0

    for idx, listing_elem in enumerate(listing_elements, 1):
        try:
            # Extract title
            title = listing_elem.select_one("span.e-make-model-title__yWb_LfShP7iz22PX")
            title = title.get_text(strip=True) if title else None

            # Extract price
            price = listing_elem.select_one("h2.e-price__IA1Hxg4LkKwwRqMB")
            price = price.get_text(strip=True) if price else None

            # Extract specifications (condition, kilometers)
            spec_div = listing_elem.select_one("div.b-vehicle-specifications__G33kWAOWZs0tmFIT")

            condition = "N/A"
            kilometers = "N/A"

            if spec_div:
                specs = [s.get_text(strip=True) for s in spec_div.select("span.e-text__XJ7raWOpNHUkT6ZU")]
                for spec in specs:
                    spec_lower = spec.lower()
                    if "km" in spec_lower:
                        kilometers = spec
                    elif spec_lower in ["used", "new", "demo"]:
                        condition = spec

            # Extract location
            location_elem = listing_elem.select_one("span.e-suburb__eiCxIOrnXW9SrLIq")
            location = location_elem.get_text(strip=True) if location_elem else "N/A"

            # Extract URL
            href = listing_elem.get("href", "")

            # Extract listing ID
            listing_id = href.split("/")[-1].split("?")[0]

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
            full_url = f"https://www.autotrader.co.za{href}"

            listings[listing_id] = create_listing(
                listing_id=listing_id,
                title=title,
                price=price,
                url=full_url,
                search_term=search_term,
                source=SOURCE
            )

            # Add additional fields
            listings[listing_id]["kilometers"] = kilometers
            listings[listing_id]["condition"] = condition
            listings[listing_id]["location"] = location

            # listings.append(listing_data)
        # print(f"found {len(listings)} listings")
        except AttributeError as e:
            logger.warning(f"[{SOURCE}] Skipping malformed listing {idx}: {e}")
            skipped += 1
            continue
        except Exception as e:
            logger.error(f"[{SOURCE}] Error processing listing {idx}: {e}")
            skipped += 1
            continue
    
    logger.info(f"[{SOURCE}] Found {len(listings)} listing(s) for {search_term}" + 
                (f" ({skipped} skipped)" if skipped > 0 else ""))
    
    return listings

