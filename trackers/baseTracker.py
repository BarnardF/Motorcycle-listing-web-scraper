import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from logger.logger import logger
from config.config import DATA_FILE, BIKE_FILE, REQUEST_TIMEOUT, USER_AGENT



HEADERS = {
    "User-Agent": USER_AGENT
}



def fetch_page(url):
    """
    Fetch a webpage and return BeautifulSoup object
    
    Args:
        url: URL to fetch
        
    Returns:
        BeautifulSoup object or None if request fails
    """
    try:
        logger.debug(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        logger.debug(f"Successfully fetched {url} (status: {response.status_code})")
        return BeautifulSoup(response.content, 'html.parser')
    except requests.Timeout:
        logger.error(f"Request timeout for {url}")
        return None
    except requests.HTTPError as e:
        logger.error(f"HTTP error for {url}: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Request failed for {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None


def create_listing(listing_id, title, price, url, search_term, source):
    """
    Create a standardized listing dictionary
    
    Args:
        listing_id: Unique identifier for the listing
        title: Listing title
        price: Listing price
        url: Full URL to the listing
        search_term: Search term used to find this listing
        source: Source website name
        
    Returns:
        Dictionary containing listing information
    """
    return {
        'id': listing_id,
        'title': title.strip() if title else "",
        'price': price.strip() if price else "N/A",
        'url': url,
        'search_term': search_term,
        'source': source,
        'found_date': datetime.now().isoformat()
    }


def load_bike_list(filename=BIKE_FILE):
    """
    Load bike models from text file
    
    Args:
        filename: Path to bike list file
        
    Returns:
        List of bike model strings
    """
    if not os.path.exists(filename):
        logger.error(f"{filename} not found, Please create it with bike models (one per line)")
        return []
    
    bikes = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f,1):
                #strip whitespaces including newlines
                line = line.strip()
                #skip empty lines and comments
                if line and not line.startswith("#"):
                    bikes.append(line)
                    logger.debug(f"Loaded bike from line {line_num}: {line}")

        #remove duplicates while preserving order
        seen = set()
        unique_bikes = []
        for bike in bikes:
            if bike not in seen:
                seen.add(bike)
                unique_bikes.append(bike)
        
        logger.info(f"Loaded {len(unique_bikes)} unique bike model(s) form {filename}")
        return unique_bikes
    except Exception as e:
        logger.error(f"Error reading {filename}: {e}")
        return []


def load_previous_listings(filename=DATA_FILE):
    """
    Load previously saved listings from JSON file
    
    Args:
        filename: Path to listings JSON file
        
    Returns:
        Dictionary of previous listings organized by bike model
    """
    if not os.path.exists(filename):
        logger.info(f"{filename} not found, creating new file...")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)
                return {}
        except Exception as e:
            logger.error(f"Could not create {filename}: {e}")
            return {}
        
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Loaded previous listings from {filename}")
        return data
    except json.JSONDecodeError as e:
        logger.warning(f"Currupted {filename}, resetting file: {e}")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)
        except Exception as e2:
            logger.error(f"Could not reset {filename}: {e2}")
        return {}
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        return {}

            

def save_listings(listings_by_bike, filename=DATA_FILE):
    """
    Save all listings organized by bike model to JSON file
    
    Args:
        listings_by_bike: Dictionary of listings organized by bike model
        filename: Path to save JSON file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        #ensure directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(listings_by_bike, f, indent=2, ensure_ascii=False)

        total = sum(len(listings) for listings in listings_by_bike.values())
        logger.info(f"Saved {total} total listing(s) for {len(listings_by_bike)} bike model(s)")
        return True
    except Exception as e:
        logger.error(f"Error saving listings to {filename}: {e}")
        return False
    

def clean_stale_listings(all_listings, current_run_ids):
    """
    Remove listings that no longer appear on the websites
    
    Args:
        all_listings: Dict of all stored listings by bike
        current_run_ids: Set of listing IDs found in current scrape
        
    Returns:
        Cleaned listings dict and count of removed listings
    """
    removed_count = 0
    cleaned = {}
    
    for bike, listings in all_listings.items():
        cleaned[bike] = {}
        for listing_id, listing_data in listings.items():
            if listing_id in current_run_ids:
                # Listing still exists on website
                cleaned[bike][listing_id] = listing_data
            else:
                # Listing no longer found - likely sold/removed
                logger.info(f"Removing stale listing: {listing_data.get('title', 'Unknown')} ({listing_data.get('source', 'Unknown')})")
                removed_count += 1
    
    return cleaned, removed_count


def validate_search_term(search_term, required_format=True):
    """
    Validate search term format
    
    Args:
        search_term: The search term to validate
        required_format: Optional format requirement (e.g., "Brand Model")
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not search_term or not search_term.strip():
        return False, "Search term is empty"
    
    if required_format == "Brand Model":
        parts = search_term.strip().split(maxsplit=1)
        if len(parts) < 2:
            return False, f"Invalid foramt: '{search_term}' (Expected: Brand Model, e.g., 'Honda CB500X')"
        
    return True, None


def is_relevant_match(listing_title, search_term, min_match_ratio=0.5):
    """
    Check if listing title is relevant to search term
    
    Args:
        listing_title: The listing title
        search_term: Original search term
        min_match_ratio: Minimum ratio of matching words (0.0-1.0)
        
    Returns:
        True if relevant, False otherwise
    """
    # Normalize strings
    title_words = set(listing_title.lower().split())
    search_words = set(search_term.lower().split())
    
    # Remove common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'for', 'with'}
    title_words -= stop_words
    search_words -= stop_words
    
    # Calculate match ratio
    if not search_words:
        return True
    
    matching_words = title_words & search_words
    match_ratio = len(matching_words) / len(search_words)
    
    return match_ratio >= min_match_ratio
