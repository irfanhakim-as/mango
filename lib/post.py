from base.methods import (
    get_post_model,
    get_values_list,
)
from base.post import clean_data as _clean_data
PostModel = get_post_model()


#====================POST: CLEAN DATA====================#
def clean_data(**kwargs):
    # populate deletion candidates with model objects that have been posted and not currently being scheduled
    deletion_candidates = PostModel.objects.filter(post_id__isnull=False, postschedule__isnull=True)

    # populate schedule candidates with model objects that have neither been posted nor scheduled and not among the deletion candidates
    schedule_candidates = PostModel.objects.filter(post_id__isnull=True, postschedule__isnull=True).exclude(pk__in=get_values_list("pk", queryset=deletion_candidates))

    _clean_data(deletion_candidates, schedule_candidates, **kwargs)
