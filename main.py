import time
import random
from trackers.autotraderTracker import scrape_autotrader
from trackers.gumtreeTracker import scrape_gumtree
from trackers.baseTracker import load_bike_list, load_previous_listings, save_listings
from logger.logger import logger
from config.config import SLEEP_MIN, SLEEP_MAX


SCRAPERS = [
    scrape_autotrader,
    scrape_gumtree 
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

            print("\n" + "─"*60)
            print("DETAILS:")
            print("─"*60 + "\n")

            for listing in all_new_listings:
                print(f"[{listing['source']}] {listing['title']}")
                print(f"   {listing['price']}")
                print(f"   {listing['url']}")
                print(f"   Search: {listing['search_term']}\n")
        
        else:
            print("\nNo new listings found accross all sites")

        print("="*60 + "\n")  

        # Save current data
        save_listings(current)
        return all_new_listings
    except KeyboardInterrupt:
        logger.warning('\n\n    Tracker interrupted by user')
        return []
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        return []
    
if __name__ == "__main__":
    main()