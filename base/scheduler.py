import logging
import math
import random
from django.conf import settings
from base.methods import (
    emojize,
    get_active_accounts,
    get_domain,
    is_debug,
    message,
    sanitise_string,
    string_list,
)
from lib.bluesky import (
    instantiate as instantiate_bluesky,
    prepare_post as prepare_bluesky_post,
    send_post as send_bluesky_post,
)
from lib.mastodon import (
    instantiate as instantiate_mastodon,
    prepare_post as prepare_mastodon_post,
    send_post as send_mastodon_post,
)
logger = logging.getLogger("base")


#====================SETTINGS: GETATTR====================#
DB_TYPE = getattr(settings, "DB_TYPE")
ORGANIC_POSTS = getattr(settings, "ORGANIC_POSTS")
POST_LIMIT = getattr(settings, "POST_LIMIT")
RETRY_POST = getattr(settings, "RETRY_POST")


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

    log_message = message("LOG_EVENT", event='%s object "%s" (%s) has been scheduled' % (schedule_model.__name__, post_object, post_object.subject))
    logger.info(log_message)


#====================BASE: POST SCHEDULER====================#
def post_scheduler(pending_objects, updating_objects, **kwargs):
    account_objects = kwargs.get("account_objects", get_active_accounts())
    clients = kwargs.get("clients", {})
    limit = kwargs.get("limit", POST_LIMIT)
    organic = kwargs.get("organic", ORGANIC_POSTS)
    retry_post = kwargs.get("retry_post", RETRY_POST)

    if not account_objects:
        if is_debug():
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

    # instantiate all clients
    for account in account_objects:
        access_token = getattr(account, "access_token", None)
        api_base_url = getattr(account, "api_base_url", None)
        api_domain = get_domain(api_base_url)
        host = getattr(account, "host", None)
        uid = getattr(account, "uid", None)
        # format a unique account id
        account_id = "%s%s%s" % (uid, "." if host and host.lower() == "bluesky" else "@", api_domain) if api_domain and uid else None
        client = instantiate_bluesky(access_token, account_id) if host and host.lower() == "bluesky" else instantiate_mastodon(access_token, api_base_url)
        # abort if client instantiation failed
        if not client:
            verbose_error = 'Client "%s" has failed to be instantiated' % account_id
            log_error = message("LOG_EXCEPT", exception=e, verbose=verbose_error, object=account.pk)
            logger.error(log_error)
            continue
        clients[account.pk] = dict(account_id=account_id, client=client, host=host)

    for post_object in post_objects:
        delete = True
        # prepare post title, tags, and link
        post_title = emojize(post_object.subject.title)
        post_tags = emojize(" " + " ".join(["#" + sanitise_string(i) for i in post_object.subject.tags]) if post_object.subject.tags else "")
        post_link = emojize(post_object.subject.link if post_object.subject.link else "")
        bluesky_post = prepare_bluesky_post(post_title, post_tags, post_link, embed_only=True)
        mastodon_post = prepare_mastodon_post(post_title, post_tags, post_link)

        for account in account_objects:
            if not (account_client := clients.get(account.pk, None)): continue
            account_id = account_client.get("account_id")
            client = account_client.get("client")
            host = account_client.get("host")
            # get post_id specific to account if it is an existing and format conforming post
            account_pid = [pid.split("_")[-1] for pid in post_object.subject.post_id if pid.split("_")[0] == account_id] if post_object.subject.post_id and isinstance(post_object.subject.post_id, list) else []
            account_pid = account_pid[0] if account_pid else None
            try:
                if host and host.lower() == "bluesky":
                    post_id = send_bluesky_post(
                        bluesky_post,
                        # access_token=access_token,
                        # account_id=account_id,
                        bluesky=client,
                        post_id=account_pid,
                        receiver=post_object.receiver,
                    )
                else:
                    post_id = send_mastodon_post(
                        mastodon_post,
                        # access_token=access_token,
                        # api_base_url=api_base_url,
                        mastodon=client,
                        post_id=account_pid,
                        receiver=post_object.receiver,
                        visibility=post_object.visibility,
                    )
            except Exception as e:
                # cancel mark for deletion due to error
                delete = False
                verbose_error = 'Post "%s" (%s) has failed to be sent' % (post_object, account_id)
                log_error = message("LOG_EXCEPT", exception=e, verbose=verbose_error, object=post_object)
                logger.error(log_error)
            else:
                if not post_id:
                    # cancel mark for deletion since post has not been sent on current account
                    delete = False
                    verbose_error = 'Post "%s" (%s) has not successfully returned an ID' % (post_object, account_id)
                    log_error = message("LOG_EXCEPT", exception=None, verbose=verbose_error, object=post_object)
                    logger.error(log_error)
                    continue
                pid = "%s_%s" % (account_id, post_id)
                # update subject object post_id if new or non-format conforming post
                if not account_pid:
                    if not isinstance(post_object.subject.post_id, list):
                        post_object.subject.post_id = list()
                    post_object.subject.post_id.append(pid)
                    post_object.subject.save(update_fields=["post_id"])
                log_message = message("LOG_EVENT", event='Post "%s" (%s) has been sent' % (post_object, pid))
                logger.info(log_message)
                # cancel mark for deletion if post has not been sent on an account
                # NOTE: check for account_id instead as pid changes with every quote post for bluesky due to absence of real post updates
                # if not pid in post_object.subject.post_id:
                if not any(account_id in i for i in post_object.subject.post_id):
                    delete = False
        # delete post schedule object if it has been sent successfully on all accounts or if configured to not retry
        if delete or not retry_post:
            if delete:
                verbose_event = 'Post Schedule "%s" which has been sent successfully to "%s" has been deleted' % (post_object, string_list(post_object.subject.post_id))
            else:
                verbose_event = 'Post Schedule "%s" has been deleted' % post_object
            post_object.delete()
            log_message = message("LOG_EVENT", event=verbose_event)
            logger.info(log_message)
