import logging
from django.conf import settings
from base.methods import (
    get_values_list,
    message,
    string_list,
)
from lib.scheduler import schedule_post
logger = logging.getLogger("base")


#====================SETTINGS: GETATTR====================#
RETRY_POST = getattr(settings, "RETRY_POST")


#====================BASE: CLEAN DATA====================#
def clean_data(deletion_candidates, schedule_candidates, **kwargs):
    retry_post = kwargs.get("retry_post", RETRY_POST)
    # delete deletion candidate model objects
    if deletion_candidates.exists():
        log_message = message("LOG_EVENT", event='Objects "%s" have been deleted' % string_list(get_values_list("pk", queryset=deletion_candidates, unique=False)))
        deletion_candidates.delete()
        logger.info(log_message)
    # schedule or delete schedule candidate model objects
    if schedule_candidates.exists():
        if not retry_post:
            verbose_event = 'Objects "%s" that were left behind have been deleted' % string_list(get_values_list("pk", queryset=schedule_candidates, unique=False))
            log_message = message("LOG_EVENT", event=verbose_event)
            schedule_candidates.delete()
            logger.info(log_message)
        else:
            for candidate in schedule_candidates:
                log_message = message("LOG_EVENT", event='Scheduling object "%s" that was left behind' % candidate.pk)
                logger.info(log_message)
                schedule_post(candidate)
