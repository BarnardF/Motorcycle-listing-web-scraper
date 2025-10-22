import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime


def load_previous_listings(filename='listings.json'):
    if not os.path.exists(filename):
        return {}
    
    with open(filename, "r") as f:
        listings_list = json.load(f)

    #conversts list to dict with ID as key
    return {listing['id']: listing for listing in listings_list}



def save_listings(listings, filename='listings.json'):
    listings_list = list(listings.values())

    with open(filename, "w") as f:
        json.dump(listings_list, f, indent=2)
    print(f"SAVED {len(listings_list)} listings to {filename}")



def scrape_autotrader(search_term):
    url = f"https://www.autotrader.co.za/bikes-for-sale/suzuki/{search_term}"

    headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" 
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"error fetching page:{response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    listing_elements = soup.find_all("a", class_="b-result-tile__nUiUiFtR93FVbMOF")
    print(f"\nFound {len(listing_elements)} listing elements")

    listings = {}
    seen_ids = set()

    for listing_elem in listing_elements:
        title_tag = listing_elem.find("span", class_="e-make-model-title__yWb_LfShP7iz22PX")
        title = title_tag.get_text(strip=True) if title_tag else None

        price_tag = listing_elem.find("h2", class_="e-price__IA1Hxg4LkKwwRqMB")
        price = price_tag.get_text(strip=True) if price_tag else None

        link = listing_elem.get("href", "")
        # print(f"DEBUG: Raw link = {link}")
        if link:
            full_link = f"https://www.autotrader.co.za{link}" if link else None
            #extracts unique id form url
            listing_id = link.split("/")[-1].split("?")[0] if link else None
        else:
            full_link = None
            listing_id = None


        # skips  'undefined' titles
        if not title or not price or not listing_id or title == "undefined":
            # print(f"skipping invalid listing: {title}")
            continue

        #skips duplicates
        if listing_id in seen_ids:
            # print(f"skipping duplicate listing: {listing_id}")
            continue
        seen_ids.add(listing_id)

        listings[listing_id] = {
            'id': listing_id,
            'title': title,
            'price': price,
            'url': full_link,
            'found_date': datetime.now().isoformat()
        }

        # listings.append(listing_data)
        return listings

def main():
    print("="*30)
    print("Motercycle listing tracker")
    print("="*30)

    previous_listings = load_previous_listings()
    print(f"Loaded {len(previous_listings)} previous_listings")

    current_listings = scrape_autotrader("DS%20250%20SX%20V-STROM")
    print(f"Found {len(current_listings)} current listings")

    new_listings = {}
    for listing_id, listing in current_listings.items():
        if listing_id not in previous_listings:
            new_listings[listing_id] = listing

    print("\n" + "="*20)
    if new_listings:
        print(f"FOUND {len(new_listings)} NEW LISITNG(S)")
        print("="*30)
        for listing in new_listings.values():
            print(f"\n {listing['title']}")
            print(f" Price: {listing['price']}")
            print(f" Link: {listing['url']}")
    else:
        print("No new listings found")
        print("="*30)

    save_listings(current_listings)

    return new_listings
    
if __name__ == "__main__":
    main()