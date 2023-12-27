from django.db import models
from django.utils.translation import gettext_lazy as _
from base.models.base import ObjectFeed


#=====================FEED: OBJECT====================#
class FeedObject(ObjectFeed):
    class Meta:
        verbose_name = "Feed object"
        verbose_name_plural = "feed objects"

    date_format = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("Date format"),
        help_text=_("The date format of the feed's entries.")
    )
