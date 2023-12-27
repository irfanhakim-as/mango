import logging
from django.dispatch import receiver
from django.db.models.signals import post_save
from base.methods import (
    get_account_model,
    get_post_model,
    message,
)
from lib.mastodon import update_account
from lib.scheduler import schedule_post
logger = logging.getLogger("base")
AccountModel = get_account_model()
PostModel = get_post_model()


#====================POST: SCHEDULE POSTS====================#
@receiver(post_save, sender=PostModel)
def schedule_posts(sender, instance, created, **kwargs):
    # schedule object if it has not been scheduled yet
    if not instance.postschedule_set.exists():
        log_message = message("LOG_EVENT", event='Scheduling %s object "%s"' % (PostModel.__name__, instance))
        logger.info(log_message)
        schedule_post(instance)
    else:
        log_message = message("LOG_EVENT", event='%s object "%s" already has a PostSchedule object "%s"' % (PostModel.__name__, instance, instance.postschedule_set.first().pk))
        logger.info(log_message)


#====================MASTODON: UPDATE ACCOUNTS====================#
@receiver(post_save, sender=AccountModel)
def update_accounts(sender, instance, created, **kwargs):
    params = dict(
        access_token = getattr(instance, "access_token"),
        api_base_url = getattr(instance, "api_base_url"),
        is_bot = getattr(instance, "bot"),
        is_discoverable = getattr(instance, "discoverable"),
        display_name = getattr(instance, "display_name"),
        fields = getattr(instance, "fields"),
        is_locked = getattr(instance, "locked"),
        note = getattr(instance, "note"),
    )
    # update mastodon account
    account = update_account(**params)
    if not account:
        verbose_warning = "Mastodon account failed to be updated"
        log_message = message("LOG_EXCEPT", exception=None, verbose=verbose_warning, object=instance)
        logger.warning(log_message)
