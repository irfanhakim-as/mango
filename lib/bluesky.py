import logging
from atproto import (
    Client,
    models as atproto_models,
)
# from django.conf import settings
from base.methods import (
    count_emoji,
    get_active_accounts,
    get_domain,
    message,
)
logger = logging.getLogger("base")


#====================SETTINGS: GETATTR====================#
# DEFAULT_VISIBILITY = getattr(settings, "DEFAULT_VISIBILITY")


#====================BLUESKY: INSTANTIATE====================#
def instantiate(access_token, account_id):
    if not (access_token and account_id):
        log_message = message("LOG_EVENT", event="Bluesky not configured to be instantiated")
        logger.warning(log_message)
        return
    else:
        client = Client()
        login = client.login(
            account_id,
            access_token,
        )
        return client


#====================BLUESKY: CLEAN VISIBILITY====================#
# NOTE: post visibility not currently supported on bluesky
# def clean_visibility(visibility, **kwargs):
#     default_visibility = kwargs.get("default_visibility", DEFAULT_VISIBILITY)
#     if visibility and visibility.lower() in ["public", "unlisted", "private", "direct"]:
#         return visibility.lower()
#     else:
#         return default_visibility.lower()


#====================BLUESKY: PREPARE POST====================#
def prepare_post(title, tags, link):
    # set character limits
    char_limit = 300
    link_limit = sum((23, 2)) # additional 2 for newlines
    # count characters
    title_count = len(title)
    tags_count = len(tags)
    link_count = 0 if not link else (link_limit if len(link) > link_limit else len(link))
    emoji_count, emoji_length = count_emoji(title + tags + link)
    # prioritise removing tags, then limiting title to accommodate link
    if sum((title_count, tags_count, link_count, emoji_count - emoji_length)) > char_limit:
        tags = ""
        emoji_count = count_emoji(title + tags + link)[0]
        title = title[:char_limit-link_count-emoji_count]
    # return post content
    return message(
        "FEED_POST",
        title=title,
        tags=tags,
        link=link
    )


#====================BLUESKY: SEND POST====================#
def send_post(content, **kwargs):
    access_token = kwargs.get("access_token")
    account_id = kwargs.get("account_id")
    post_id = kwargs.get("post_id")
    receiver = kwargs.get("receiver")
    # visibility = kwargs.get("visibility")

    # set up bluesky
    bluesky = instantiate(access_token, account_id)
    if not bluesky:
        log_message = message("LOG_EVENT", event="Bluesky has failed to be instantiated")
        logger.warning(log_message)
        return

    if receiver:
        content = "@%s %s" % (receiver.strip(), content)
        # if not visibility:
        #     visibility = "direct"

    params = dict(
        # visibility=clean_visibility(visibility),
    )

    # send bluesky post
    # NOTE: post update not currently supported on bluesky - alternative implementation would be to quote instead
    if not post_id:
        post = bluesky.send_post(text=content, **params)
    else:
        post = bluesky.send_post(
            text=content,
            embed=atproto_models.app.bsky.embed.record.Main(
                record=atproto_models.ComAtprotoRepoStrongRef.Main(
                    uri=post_id.split(",")[0],
                    cid=post_id.split(",")[1]
                )
            ),
            **params
        )

    # return post id
    return "%s,%s" % (getattr(post, "uri"), getattr(post, "cid"))


#====================BLUESKY: CHECK HEALTH====================#
def check_health(**kwargs):
    account_objects = kwargs.get("account_objects", get_active_accounts(host="bluesky"))
    # visibility = "private"

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
        content = message("BLUESKY_TEST", id=account_id)
        try:
            # send test post
            send_post(
                content,
                access_token=access_token,
                account_id=account_id,
                # visibility=visibility
            )
        except Exception as e:
            verbose_error = 'Test post to "%s" has failed to be sent' % account_id
            log_error = message("LOG_EXCEPT", exception=e, verbose=verbose_error, object=content)
            logger.error(log_error)
        else:
            log_message = message("LOG_EVENT", event='Test post to "%s" has been sent' % account_id)
            logger.info(log_message)


#====================BLUESKY: UPDATE ACCOUNT====================#
# NOTE: to be implemented for bluesky - reference: https://github.com/MarshalX/atproto/blob/main/examples/advanced_usage/update_profile.py
# def update_account(**kwargs):
#     access_token = kwargs.get("access_token")
#     api_base_url = kwargs.get("api_base_url")
#     bot = kwargs.get("bot")
#     discoverable = kwargs.get("discoverable")
#     display_name = kwargs.get("display_name")
#     fields = kwargs.get("fields")
#     locked = kwargs.get("locked")
#     note = kwargs.get("note")

#     # set up bluesky
#     bluesky = instantiate(access_token, account_id)
#     if not bluesky:
#         log_message = message("LOG_EVENT", event="Bluesky has failed to be instantiated")
#         logger.warning(log_message)
#         return

#     params = dict(
#         bot=bot,
#         discoverable=discoverable,
#         display_name=display_name,
#         fields=fields,
#         locked=locked,
#         note=note,
#     )

#     # update bluesky account
#     account = mastodon.account_update_credentials(**params)
#     if account:
#         url = account.get("url")
#         username = account.get("username")
#         account_id = "%s@%s" % (username, get_domain(url)) if url and username else None
#         log_message = message("LOG_EVENT", event='Mastodon account "%s" has been updated' % account_id)
#         logger.info(log_message)
#     return account
