import random
from django.conf import settings
from base.models import PostSchedule
from base.scheduler import (
    post_scheduler as _post_scheduler,
    schedule_post as _schedule_post,
)


#====================SETTINGS: GETATTR====================#
POST_LIMIT = getattr(settings, "POST_LIMIT")


#====================SCHEDULER: SCHEDULE POST====================#
def schedule_post(subject_object, **kwargs):
    _schedule_post(PostSchedule, subject_object, **kwargs)


#====================SCHEDULER: POST SCHEDULER====================#
def post_scheduler(limit=POST_LIMIT, **kwargs):
    count = kwargs.get("count", random.randint(1, limit))
    # get `count` number of PostSchedule objects that have not been posted, ordered by id (ascending)
    pending_objects = PostSchedule.objects.filter(subject__post_id__isnull=True).order_by("id")[:count]
    # get all PostSchedule objects that have been posted, ordered by id (ascending)
    updating_objects = PostSchedule.objects.filter(subject__post_id__isnull=False).order_by("id")
    # combine the two querysets
    post_objects = pending_objects | updating_objects

    _post_scheduler(limit, post_objects, **kwargs)
