import time
import random
import sys
import os
from datetime import datetime



from trackers.baseTracker import load_bike_list, load_previous_listings, save_listings, clean_stale_listings
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


def main():
    try:
        print("="*60)
        print("MOTORCYCLE LISTING TRACKER")
        print("="*60)

        bikes = load_bike_list()
        if not bikes:
            logger.error("No bikes to track. Please add bikes to bikes.txt")
            return
        
        logger.info(f"Tracking {len(bikes)} bike model(s)...")
        for bike in bikes:
            print(f"     -- {bike}")
        print()

        previous = load_previous_listings()
        current = {}
        all_new_listings = []
        all_price_drops = []

        #Scrape each bike on each site
        for bike in bikes:
            print(f"\n{'─'*60}")
            print(f"Searching for: {bike}")
            print(f"{'─'*60}")

            bike_listings = {}

            for scraper in SCRAPERS:
                try:
                    scraper_listings = scraper(bike)
                    bike_listings.update(scraper_listings)

                    sleep_time = random.uniform(SLEEP_MIN, SLEEP_MAX)
                    logger.debug(f"Sleeping for {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                except Exception as e:
                    logger.error(f"Error running scraper {scraper.__name__} for {bike}: {e}")
                    continue

            previous_listings = previous.get(bike, {})
            new_listings = {}

            for listings_id, listing in bike_listings.items():
                if listings_id not in previous_listings:
                    new_listings[listings_id] = listing
                    all_new_listings.append(listing)

            if new_listings:
                print(f"{len(new_listings)} NEW listing(s) for {bike}")
                for listing in new_listings.values():
                    print(f"    --[{listing['source']}] {listing['title']} - {listing['price']}")
            else:
                print(f"\nNo new listings for {bike}")

            #price comparison
            for listing_id, current_listing in bike_listings.items():
                if listing_id in previous_listings:
                    old_listing = previous_listings[listing_id]

                    #carry over price history
                    current_listing['price_history'] = previous_listings[listing_id].get('price_history', [])

                    old_price = old_listing.get('price', '').replace("R", "").replace(",", "").strip()
                    new_price = current_listing.get('price', '').replace("R", "").replace(",", "").strip()

                    # Default values
                    current_listing['price_dropped'] = False
                    current_listing['old_price'] = None

                    if old_price.isdigit() and new_price.isdigit():
                        old_price_val = int(old_price)
                        new_price_val = int(new_price)

                        #check if price changed
                        if new_price_val != old_price_val:
                            #update price history
                            current_listing['price_history'].append({
                                'date': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                                'price': current_listing.get('price', 'N/A')
                            })

                            #check if price dropped
                            if new_price_val < old_price_val:
                                drop_amount = old_price_val - new_price_val
                                logger.info(f"Price drop detected for {current_listing['title']}: "
                                            f"R{old_price_val} -> R{new_price_val} " 
                                            f"(R{drop_amount} drop) [{current_listing['source']}]")
                                current_listing['price_dropped'] = True
                                current_listing['old_price'] = old_listing.get('price') 
                                all_price_drops.append(current_listing)

                                print(f"   Price drop: {current_listing['title']}")
                                print(f"   {old_listing.get('price')} -> {current_listing['price']} (Save R{drop_amount}!)")

            current[bike] = bike_listings

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)    

        if all_new_listings:
            by_source = {}
            for listing in all_new_listings:
                source = listing['source']
                by_source.setdefault(source, []).append(listing)

            print(f"\n TOTAL: {len(all_new_listings)} NEW LISTING(S) FOUND\n")

            for source, listing in by_source.items():
                print(f"    {source}: {len(listing)} new listing(s)")

            # print("\n" + "─"*60)
            # print("DETAILS:")
            # print("─"*60 + "\n")

            # for listing in all_new_listings:
            #     print(f"[{listing['source']}] {listing['title']}")
            #     print(f"   {listing['price']}")
            #     print(f"   {listing['url']}")
            #     print(f"   Search: {listing['search_term']}\n")
        
        else:
            print("\nNo new listings found accross all sites")

        print("="*60 + "\n")  

        # Clean up old listings - ONLY for live scrapers (AutoTrader, Gumtree)
        # Don't remove WeBuyCars listings (cache-based, IDs change each run)
        current_run_ids = set()
        for bike_listings in current.values():
            for listing_id, listing in bike_listings.items():
                # Only track IDs from live scrapers
                if listing.get('source') in LIVE_SCRAPERS:
                    current_run_ids.add(listing_id)

        # Clean stale listings - only for live scrapers
        previous_for_cleanup = {}
        for bike, listings in previous.items():
            # Filter to only live scraper listings
            previous_for_cleanup[bike] = {
                lid: listing for lid, listing in listings.items() 
                if listing.get('source') in LIVE_SCRAPERS
            }

        all_listings, removed_count = clean_stale_listings(previous_for_cleanup, current_run_ids)

        if removed_count > 0:
            logger.info(f"Removed {removed_count} stale listing(s) (likely sold/removed)")  
        # Merge ALL current listings (including WeBuyCars cache)
        for bike, listings in current.items():
            if bike not in all_listings:
                all_listings[bike] = {}
            all_listings[bike].update(listings)

        # Save current listings
        if save_listings(all_listings):
            logger.info("Listings saved successfully")
        else:
            logger.error("Failed to save listings")

        # Pass ALL listings (both old and new), not just new ones
        all_listings_flat = []
        for bike_listings in current.items():
            all_listings_flat.extend(bike_listings[1].values())

        generate_html_report(all_listings_flat, bikes, "docs/index.html")
        
        logger.info(f"Tracking completed! Found {len(all_new_listings)} new listing(s)")

        return all_new_listings
    
    except KeyboardInterrupt:
        logger.warning('\n\n    Tracker interrupted by user')
        return []
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        return []
    
if __name__ == "__main__":
    main()