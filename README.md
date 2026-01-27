# Motorcycle Listing Tracker

A Python-based web scraper that automatically tracks motorcycle listings across multiple South African websites. View your findings on a beautiful, interactive GitHub Pages dashboard!

## Features

- **Multi-Site Scraping**: Gumtree & WeBuyCars with GitHub Actions automation
- **Smart Deduplication**: Fuzzy matching with search variations
- **Price Tracking**: Complete history with drop detection and alerts
- **Interactive Dashboard**: Toggle between bike-grouped, source-grouped, and price-drop views
- **Concurrent Processing**: ThreadPoolExecutor-based scraping for speed
- **Persistent Storage**: Auto-detects stale listings, remembers previous runs
- **WeBuyCars Cache**: Daily API refresh with server-respectful searching
- **Professional Logging**: Detailed logs for debugging and monitoring
- **Rotating User Agents**: Avoids detection with varied request headers
- **GitHub Actions Automation**: Runs every Sunday at 5:00 AM SAST automatically

## System Architecture

### Current Design (Phase 2.5)

**Why this approach:**
- **JSON file storage** for simplicity during MVP, but identifies scaling bottlenecks:
  - File-level locking during concurrent scraper writes
  - No query API (must parse JSON to analyze data)
  - Price history as arrays = O(n) search complexity
  - Static HTML rebuilds on every run

This is intentional—proving the concept before infrastructure investment.

### Design Decisions & Trade-offs

**Fuzzy Matching over Exact Search**
- Problem: "Honda CB 500X" vs "CB500X" vs "CB 500 X" across sites
- Solution: Levenshtein distance-based matching (fuzzywuzzy)
- Trade-off: Slightly slower, but catches all variations without manual rules

**Playwright Cache vs Live Scraping**
- WeBuyCars has no public search API
- Solution: Playwright intercepts API responses, caches locally, searches in-memory
- Trade-off: 1-day stale data, but respects server load + eliminates rate-limiting

**Concurrent ThreadPoolExecutor vs Sequential**
- Old: 13 bikes × 2 sites = 30+ seconds
- New: All parallel = 3-5 minutes with full dedup
- Trade-off: More CPU/memory, acceptable for weekly runs

---

## Phase 6: Production-Ready Upgrade (Planned)

### Backend: FastAPI

**Why FastAPI (not Flask/Django):**
- Async-first design handles concurrent scraper requests without threading issues
- Pydantic models force schema consistency across scrapers
- Built-in OpenAPI/Swagger documentation (industry standard)
- 10x faster than Flask on async I/O operations

**Current pain point:** Flask + ThreadPoolExecutor = RequestContext complexity and race conditions

### Database: PostgreSQL

**Why PostgreSQL (not SQLite):**
- SQLite file-level locks block concurrent scraper writes
- PostgreSQL row-level locking prevents duplicate listings during concurrent inserts
- ACID transactions ensure data integrity during crashes
- Native JSON support for price_history tracking
- Window functions for analytics queries
- Full-text search on listing titles (faster than fuzzy match on 10k+ rows)

**Proposed schema:**
```sql
CREATE TABLE motorcycles (
    id SERIAL PRIMARY KEY,
    make VARCHAR(50), model VARCHAR(100),
    UNIQUE(make, model)  -- Prevents "Honda" vs "honda" inconsistency
);

CREATE TABLE listings (
    id SERIAL PRIMARY KEY,
    motorcycle_id INT REFERENCES motorcycles,
    source ENUM('gumtree', 'webuycars'),
    price_current INT, price_previous INT,
    kilometers INT, location VARCHAR(100),
    url TEXT UNIQUE,  -- Prevents duplicates at DB level
    created_at TIMESTAMP, updated_at TIMESTAMP,
    INDEX idx_motorcycle_source (motorcycle_id, source),
    INDEX idx_updated_at (updated_at)
);

CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    listing_id INT REFERENCES listings ON DELETE CASCADE,
    price INT, recorded_at TIMESTAMP,
    INDEX idx_listing_recorded (listing_id, recorded_at)  -- Fast time-series queries
);
```

**Why this schema:**
- Normalization prevents data anomalies
- Foreign keys enforce referential integrity
- Composite indexes handle "show all Hondas on Gumtree" in milliseconds
- Separate price_history table = fast analytics (impossible with JSON arrays)

### API Design: REST with Future GraphQL

**Initial endpoints:**
```
GET    /api/listings                     # Filterable listings
GET    /api/listings/{id}                # Single listing + full history
GET    /api/listings/search?q=Honda      # Search by title
GET    /api/motorcycles                  # All tracked bikes
GET    /api/analytics/price-drops        # Price drop analytics
```

**Why REST initially:** Standard HTTP semantics, works perfectly for CRUD + analytics

**Future GraphQL (Phase 7):** Once query complexity grows (nested filters, multiple joins)

### Deployment Strategy

**Development:** Docker Compose (FastAPI + PostgreSQL locally)

**Production:**
- **FastAPI**: Railway.app ($10-20/month) with auto-deploy on GitHub push
- **Static dashboard**: GitHub Pages (free)
- **Scraper automation**: GitHub Actions (free)

### Why This Upgrade Matters

| Current Bottleneck | Impact | Solution |
|------------------|--------|----------|
| No query API | Must clone repo to analyze listings | `/api/listings?filters=...` |
| JSON file locks | Concurrent writes = corruption risk | PostgreSQL ACID transactions |
| Static HTML rebuilds | 10k-row table regenerates every run | React SPA fetches incremental data |
| No authentication | Can't safely share dashboard | JWT tokens + user accounts (Phase 6.3) |
| O(n) price history search | "Show price trend" = slow JSON parsing | Indexed SQL queries return in <50ms |

---

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
playwright install 
```

3. **Configure your bikes**

Create a `bikes.txt` file with the motorcycles you want to track (one per line):
```
Suzuki DS 250 SX V-STROM
Triumph Scrambler 400 x
Honda CB 500 X
BMW G 310
```

4. **Run locally (optional)**
```bash
# Cache refresh (run once, then daily)
python cache_webuycars.py

# Run tracker
python main.py
```

This will:
- Concurrently scrape all configured websites (faster!)
- Save results to `data/listings.json`
- Generate an interactive HTML dashboard in `docs/index.html`
- Create detailed logs in `tracker.log`
- Remove stale listings (sold/removed items)
- Track complete price history for all listings

**OR** - Let GitHub Actions do it automatically! Once set up, your tracker runs every Sunday at 5:00 AM SAST without any manual intervention.

## Project Structure
```
motorcycle-tracker/
├── main.py                     # Main entry point
├── cache_webuycars.py          # WeBuyCars cache refresh script
├── bikes.txt                   # List of bikes to track
├── data/
│   ├── .gitkeep                # Ensures folder is tracked
│   ├── listings.json           # Stored listings (auto-generated)
│   └── webuycars_cache.json   # WeBuyCars cache (auto-generated)
├── config/
│   └── config.py               # Configuration settings
├── docs/
│   ├── index.html              # GitHub Pages dashboard (auto-generated)
│   └── styles.css              # Dashboard stylesheet
├── logger/
│   └── logger.py               # Logging utility
├── trackers/
│   ├── __init__.py
│   ├── autotraderTracker.py    # Autotrader scraper
│   ├── baseTracker.py          # Shared functionality
│   ├── gumtreeTracker.py       # Gumtree scraper
│   └── webuycarsTracker.py     # WeBuyCars cache searcher
├── template_generator/
│   └── html_generator.py       # GitHub Pages HTML generator
├── utils/
│   ├── relevant_match.py       # Fuzzy matching engine
│   ├── search_variation_generator.py # Search variation logic
│   ├── validate_search_term.py # Input validation
│   └── listing_builder.py      # Unified listing creator
├── .github/workflows/
│   └── sunday-tracker.yml      # GitHub Actions automation
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## GitHub Pages Dashboard

The tracker automatically generates a beautiful, interactive web dashboard that you can host on GitHub Pages!

### Dashboard Features

**Compact Statistics Header**
- Total listings found
- Number of bikes tracked
- Number of sources
- **Price drops detected** (live counter)

**Triple-View Toggle**
- **By Bike Model** (default): Groups all listings by motorcycle
- **By Source**: Groups all listings by website (Gumtree, WeBuyCars)
- **Price Drops**: Dedicated view showing only listings with price reductions
- Instant switching with toggle buttons

**Price Drop Indicators**
- Visual strikethrough on old prices: ~~R 95,000~~ R 85,000
- Green row highlighting for discounted listings
- Automatic price history tracking
- Drop amount calculated and logged

**Comprehensive Data Tables**

Each listing shows:
- **Source**: Which website (Gumtree, WeBuyCars)
- **Title**: Full listing title
- **Price**: Listed price
- **Kilometers**: Mileage/odometer reading
- **Location**: Geographic location (suburb/city)
- **Link**: Direct link to view the listing

**Modern Design**
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

### Automatic Updates

The GitHub Actions workflow runs every Sunday at 5:00 AM SAST:
1. Refreshes WeBuyCars cache (Playwright API interception)
2. Runs the full tracker (Gumtree + WeBuyCars)
3. Generates updated dashboard
4. Commits changes automatically
5. GitHub Pages auto-updates within minutes

No manual intervention needed after initial setup!

## Configuration

### Global Settings

Edit `config/config.py` to customize:
- **File paths**: Change where data/logs are stored
- **Request settings**: Adjust timeouts and user agent rotation
- **Rate limiting**: Modify sleep intervals between requests
- **Logging**: Change log levels and formats
- **Match thresholds**: Adjust fuzzy matching sensitivity

Example:
```python
# File paths
DATA_FILE = "data/listings.json"
WEBUYCARS_CACHE_FILE = "data/webuycars_cache.json"
BIKE_FILE = "bikes.txt"
LOG_FILE = "tracker.log"

# Rate limiting (seconds)
SLEEP_MIN = 3
SLEEP_MAX = 5

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Fuzzy matching thresholds
MATCH_THRESHOLDS = {
    "gumtree": 0.40,       # Lower = more lenient matching
    "webuycars": 0.4575,   # Adjust based on your results
}
```

### Adding Bikes

Edit `bikes.txt` and add bikes (one per line):
```
# Adventure bikes
Suzuki DS 250 SX V-STROM
BMW G 310

# Cruisers
Honda Rebel 500
Triumph Bonneville

# Comments start with #
```

**Important:** Remove any trailing spaces or empty lines.

### Match Ratio Tuning

If you're getting too many false positives or false negatives:

```bash
python tune_match_ratio.py
```

This tests different thresholds and recommends optimal values. Update `MATCH_THRESHOLDS` in `config.py` based on results.

### Supported Websites

Currently supports:

- **Gumtree** (gumtree.co.za) 
  - Flexible search format
  - Captures: price, kilometers, location, title
  - Uses fuzzy matching with search variations
  - Live scraping with rotating user agents
  
- **WeBuyCars** (webuycars.co.za)
  - Uses Playwright API interception for daily cache refresh
  - Captures: price, kilometers, location, make, model, title
  - Fast local searching with fuzzy matching
  - **No live API calls** (uses cached data)
  - Run `python cache_webuycars.py` daily to refresh cache

### WeBuyCars Cache System

WeBuyCars uses an efficient **caching approach**:

**How it works:**
1. `cache_webuycars.py` fetches ALL motorcycle listings daily via Playwright API interception
2. Stores ~445 listings in `data/webuycars_cache.json`
3. `webuycarsTracker.py` searches the local cache using fuzzy matching
4. No repeated API calls = fast & reliable searches

**Setup:**
```bash
# One-time setup (or run before tracker)
python cache_webuycars.py

# Then run tracker normally
python main.py
```

**Benefits:**
-  Fast searches (<100ms)
-  Respectful to WeBuyCars servers (1 request/day vs dozens)
-  No search API failures or rate limiting
-  Price tracking works across cache refreshes

**Schedule daily refresh (Linux/Mac cron):**
```bash
crontab -e
# Add: 0 2 * * * cd /path/to/motorcycle-tracker && python cache_webuycars.py
```

### Unified Listing Builder

All scrapers use a centralized `utils/listing_builder.py`:

**Benefits:**
- **Consistency**: All listings have identical structure
- **Price History**: Automatic tracking across all sources
- **Maintainability**: Single source of truth for listing format
- **Easy Expansion**: Add new fields without modifying each scraper

**Example:**
```python
from utils.listing_builder import build_listing

listing = build_listing(
    listing_id="gt_12345",
    title="2025 Honda CB500X",
    price="R 89,900",
    url="https://www.gumtree.co.za/...",
    search_term="Honda CB 500 X",
    source="Gumtree",
    kilometers="5,000 km",
    location="Cape Town"
)
```

All listings automatically include `price_history` tracking.

### Rotating User Agents

The scraper uses multiple user agents to avoid detection:

```python
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)...",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)...",
]
```

Each request uses a random user agent from this list, making requests appear more human-like.

### Async & Concurrent Scraping

**How it works:**
- Scraper tasks run in parallel (not sequential)
- ThreadPoolExecutor with configurable max workers
- All bikes scraped concurrently across all sites
- One sleep per bike (not per scraper)

**Performance:**
- Sequential (old): 13 bikes × 2 sites = 30+ seconds
- Concurrent (new): 13 bikes × 2 sites = ~3-5 minutes with full data
- Result: **Efficient resource usage**

### Stale Listing Detection

**What it does:**
- Tracks which listings appeared in current run
- Compares against previous run
- Removes listings that disappeared (likely sold/removed)
- Only applies to live scrapers (Gumtree)
- WeBuyCars cache listings preserved

**Example:**
```
Run 1: Found 50 listings
Run 2: Only 45 still exist
Action: Remove 5 stale listings automatically
Result: Clean, current-only data
```

## Data Captured

### Gumtree Listings
- Title (bike make/model/year/description)
- Price
- Kilometers (when available)
- Location (suburb/city)
- Direct URL

### WeBuyCars Listings
- Title (vehicle description)
- Price
- Make and Model (stored separately)
- Kilometers (mileage)
- Location (dealer location)
- Direct URL
- **Note**: Uses cached API data (not live search)

## Output Example

### Console Output
```
============================================================
  MOTORCYCLE LISTING TRACKER
============================================================

 Running on GitHub Actions
ℹ  AutoTrader disabled (IP blocked on GitHub Actions)
✓ Using: Gumtree + WeBuyCars

Loaded 13 unique bike model(s) from bikes.txt
Tracking 13 bike model(s)...
     • Suzuki DS 250 SX V-STROM
     • Honda CB 500 X
     • BMW G 310

────────────────────────────────────────────────────────────
Searching for: Suzuki DS 250 SX V-STROM
────────────────────────────────────────────────────────────
[Gumtree] Trying 6 variation(s) for Suzuki DS 250 SX V-STROM
[Gumtree] Variation 'Suzuki 250': 8 found, 6 added, 2 skipped
[WeBuyCars] Loaded cache (445 listings, last updated: 01/12/2025 09:26:35)
[WeBuyCars] Found 6 listing(s) matching 'Suzuki DS 250 SX V-STROM'

6 NEW listing(s) for Suzuki DS 250 SX V-STROM
    --[Gumtree] 2023 Suzuki Vstrom 250 SX - R 50,000
    --[WeBuyCars] 2025 Suzuki 250 DS 250 - R 49,900
    ...

============================================================
SUMMARY
============================================================

 TOTAL: 46 NEW LISTING(S) FOUND

    Gumtree: 25 new listing(s)
    WeBuyCars: 21 new listing(s)
============================================================
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

**Console Output:**
```
Price drop detected for 2024 Honda Rebel 500: R95,000 → R85,000 (R10,000 drop) [Gumtree]
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

Track price trends over time and identify the best deals!

## Logging

The tracker creates detailed logs in `tracker.log`:

```
2025-12-01 09:26:35 - INFO - Loaded 13 unique bike model(s) from bikes.txt
2025-12-01 09:26:36 - INFO - [Gumtree] Trying 6 variation(s) for Suzuki DS 250 SX V-STROM
2025-12-01 09:26:37 - INFO - [Gumtree] Found 6 listing(s) for Suzuki DS 250 SX V-STROM
2025-12-01 09:27:45 - INFO - Saved 46 total listing(s) for 13 bike model(s)
2025-12-01 09:27:46 - INFO - ✓ Generated HTML report: docs/index.html
```

**Log Levels:**
- **DEBUG**: Detailed information (URL fetches, parsing details)
- **INFO**: Confirmation that things are working
- **WARNING**: Unexpected but working (malformed listings skipped)
- **ERROR**: Serious problems (connection failures, parsing errors)

Change log level in `config/config.py`:
```python
LOG_LEVEL = "DEBUG"   # Verbose logging
LOG_LEVEL = "INFO"    # Default (recommended)
LOG_LEVEL = "ERROR"   # Only errors
```

## Troubleshooting

### No listings found for existing bikes

- Check bike name format (exact match on websites)
- Try different variations (e.g., "CB500X" vs "CB 500 X")
- Look in `tracker.log` for detailed error messages
- Enable DEBUG logging: `LOG_LEVEL = "DEBUG"`
- Verify bike exists on website manually

### Fuzzy Matching Issues

Getting too many false positives or false negatives?
- Run `python tune_match_ratio.py` to find optimal threshold
- Check match scores in `tracker.log` (DEBUG level)
- Adjust `MATCH_THRESHOLDS` in `config/config.py`
- Lower threshold = catch more variations
- Higher threshold = filter more strictly

### Kilometers Showing "N/A"

- Some listings don't include mileage information
- Gumtree listings may not always have kilometers
- This is normal - data just isn't available on website

### Rate Limiting / Getting Blocked

If getting blocked on Gumtree:
- Increase sleep intervals in `config/config.py`:
  ```python
  SLEEP_MIN = 5
  SLEEP_MAX = 8
  ```
- Run less frequently
- Check website's `robots.txt`

### WeBuyCars Cache Issues

**"Cache file not found" error:**
- Run: `python cache_webuycars.py`
- Check that `data/` folder exists
- Verify `WEBUYCARS_CACHE_FILE` path in config.py

**"Cache is empty or unavailable":**
- Cache refresh failed - check `tracker.log` for Playwright errors
- Ensure Playwright installed: `playwright install`
- Try running cache refresh manually

**WeBuyCars listings not showing up:**
- Run cache refresh first: `python cache_webuycars.py`
- Check `tracker.log` for fuzzy matching scores
- Run `python tune_match_ratio.py` to optimize thresholds

### GitHub Actions Not Running

- Check Actions tab for workflow status
- Verify `.github/workflows/sunday-tracker.yml` exists
- Check that GitHub Actions is enabled in Settings
- Verify cron syntax is correct (runs Sunday 03:00 UTC = 05:00 SAST)

### GitHub Pages Not Updating

- Wait a few minutes after push (GitHub takes time)
- Check Actions tab for build errors
- Verify `docs/index.html` is committed
- Clear browser cache (Ctrl+Shift+R)

### Toggle Buttons Not Working

- Enable JavaScript in your browser
- Check browser console (F12 → Console tab)
- Verify `docs/index.html` includes JavaScript
- Try a different browser

## Adding New Websites

Want to track more sites? Here's how:

1. Create a new scraper in `trackers/` folder
2. Follow the pattern from `gumtreeTracker.py`
3. Extract: title, price, kilometers, location, URL
4. Use `build_listing()` from `utils/listing_builder.py`
5. Add to `SCRAPERS` list in `main.py`

**Code Standards:**
- Use logging instead of print statements
- Handle errors gracefully (try-except)
- Add docstrings to functions
- Follow existing naming conventions
- Use `build_listing()` for all listing creation
- Create utility functions in `utils/` for reusable logic
- Update `MATCH_THRESHOLDS` in `config.py` if adding new scrapers
- Use fuzzy matching for flexible search term matching

## Advanced Usage

### Performance Tuning

**Adjust max concurrent workers:**

Edit `main.py`:
```python
executor = concurrent.futures.ThreadPoolExecutor(max_workers=6)
```

Values:
- `3-5`: Conservative (less CPU/memory)
- `6-10`: Default (balanced)
- `15+`: Aggressive (faster, uses more resources)

**Reduce between-request sleep:**

Edit `config/config.py`:
```python
SLEEP_MIN = 2  # Lower = less delay
SLEEP_MAX = 4
```

**Monitor execution time:**
- Check timestamps in `tracker.log`
- Compare run times week-to-week

### Automated Git Push (Optional)

Create `update_and_push.sh`:
```bash
#!/bin/bash
cd /path/to/motorcycle-tracker
python cache_webuycars.py
python main.py

git add -f docs/index.html data/listings.json
git commit -m "Auto-update listings $(date '+%Y-%m-%d %H:%M')" || true
git push
```

Make executable:
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

**View specific bike searches:**
```bash
grep "Honda CB 500" tracker.log
```

## Roadmap

### Phase 1: Foundation (Complete)
- [x] Multi-site scraping (Gumtree, WeBuyCars)
- [x] Duplicate detection
- [x] Professional logging system
- [x] Robust error handling
- [x] Centralized configuration

### Phase 2: Enhanced Data & UI (Complete)
- [x] Kilometers/mileage tracking
- [x] Location data capture
- [x] Interactive GitHub Pages dashboard
- [x] Multiple view options (by bike / by source)
- [x] Mobile-responsive design
- [x] Table format with comprehensive data

### Phase 3: Price Tracking (Complete)
- [x] Price history tracking
- [x] Price drop alerts
- [x] Visual price drop indicators
- [x] Dedicated "Price Drops" view

### Phase 3.5: WeBuyCars Enhancement (Complete)
- [x] Playwright API interception for cache refresh
- [x] Daily cache system (~445 listings)
- [x] Local fuzzy matching
- [x] Price history tracking for WeBuyCars
- **Result:** Fast, reliable, respectful to servers

### Phase 4: Automation & GitHub Actions (Complete)
- [x] GitHub Actions workflow
- [x] Automatic Sunday runs at 5:00 AM SAST
- [x] Auto-commit cache and dashboard updates
- [x] Rotating user agents to avoid detection
- [x] Async/concurrent scraping

### Phase 5: Future Enhancements
- [ ] Email/SMS notifications
- [ ] Command-line arguments (--quiet, --verbose, --bike "Honda Rebel")
- [ ] More scrapers (OLX, Cars.co.za, dealerships)
- [ ] Sortable/filterable table columns
- [ ] Filter by price range, kilometers, location

### Future: Full-Stack Upgrade
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
- Reasonable request intervals (2+ seconds minimum)
- Proper User-Agent identification
- Respect rate limits and 429 responses
- Don't scrape personal/private information
- Use scraped data responsibly

## Contributing

Contributions are welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/new-scraper`)
3. Follow existing code patterns
4. Update documentation if adding features
5. Test thoroughly with various bikes
6. Commit changes (`git commit -am 'Add feature'`)
7. Push to branch (`git push origin feature/new-scraper`)
8. Open a Pull Request

## Changelog

### Version 2.5 (Current)
- **GitHub Actions Automation**: Runs every Sunday 5:00 AM SAST automatically
- **Fixed Fuzzy Matching**: Improved matching for Gumtree (threshold 0.40)
- **Rotating User Agents**: Multiple user agents to avoid detection
- **Cache Commit Support**: WeBuyCars cache now tracked in Git
- **HTML Auto-Commit**: Dashboard updates committed to GitHub
- **Removed AutoTrader**: Disabled on GitHub Actions (503 blocking), works locally
- **Better Logging**: Cleaner environment detection and reporting

### Version 2.4
- Async Concurrent Scraping (50-66% faster)
- Stale Listing Detection
- Unified Listing Builder
- WeBuyCars Cache System (Playwright API interception)
- Price History for All Sources
- Fuzzy Matching System
- Search Variations Generator

### Version 2.3
- Price Tracking System with history
- Price Drop Alerts with visual indicators
- Price Drops dedicated view
- Enhanced price display

### Version 2.2
- Kilometers/mileage tracking
- Location data capture
- Interactive dashboard with table format
- Dual-view toggle (by bike / by source)

### Version 2.1
- GitHub Pages HTML dashboard
- Dark theme with red accents
- Mobile-responsive design

### Version 2.0
- Centralized configuration
- Professional logging system
- Enhanced error handling

### Version 1.0
- Initial release (AutoTrader + Gumtree scrapers)

## Acknowledgments

- Built as a learning project to understand web scraping and automation
- Inspired by the need to find good motorcycle deals in South Africa
- Created with the assistance of AI (Claude)
- HTML dashboard design inspired by [HTML5 UP](https://html5up.net/)
- Thanks to the Python community for excellent libraries

---

**Questions or Issues?** Check `tracker.log` first, then open an issue on GitHub!

**Live Demo:** Check out your GitHub Pages dashboard at `[https://barnardf.github.io/Motorcycle-listing-web-scraper/]`
