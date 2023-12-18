from base.models import PostItem
from base.post import clean_data as _clean_data


#====================POST: CLEAN DATA====================#
def clean_data():
    # populate deletion candidates with model objects that have been posted and not currently being scheduled
    deletion_candidates = PostItem.objects.filter(post_id__isnull=False, postschedule__isnull=True)

    # populate schedule candidates with model objects that have neither been posted nor scheduled
    schedule_candidates = PostItem.objects.filter(post_id__isnull=True, postschedule__isnull=True)

    _clean_data(deletion_candidates, schedule_candidates)
