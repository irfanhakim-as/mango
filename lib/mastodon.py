import logging
from mastodon import Mastodon
from django.conf import settings
from base.methods import (
    count_emoji,
    get_active_accounts,
    get_domain,
    message,
)
logger = logging.getLogger("base")


#====================SETTINGS: GETATTR====================#
# ACCESS_TOKEN = getattr(settings, "ACCESS_TOKEN")
# API_BASE_URL = getattr(settings, "API_BASE_URL")
# BOT_ID = getattr(settings, "BOT_ID")
DEFAULT_VISIBILITY = getattr(settings, "DEFAULT_VISIBILITY")


#====================MASTODON: INSTANTIATE====================#
def instantiate(access_token, home_instance):
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


#====================MASTODON: PREPARE POST====================#
def prepare_post(title, tags, link):
    # set character limits
    char_limit = 500
    link_limit = sum((23, 2)) # additional 2 for newlines
    title_count = len(title)
    tags_count = len(tags)
    link_count = 0 if not link else (link_limit if len(link) > link_limit else len(link))
    emoji_count = count_emoji(title + tags + link)
    # prioritise removing tags, then limiting title to accommodate link
    if title_count + tags_count + link_count + emoji_count > char_limit:
        tags = ""
        emoji_count = count_emoji(title + tags + link)
        title = title[:char_limit-link_count-emoji_count]
    # return post content
    return message(
        "FEED_POST",
        title=title,
        tags=tags,
        link=link
    )


#====================MASTODON: SEND POST====================#
def send_post(content, **kwargs):
    access_token = kwargs.get("access_token")
    api_base_url = kwargs.get("api_base_url")
    post_id = kwargs.get("post_id")
    receiver = kwargs.get("receiver")
    visibility = kwargs.get("visibility")

    # set up mastodon
    mastodon = instantiate(access_token, api_base_url)

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


#====================MASTODON: CHECK HEALTH====================#
def check_health(**kwargs):
    account_objects = kwargs.get("account_objects", get_active_accounts())
    visibility = "private"

    if not account_objects:
        log_message = message("LOG_EVENT", event="No active account objects were found")
        logger.info(log_message)
        return

    for account in account_objects:
        access_token = getattr(account, "access_token")
        api_base_url = getattr(account, "api_base_url")
        api_domain = get_domain(api_base_url)
        uid = getattr(account, "uid")
        # format a unique account id
        account_id = "%s@%s" % (uid, api_domain) if api_domain and uid else None
        content = message("MASTODON_TEST", visibility=visibility, name=uid)
        try:
            # send test post
            send_post(
                content,
                access_token=access_token,
                api_base_url=api_base_url,
                visibility=visibility
            )
        except Exception as e:
            verbose_error = 'Test post to "%s" has failed to be sent' % account_id
            log_error = message("LOG_EXCEPT", exception=e, verbose=verbose_error, object=content)
            logger.error(log_error)
        else:
            log_message = message("LOG_EVENT", event='Test post to "%s" has been sent' % account_id)
            logger.info(log_message)


#====================MASTODON: UPDATE ACCOUNT====================#
def update_account(**kwargs):
    access_token = kwargs.get("access_token")
    api_base_url = kwargs.get("api_base_url")
    bot = kwargs.get("bot")
    discoverable = kwargs.get("discoverable")
    display_name = kwargs.get("display_name")
    fields = kwargs.get("fields")
    locked = kwargs.get("locked")
    note = kwargs.get("note")

    # set up mastodon
    mastodon = instantiate(access_token, api_base_url)
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
    account = mastodon.account_update_credentials(**params)
    if account:
        url = account.get("url")
        username = account.get("username")
        account_id = "%s@%s" % (username, get_domain(url)) if url and username else None
        log_message = message("LOG_EVENT", event='Mastodon account "%s" has been updated' % account_id)
        logger.info(log_message)
    return account
