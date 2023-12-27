from django.utils.translation import gettext_lazy as _
from base.models.base import ObjectAccount


#=====================MASTODON: ACCOUNT====================#
class MastodonAccount(ObjectAccount):
    class Meta:
        verbose_name = "Account"
        verbose_name_plural = "accounts"
