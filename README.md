# Motorcycle Listing Tracker

A Python-based web scraper that automatically tracks motorcycle listings across multiple South African websites. Get notified when new bikes matching your criteria appear online!

## Features

- **Multi-Site Scraping**: Tracks listings from AutoTrader and Gumtree
- **Smart Duplicate Detection**: Avoids showing the same listing twice
- **Persistent Storage**: Remembers previous runs to detect new listings
- **Configurable Searches**: Track multiple bike models from a simple text file
- **Professional Logging**: Detailed logs for debugging and monitoring
- **Robust Error Handling**: Continues running even if individual listings fail
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
├── config.py                   # Configuration settings
├── logger.py                   # Logging utility
├── bikes.txt                   # List of bikes to track
├── listings.json              # Stored listings (auto-generated)
├── tracker.log                # Detailed logs (auto-generated)
├── trackers/
│   ├── __init__.py
│   ├── baseTracker.py        # Shared functionality
│   ├── autotraderTracker.py  # AutoTrader scraper
│   └── gumtreeTracker.py     # Gumtree scraper
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Configuration

### Global Settings

Edit `config.py` to customize:
- **File paths**: Change where data/logs are stored
- **Request settings**: Adjust timeouts and user agent
- **Rate limiting**: Modify sleep intervals between requests
- **Logging**: Change log levels and formats

Example:
```python
# File paths
DATA_FILE = "listings.json"
BIKE_FILE = "bikes.txt"
LOG_FILE = "tracker.log"

# Rate limiting (seconds)
SLEEP_MIN = 2
SLEEP_MAX = 4

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

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
- **AutoTrader** (autotrader.co.za) - Requires "Brand Model" format
- **Gumtree** (gumtree.co.za) - Flexible search format

## Output Example
```
============================================================
🏍️  MOTORCYCLE LISTING TRACKER
============================================================

📋 Tracking 2 bike model(s) across 2 site(s):
   • Honda Rebel 500
   • Triumph Scrambler 400 x

------------------------------------------------------------
🔍 [1/2] Searching for: Honda Rebel 500
------------------------------------------------------------

[AutoTrader] Searching: Honda Rebel 500
[AutoTrader] Found 3 listing(s) for Honda Rebel 500
[Gumtree] Searching: Honda Rebel 500
[Gumtree] Found 1 listing(s) for Honda Rebel 500

🆕 2 NEW listing(s) for Honda Rebel 500
   • [AutoTrader] 2024 Honda Rebel 500 - R 85,000
   • [Gumtree] Honda Rebel 500 ABS - R 78,000

============================================================
📊 SUMMARY
============================================================

🎉 TOTAL: 2 NEW LISTING(S) FOUND

   • AutoTrader: 1 new listing(s)
   • Gumtree: 1 new listing(s)

------------------------------------------------------------
📋 DETAILS
------------------------------------------------------------

[AutoTrader] 2024 Honda Rebel 500
   💰 R 85,000
   🔗 https://www.autotrader.co.za/bikes-for-sale/...
   🔍 Search: Honda Rebel 500

[Gumtree] Honda Rebel 500 ABS
   💰 R 78,000
   🔗 https://www.gumtree.co.za/...
   🔍 Search: Honda Rebel 500

============================================================

✓ Listings saved successfully
✓ Tracking complete! Found 2 new listing(s)
```

## Logging

The tracker creates detailed logs in `tracker.log`:

```
2024-11-01 14:23:15 - INFO - Loaded 5 bike model(s) from bikes.txt
2024-11-01 14:23:16 - INFO - [AutoTrader] Searching: Honda Rebel 500
2024-11-01 14:23:17 - DEBUG - Fetching: https://www.autotrader.co.za/...
2024-11-01 14:23:18 - INFO - [AutoTrader] Found 3 listing(s)
2024-11-01 14:23:19 - WARNING - [AutoTrader] Skipping malformed listing 2
```

**Log Levels:**
- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: Something unexpected happened, but still working
- **ERROR**: A serious problem occurred

Change log level in `config.py`:
```python
LOG_LEVEL = "DEBUG"  # For verbose logging
LOG_LEVEL = "INFO"   # Default (recommended)
LOG_LEVEL = "ERROR"  # Only show errors
```

## Adding New Websites

1. Create a new scraper in `trackers/`
2. Follow the pattern from existing scrapers
3. Add to `SCRAPERS` list in `main.py`

Example:
```python
# trackers/newSiteTracker.py
from trackers.baseTracker import fetch_page, create_listing
from logger import logger
from config import NEW_SITE_BASE_URL

SOURCE = "NewSite"

def scrape_newsite(search_term):
    """Scrape NewSite for a specific search term"""
    url = f"{NEW_SITE_BASE_URL}/search?q={search_term}"
    
    logger.info(f"[{SOURCE}] Searching: {search_term}")
    
    soup = fetch_page(url)
    if not soup:
        return {}
    
    listings = {}
    # ... extract listings ...
    
    logger.info(f"[{SOURCE}] Found {len(listings)} listing(s)")
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

And in `config.py`:
```python
NEW_SITE_BASE_URL = "https://newsite.com"
```

## Troubleshooting

### "No listings found" for existing bikes

- Check the bike name format matches the website exactly
- Try different variations (e.g., "CB500X" vs "CB 500 X")
- Check if the bike exists on that website
- Look in `tracker.log` for detailed error messages

### 404 Errors

- Verify the bike model name is correct
- Some bikes may not be available on all sites
- Check the website URL structure hasn't changed
- View the actual URL in `tracker.log` (set `LOG_LEVEL = "DEBUG"`)

### Rate Limiting / Getting Blocked

If you're getting blocked:
- Increase sleep intervals in `config.py`:
  ```python
  SLEEP_MIN = 4
  SLEEP_MAX = 7
  ```
- Run less frequently
- Check website's `robots.txt`
- Review logs for HTTP 429 (Too Many Requests) errors

### Script Crashes

- Check `tracker.log` for detailed error messages
- Enable DEBUG logging in `config.py`:
  ```python
  LOG_LEVEL = "DEBUG"
  ```
- Look for patterns in which scraper is failing
- One scraper failure won't crash the entire script anymore

### Malformed Listings

The tracker now handles malformed listings gracefully:
- Skips listings with missing data
- Logs warnings for debugging
- Continues processing other listings
- Check `tracker.log` to see which listings were skipped

## Advanced Usage

### Running Periodically

**Linux/Mac (cron):**
```bash
# Edit crontab
crontab -e

# Run every day at 9 AM
0 9 * * * cd /path/to/motorcycle-tracker && python main.py

# Run every 6 hours
0 */6 * * * cd /path/to/motorcycle-tracker && python main.py
```

**Windows (Task Scheduler):**
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, hourly, etc.)
4. Action: Start a program
5. Program: `python`
6. Arguments: `C:\path\to\motorcycle-tracker\main.py`
7. Start in: `C:\path\to\motorcycle-tracker`

### Monitoring Logs

**View recent activity:**
```bash
tail -f tracker.log
```

**Search for errors:**
```bash
grep ERROR tracker.log
```

**Count new listings found today:**
```bash
grep "NEW listing(s)" tracker.log | grep "$(date +%Y-%m-%d)"
```

## To-Do

Phase 2 (High-Value Features):
- [ ] Email notifications
- [ ] Price drop alerts
- [ ] Better CLI output with colors

Phase 3 (Automation):
- [ ] Command-line arguments (--quiet, --verbose, etc.)
- [ ] Daily automation guide
- [ ] Summary reports

Phase 4 (Polish):
- [ ] More scrapers (Cars.co.za, OLX)
- [ ] Web dashboard (Flask)
- [ ] SQLite database
- [ ] Price history tracking
- [ ] Export to CSV/HTML

## Legal & Ethics

This project is for **personal use only**. Please:
- Respect website Terms of Service
- Don't overwhelm servers (use rate limiting)
- Don't use scraped data commercially
- Check `robots.txt` for each website
- Be a good internet citizen
- Don't circumvent anti-scraping measures

**Ethical Guidelines:**
- Reasonable request intervals (2-4 seconds minimum)
- Proper User-Agent identification
- Respect rate limits and 429 responses
- Don't scrape personal/private information
- Use scraped data responsibly

## Contributing

Contributions are welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/new-scraper`)
3. Follow existing code patterns (error handling, logging, etc.)
4. Update documentation if adding features
5. Test thoroughly with various bikes
6. Commit changes (`git commit -am 'Add OLX scraper'`)
7. Push to branch (`git push origin feature/new-scraper`)
8. Open a Pull Request

**Code Standards:**
- Use logging instead of print statements
- Handle errors gracefully (try-except)
- Add docstrings to functions
- Follow existing naming conventions
- Update `config.py` for new settings

## Changelog

### Version 2.0 (Current)
- Added centralized configuration (`config.py`)
- Implemented professional logging system
- Enhanced error handling and resilience
- Random sleep intervals for human-like behavior
- Better validation and debugging tools
- Fixed typos and improved output formatting

### Version 1.0
- Initial release
- AutoTrader and Gumtree scrapers
- Basic duplicate detection
- JSON storage for listings

## Acknowledgments

- Built as a learning project to understand web scraping
- Inspired by the need to find good motorcycle deals in South Africa
- This project was created with the assistance of AI (Claude and ChatGPT)
- Thanks to the Python community for excellent libraries (requests, BeautifulSoup)

---

**Questions or Issues?** Check `tracker.log` first, then open an issue on GitHub!