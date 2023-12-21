from base.models import PostSchedule
from base.scheduler import (
    post_scheduler as _post_scheduler,
    schedule_post as _schedule_post,
)


#====================SCHEDULER: SCHEDULE POST====================#
def schedule_post(subject_object, **kwargs):
    _schedule_post(PostSchedule, subject_object, **kwargs)


#====================SCHEDULER: POST SCHEDULER====================#
def post_scheduler(**kwargs):
    # get PostSchedule objects that have not been posted, ordered by id (ascending)
    pending_objects = PostSchedule.objects.filter(subject__post_id__isnull=True).order_by("id")
    # get PostSchedule objects that have been posted, ordered by id (ascending)
    updating_objects = PostSchedule.objects.filter(subject__post_id__isnull=False).order_by("id")

    _post_scheduler(pending_objects, updating_objects, **kwargs)
