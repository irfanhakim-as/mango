from django.db import models
from django.utils.translation import gettext_lazy as _
from base.models.base import ObjectSchedule
from base.models.post import PostItem


#====================SCHEDULE: POST====================#
class PostSchedule(ObjectSchedule):
    class Meta:
        verbose_name = "Post Schedule"
        verbose_name_plural = "post schedules"

    SubjectReference = PostItem

    # subject = models.ForeignKey(
    #     PostItem,
    #     blank=False,
    #     null=False,
    #     on_delete=models.CASCADE,
    #     verbose_name=_("Subject"),
    #     help_text=_("Scheduled subject.")
    # )

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

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return str(self.pk)
