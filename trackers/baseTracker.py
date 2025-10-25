import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )
}
DATA_FILE = "listings.json"
BIKE_FILE = "bikes.txt"


def fetch_page(url):
    """Fetch a webpage and return BeautifulSoup object"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"  ❌ Request failed: {e}")
        return None


def create_listing(listing_id, title, price, url, search_term, source):
    """Create a standardized listing dictionary"""
    return {
        'id': listing_id,
        'title': title,
        'price': price,
        'url': url,
        'search_term': search_term,
        'source': source,
        'found_date': datetime.now().isoformat()
    }


def load_bike_list(filename=BIKE_FILE):
    """Load bike models from text file"""
    if not os.path.exists(filename):
        print(f"{filename} not found")
        return []
    
    bikes = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                bikes.append(line)
    return bikes


def load_previous_listings(filename=DATA_FILE):
    """Load previously saved listings"""
    if not os.path.exists(filename):
        print(f"{filename} not found, creating new file...")
        with open(filename, "w") as f:
            json.dump({}, f, indent=2)
        return {}
    
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        print(f"Currupter {filename}, resetting file...")    
        with open(filename, "w") as f:
            json.dump({}, f, indent=2)
        return {}


def save_listings(listings_by_bike, filename=DATA_FILE):
    """Save all listings organized by bike model"""
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump({}, f, indent=2)

    with open(filename, "w") as f:
        json.dump(listings_by_bike, f, indent=2)

    total = sum(len(listings) for listings in listings_by_bike.values())
    print(f"SAVED {total} total listings for {len(listings_by_bike)} bike model(s)")
