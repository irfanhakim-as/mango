import emoji
import json
import logging
import os
import re
import urllib.request
from datetime import (
    datetime,
    timedelta,
)
from dateutil import (
    parser,
    tz,
)
from urllib.parse import urlparse
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import (
    ImproperlyConfigured,
    ValidationError,
)
from lib.messages import (
    ICONS,
    MESSAGES,
)
logger = logging.getLogger("base")


#====================SETTINGS: GETATTR====================#
DEBUG = getattr(settings, "DEBUG")
ACCOUNT_MODEL = getattr(settings, "ACCOUNT_MODEL")
FEED_MODEL = getattr(settings, "FEED_MODEL")
POST_MODEL = getattr(settings, "POST_MODEL")
SCHEDULE_MODEL = getattr(settings, "SCHEDULE_MODEL")
SYNC_CONFIG = getattr(settings, "SYNC_CONFIG", dict())
TIME_ZONE = getattr(settings, "TIME_ZONE")


#====================BASE: IS DEBUG====================#
def is_debug():
    return DEBUG is True


#====================BASE: GET ACTIVE ACCOUNTS====================#
def get_active_accounts(**kwargs):
    AccountModel = get_account_model()
    return AccountModel.objects.filter(is_enabled=True, **kwargs) if AccountModel else []


#====================BASE: GET ACTIVE FEEDS====================#
def get_active_feeds(**kwargs):
    FeedModel = get_feed_model()
    return FeedModel.objects.filter(is_enabled=True, **kwargs) if FeedModel else []


#====================BASE: SYNC DATA====================#
def sync_data(sync_dict=SYNC_CONFIG):
    for k, v in sync_dict.items():
        model = v.get("model")
        data = v.get("data")
        object_id = v.get("object_id")
        if not (model and data):
            verbose_warning = 'Sync dictionary was improperly configured. Each key must be a valid JSON dictionary key and its value must be a dictionary with "model" and "data" keys.'
            log_message = message("LOG_EXCEPT", exception=None, verbose=verbose_warning, object=k)
            logger.warning(log_message)
            continue
        model_object = get_model(model)
        if os.path.isfile(data):
            data_dicts = get_json_dicts(data, key=k)
            dicts_to_models(data_dicts, model_object, object_id=object_id)
        else:
            verbose_warning = 'Data file "%s" does not exist' % data
            log_message = message("LOG_EXCEPT", exception=None, verbose=verbose_warning, object=data)
            logger.warning(log_message)


#====================MODELS: GET MODEL====================#
def get_model(model_name, **kwargs):
    model_variable = kwargs.get("model_variable", "MODEL")
    # return the model object
    try:
        return django_apps.get_model(model_name, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("%s must be of the form 'app_label.model_name'" % model_variable)
    except LookupError:
        raise ImproperlyConfigured(
            "%s refers to model '%s' that has not been installed" % (model_variable, model_name)
        )


#====================MODELS: GET POST MODEL====================#
def get_post_model():
    # return the Post model that is active in this project
    return get_model(POST_MODEL, model_variable="POST_MODEL")


#====================MODELS: GET SCHEDULE MODEL====================#
def get_schedule_model():
    # return the Schedule model that is active in this project
    return get_model(SCHEDULE_MODEL, model_variable="SCHEDULE_MODEL")


#====================MODELS: GET FEED MODEL====================#
def get_feed_model():
    # return the Feed model that is active in this project
    return get_model(FEED_MODEL, model_variable="FEED_MODEL")


#====================MODELS: GET ACCOUNT MODEL====================#
def get_account_model():
    # return the Account model that is active in this project
    return get_model(ACCOUNT_MODEL, model_variable="ACCOUNT_MODEL")


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


#====================MODELS: GET VALUES====================#
def get_values(*fields, **kwargs) -> list:
    model = kwargs.get("model")
    query = kwargs.get("query")
    queryset = kwargs.get("queryset")
    if model and not queryset:
        queryset = model.objects.all()
    if query and queryset is not None:
        queryset = queryset.filter(**query)
    if queryset is None or not fields:
        return []
    return list(queryset.values(*fields))


#====================MODELS: DICTS TO MODELS====================#
def dicts_to_models(dicts, model_object, **kwargs):
    object_id = kwargs.get("object_id", ("uid",))
    # iterate through list of dicts to sync
    for d in dicts:
        identifier = dict()
        keys_exist = True
        update = False
        # ensure unique identifiers have values
        for i in object_id:
            if not d.get(i):
                keys_exist = False
                break
            identifier[i] = d.get(i)
        # proceed if all attributes in object_id are set
        if keys_exist:
            try:
                # create or get object if already exists
                obj, created = model_object.objects.get_or_create(**identifier)
            except ValidationError as e:
                verbose_error = 'Failed to create or get %s object with identifier "%s"' % (model_object.__name__, identifier)
                log_error = message("LOG_EXCEPT", exception=e, verbose=verbose_error, object=d)
                logger.error(log_error)
                continue
            # iterate through dict field and value pairs
            for k, v in d.items():
                # skip updating any object_id fields
                if k in object_id:
                    continue
                # update value if field exists in object and its value is different from json value
                if hasattr(obj, k) and getattr(obj, k) != sanitise_value(v):
                    log_message = message("LOG_EVENT", event='Updating %s object "%s.%s" from "%s" to "%s"' % (model_object.__name__, obj.pk, k, getattr(obj, k), sanitise_value(v)))
                    logger.info(log_message)
                    setattr(obj, k, sanitise_value(v))
                    update = True
        if update:
            obj.save()
            log_message = message("LOG_EVENT", event='%s object "%s" has been updated' % (model_object.__name__, obj.pk))
            logger.info(log_message)


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


#====================UTILS: GET JSON DICTS====================#
def get_json_dicts(json_file, **kwargs):
    key = kwargs.get("key")
    with open(json_file, "r") as f:
        json_dict = json.load(f)
        if not key:
            return json_dict
        return json_dict.get(key) if json_dict.get(key) else list()


#====================UTILS: GET KEY VALUES====================#
def get_key_values(**kwargs):
    json_file = kwargs.get("json_file")
    key = kwargs.get("key")
    settings_dict = kwargs.get("settings_dict")
    if json_file:
        settings_dict = get_json_dicts(json_file, key=key)
    # cast empty strings to None
    return [sanitise_value(d.get(key)) for d in settings_dict if key in d]


#====================UTILS: FILTER JSON DICTS====================#
def filter_json_dicts(dict_list, **kwargs):
    filtered_results = []
    for item in dict_list:
        matches_query = all(item.get(key) == value for key, value in kwargs.items())
        if matches_query:
            filtered_results.append(item)
    return filtered_results


#====================UTILS: SANITISE STRING====================#
def sanitise_string(text):
    # remove characters that are not letters or numbers
    return re.sub(r"[^a-zA-Z0-9]", "", text)


#====================UTILS: SANITISE VALUE====================#
def sanitise_value(v):
    # cast empty strings to None
    return v if str(v).strip() != "" else None


#====================UTILS: COUNT EMOJI====================#
def count_emoji(text):
    tokens = list(emoji.analyze(text))
    # return count, length of emoji
    return len(tokens), sum([len(t.value.emoji) for t in tokens])


#====================UTILS: HAS EMOJI====================#
def has_emoji(text):
    return count_emoji(text)[0] > 0


#====================UTILS: EMOJIZE====================#
def emojize(text):
    return emoji.emojize(text, language="alias")


#====================UTILS: DEMOJIZE====================#
def demojize(text):
    return emoji.replace_emoji(text, replace=lambda chars, data_dict: data_dict["en"]) if has_emoji(text) else text


#====================UTILS: MESSAGE====================#
def message(key, **kwargs):
    # if not key.startswith("LOG_"):
    #     kwargs = {k:escape_md(v) for k, v in kwargs.items()}
    return MESSAGES[key].format(**kwargs)


#====================UTILS: ICON====================#
def icon(**kwargs):
    key = kwargs.get("key")
    alias = ":%s:" % kwargs.get("alias", ICONS.get(key))
    spacer = kwargs.get("spacer", False)
    icon = emojize(alias)
    if not emoji.is_emoji(icon):
        return ""
    else:
        return icon + " " if spacer else icon


#====================UTILS: GET DOMAIN====================#
def get_domain(url):
    return urlparse(url).netloc if url else None


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
    return ", ".join(map(str, l)) if isinstance(l, (list, tuple)) and l else None
    # return str(l)[1:-1]


#====================UTILS: UNIQUE LIST====================#
def unique_list(l):
    return list(set(l))


#====================UTILS: GET EXPIRED DATE====================#
def get_expired_date(max_age):
    # return date of creation that should have expired at the current time
    return get_datetime().get("utc_now") - timedelta(days=max_age)


#====================UTILS: IS EXPIRED====================#
def is_expired(datetime, max_age):
    return datetime < get_expired_date(max_age)


#====================DATETIME: CONVERT DATETIME TIMEZONE====================#
def convert_timezone(datevar, **kwargs):
    tz_name = kwargs.get("tz_name", TIME_ZONE)
    tz_target = kwargs.get("tz_target", tz.gettz(tz_name))
    # convert timezone aware datetime to another timezone
    return datevar.astimezone(tz_target)


#====================DATETIME: GET CURRENT DATETIME====================#
def get_datetime(timezone=TIME_ZONE):
    # now according to timezone
    now = datetime.now(tz=tz.gettz(timezone))
    # now in UTC
    utc_now = convert_timezone(now, tz_name="UTC")
    # now in system timezone
    sys_now = convert_timezone(now, tz_name=timezone)
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
def make_aware_datetime(**kwargs):
    datestr = kwargs.get("datestr")
    datevar = kwargs.get("datevar")
    tz_name = kwargs.get("tz_name", "UTC")
    tz_target = kwargs.get("tz_target", tz.gettz(tz_name))
    # make naive or timezone aware datetime out of string
    if datestr:
        datevar = parser.parse(datestr)
    # make timezone aware datetime out of naive datetime
    if datevar.tzinfo is None or datevar.tzinfo.utcoffset(datevar) is None:
        datevar = datevar.replace(tzinfo=tz_target)
    return datevar


#====================DATETIME: GLOBALISE LOCAL DATETIME====================#
def globalise_local_datetime(**kwargs):
    datestr = kwargs.get("datestr")
    datevar = kwargs.get("datevar")
    tz_name = kwargs.get("tz_name", TIME_ZONE)
    # make timezone aware datetime out of string
    if datestr:
        datevar = make_aware_datetime(**kwargs)
    # convert timezone aware datetime to UTC
    return convert_timezone(datevar, tz_name="UTC")


#====================DATETIME: MAKE TIME STRING====================#
def make_time_str(datevar):
    # make time string out of datetime
    return datevar.strftime("%H:%M")


#====================DATETIME: MAKE DATE STRING====================#
def make_date_str(datevar, datefmt="%d-%m-%Y"):
    # make date string out of datetime
    return datevar.strftime(datefmt)
