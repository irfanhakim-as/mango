import emoji
import logging
import re
import urllib.request
from datetime import datetime
from dateutil import tz
from mastodon import Mastodon
from django.conf import settings
from base.models import PostSchedule
from lib.messages import (
    ICONS,
    MESSAGES,
)
logger=logging.getLogger('base')


#=====================SETTINGS: GETATTR====================#
BOT_ID = getattr(settings, 'BOT_ID', 'mango')
TIME_ZONE = getattr(settings, 'TIME_ZONE', 'UTC')
ACCESS_TOKEN = getattr(settings, 'ACCESS_TOKEN', None)
API_BASE_URL = getattr(settings, 'API_BASE_URL', 'https://botsin.space/')


#=====================UTILS: ESCAPE MARKDOWN====================#
def escape_md(text):
    try:
        text = str(text)
        escape_chars = r'_*['
        text = re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
    except Exception as e:
        verbose_warning = 'Failed to escape markdown characters'
        log_message=message('LOG_EXCEPT', exception=e, verbose=verbose_warning, object=text)
        logger.warning(log_message)
    return text


#=====================UTILS: MESSAGE====================#
def message(key,**kwargs):
    if not key.startswith('LOG_'):
        kwargs = {k:escape_md(v) for k, v in kwargs.items()}
    return MESSAGES[key].format(**kwargs)


#=====================UTILS: ICON====================#
def icon(**kwargs):
    key = kwargs.get('key')
    spacer = kwargs.get('spacer', False)
    alias = kwargs.get('alias', ICONS.get(key))
    icon = emoji.emojize(f":{alias}:")
    
    if not emoji.is_emoji(icon):
        return ""
    else:
        if spacer:
            icon += " "
        return icon


#=====================UTILS: READ URL====================#
def read_url(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})).read()


#=====================UTILS: REMOVE DICTIONARY KEYS====================#
def remove_dict_keys(dictvar,keys):
    for k in keys:
        dictvar.pop(k,None)
    return dictvar


#=====================UTILS: LIST AS STRING====================#
def string_list(list):
    return str(list)[1:-1]


#=====================DATETIME: CONVERT DATETIME TIMEZONE====================#
def convert_timezone(datevar,tzvar=TIME_ZONE):
    # convert timezone aware datetime to another timezone
    return datevar.astimezone(tz.gettz(tzvar))


#=====================DATETIME: GET CURRENT DATETIME====================#
def get_datetime(timezone=TIME_ZONE):
    # now according to timezone
    now = datetime.now(tz=tz.gettz(timezone))
    # now in UTC
    utc_now = convert_timezone(now,'UTC')
    # now in system timezone
    sys_now = convert_timezone(now)
    # now as date string
    today = now.date()

    date_dict = {
        'now': now,
        'utc_now': utc_now,
        'sys_now': sys_now,
        'today': today,
    }
    return date_dict


#=====================DATETIME: MAKE TIMEZONE AWARE DATETIME====================#
def make_aware_datetime(tzvar,**kwargs):
    datestr=kwargs.get('datestr')
    datefmt=kwargs.get('datefmt', '%Y-%m-%d')
    datevar=kwargs.get('datevar')
    
    # make naive datetime out of string
    if datestr:
        datevar=datetime.strptime(datestr, datefmt)
    # make timezone aware datetime out of naive datetime
    return datevar.replace(tzinfo=tz.gettz(tzvar))


#=====================DATETIME: GLOBALISE LOCAL DATETIME====================#
def globalise_local_datetime(tzvar=TIME_ZONE,**kwargs):
    datestr=kwargs.get('datestr')
    datefmt=kwargs.get('datefmt','%Y-%m-%d')
    datevar=kwargs.get('datevar')
    
    # make timezone aware datetime out of string
    if datestr:
        datevar=make_aware_datetime(tzvar, datestr=datestr, datefmt=datefmt)
    # convert timezone aware datetime to UTC
    return convert_timezone(datevar,'UTC')


#=====================DATETIME: MAKE TIME STRING====================#
def make_time_str(datevar):
    # make time string out of datetime
    return datevar.strftime("%H:%M")


#=====================DATETIME: MAKE DATE STRING====================#
def make_date_str(datevar,datefmt="%d-%m-%Y"):
    # make date string out of datetime
    return datevar.strftime(datefmt)


#=====================SCHEDULER: SCHEDULE POST====================#
def schedule_post(**kwargs):
    msg=kwargs.get('msg')
    receiver=kwargs.get('receiver')
    visibility=kwargs.get('visibility')

    if not msg:
        return
    
    if not receiver:
        name = 'Public'
    else:
        name = receiver
    
    object_values = dict(name=name, msg=msg, receiver=receiver, visibility=visibility)
    post_object = PostSchedule.objects.create(**object_values)

    log_message = message('LOG_EVENT', event='Post "%s" (%s) has been scheduled' % (post_object, name))
    logger.info(log_message)


#=====================SCHEDULER: POST SCHEDULER====================#
def post_scheduler():
    post_object = PostSchedule.objects.order_by('date_scheduled').first()

    if not post_object:
        return
    
    try:
        post_sender(
            post_object.msg,
            receiver = post_object.receiver,
            visibility = post_object.visibility,
        )
    except Exception as e:
        log_error = message('LOG_EXCEPT', exception=e, verbose='Post "%s" (%s) has failed to be sent' % (post_object, post_object.name), object=post_object)
        logger.error(log_error)
    else:
        log_message = message('LOG_EVENT', event='Post "%s" (%s) has been sent' % (post_object, post_object.name))
        logger.info(log_message)
    
    post_object.delete()


#=====================MASTODON: CLEAN VISIBILITY====================#
def clean_visibility(visibility):
    if visibility and visibility.lower() in ['public','unlisted','private','direct']:
        return visibility.lower()
    else:
        return 'public'


#=====================MASTODON: POST SENDER====================#
def post_sender(msg,**kwargs):
    receiver=kwargs.get('receiver')
    visibility=kwargs.get('visibility')
    
    if receiver:
        msg = '@%s %s' % (receiver.strip(), msg)
        if not visibility:
            visibility = 'direct'
    
    visibility = clean_visibility(visibility)

    send_post(msg, visibility)


#=====================MASTODON: SEND POST====================#
def send_post(msg,visibility):
    # set up mastodon
    mastodon = Mastodon(
        access_token = ACCESS_TOKEN,
        api_base_url = API_BASE_URL,
    )

    params = dict(
        visibility = visibility,
    )
    
    # send mastodon post
    mastodon.status_post(msg, **params)


#=====================MASTODON: CHECK MASTODON HEALTH====================#
def check_mastodon_health():
    visibility = "unlisted"
    msg = message('MASTODON_TEST', visibility=visibility, name=BOT_ID)
    try:
        # schedule test post
        schedule_post(msg=msg, visibility=visibility)
    except Exception as e:
        log_error = message('LOG_EXCEPT', exception=e, verbose='Test post failed', object=msg)
        logger.error(log_error)
    else:
        log_message = message('LOG_EVENT', event='Test post succeeded')
        logger.info(log_message)
