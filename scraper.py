import requests
from bs4 import BeautifulSoup

url = "https://www.autotrader.co.za/bikes-for-sale/suzuki/DS%20250%20SX%20V-STROM"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("it worked")
else:
    print(f"error:{response.status_code}")

soup = BeautifulSoup(response.content, 'html.parser')


listings = soup.find_all("a", class_="b-result-tile__nUiUiFtR93FVbMOF")
print(f"\nFound {len(listings)} listing\n")

for listing in listings:
    title_tag = listing.find("span", class_="e-make-model-title__yWb_LfShP7iz22PX")
    title = title_tag.get_text(strip=True) if title_tag else "no title"

    price_tag = listing.find("h2", class_="e-price__IA1Hxg4LkKwwRqMB")
    price = price_tag.get_text(strip=True) if price_tag else "no price"

    link = listing.get("href", "")
    full_link = f"https://www.autotrader.co.za{link}"

    print(f"title: {title}")
    print(f"price: {price}")
    print(f"link: {full_link}")


# print(f"page title: {soup.title.string}")