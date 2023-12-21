from django.db import models
from django.utils.translation import gettext_lazy as _
from base.methods import get_post_model
from base.models.base import ObjectSchedule
PostModel = get_post_model()


#====================SCHEDULE: POST====================#
class PostSchedule(ObjectSchedule):
    class Meta:
        verbose_name = "Post Schedule"
        verbose_name_plural = "post schedules"

    SubjectReference = PostModel

    receiver = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("Receiver"),
        help_text=_("Individual receiver of the post.")
    )

    visibility = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("Visibility"),
        help_text=_("Visibility of the post.")
    )
