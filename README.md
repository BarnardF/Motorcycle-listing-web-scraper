# Motorcycle Listing Tracker

A Python-based web scraper that automatically tracks motorcycle listings across multiple South African websites. Get notified when new bikes matching your criteria appear online!

## Features

- **Multi-Site Scraping**: Tracks listings from AutoTrader and Gumtree
- **Smart Duplicate Detection**: Avoids showing the same listing twice
- **Persistent Storage**: Remembers previous runs to detect new listings
- **Configurable Searches**: Track multiple bike models from a simple text file
- **Clean Output**: Organized summary by source with detailed listing information
- **Extensible Architecture**: Easy to add new websites

## Quick Start


### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/motorcycle-tracker.git
cd motorcycle-tracker
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure your bikes**

Create a `bikes.txt` file with the motorcycles you want to track (one per line):
```
Suzuki DS 250 SX V-STROM
Triumph Scrambler 400 x
Honda Rebel 500
BMW G 310
```

4. **Run the tracker**
```bash
python main.py
```

## Project Structure
```
motorcycle-tracker/
├── main.py                     # Main entry point
├── bikes.txt                   # List of bikes to track
├── listings.json              # Stored listings (auto-generated)
├── trackers/
│   ├── __init__.py
│   ├── baseTracker.py        # Shared functionality
│   ├── autotraderTracker.py  # AutoTrader scraper
│   └── gumtreeTracker.py     # Gumtree scraper
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Configuration

### Adding Bikes

Edit `bikes.txt` and add bikes in the format: `Brand Model`
```
# Adventure bikes
Suzuki DS 250 SX V-STROM
BMW G 310 GS

# Cruisers
Honda Rebel 500
Triumph Bonneville

# Comments start with #
```

### Supported Websites

Currently supports:
- **AutoTrader** (autotrader.co.za)
- **Gumtree** (gumtree.co.za)


## Output Example
```
Searching for: Suzuki DS 250 SX V-STROM
────────────────────────────────────────
  AutoTrader: Suzuki DS 250 SX V-STROM
  Found 3 listings
  Gumtree: Suzuki DS 250 SX V-STROM
  Found 1 listings

  4 NEW listing(s) for Suzuki DS 250 SX V-STROM
     • [AutoTrader] 2025 Suzuki DS 250 - R 61 800
     • [Gumtree] 2024 Suzuki V-Strom - R 51,000

========================================
SUMMARY
========================================

TOTAL: 4 NEW LISTING(S) FOUND

    AutoTrader: 3 new listing(s)
    Gumtree: 1 new listing(s)
```



## Adding New Websites

1. Create a new scraper in `trackers/`
2. Follow the pattern from existing scrapers
3. Add to `SCRAPERS` list in `main.py`

Example:
```python
# trackers/newSiteTracker.py
from .baseTracker import fetch_page, create_listing

def scrape_newsite(search_term):
    url = f"https://newsite.com/search?q={search_term}"
    soup = fetch_page(url)
    # ... extract listings ...
    return listings
```

Then in `main.py`:
```python
from trackers.newSiteTracker import scrape_newsite

SCRAPERS = [
    scrape_autotrader,
    scrape_gumtree,
    scrape_newsite  # Add here
]
```

## Troubleshooting

### "No listings found" for existing bikes

- Check the bike name format matches the website exactly
- Try different variations (e.g., "CB500X" vs "CB 500 X")
- Check if the bike exists on that website

### 404 Errors

- Verify the bike model name is correct
- Some bikes may not be available on all sites
- Check the website URL structure hasn't changed

### Rate Limiting

If you're getting blocked:
- Increase `time.sleep(2)` to `time.sleep(5)` in `main.py`
- Run less frequently
- Check website's `robots.txt`

## To-Do

- [ ] Daily Automation
- [ ] Email notifications
- [ ] Price drop alerts
- [ ] Web dashboard (Flask)
- [ ] SQLite database
- [ ] Price history tracking


## Legal & Ethics

This project is for **personal use only**. Please:
- Respect website Terms of Service
- Don't overwhelm servers (use rate limiting)
- Don't use scraped data commercially
- Check `robots.txt` for each website
- Be a good internet citizen

## Contributing

Contributions are welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/new-scraper`)
3. Commit changes (`git commit -am 'Add OLX scraper'`)
4. Push to branch (`git push origin feature/new-scraper`)
5. Open a Pull Request


## Acknowledgments

- Built as a learning project to understand web scraping
- Inspired by the need to find good motorcycle deals in South Africa

---
