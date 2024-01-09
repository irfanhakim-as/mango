from django.utils.translation import gettext_lazy as _
from base.models.base import ObjectItem


#=====================POST: ITEM====================#
class PostItem(ObjectItem):
    class Meta(ObjectItem.Meta):
        verbose_name = "Post Item"
        verbose_name_plural = "post items"
