import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
AERIAL_IMAGES_DIR = DATA_DIR / "aerial_images"
EXPORTS_DIR = DATA_DIR / "exports"
CACHE_DIR = DATA_DIR / "cache"

# Ensure directories exist
for directory in [DATA_DIR, AERIAL_IMAGES_DIR, EXPORTS_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()

# User-Agent for ethical web requests
DEFAULT_USER_AGENT = os.getenv(
    "USER_AGENT",
    "DiscoveryWebMiningBot/2.0 (CommercialPropertyResearch; contact: research@trustgridworks.internal)"
)

# Request configurations
REQUEST_TIMEOUT = 12
MAX_CONCURRENT_REQUESTS = 10
RATE_LIMIT_DELAY = 0.25

# Satellite Imagery Settings
AERIAL_ZOOM_LEVEL = 19
AERIAL_IMAGE_SIZE = (600, 600)
ESRI_SATELLITE_EXPORT_URL = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/export"
)

# Computer Vision Thresholds
SOLAR_PV_CONFIDENCE_THRESHOLD = 0.40
WIND_TURBINE_CONFIDENCE_THRESHOLD = 0.50

