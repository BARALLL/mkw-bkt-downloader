import pathlib
from rate_limiter import RateLimiter
import logging

SELF_PATH = pathlib.Path(__file__).parent
CACHE_PATH = SELF_PATH / "cache"
TRACK_PATH_IN_CACHE = CACHE_PATH / "tracks"

logging.basicConfig(
    filename=SELF_PATH / "downloader.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# example of proxy used every 10s
proxy_list = [
    # {"proxy": "http://IPv4:PORT", "rate_limiter": RateLimiter(10)},
]

chadsoft_subdomain = "https://tt.chadsoft.co.uk"
leaderboard_name = "ctgp-tracks"

max_workers = 2
cache_expiration = 1 # in days

# soft filters, try to match the majority of them (best match) but always pick a track from all the possibilities
track_filters = {
    "inCtgp": True,
    # 'categoryId': 0, #? meaning?
    "200cc": False,
}

# TODO check track hash + re