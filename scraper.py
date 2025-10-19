import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

url = "https://www.autotrader.co.za/bikes-for-sale/suzuki/DS%20250%20SX%20V-STROM"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("it worked")
else:
    print(f"error:{response.status_code}")
    exit()

soup = BeautifulSoup(response.content, 'html.parser')


listing_elements = soup.find_all("a", class_="b-result-tile__nUiUiFtR93FVbMOF")
print(f"\nFound {len(listing_elements)} listing\n")

listings = []
seend_ids = set()

for listing_elem in listing_elements:
    title_tag = listing_elem.find("span", class_="e-make-model-title__yWb_LfShP7iz22PX")
    title = title_tag.get_text(strip=True) if title_tag else None

    price_tag = listing_elem.find("h2", class_="e-price__IA1Hxg4LkKwwRqMB")
    price = price_tag.get_text(strip=True) if price_tag else None

    link = listing_elem.get("href", "")
    print(f"DEBUG: Raw link = {link}")
    if link:
        if not link.startswith("http"):
            full_link = f"https://www.autotrader.co.za{link}" if link else None
        else:
            full_link = link

        listing_id = link.split("/")[-1].split("?")[0] if link else None
    else:
        full_link = None
        listing_id = None

    if not title or not price or not listing_id or title == "undefined":
        print(f"skipping invalid listing: {title}")
        continue

    if listing_id in seend_ids:
        print(f"skipping duplicate listing: {listing_id}")
        continue
    seend_ids.add(listing_id)

    listing_data = {
        'id': listing_id,
        'title': title,
        'price': price,
        'url': full_link,
        'found_date': datetime.now().isoformat()
    }

    listings.append(listing_data)

    print(f"id: {listing_data['id']}")
    print(f"title: {listing_data['title']}")
    print(f"price: {listing_data['price']}")
    print(f"link: {listing_data['url']}")

output_file = 'listings.json'
with open(output_file, 'w') as f:
    json.dump(listings, f, indent=2)

print(f'\n Saved {len(listings)} valid listings to {output_file}')


# print(f"page title: {soup.title.string}")