from datetime import timedelta
from django.conf import settings
from django.db.models import Q
from base.methods import (
    get_datetime,
    get_post_model,
    get_values_list,
)
from base.post import clean_data as _clean_data
PostModel = get_post_model()


#====================SETTINGS: GETATTR====================#
POST_EXPIRY = getattr(settings, "POST_EXPIRY")


#====================POST: CLEAN DATA====================#
def clean_data(**kwargs):
    # populate deletion candidates with (model objects that have been posted and not currently scheduled) or (model objects that have been created past expiry date)
    deletion_candidates = PostModel.objects.filter(
        (Q(post_id__isnull=False) & Q(postschedule__isnull=True)) |
        Q(date_created__lte=get_datetime().get("utc_now") - timedelta(days=POST_EXPIRY))
    )

    # populate schedule candidates with model objects that have neither been posted nor scheduled and not among the deletion candidates
    schedule_candidates = PostModel.objects.filter(post_id__isnull=True, postschedule__isnull=True).exclude(pk__in=get_values_list("pk", queryset=deletion_candidates))

    _clean_data(deletion_candidates, schedule_candidates, **kwargs)
