from __future__ import absolute_import, unicode_literals
import logging
from celery import shared_task
from base.methods import post_scheduler
logger=logging.getLogger('base')


# check for any posts that need to be posted
@shared_task
def post_scheduler_task():
    post_scheduler()
