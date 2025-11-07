# Motorcycle Listing Tracker

A Python-based web scraper that automatically tracks motorcycle listings across multiple South African websites. View your findings on a beautiful, interactive GitHub Pages dashboard!

## Features

- **Multi-Site Scraping**: Tracks listings from AutoTrader and Gumtree
- **Comprehensive Data**: Captures price, kilometers, condition, and location
- **Interactive Dashboard**: Toggle between bike-grouped and source-grouped views
- **Table Format**: Clean, sortable tables with all listing details
- **Smart Duplicate Detection**: Avoids showing the same listing twice
- **Persistent Storage**: Remembers previous runs to detect new listings
- **Price Tracking**: Monitors price changes and maintains complete history
- **Price Drop Alerts**: Visual indicators and dedicated view for discounts
- **Green Highlighting**: Easy identification of price-reduced listings
- **GitHub Pages Integration**: Beautiful web interface to view all listings
- **Configurable Searches**: Track multiple bike models from a simple text file
- **Professional Logging**: Detailed logs for debugging and monitoring
- **Robust Error Handling**: Continues running even if individual listings fail
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

This will:
- Scrape all configured websites
- Save results to `listings.json`
- Generate an interactive HTML dashboard in `docs/index.html`
- Create detailed logs in `tracker.log`

## Project Structure
```
motorcycle-tracker/
├── main.py                     # Main entry point
├── html_generator.py           # GitHub Pages HTML generator
├── bikes.txt                   # List of bikes to track
├── listings.json              # Stored listings (auto-generated)
├── tracker.log                # Detailed logs (auto-generated)
├── config/
│   └── config.py              # Configuration settings
├── docs/
│   ├── index.html             # GitHub Pages dashboard (auto-generated)
│   └── styles.css             # Dashboard stylesheet
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

The tracker automatically generates a beautiful, interactive web dashboard that you can host on GitHub Pages!

### Dashboard Features

**📊 Compact Statistics Header**
- Total listings found
- Number of bikes tracked
- Number of sources
- **Price drops detected** (live counter)

**🔄 Triple-View Toggle**
- **By Bike Model** (default): Groups all listings by motorcycle
- **By Source**: Groups all listings by website (AutoTrader, Gumtree, etc.)
- **Price Drops**: Dedicated view showing only listings with price reductions
- Instant switching with toggle buttons

**💸 Price Drop Indicators**
- Visual strikethrough on old prices: ~~R 95,000~~ R 85,000
- Green row highlighting for discounted listings
- Automatic price history tracking
- Drop amount calculated and logged

**📋 Comprehensive Data Tables**

Each listing shows:
- **Source**: Which website (AutoTrader, Gumtree)
- **Title**: Full listing title
- **Price**: Listed price
- **Kilometers**: Mileage/odometer reading
- **Location**: Geographic location (suburb/city)
- **Link**: Direct link to view the listing

**🎨 Modern Design**
- Dark theme with red accents (#e44c65)
- Responsive tables (works on desktop, tablet, mobile)
- Hover effects on table rows
- Clean, professional layout

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

## Configuration

### Global Settings

Edit `config/config.py` to customize:
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

**Important:** Remove any trailing spaces or empty lines to avoid scraping issues.

### Supported Websites

Currently supports:
- **AutoTrader** (autotrader.co.za) 
  - Requires "Brand Model" format
  - Captures: price, kilometers, condition, location
- **Gumtree** (gumtree.co.za) 
  - Flexible search format
  - Captures: price, kilometers, location

## Data Captured

### AutoTrader Listings
- Title (bike make/model/year)
- Price
- Kilometers (odometer reading)
- Condition (New, Used, Demo)
- Location (suburb/city)
- Direct URL

### Gumtree Listings
- Title (bike make/model/year)
- Price
- Kilometers (when available in listing)
- Location (suburb/city)
- Direct URL

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
   • BMW G 310

------------------------------------------------------------
🔍 [1/5] Searching for: Suzuki DS 250 SX V-STROM
------------------------------------------------------------

[AutoTrader] Searching: Suzuki DS 250 SX V-STROM
[AutoTrader] Found 3 listing(s) for Suzuki DS 250 SX V-STROM
[Gumtree] Searching: Suzuki DS 250 SX V-STROM
[Gumtree] Found 1 listing(s) for Suzuki DS 250 SX V-STROM

🆕 4 NEW listing(s) for Suzuki DS 250 SX V-STROM
   • [AutoTrader] 2025 Suzuki DS 250 SX V-STROM - R 61 800
   • [AutoTrader] 2025 Suzuki DS 250 SX V-STROM - R 61 800
   • [AutoTrader] 2025 Suzuki DS 250 SX V-STROM - R 62 420
   • [Gumtree] 2024 Suzuki V-Strom DS 250 SX - R 48,000

============================================================
📊 SUMMARY
============================================================

🎉 TOTAL: 21 NEW LISTING(S) FOUND

   • AutoTrader: 19 new listing(s)
   • Gumtree: 2 new listing(s)

✓ Generated HTML report: docs/index.html
  Total listings: 21
  Bikes with listings: 5
  Sources: 2
✓ Listings saved successfully
✓ Tracking complete! Found 21 new listing(s)
```

## Price Tracking

The tracker automatically monitors price changes across runs:

### How It Works

1. **First Run**: All listings are recorded with their current prices
2. **Subsequent Runs**: 
   - Compares current prices to previous prices
   - Detects drops and increases
   - Updates price history for each listing
   - Highlights price drops in console and dashboard

### Price Drop Detection

When a price drops, you'll see:

**Console Output:**
```
💰 Price drop detected for 2024 Honda Rebel 500: R95,000 → R85,000 (R10,000 drop) [AutoTrader]
   💰 PRICE DROP: 2024 Honda Rebel 500
      R 95,000 → R 85,000 (Save R10,000!)
```

**Dashboard Display:**
- Old price with strikethrough: ~~R 95,000~~
- New price shown clearly: R 85,000
- Entire row highlighted in green
- Listing appears in "Price Drops" tab

### Price History

Each listing maintains a complete price history:
```json
{
  "price_history": [
    {"date": "01-11-2025 10:00:00", "price": "R 95,000"},
    {"date": "05-11-2025 14:30:00", "price": "R 85,000"}
  ]
}
```

This allows you to track price trends over time and identify the best deals.

### Dashboard View

The generated HTML page shows listings in a clean table format:

**View: By Bike Model**
```
Suzuki DS 250 SX V-STROM (4 listings)
┌────────────┬──────────────────────┬──────────┬────────────┬────────────┬──────┐
│ Source     │ Title                │ Price    │ Kilometers │ Location   │ Link │
├────────────┼──────────────────────┼──────────┼────────────┼────────────┼──────┤
│ AutoTrader │ 2025 Suzuki DS 250   │ R 61,800 │ New        │ Cape Town  │ View │
│ AutoTrader │ 2025 Suzuki DS 250   │ R 62,420 │ New        │ Pretoria   │ View │
│ Gumtree    │ 2024 Suzuki V-Strom  │ R 48,000 │ 5,000 km   │ Menlyn     │ View │
└────────────┴──────────────────────┴──────────┴────────────┴────────────┴──────┘
```

**View: By Source** (click toggle button)
```
AutoTrader (19 listings)
┌──────────────────────┬──────────────────────┬──────────┬────────────┬────────────┬──────┐
│ Bike Model           │ Title                │ Price    │ Kilometers │ Location   │ Link │
├──────────────────────┼──────────────────────┼──────────┼────────────┼────────────┼──────┤
│ Suzuki DS 250        │ 2025 Suzuki DS 250   │ R 61,800 │ New        │ Cape Town  │ View │
│ Triumph Speed 400    │ 2025 Triumph Speed   │ R 89,900 │ 500 km     │ Sandton    │ View │
└──────────────────────┴──────────────────────┴──────────┴────────────┴────────────┴──────┘
```

## Logging

The tracker creates detailed logs in `tracker.log`:

```
2025-11-01 11:28:15 - INFO - Loaded 5 unique bike model(s) from bikes.txt
2025-11-01 11:28:16 - INFO - [AutoTrader] Searching: Honda Rebel 500
2025-11-01 11:28:17 - DEBUG - Fetching: https://www.autotrader.co.za/...
2025-11-01 11:28:18 - INFO - [AutoTrader] Found 3 listing(s) for Honda Rebel 500
2025-11-01 11:28:19 - WARNING - [AutoTrader] Skipping malformed listing 2
2025-11-01 11:28:25 - INFO - ✓ Generated HTML report: docs/index.html
```

**Log Levels:**
- **DEBUG**: Detailed information for diagnosing problems (URL fetches, parsing details)
- **INFO**: Confirmation that things are working as expected
- **WARNING**: Something unexpected happened, but still working (malformed listings skipped)
- **ERROR**: A serious problem occurred (connection failures, parsing errors)

Change log level in `config/config.py`:
```python
LOG_LEVEL = "DEBUG"  # For verbose logging
LOG_LEVEL = "INFO"   # Default (recommended)
LOG_LEVEL = "ERROR"  # Only show errors
```

## Adding New Websites

Want to track more sites? Here's how:

1. Create a new scraper in `trackers/` folder
2. Follow the pattern from existing scrapers
3. Extract: title, price, kilometers, location, URL
4. Add to `SCRAPERS` list in `main.py`

**Example:**
```python
# trackers/newSiteTracker.py
from trackers.baseTracker import fetch_page, create_listing
from logger.logger import logger
from config.config import NEW_SITE_BASE_URL

SOURCE = "NewSite"

def scrape_newsite(search_term):
    """Scrape NewSite for a specific search term"""
    if not search_term or not search_term.strip():
        logger.warning(f"[{SOURCE}] Skipping empty search term")
        return {}
    
    url = f"{NEW_SITE_BASE_URL}/search?q={search_term}"
    logger.info(f"[{SOURCE}] Searching: {search_term}")
    
    soup = fetch_page(url)
    if not soup:
        return {}
    
    listings = {}
    # ... extract listings ...
    
    # Add extra fields
    listings[listing_id]['kilometers'] = kilometers
    listings[listing_id]['location'] = location
    
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

## Troubleshooting

### "No listings found" for existing bikes

- Check the bike name format matches the website exactly
- Try different variations (e.g., "CB500X" vs "CB 500 X")
- Check if the bike exists on that website
- Look in `tracker.log` for detailed error messages
- Enable DEBUG logging to see actual URLs being scraped

### 404 Errors

- Verify the bike model name is correct
- Some bikes may not be available on all sites
- Check the website URL structure hasn't changed
- View the actual URL in `tracker.log` (set `LOG_LEVEL = "DEBUG"`)

### Empty Lines in bikes.txt

- Remove trailing spaces and empty lines
- Each bike should be on its own line
- Lines starting with `#` are comments (ignored)

### Kilometers Showing "N/A"

- Some listings don't include mileage information
- AutoTrader usually shows "New" for brand new bikes
- Gumtree listings may not always include kilometers
- This is normal - the data just isn't available on the website

### Rate Limiting / Getting Blocked

If you're getting blocked:
- Increase sleep intervals in `config/config.py`:
  ```python
  SLEEP_MIN = 4
  SLEEP_MAX = 7
  ```
- Run less frequently
- Check website's `robots.txt`
- Review logs for HTTP 429 (Too Many Requests) errors

### Script Crashes

- Check `tracker.log` for detailed error messages
- Enable DEBUG logging in `config/config.py`:
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
- Clear your browser cache to see the latest version

### Toggle Buttons Not Working

- Make sure JavaScript is enabled in your browser
- Check browser console for errors (F12 → Console tab)
- Verify `docs/index.html` includes the JavaScript code
- Try a different browser

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

**View specific bike searches:**
```bash
grep "Triumph Speed 400" tracker.log
```

## Roadmap

### ✅ Phase 1: Foundation (Complete)
- [x] Multi-site scraping (AutoTrader, Gumtree)
- [x] Duplicate detection
- [x] Professional logging system
- [x] Robust error handling
- [x] Centralized configuration

### ✅ Phase 2: Enhanced Data & UI (Complete)
- [x] Kilometers/mileage tracking
- [x] Location data capture
- [x] Condition tracking (New/Used/Demo)
- [x] Interactive GitHub Pages dashboard
- [x] Dual-view tables (by bike / by source)
- [x] Mobile-responsive design
- [x] Table format with comprehensive data

### ✅ Phase 3: Price Tracking (Complete)
- [x] Price history tracking
- [x] Price drop alerts
- [x] Visual price drop indicators (strikethrough + green highlighting)
- [x] Dedicated "Price Drops" view

### 📋 Phase 4: Automation & Features
- [ ] Email/SMS notifications
- [ ] Command-line arguments (--quiet, --verbose, --bike "Honda Rebel")
- [ ] More scrapers (OLX, Cars.co.za, dealerships)
- [ ] Sortable table columns
- [ ] Filter by price range, kilometers, location

### 🚀 Future: Full-Stack Upgrade
- [ ] FastAPI backend
- [ ] PostgreSQL database
- [ ] React frontend
- [ ] User accounts (multi-user support)
- [ ] Real-time updates
- [ ] Mobile app

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
- Update `config/config.py` for new settings
- Add extra fields like `kilometers` and `location` after `create_listing()`

## Changelog

### Version 2.3 (Current)
- **Price Tracking System**: Full price history and drop detection
- **Price Drop Alerts**: Visual indicators with strikethrough old prices
- **Price Drops View**: Dedicated tab showing only discounted listings
- **Compact Stats Header**: Cleaner, inline statistics display
- **Enhanced Price Display**: ~~R 95,000~~ R 85,000 format for drops
- **Green Row Highlighting**: Easy visual identification of deals
- **Improved Data Persistence**: Price history carried across runs

### Version 2.2
- Added kilometers/mileage tracking for all listings
- Added location data (suburb/city) for all listings
- Added condition tracking (New/Used/Demo) for AutoTrader
- Redesigned dashboard with interactive table format
- Dual-view toggle: switch between bike-grouped and source-grouped tables
- Improved data extraction for Gumtree listings
- Enhanced error handling for malformed listings
- South African date format (DD/MM/YYYY) in dashboard

### Version 2.1
- Added GitHub Pages HTML dashboard
- Beautiful dark theme with red accents
- Mobile-responsive design
- Auto-generates static HTML report
- Statistics and organized listing cards

### Version 2.0
- Added centralized configuration (`config/config.py`)
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