import time

from trackers.autotraderTracker import scrape_autotrader
from trackers.gumtreeTracker import scrape_gumtree
from trackers.baseTracker import load_bike_list, load_previous_listings, save_listings

SCRAPERS = [
    scrape_autotrader,
    scrape_gumtree 
]


def main():
    print("="*40)
    print("Motercycle listing tracker")
    print("="*40)

    bikes = load_bike_list()
    if not bikes:
        print("No bikes to track, add bikes to bikes.txt")
        return
    
    print(f"\n📋 Tracking {len(bikes)} bike model(s) across {len(SCRAPERS)} site(s):")
    for bike in bikes:
        print(f"     -- {bike}")
    print()

    previous = load_previous_listings()
    current = {}
    all_new_listings = []

    #Scrape each bike on each site
    for bike in bikes:
        print(f"\n{'─'*40}")
        print(f"Searching for: {bike}")
        print(f"{'─'*40}")

        bike_listings = {}

        for scraper in SCRAPERS:
            scraper_listings = scraper(bike)
            bike_listings.update(scraper_listings)
            time.sleep(2)

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
            print(f"\n  No new listings for {bike}")

        current[bike] = bike_listings

    print("\n" + "="*40)
    print("SUMMARY")
    print("="*40)    

    if all_new_listings:
        by_source = {}
        for listing in all_new_listings:
            source = listing['source']
            by_source.setdefault(source, []).append(listing)

        print(f"\n TOTAL: {len(all_new_listings)} NEW LISTING(S) FOUND\n")

        for source, listing in by_source.items():
            print(f"    {source}: {len(listing)} new listing(s)")

        print("\n" + "─"*40)
        print("DETAILS:")
        print("─"*40 + "\n")

        for listing in all_new_listings:
            print(f"[{listing['source']}] {listing['title']}")
            print(f"   {listing['price']}")
            print(f"   {listing['url']}")
            print(f"   Search: {listing['search_term']}\n")
    
    else:
        print("\n No new listings found accross all sites")

    print("="*40 + "\n")  

    # Save current data
    save_listings(current)
    return all_new_listings
    
if __name__ == "__main__":
    main()