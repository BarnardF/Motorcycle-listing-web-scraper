from urllib.parse import quote

from trackers.baseTracker import fetch_page, create_listing, HEADERS, BIKE_FILE, DATA_FILE


BASE_URL = "https://www.autotrader.co.za/bikes-for-sale"
SOURCE = "AutoTrader"



def scrape_autotrader(search_term):
    """Scrape AutoTrader for a specific search term"""
    parts = search_term.split(maxsplit=1)
    if len(parts) < 2:
        print(f"invalid format: '{search_term}' (need: Brand Model)")
        return {}
    
    brand, model = parts[0].lower(), parts[1]
    encoded_model = quote(model, safe='')
    url = f"{BASE_URL}/{brand}/{encoded_model}"

    print(f"Searching: {search_term}")
    print(f"URL: {url}")

    soup = fetch_page(url)
    if not soup:
        return {}

    listing_elements = soup.find_all("a", class_="b-result-tile__nUiUiFtR93FVbMOF")
    # print(f"\nFound {len(listing_elements)} listing elements")

    if not listing_elements:
        print("No listings found")
        return {}
    
    listings = {}
    seen_ids = set()

    for listing_elem in listing_elements:
        title = listing_elem.select_one("span.e-make-model-title__yWb_LfShP7iz22PX")
        title = title.get_text(strip=True) if title else None

        price = listing_elem.select_one("h2.e-price__IA1Hxg4LkKwwRqMB")
        price = price.get_text(strip=True) if price else None
        
        href = listing_elem.get("href", "")

        if not href or not title or not price or title == "undefined":
            continue

        listing_id = href.split("/")[-1].split("?")[0]
        if listing_id in seen_ids:
            continue
        seen_ids.add(listing_id)

        full_url = f"https://www.autotrader.co.za{href}"

        listings[listing_id] = create_listing(
            listing_id=listing_id,
            title=title,
            price=price,
            url=full_url,
            search_term=search_term,
            source=SOURCE,
        )

        # listings.append(listing_data)
    print(f"found {len(listings)} listings")
    return listings

