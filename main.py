import concurrent.futures
import random
from datetime import datetime
import asyncio

from trackers.baseTracker import (
    load_bike_list,
    load_previous_listings,
    save_listings,
    clean_stale_listings
)
from logger.logger import logger
from config.config import SLEEP_MIN, SLEEP_MAX
from template_generator.html_generator import generate_html_report

#scrapers
from trackers.autotraderTracker import scrape_autotrader
from trackers.gumtreeTracker import scrape_gumtree
from trackers.webuycarsTracker import scrape_webuycars_cached

SCRAPERS = [
    scrape_autotrader,
    scrape_gumtree,
    scrape_webuycars_cached  
]

LIVE_SCRAPERS = [
    'Autotrader',
    'Gumtree',
]


# ─────────────────────────────────────────────────────────────
# Utility
# ─────────────────────────────────────────────────────────────
def clean_price(price_str: str):
    """Convert 'R 65,000' → 65000 safely."""
    cleaned = price_str.replace("R", "").replace(",", "").strip()
    return int(cleaned) if cleaned.isdigit() else None


# ─────────────────────────────────────────────────────────────
# Async Scraping Logic
# ─────────────────────────────────────────────────────────────
executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)

async def scrape_bike_async(bike, scraper):
    """Run scraping in a thread pool."""
    try:
        loop = asyncio.get_running_loop()
        listings = await loop.run_in_executor(executor, scraper, bike)
        return listings
    except Exception as e:
        logger.error(f"Error running scraper {scraper.__name__} for {bike}: {e}")
        return {}
    
async def scrape_all_bikes_async(bikes):
    """Scrape all bikes across all scrapers concurrently."""
    current = {}

    for bike in bikes:
        print(f"\n{'─'*60}")
        print(f"Searching for: {bike}")
        print(f"{'─'*60}")

        tasks = [scrape_bike_async(bike, scraper) for scraper in SCRAPERS]
        results = await asyncio.gather(*tasks)

        bike_listings = {}
        for result in results:
            if isinstance(result, dict):
                bike_listings.update(result)

        current[bike] = bike_listings

        #only one sleep per bike
        await asyncio.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))
    return current


# ─────────────────────────────────────────────────────────────
# Processing Logic
# ─────────────────────────────────────────────────────────────
def process_listings(current, previous):
    all_new_listings = []
    all_price_drops = []

    for bike, bike_listings in current.items():
        previous_listings = previous.get(bike, {})
        new_for_bike = {}

        #NEW LISITINGS
        for listings_id, listing in bike_listings.items():
            if listings_id not in previous_listings:
                new_for_bike[listings_id] = listing
                all_new_listings.append(listing)

        if new_for_bike:
            print(f"{len(new_for_bike)} NEW listing(s) for {bike}")
            for listing in new_for_bike.values():
                print(f"    --[{listing['source']}] {listing['title']} - {listing['price']}")
        else:
            print(f"\nNo new listings for {bike}")

        #PRICE DROPS
        for listing_id, current_listing in bike_listings.items():
            if listing_id in previous_listings:
                old_listing = previous_listings[listing_id]

                current_listing['price_history'] = old_listing.get('price_history', [])
                current_listing['price_dropped'] = False
                current_listing['old_price'] = None

                old_p = clean_price(old_listing.get('price', ''))
                new_p = clean_price(current_listing.get('price', ''))

                if old_p is not None and new_p is not None and old_p != new_p:
                    #update price history
                    current_listing['price_history'].append({
                        'date': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        'price': current_listing.get('price', 'N/A')
                    })

                    #check for price drop
                    if new_p < old_p:
                        drop_amount = old_p - new_p
                        logger.info(
                            f"Price drop detected for {current_listing['title']}: "
                            f"R{old_p} -> R{new_p} (R{drop_amount} drop)"
                        )

                        current_listing['price_dropped'] = True
                        current_listing['old_price'] = old_listing.get('price') 
                        all_price_drops.append(current_listing)

                        print(f"   Price drop: {current_listing['title']}")
                        print(f"   {old_listing.get('price')} -> {current_listing['price']} (Save R{drop_amount}!)")
    
    return all_new_listings, all_price_drops

def print_summary(new_listings):
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if not new_listings:
        print("\nNo new listings found accross all sites")
        print("="*60 + "\n")
        return
    
    by_source = {}
    for l in new_listings:
        by_source.setdefault(l['source'], []).append(l)

    print(f"\n TOTAL: {len(new_listings)} NEW LISTING(S) FOUND\n")
    for source, items in by_source.items():
        print(f"    {source}: {len(items)} new listing(s)")

    print("="*60 + "\n")


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
async def main():
    try:
        print("=" * 60)
        print("MOTORCYCLE LISTING TRACKER")
        print("=" * 60)

        bikes = load_bike_list()
        if not bikes:
            logger.error("No bikes to track. Please add bikes to bikes.txt")
            return []

        logger.info(f"Tracking {len(bikes)} bike model(s)...")
        for b in bikes:
            print(f"     • {b}")
        print()

        previous = load_previous_listings()

        # Scraping
        current = await scrape_all_bikes_async(bikes)

        # Processing
        new_listings, price_drops = process_listings(current, previous)
        print_summary(new_listings)

        # Clean stale listings (only for live scrapers)
        # Collect all IDs from *this run* that came from live scrapers
        current_run_ids = set()

        for bike_listings in current.values():
            for listing_id, listing in bike_listings.items():
                if listing.get("source") in LIVE_SCRAPERS:
                    current_run_ids.add(listing_id)

        # Build a filtered version of previous listings containing ONLY live-scraper entries
        previous_for_cleanup = {}

        for bike, listings in previous.items():
            live_only = {}
            for listing_id, listing in listings.items():
                if listing.get("source") in LIVE_SCRAPERS:
                    live_only[listing_id] = listing
            previous_for_cleanup[bike] = live_only

        # Clean out stale (missing / sold) listings
        all_listings, removed_count = clean_stale_listings(previous_for_cleanup, current_run_ids)

        if removed_count > 0:
            logger.info(f"Removed {removed_count} stale listing(s) (likely sold/removed)")

        # Merge current listings into all_listings
        for bike, listings in current.items():
            all_listings.setdefault(bike, {})
            all_listings[bike].update(listings)

        # Save
        save_listings(all_listings)

        # Generate HTML
        all_flat = [
            listing
            for bike_listings in current.values()
            for listing in bike_listings.values()
        ]

        generate_html_report(all_flat, bikes, "docs/index.html")
        logger.info("✓ Generated HTML report")

        return new_listings

    except KeyboardInterrupt:
        logger.warning("Tracker interrupted by user")
        return []

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    asyncio.run(main())
