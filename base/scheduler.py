import logging
import random
from django.conf import settings
from base.methods import (
    emojize,
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
    limit = kwargs.get("limit", POST_LIMIT)
    organic = kwargs.get("organic", ORGANIC_POSTS)

    # set count of posts to be sent
    limit = limit if limit > 0 else 100
    if organic:
        count = random.randint(1, limit)
    else:
        count = limit

    if DB_TYPE == "postgresql":
        # limit pending objects to count and combine the two querysets
        post_objects = pending_objects[:count] | updating_objects
    else:
        # databases such as MariaDB does not support limiting querysets
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

        # prepare content
        content = message(
            "MASTODON_POST",
            title=post_title,
            tags=post_tags,
            link=post_link
        )
        try:
            post_id = send_post(
                content,
                post_id=post_object.subject.post_id,
                receiver=post_object.receiver,
                visibility=post_object.visibility,
            )
        except Exception as e:
            log_error = message("LOG_EXCEPT", exception=e, verbose='Post "%s" (%s) has failed to be sent' % (post_object, post_object.name), object=post_object)
            logger.error(log_error)
        else:
            # update subject object post_id
            post_object.subject.post_id = post_id
            post_object.subject.save(update_fields=["post_id"])
            log_message = message("LOG_EVENT", event='Post "%s" (%s) has been sent' % (post_object, post_object.name))
            logger.info(log_message)

        # delete post schedule object if it has been sent
        if post_object.subject.post_id:
            post_object.delete()
