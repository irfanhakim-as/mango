from django.db import models
from django.utils.translation import gettext_lazy as _
from base.models.base import ObjectFeed


#=====================FEED: OBJECT====================#
class FeedObject(ObjectFeed):
    class Meta(ObjectFeed.Meta):
        verbose_name = "Feed object"
        verbose_name_plural = "feed objects"
