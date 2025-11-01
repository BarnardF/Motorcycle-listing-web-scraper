import os

# File paths
DATA_FILE = "listings.json"
BIKE_FILE = "bikes.txt"
LOG_FILE = "tracker.log"

# Request settings
REQUEST_TIMEOUT = 10
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)

# Rate limiting (seconds)
SLEEP_MIN = 2
SLEEP_MAX = 4

# Scraper URLs
AUTOTRADER_BASE_URL = "https://www.autotrader.co.za/bikes-for-sale"
GUMTREE_BASE_URL = "https://www.gumtree.co.za/s-motorcycles-scooters/v1c9027p1"

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Console output
ENABLE_COLORS = False  # Set to True to enable colored console output