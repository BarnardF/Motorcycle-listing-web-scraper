"""
Debug script to inspect ZABikers HTML structure
Helps identify correct CSS classes for scraping
"""

import requests
from bs4 import BeautifulSoup
from config.config import get_random_user_agent, REQUEST_TIMEOUT

BASE_URL = "https://www.zabikers.co.za/bikes-for-sale/"

def debug_page_structure():
    """Fetch page 1 and inspect the HTML structure"""
    
    url = f"{BASE_URL}?paged=1"
    
    headers = {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    print(f"Fetching: {url}")
    response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    print(f"Status: {response.status_code}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Debug: Find all divs and their classes
    print("\n=== SEARCHING FOR LISTING ELEMENTS ===\n")
    
    # Try different class patterns
    patterns = [
        ('div', 'listing-tile'),
        ('div', 'listing'),
        ('div', 'bike'),
        ('article', None),
        ('div', 'product'),
    ]
    
    for tag, class_name in patterns:
        if class_name:
            elements = soup.find_all(tag, class_=class_name)
            print(f"Found {len(elements)} elements with <{tag} class='{class_name}'>")
        else:
            elements = soup.find_all(tag)
            print(f"Found {len(elements)} <{tag}> elements")
    
    # Print first listing element's HTML (if found)
    print("\n=== FIRST LISTING ELEMENT (if found) ===\n")
    
    listing = soup.find('div', class_='listing-tile')
    if listing:
        print(listing.prettify()[:2000])  # First 2000 chars
    else:
        print("No listing-tile found. Trying other patterns...")
        
        # Try to find ANY div that might be a listing
        all_divs = soup.find_all('div')
        print(f"Total divs on page: {len(all_divs)}")
        
        # Print classes of first 20 divs
        print("\nFirst 20 div classes:")
        for i, div in enumerate(all_divs[:20]):
            classes = div.get('class', [])
            print(f"  {i}: {classes}")
    
    # Look for price elements
    print("\n=== LOOKING FOR PRICES ===\n")
    
    price_patterns = ['R', 'price', 'cost', 'amount']
    for pattern in price_patterns:
        elements = soup.find_all(text=lambda t: pattern in str(t).upper())[:3]
        if elements:
            print(f"Found elements containing '{pattern}':")
            for e in elements:
                print(f"  - {str(e)[:100]}")
    
    # Check page title/structure
    print("\n=== PAGE STRUCTURE ===\n")
    title = soup.find('title')
    print(f"Title: {title.string if title else 'N/A'}")
    
    main_content = soup.find('main') or soup.find('div', class_='container')
    print(f"Main content tag: {main_content.name if main_content else 'Not found'}")

if __name__ == "__main__":
    debug_page_structure()