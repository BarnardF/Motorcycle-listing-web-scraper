from urllib.parse import quote_plus
from .baseTracker import fetch_page, create_listing

BASE_URL = "https://www.gumtree.co.za/s-motorcycles-scooters/v1c9027p1"


def scrape_gumtree(search_term):
    """Scrape Gumtree for a specific search term"""
    encoded_term = quote_plus(search_term)
    url = f"{BASE_URL}?q={encoded_term}" #https://www.gumtree.co.za/s-motorcycles-scooters/v1c9027p1?q=triumph

    print(f"Gumtree: {search_term}")

    soup = fetch_page(url)
    if not soup:
        return {}
    
    listing_elements = soup.find_all("span", class_="related-item")

    if not listing_elements:
        print("No listings found")
        return {}
    
    listings = {}
    seen_ids = set()

    for listing_elem in listing_elements:
        listing_id = listing_elem.get("data-adid", "")
        if not listing_id:
            continue

        listing_id = f"gt_{listing_id}" #"gt_" for gumtree

        if listing_id in seen_ids:
            continue

        title_elem = listing_elem.select_one("a.related-ad-title span")
        title = title_elem.get_text(strip=True) if title_elem else None

        price_elem = listing_elem.select_one("span.ad-price")
        price = price_elem.get_text(strip=True) if price_elem else None  

        link_elem = listing_elem.select_one("a.related-ad-title")   
        href = link_elem.get("href", "") if link_elem else ""

        if not title or not price or not href:
            continue

        seen_ids.add(listing_id)

        listings[listing_id] = create_listing(
            listing_id=listing_id,
            title=title,
            price=price,
            url=f"https://www.gumtree.co.za{href}",
            search_term=search_term,
            source="Gumtree"
        )           

        # listings.append(listing_data)
    print(f"found {len(listings)} listings")
    return listings