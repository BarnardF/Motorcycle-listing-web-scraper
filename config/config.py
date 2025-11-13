from pathlib import Path

# ==================== DATA FOLDER ====================
# Ensure data folder exists
DATA_FOLDER = Path("data")
DATA_FOLDER.mkdir(exist_ok=True)


# ==================== FILE PATHS ====================
# Main data files (in data folder)
DATA_FILE = str(DATA_FOLDER / "listings.json")
WEBUYCARS_CACHE_FILE = str(DATA_FOLDER / "webuycars_cache.json")

# Other files (in root)
BIKE_FILE = "bikes.txt"
LOG_FILE = "tracker.log"


# ==================== REQUEST SETTINGS ====================
# User agent for web requests
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)

# Request timeout (seconds)
REQUEST_TIMEOUT = 10


# ==================== RATE LIMITING ====================
# Sleep interval between requests (in seconds)
SLEEP_MIN = 2
SLEEP_MAX = 4


# ==================== LOGGING ====================
# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ==================== SCRAPER URLs ====================
AUTOTRADER_BASE_URL = "https://www.autotrader.co.za/bikes-for-sale"
GUMTREE_BASE_URL = "https://www.gumtree.co.za/s-motorcycles-scooters/v1c9027p1"
WEBUYCARS_BASE_URL = 'https://www.webuycars.co.za/buy-a-car?activeTypeSearch=["Motorbike"]'

# API Keywords to identify relevant responses
API_KEYWORDS = "website-elastic-backend/api/search"


# ==================== FUZZY MATCHING ====================
# Match thresholds for fuzzy matching (0.0 to 1.0)
# Lower = more lenient, Higher = stricter
MATCH_THRESHOLDS = {
    "gumtree": 0.435,      # Threshold for Gumtree fuzzy matching
    "autotrader": 0.50,    # Threshold for AutoTrader relevance matching
    "webuycars": 0.4575,     # Threshold for WeBuyCars cache searching
}