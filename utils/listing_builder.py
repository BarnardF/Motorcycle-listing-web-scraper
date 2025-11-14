"""
Unified Listing Builder
Creates standardized listing dictionaries with price history tracking.
Used by all scrapers for consistency.
"""

from datetime import datetime


def build_listing(listing_id, title, price, url, search_term, source, **extra_fields):
    """
    Create a standardized listing dictionary with all required fields.
    
    This function ensures ALL scrapers use the same structure, preventing bugs
    from inconsistent data formats.
    
    Args:
        listing_id (str): Unique identifier for the listing
                         - AutoTrader: listing ID from URL
                         - Gumtree: gt_{data-adid}
                         - WeBuyCars: webuycars_{StockNumber}
        
        title (str): Listing title/description
                    - AutoTrader: span.e-make-model-title
                    - Gumtree: a.related-ad-title span
                    - WeBuyCars: OnlineDescription field
        
        price (str): Listing price (should include "R" prefix if available)
                    Examples: "R 61,800", "R 89,900", "R 48,000"
        
        url (str): Full URL to the listing on the source website
                  - AutoTrader: https://www.autotrader.co.za/...
                  - Gumtree: https://www.gumtree.co.za/...
                  - WeBuyCars: https://www.webuycars.co.za/...
        
        search_term (str): Original search term used to find this listing
                          This is used for grouping in the dashboard
                          Example: "Honda CB 500 X" (from bikes.txt)
        
        source (str): Source website name
                     Must be one of: "AutoTrader", "Gumtree", "WeBuyCars"
                     This is critical for tracking and display
        
        **extra_fields: Additional optional fields
                       - kilometers (str): Mileage or "New"
                       - location (str): Suburb/city
                       - condition (str): "New", "Used", "Demo" (Where applicable)
                       - Any other custom fields
        
    Returns:
        dict: Standardized listing with price_history tracking
    """
    clean_price = price.strip() if price else "N/A"
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    listing = {
        'id': listing_id,
        'title': title.strip() if title else "",
        'price': clean_price,
        'price_history': [{
            'date': current_time,
            'price': clean_price
        }],
        'url': url,
        'search_term': search_term,
        'source': source,
        'found_date': current_time
    }
    
    # Add any extra fields (kilometers, location, condition, etc.)
    listing.update(extra_fields)
    
    return listing