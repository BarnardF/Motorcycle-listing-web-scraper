import json
from datetime import datetime, timedelta


def generate_summary(listings: dict, summary_file="data/summary.json"):
    """
    Generates a summary.json file for Make.com to consume.
    
    Args:
        listings: the all_listings dict passed directly from main.py
        summary_file: where to save the summary JSON
    """

    total_listings = 0
    new_listings = []
    price_drops = []

    # Consider a listing "new" if found in the last 8 days (covers weekly runs)
    cutoff = datetime.now() - timedelta(days=8)

    for bike_model, bike_listings in listings.items():

        # Skip empty bike models
        if not bike_listings:
            continue

        for listing_id, listing in bike_listings.items():

            # Skip if listing is not a proper dict
            if not isinstance(listing, dict):
                continue

            total_listings += 1

            # Check for new listings
            found_date_str = listing.get("found_date")
            if found_date_str:
                try:
                    found_date = datetime.strptime(found_date_str, "%d-%m-%Y %H:%M:%S")
                    if found_date >= cutoff:
                        new_listings.append({
                            "bike_model": bike_model,
                            "title": listing.get("title", "Unknown"),
                            "price": listing.get("price", "N/A"),
                            "kilometers": listing.get("kilometers", "N/A"),
                            "location": listing.get("location", "N/A"),
                            "source": listing.get("source", "N/A"),
                            "url": listing.get("url", "")
                        })
                except ValueError:
                    pass

            # Check for price drops
            if listing.get("price_dropped") and listing.get("old_price"):
                price_drops.append({
                    "bike_model": bike_model,
                    "title": listing.get("title", "Unknown"),
                    "old_price": listing.get("old_price"),
                    "new_price": listing.get("price"),
                    "kilometers": listing.get("kilometers", "N/A"),
                    "location": listing.get("location", "N/A"),
                    "source": listing.get("source", "N/A"),
                    "url": listing.get("url", "")
                })

    summary = {
        "run_date": datetime.now().strftime("%d-%m-%Y %H:%M"),
        "total_listings": total_listings,
        "new_listings_count": len(new_listings),
        "price_drops_count": len(price_drops),
        "new_listings": new_listings,
        "price_drops": price_drops
    }

    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Summary generated: {total_listings} listings, {len(new_listings)} new, {len(price_drops)} price drops")
    return summary
