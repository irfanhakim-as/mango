from base.methods import get_schedule_model
from base.scheduler import (
    post_scheduler as _post_scheduler,
    schedule_post as _schedule_post,
)
ScheduleModel = get_schedule_model()


#====================SCHEDULER: SCHEDULE POST====================#
def schedule_post(subject_object, **kwargs):
    _schedule_post(ScheduleModel, subject_object, **kwargs)


#====================SCHEDULER: POST SCHEDULER====================#
def post_scheduler(**kwargs):
    # get ScheduleModel objects that have not been posted, ordered by id (ascending)
    pending_objects = ScheduleModel.objects.filter(subject__post_id__isnull=True).order_by("id")
    # get ScheduleModel objects that have been posted, ordered by id (ascending)
    updating_objects = ScheduleModel.objects.filter(subject__post_id__isnull=False).order_by("id")

    _post_scheduler(pending_objects, updating_objects, **kwargs)
