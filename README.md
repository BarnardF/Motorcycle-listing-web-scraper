# Motorcycle Listing Tracker

A Python-based web scraper that automatically tracks motorcycle listings across multiple South African websites. View your findings on a beautiful GitHub Pages dashboard!

## Features

- **Multi-Site Scraping**: Tracks listings from AutoTrader and Gumtree
- **Smart Duplicate Detection**: Avoids showing the same listing twice
- **Persistent Storage**: Remembers previous runs to detect new listings
- **GitHub Pages Dashboard**: Beautiful web interface to view all listings
- **Configurable Searches**: Track multiple bike models from a simple text file
- **Professional Logging**: Detailed logs for debugging and monitoring
- **Robust Error Handling**: Continues running even if individual listings fail
- **Clean Output**: Organized summary by source with detailed listing information
- **Extensible Architecture**: Easy to add new websites


## Project Structure
```
motorcycle-tracker/
├── main.py                     # Main entry point
├── config.py                   # Configuration settings
├── html_generator.py           # GitHub Pages HTML generator
├── bikes.txt                   # List of bikes to track
├── listings.json              # Stored listings (auto-generated)
├── tracker.log                # Detailed logs (auto-generated)
├── docs/
│   └── index.html             # GitHub Pages dashboard (auto-generated)
├── logger/
│   └── logger.py              # Logging utility
├── trackers/
│   ├── __init__.py
│   ├── baseTracker.py        # Shared functionality
│   ├── autotraderTracker.py  # AutoTrader scraper
│   └── gumtreeTracker.py     # Gumtree scraper
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## GitHub Pages Dashboard

The tracker automatically generates a beautiful web dashboard that you can host on GitHub Pages!

### Setting Up GitHub Pages

1. **Push your repository to GitHub** (if not already done)
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Click **Settings** → **Pages**
   - Under "Source", select:
     - Branch: `main`
     - Folder: `/docs`
   - Click **Save**

3. **Access your dashboard**
   - Your listings will be available at: `https://yourusername.github.io/motorcycle-tracker`
   - GitHub will show you the exact URL in Settings → Pages

### Updating the Dashboard

Every time you run `python main.py`, the dashboard is automatically updated with the latest listings. To publish changes:

```bash
git add docs/index.html
git commit -m "Update motorcycle listings"
git push
```

GitHub Pages will automatically refresh within a few minutes.

### Dashboard Features

The web dashboard includes:
- 📊 **Statistics**: Total listings, bikes tracked, sources
- 🏍️ **Grouped Listings**: Organized by motorcycle model
- 🎨 **Dark Theme**: Easy on the eyes with red accents
- 📱 **Mobile Responsive**: Works great on phones and tablets
- ✨ **Hover Effects**: Interactive cards with smooth animations
- 🔗 **Direct Links**: Click to view any listing on the original site
- ⏰ **Timestamp**: See when the page was last updated

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

### Console Output
```
============================================================
🏍️  MOTORCYCLE LISTING TRACKER
============================================================

📋 Tracking 5 bike model(s) across 2 site(s):
   • Suzuki DS 250 SX V-STROM
   • Triumph Scrambler 400 x
   • Honda Rebel 500

------------------------------------------------------------
🔍 [1/5] Searching for: Suzuki DS 250 SX V-STROM
------------------------------------------------------------

[AutoTrader] Searching: Suzuki DS 250 SX V-STROM
[AutoTrader] Found 3 listing(s)
[Gumtree] Searching: Suzuki DS 250 SX V-STROM
[Gumtree] Found 1 listing(s)

🆕 4 NEW listing(s) for Suzuki DS 250 SX V-STROM

============================================================
📊 SUMMARY
============================================================

🎉 TOTAL: 21 NEW LISTING(S) FOUND

   • AutoTrader: 19 new listing(s)
   • Gumtree: 2 new listing(s)

✓ Generated HTML report: docs/index.html
✓ Listings saved successfully
✓ Tracking complete! Found 21 new listing(s)
```

## Logging

The tracker creates detailed logs in `tracker.log`:

```
2025-11-01 14:23:15 - INFO - Loaded 5 unique bike model(s) from bikes.txt
2025-11-01 14:23:16 - INFO - [AutoTrader] Searching: Honda Rebel 500
2025-11-01 14:23:17 - DEBUG - Fetching: https://www.autotrader.co.za/...
2025-11-01 14:23:18 - INFO - [AutoTrader] Found 3 listing(s)
2025-11-01 14:23:19 - WARNING - [AutoTrader] Skipping malformed listing 2
2025-11-01 14:23:25 - INFO - ✓ Generated HTML report: docs/index.html
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
from logger.logger import logger
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

### GitHub Pages Not Updating

- Make sure you've enabled GitHub Pages in Settings
- Check that you selected the `/docs` folder
- Wait a few minutes after pushing (GitHub takes time to rebuild)
- Check the Actions tab for build errors
- Verify `docs/index.html` exists and is committed

## Advanced Usage

### Running Periodically

**Linux/Mac (cron):**
```bash
# Edit crontab
crontab -e

# Run every day at 9 AM and auto-push to GitHub
0 9 * * * cd /path/to/motorcycle-tracker && python main.py && git add docs/index.html && git commit -m "Auto-update listings" && git push

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

### Automated Git Push (Optional)

Create a bash script `update_and_push.sh`:
```bash
#!/bin/bash
cd /path/to/motorcycle-tracker
python main.py

# Check if docs/index.html changed
if git diff --quiet docs/index.html; then
    echo "No changes to publish"
else
    git add docs/index.html
    git commit -m "Auto-update listings $(date '+%Y-%m-%d %H:%M')"
    git push
    echo "Listings updated and pushed to GitHub"
fi
```

Make it executable:
```bash
chmod +x update_and_push.sh
```

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

### Version 2.1 (Current)
- Added GitHub Pages HTML dashboard
- Beautiful dark theme with red accents
- Mobile-responsive design
- Auto-generates static HTML report
- Statistics and organized listing cards

### Version 2.0
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

- Built as a learning project to understand web scraping and automation
- Inspired by the need to find good motorcycle deals in South Africa
- This project was created with the assistance of AI (Claude)
- HTML dashboard design inspired by [HTML5 UP](https://html5up.net/)
- Thanks to the Python community for excellent libraries (requests, BeautifulSoup)

---

**Questions or Issues?** Check `tracker.log` first, then open an issue on GitHub!

**Want to see a live demo?** Check out the example dashboard at your GitHub Pages URL!