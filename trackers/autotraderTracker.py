from urllib.parse import quote
from trackers.baseTracker import fetch_page, create_listing, validate_search_term, is_relevant_match
from logger.logger import logger
from config.config import AUTOTRADER_BASE_URL

SOURCE = "AutoTrader"

def is_relevant_autotrader_match(listing_title, search_term):
    """
    Check if AutoTrader listing is relevant to search term
    Focus on model matching since AutoTrader searches by brand
    
    Args:
        listing_title: The listing title from AutoTrader
        search_term: Original search term (e.g., "Harley-Davidson Street 750")
    
    Returns:
        True if relevant, False otherwise
    """
    # Extract model from search term (everything after brand)
    parts = search_term.split(maxsplit=1)
    if len(parts) < 2:
        return True  # Can't validate, allow it
    
    model = parts[1].lower()  # e.g., "street 750"
    title_lower = listing_title.lower()
    
    # Split model into words and check if ALL key words appear in title
    model_words = model.split()
    
    # For models with numbers, MUST match the number exactly
    # e.g., "Street 750" should NOT match "Street Glide"
    has_number = any(word.replace(',', '').replace('.', '').isdigit() for word in model_words)
    
    if has_number:
        # Extract numbers from both
        import re
        search_numbers = set(re.findall(r'\d+', model))
        title_numbers = set(re.findall(r'\d+', listing_title))
        
        # If search has numbers, at least one must appear in title
        if search_numbers and not (search_numbers & title_numbers):
            return False
    
    # Check if key model words appear in title
    # Allow some flexibility but require significant overlap
    matching_words = sum(1 for word in model_words if word in title_lower)
    match_ratio = matching_words / len(model_words)
    
    return match_ratio >= 0.5  # At least 50% of words must match


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
    is_valid, error_msg = validate_search_term(search_term, required_format="Brand Model")
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
            #validate relevance
            if title and not is_relevant_autotrader_match(title, search_term):
                logger.debug(f"[{SOURCE}] Skipping irrelevant match: {title}")
                skipped += 1
                continue

            # Extract price
            price = listing_elem.select_one("h2.e-price__IA1Hxg4LkKwwRqMB")
            price = price.get_text(strip=True) if price else None

            # Extract specifications (condition, kilometers)
            spec_container = listing_elem.select_one(".b-vehicle-specifications__G33kWAOWZs0tmFIT")

            condition = "N/A"
            kilometers = "N/A"

            if spec_container:
                spec_tags = spec_container.select(".e-text__XJ7raWOpNHUkT6ZU")
                for tag in spec_tags:
                    text = tag.get_text(strip=True)
                    text_lower = text.lower()
                    if "km" in text_lower:
                        kilometers = text.replace("\xa0", " ")  # clean non-breaking space
                    elif text_lower in ["used", "new", "demo"]:
                        condition = text

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

