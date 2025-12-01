from pathlib import Path
from random import random
import os

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

# ==================== ENVIRONMENT DETECTION ====================
IS_GITHUB_ACTIONS = os.getenv('GITHUB_ACTIONS') == 'true'
IS_LOCAL = not IS_GITHUB_ACTIONS


# ==================== REQUEST SETTINGS ====================
# User agents for web requests
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/131.0",
]

def get_random_user_agent():
    """Return a random user agent to avoid detection"""
    return random.choice(USER_AGENTS)

# Default user agent (fallback, not used if rotating)
USER_AGENT = USER_AGENTS[0]

# Request timeout (seconds)
REQUEST_TIMEOUT = 10


# ==================== RATE LIMITING ====================
# Sleep interval between requests (in seconds)
SLEEP_MIN = 3
SLEEP_MAX = 5


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
    "gumtree": 0.40,      # Threshold for Gumtree fuzzy matching
    "autotrader": 0.50,    # Threshold for AutoTrader relevance matching
    "webuycars": 0.4575,     # Threshold for WeBuyCars cache searching
}