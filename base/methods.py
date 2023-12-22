import emoji
import logging
import re
import urllib.request
from datetime import datetime
from dateutil import tz
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from lib.messages import (
    ICONS,
    MESSAGES,
)
logger = logging.getLogger("base")


#====================SETTINGS: GETATTR====================#
DEBUG = getattr(settings, "DEBUG")
POST_MODEL = getattr(settings, "POST_MODEL")
TIME_ZONE = getattr(settings, "TIME_ZONE")


#====================BASE: IS DEBUG====================#
def is_debug():
    return DEBUG is True


#====================MODELS: GET POST MODEL====================#
def get_post_model():
    # return the Post model that is active in this project
    try:
        return django_apps.get_model(POST_MODEL, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("POST_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "POST_MODEL refers to model '%s' that has not been installed" % POST_MODEL
        )


#====================MODELS: GET VALUES LIST====================#
def get_values_list(field, **kwargs):
    model = kwargs.get("model")
    queryset = kwargs.get("queryset")
    unique = kwargs.get("unique", True)
    if model and not queryset:
        queryset = model.objects.all()
    if not unique:
        return list(queryset.values_list(field, flat=True))
    else:
        return list(queryset.values_list(field, flat=True).distinct())


#====================UTILS: ESCAPE MARKDOWN====================#
def escape_md(text):
    try:
        text = str(text)
        escape_chars = r'_*['
        text = re.sub(f"([{re.escape(escape_chars)}])", r'\\\1', text)
    except Exception as e:
        verbose_warning = "Failed to escape markdown characters"
        log_message = message("LOG_EXCEPT", exception=e, verbose=verbose_warning, object=text)
        logger.warning(log_message)
    return text


#====================UTILS: MESSAGE====================#
def message(key, **kwargs):
    # if not key.startswith("LOG_"):
    #     kwargs = {k:escape_md(v) for k, v in kwargs.items()}
    return MESSAGES[key].format(**kwargs)


#====================UTILS: ICON====================#
def icon(**kwargs):
    key = kwargs.get("key")
    spacer = kwargs.get("spacer", False)
    alias = kwargs.get("alias", ICONS.get(key))
    icon = emoji.emojize(":%s:" % alias)
    if not emoji.is_emoji(icon):
        return ""
    else:
        if spacer:
            icon += " "
        return icon


#====================UTILS: READ URL====================#
def read_url(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent" : "Mozilla/5.0"})).read()


#====================UTILS: REMOVE DICTIONARY KEYS====================#
def remove_dict_keys(dictvar, keys):
    for k in keys:
        dictvar.pop(k, None)
    return dictvar


#====================UTILS: LIST AS STRING====================#
def string_list(l):
    return str(l)[1:-1]


#====================UTILS: UNIQUE LIST====================#
def unique_list(l):
    return list(set(l))


#====================DATETIME: CONVERT DATETIME TIMEZONE====================#
def convert_timezone(datevar, tzvar=TIME_ZONE):
    # convert timezone aware datetime to another timezone
    return datevar.astimezone(tz.gettz(tzvar))


#====================DATETIME: GET CURRENT DATETIME====================#
def get_datetime(timezone=TIME_ZONE):
    # now according to timezone
    now = datetime.now(tz=tz.gettz(timezone))
    # now in UTC
    utc_now = convert_timezone(now, "UTC")
    # now in system timezone
    sys_now = convert_timezone(now)
    # now as date string
    today = now.date()
    # now as gregorian date string
    gregorian = today.strftime("%-d %B %Y")

    date_dict = {
        "now" : now,
        "utc_now" : utc_now,
        "sys_now" : sys_now,
        "today" : today,
        "gregorian" : gregorian,
    }
    return date_dict


#====================DATETIME: MAKE TIMEZONE AWARE DATETIME====================#
def make_aware_datetime(tzvar, **kwargs):
    datestr = kwargs.get("datestr")
    datefmt = kwargs.get("datefmt", "%Y-%m-%d")
    datevar = kwargs.get("datevar")
    # make naive datetime out of string
    if datestr:
        datevar = datetime.strptime(datestr, datefmt)
    # make timezone aware datetime out of naive datetime
    return datevar.replace(tzinfo=tz.gettz(tzvar))


#====================DATETIME: GLOBALISE LOCAL DATETIME====================#
def globalise_local_datetime(tzvar=TIME_ZONE, **kwargs):
    datestr = kwargs.get("datestr")
    datefmt = kwargs.get("datefmt", "%Y-%m-%d")
    datevar = kwargs.get("datevar")
    # make timezone aware datetime out of string
    if datestr:
        datevar = make_aware_datetime(tzvar, datestr=datestr, datefmt=datefmt)
    # convert timezone aware datetime to UTC
    return convert_timezone(datevar, "UTC")


#====================DATETIME: MAKE TIME STRING====================#
def make_time_str(datevar):
    # make time string out of datetime
    return datevar.strftime("%H:%M")


#====================DATETIME: MAKE DATE STRING====================#
def make_date_str(datevar, datefmt="%d-%m-%Y"):
    # make date string out of datetime
    return datevar.strftime(datefmt)
