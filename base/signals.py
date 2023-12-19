import logging
from django.dispatch import receiver
from django.db.models.signals import post_save
from base.methods import (
    get_post_model,
    message,
)
from lib.scheduler import schedule_post
logger = logging.getLogger("base")
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
