import logging
from django.dispatch import receiver
from django.db.models.signals import post_save
from base.methods import (
    get_account_model,
    get_domain,
    get_post_model,
    get_schedule_model,
    message,
)
from lib.bluesky import update_account as update_bluesky_account
from lib.mastodon import update_account as update_mastodon_account
from lib.scheduler import schedule_post
logger = logging.getLogger("base")
AccountModel = get_account_model()
PostModel = get_post_model()
ScheduleModel = get_schedule_model()


#====================POST: SCHEDULE POSTS====================#
@receiver(post_save, sender=PostModel)
def schedule_posts(sender, instance, created, **kwargs):
    schedule_related_name = "%s_set" % ScheduleModel.__name__.lower()
    schedule_obj = getattr(instance, schedule_related_name)
    # schedule object if it has not been scheduled yet
    if not schedule_obj.exists():
        log_message = message("LOG_EVENT", event='Scheduling %s object "%s"' % (PostModel.__name__, instance))
        logger.info(log_message)
        schedule_post(instance)
    else:
        log_message = message("LOG_EVENT", event='%s object "%s" already has a %s object "%s"' % (PostModel.__name__, instance, ScheduleModel.__name__, schedule_obj.first().pk))
        logger.info(log_message)


#====================ACCOUNT: UPDATE ACCOUNTS====================#
@receiver(post_save, sender=AccountModel)
def update_accounts(sender, instance, created, **kwargs):
    host = getattr(instance, "host")
    params = dict(
        access_token = getattr(instance, "access_token"),
        display_name = getattr(instance, "display_name"),
    )
    # update account
    if host and host.lower() == "bluesky":
        params.update(dict(
            account_id = "%s.%s" (getattr(instance, "uid"), get_domain(getattr(instance, "api_base_url"))),
            description = getattr(instance, "note"),
        ))
        account = update_bluesky_account(**params)
    else:
        params.update(dict(
            api_base_url = getattr(instance, "api_base_url"),
            bot = getattr(instance, "is_bot"),
            discoverable = getattr(instance, "is_discoverable"),
            fields = getattr(instance, "fields"),
            locked = getattr(instance, "is_locked"),
            note = getattr(instance, "note"),
        ))
        account = update_mastodon_account(**params)
    if not account:
        verbose_warning = "Account failed to be updated"
        log_message = message("LOG_EXCEPT", exception=None, verbose=verbose_warning, object=instance)
        logger.warning(log_message)
