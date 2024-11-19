from django.conf import settings
from base.methods import get_schedule_model
from base.scheduler import (
    post_scheduler as _post_scheduler,
    schedule_post as _schedule_post,
)
ScheduleModel = get_schedule_model()


#====================SETTINGS: GETATTR====================#
POST_ORDER = getattr(settings, "POST_ORDER")


#====================SCHEDULER: SCHEDULE POST====================#
def schedule_post(subject_object, **kwargs):
    _schedule_post(ScheduleModel, subject_object, **kwargs)


#====================SCHEDULER: POST SCHEDULER====================#
def post_scheduler(**kwargs):
    # get ScheduleModel objects that have not been posted, ordered by priority (ascending)
    pending_objects = ScheduleModel.objects.filter(subject__post_id__isnull=True).order_by(POST_ORDER)
    # get ScheduleModel objects that have been posted, ordered by priority (ascending)
    updating_objects = ScheduleModel.objects.filter(subject__post_id__isnull=False).order_by(POST_ORDER)

    _post_scheduler(pending_objects, updating_objects, **kwargs)
