from django.utils.translation import gettext_lazy as _
from base.models.base import ObjectAccount


#=====================ACCOUNT: OBJECT====================#
class AccountObject(ObjectAccount):
    class Meta(ObjectAccount.Meta):
        verbose_name = "Account"
        verbose_name_plural = "accounts"
