import logging
import math
import random
from django.conf import settings
from base.methods import (
    count_emoji,
    emojize,
    get_active_accounts,
    is_debug,
    message,
)
from lib.mastodon import send_post
logger = logging.getLogger("base")


#====================SETTINGS: GETATTR====================#
DB_TYPE = getattr(settings, "DB_TYPE")
ORGANIC_POSTS = getattr(settings, "ORGANIC_POSTS")
POST_LIMIT = getattr(settings, "POST_LIMIT")


#====================BASE: SCHEDULE POST====================#
def schedule_post(schedule_model, subject_object, **kwargs):
    receiver = kwargs.get("receiver")
    visibility = kwargs.get("visibility")

    if not receiver:
        name = "Public"
    else:
        name = "Mention"

    object_values = dict(name=name, subject=subject_object, receiver=receiver, visibility=visibility)
    post_object = schedule_model.objects.create(**object_values)

    log_message = message("LOG_EVENT", event='%s object "%s" (%s) has been scheduled' % (schedule_model.__name__, post_object, post_object.name))
    logger.info(log_message)


#====================BASE: POST SCHEDULER====================#
def post_scheduler(pending_objects, updating_objects, **kwargs):
    account_objects = kwargs.get("account_objects", get_active_accounts())
    limit = kwargs.get("limit", POST_LIMIT)
    organic = kwargs.get("organic", ORGANIC_POSTS)

    if not account_objects:
        log_message = message("LOG_EVENT", event="No active account objects were found")
        logger.info(log_message)
        return

    # set count of posts to be sent
    limit = limit if limit > 0 else 100
    if organic:
        minimum = limit / 3
        minimum = math.ceil(minimum) if minimum % 1 != 0 else int(minimum)
        count = random.randint(minimum, limit)
    else:
        count = limit

    # limit pending objects to count for supported databases
    if DB_TYPE == "postgresql":
        pending_objects = pending_objects[:count]
    # combine pending and updating objects
    post_objects = pending_objects | updating_objects

    if not post_objects.exists():
        if is_debug():
            log_message = message("LOG_EVENT", event="No pending post objects were found")
            logger.info(log_message)
        return

    for post_object in post_objects:
        # prepare post title, tags, and link
        post_title = emojize(post_object.subject.title)
        post_tags = emojize(" " + " ".join(["#" + i for i in post_object.subject.tags]) if post_object.subject.tags else "")
        post_link = emojize("\n\n%s" % post_object.subject.link if post_object.subject.link else "")

        # ensure title + tags + link does not exceed the character limit. link counts as 23 characters + 2 characters (newlines). emoji counts as 2 characters.
        char_limit = 500
        title_count = len(post_title)
        tags_count = len(post_tags)
        link_count = 25 if post_link else 0
        emoji_count = count_emoji(post_title + post_tags + post_link)
        # prioritise removing tags, then limiting title to accommodate link
        if title_count + tags_count + link_count + emoji_count > char_limit:
            post_tags = ""
            emoji_count = count_emoji(post_title + post_tags + post_link)
            post_title = post_title[:char_limit-link_count-emoji_count]

        # prepare content
        content = message(
            "MASTODON_POST",
            title=post_title,
            tags=post_tags,
            link=post_link
        )

        for account in account_objects:
            access_token = getattr(account, "access_token")
            api_base_url = getattr(account, "api_base_url")
            uid = getattr(account, "uid")
            # get post_id specific to account if it is an existing and format conforming post
            account_pid = [pid.split("_")[-1] for pid in post_object.subject.post_id if pid.split("_")[0] == uid] if post_object.subject.post_id and isinstance(post_object.subject.post_id, list) else []
            account_pid = account_pid[0] if account_pid else None
            try:
                post_id = send_post(
                    content,
                    access_token=access_token,
                    api_base_url=api_base_url,
                    post_id=account_pid,
                    receiver=post_object.receiver,
                    visibility=post_object.visibility,
                )
            except Exception as e:
                log_error = message("LOG_EXCEPT", exception=e, verbose='Post "%s" (%s) has failed to be sent' % (post_object, post_object.name), object=post_object)
                logger.error(log_error)
            else:
                if not post_id:
                    verbose_error = 'Post "%s" (%s) has not successfully returned an ID' % (post_object, post_object.name)
                    log_error = message("LOG_EXCEPT", exception=None, verbose=verbose_error, object=post_object)
                    logger.error(log_error)
                    return
                pid = "%s_%s" % (uid, post_id)
                # update subject object post_id if new or non-format conforming post
                if not account_pid:
                    if not isinstance(post_object.subject.post_id, list):
                        post_object.subject.post_id = list()
                    post_object.subject.post_id.append(pid)
                    post_object.subject.save(update_fields=["post_id"])
                log_message = message("LOG_EVENT", event='Post "%s" (%s) has been sent' % (post_object, post_object.name))
                logger.info(log_message)
                # delete post schedule object if it has been sent on current account
                if isinstance(post_object.subject.post_id, list) and pid in post_object.subject.post_id:
                    post_object.delete()
