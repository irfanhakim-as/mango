from base.settings import *


##################################################################
# CONFIGURATIONS
##################################################################

COMPULSORY_SETTINGS.extend([
    "ORGANIC_POSTS",
    "FEED_MODEL",
    "POST_MODEL",
    "SCHEDULER_TIMEZONE",
    # "ACCESS_TOKEN",
    # "API_BASE_URL",
    # "BOT_ID",
    "DEFAULT_VISIBILITY",
    "POST_LIMIT",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
    "CELERY_TIMEZONE"
])
ORGANIC_POSTS = os.getenv("ORGANIC_POSTS", False) == "true"
FEED_MODEL = os.getenv("FEED_MODEL", "base.FeedObject")
POST_MODEL = os.getenv("POST_MODEL", "base.PostItem")
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
