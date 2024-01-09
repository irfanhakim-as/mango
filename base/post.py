import logging
from base.methods import (
    get_values_list,
    message,
    string_list,
)
from lib.scheduler import schedule_post
logger = logging.getLogger("base")


#====================BASE: CLEAN DATA====================#
def clean_data(deletion_candidates, schedule_candidates):
    # delete deletion candidate model objects
    if deletion_candidates.exists():
        log_message = message("LOG_EVENT", event='Objects "%s" have been deleted' % string_list(get_values_list("pk", queryset=deletion_candidates, unique=False)))
        deletion_candidates.delete()
        logger.info(log_message)
    # schedule schedule candidate model objects
    if schedule_candidates.exists():
        for candidate in schedule_candidates:
            log_message = message("LOG_EVENT", event='Scheduling object "%s" that was left behind' % candidate.pk)
            logger.info(log_message)
            schedule_post(candidate)
