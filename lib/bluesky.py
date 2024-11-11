import logging
from atproto import (
    Client,
    models as atproto_models,
)
# from django.conf import settings
from pathlib import Path
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
            Path(access_token).read_text().strip(),
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
        account_id = "%s.%s" % (uid, api_domain) if api_domain and uid else None
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
def update_account(**kwargs):
    access_token = kwargs.get("access_token")
    account_id = kwargs.get("account_id")

    # set up bluesky
    bluesky = instantiate(access_token, account_id)
    if not bluesky:
        log_message = message("LOG_EVENT", event="Bluesky has failed to be instantiated")
        logger.warning(log_message)
        return

    # get current profile
    current_profile_record = bluesky.app.bsky.actor.profile.get(bluesky.me.did, "self")
    current_profile = getattr(current_profile_record, "value", None)

    params = dict(
        avatar=kwargs.get("avatar", getattr(current_profile, "avatar", None)), # not officially supported
        banner=kwargs.get("banner", getattr(current_profile, "banner", None)), # not officially supported
        created_at=kwargs.get("created_at", getattr(current_profile, "created_at", None)), # not officially supported
        description=kwargs.get("description", getattr(current_profile, "description", None)),
        display_name=kwargs.get("display_name", getattr(current_profile, "display_name", None)),
        joined_via_starter_pack=kwargs.get("joined_via_starter_pack", getattr(current_profile, "joined_via_starter_pack", None)), # not officially supported
        labels=kwargs.get("labels", getattr(current_profile, "labels", None)), # not officially supported
        pinned_post=kwargs.get("pinned_post", getattr(current_profile, "pinned_post", None)), # not officially supported
    )

    # update bluesky account
    account = bluesky.com.atproto.repo.put_record(
        atproto_models.ComAtprotoRepoPutRecord.Data(
            collection=atproto_models.ids.AppBskyActorProfile,
            repo=bluesky.me.did,
            rkey="self",
            swap_record=getattr(current_profile_record, "cid", None),
            record=atproto_models.AppBskyActorProfile.Record(**params),
        )
    )
    if account:
        account_id = bluesky.me.handle
        log_message = message("LOG_EVENT", event='Bluesky account "%s" has been updated' % account_id)
        logger.info(log_message)
    return account
