import logging
from mastodon import Mastodon
from django.conf import settings
from base.methods import message
logger = logging.getLogger("base")


#====================SETTINGS: GETATTR====================#
ACCESS_TOKEN = getattr(settings, "ACCESS_TOKEN")
API_BASE_URL = getattr(settings, "API_BASE_URL")
BOT_ID = getattr(settings, "BOT_ID")
DEFAULT_VISIBILITY = getattr(settings, "DEFAULT_VISIBILITY")


#====================MASTODON: INSTANTIATE====================#
def instantiate_mastodon(access_token, home_instance):
    if not (access_token and home_instance):
        log_message = message("LOG_EVENT", event="Mastodon not configured to be instantiated")
        logger.warning(log_message)
        return
    else:
        return Mastodon(
            access_token=access_token,
            api_base_url=home_instance,
        )


#====================MASTODON: CLEAN VISIBILITY====================#
def clean_visibility(visibility, **kwargs):
    default_visibility = kwargs.get("default_visibility", DEFAULT_VISIBILITY)
    if visibility and visibility.lower() in ["public", "unlisted", "private", "direct"]:
        return visibility.lower()
    else:
        return default_visibility.lower()


#====================MASTODON: SEND POST====================#
def send_post(content, **kwargs):
    access_token = kwargs.get("access_token", ACCESS_TOKEN)
    api_base_url = kwargs.get("api_base_url", API_BASE_URL)
    post_id = kwargs.get("post_id")
    receiver = kwargs.get("receiver")
    visibility = kwargs.get("visibility")

    # set up mastodon
    mastodon = instantiate_mastodon(access_token, api_base_url)

    if not mastodon:
        log_message = message("LOG_EVENT", event="Mastodon has failed to be instantiated")
        logger.warning(log_message)
        return

    if receiver:
        content = "@%s %s" % (receiver.strip(), content)
        if not visibility:
            visibility = "direct"

    params = dict(
        visibility=clean_visibility(visibility),
    )

    # send mastodon post
    if not post_id:
        toot = mastodon.status_post(content, **params)
    else:
        toot = mastodon.status_update(post_id, status=content)

    # return post id
    return toot.get("id")


#====================MASTODON: CHECK MASTODON HEALTH====================#
def check_mastodon_health(**kwargs):
    bot_id = kwargs.get("bot_id", BOT_ID)
    visibility = "private"
    content = message("MASTODON_TEST", visibility=visibility, name=bot_id)
    try:
        # send test post
        send_post(content=content, visibility=visibility)
    except Exception as e:
        log_error = message("LOG_EXCEPT", exception=e, verbose="Test post failed to be sent", object=content)
        logger.error(log_error)
    else:
        log_message = message("LOG_EVENT", event="Test post has been sent")
        logger.info(log_message)


#====================MASTODON: UPDATE ACCOUNT====================#
def update_account(**kwargs):
    access_token = kwargs.get("access_token", ACCESS_TOKEN)
    api_base_url = kwargs.get("api_base_url", API_BASE_URL)
    bot = kwargs.get("bot")
    discoverable = kwargs.get("discoverable")
    display_name = kwargs.get("display_name")
    fields = kwargs.get("fields")
    locked = kwargs.get("locked")
    note = kwargs.get("note")

    # set up mastodon
    mastodon = instantiate_mastodon(access_token, api_base_url)
    if not mastodon:
        log_message = message("LOG_EVENT", event="Mastodon has failed to be instantiated")
        logger.warning(log_message)
        return

    params = dict(
        bot=bot,
        discoverable=discoverable,
        display_name=display_name,
        fields=fields,
        locked=locked,
        note=note,
    )

    # update mastodon account
    return mastodon.account_update_credentials(**params)
