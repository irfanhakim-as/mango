import logging
from django.dispatch import receiver
from django.db.models.signals import post_save
from base.methods import message
from base.models import PostItem
from lib.scheduler import schedule_post
logger = logging.getLogger("base")


#====================POST: SCHEDULE POSTS====================#
@receiver(post_save, sender=PostItem)
def schedule_posts(sender, instance, created, **kwargs):
    # schedule object if it has not been scheduled yet
    if not instance.postschedule_set.exists():
        log_message = message("LOG_EVENT", event='Scheduling PostItem object "%s"' % instance)
        logger.info(log_message)
        schedule_post(instance)
    else:
        log_message = message("LOG_EVENT", event='PostItem object "%s" already has a PostSchedule object "%s"' % (instance, instance.postschedule_set.first().pk))
        logger.info(log_message)
