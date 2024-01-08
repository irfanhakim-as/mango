from base.settings import *


##################################################################
# CONFIGURATIONS
##################################################################

COMPULSORY_SETTINGS.extend([
    "ORGANIC_POSTS",
    "ACCOUNT_MODEL",
    "FEED_MODEL",
    "POST_MODEL",
    "SCHEDULE_MODEL",
    "SCHEDULER_TIMEZONE",
    # "ACCESS_TOKEN",
    # "API_BASE_URL",
    # "BOT_ID",
    "DEFAULT_VISIBILITY",
    "POST_LIMIT",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
    "CELERY_TIMEZONE",
    "DATA_DIR",
    "ACCOUNTS_DATA_FILE",
    "FEEDS_DATA_FILE",
    "SYNC_CONFIG",
])
ORGANIC_POSTS = os.getenv("ORGANIC_POSTS", False) == "true"
ACCOUNT_MODEL = os.getenv("ACCOUNT_MODEL", "base.MastodonAccount")
FEED_MODEL = os.getenv("FEED_MODEL", "base.FeedObject")
POST_MODEL = os.getenv("POST_MODEL", "base.PostItem")
SCHEDULE_MODEL = os.getenv("SCHEDULE_MODEL", "base.PostSchedule")
SCHEDULER_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "Asia/Kuala_Lumpur")


##################################################################
# Mastodon Settings
##################################################################

# ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "/base/base/mastodon.secret")
# API_BASE_URL = os.getenv("API_BASE_URL")
# BOT_ID = os.getenv("BOT_ID")
DEFAULT_VISIBILITY = os.getenv("DEFAULT_VISIBILITY", "public")
POST_LIMIT = int(os.getenv("POST_LIMIT", "0"))


##################################################################
# Celery Settings
##################################################################

CELERY_BROKER_URL = os.getenv("CELERY_BROKER", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_BACKEND", "redis://localhost:6379/0")
CELERY_TIMEZONE = SCHEDULER_TIMEZONE


##################################################################
# Data Settings
##################################################################

DATA_DIR = os.getenv("DATA_DIR", os.path.join(BASE_DIR, "data"))
ACCOUNTS_DATA_FILE = os.getenv("ACCOUNTS_DATA_FILE", os.path.join(DATA_DIR, "accounts.json"))
FEEDS_DATA_FILE = os.getenv("FEEDS_DATA_FILE", os.path.join(DATA_DIR, "feeds.json"))
SYNC_CONFIG = {
    "accounts" : {
        "model" : ACCOUNT_MODEL,
        "data" : ACCOUNTS_DATA_FILE,
        "object_id" : ("api_base_url", "uid"),
    },
    "feeds" : {
        "model" : FEED_MODEL,
        "data" : FEEDS_DATA_FILE,
        "object_id" : ("uid",),
    },
}
