import logging
from base.methods import message
from lib.mastodon import send_post
logger = logging.getLogger("base")


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
def post_scheduler(limit, post_objects):
    if limit <= 0:
        return

    if not post_objects.exists():
        log_message = message("LOG_EVENT", event="No pending post objects were found")
        logger.info(log_message)
        return

    for post_object in post_objects:
        # ensure title + tags + link does not exceed 500 characters. link counts as 23 characters + 2 characters (newlines).
        post_title = post_object.subject.title
        post_tags = " " + " ".join(["#" + i for i in post_object.subject.tags]) if post_object.subject.tags else ""
        post_link = "\n\n%s" % post_object.subject.link if post_object.subject.link else ""
        if len(post_title + post_tags + post_link) > 500:
            # remove tags
            post_tags = ""
        if len(post_title + post_tags + post_link) > 500:
            # limit post title to (500-23-2)
            if post_link:
                post_title = post_title[:475]
            # limit post title to 500
            else:
                post_title = post_title[:500]

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

        # delete post object if it has been sent
        if post_object.subject.post_id:
            post_object.delete()
