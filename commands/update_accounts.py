import logging
from django.core.management.base import BaseCommand
from base.methods import (
    get_active_accounts,
    get_domain,
    message,
)
from lib.bluesky import update_account as update_bluesky_account
from lib.mastodon import update_account as update_mastodon_account
logger = logging.getLogger("base")

class Command(BaseCommand):
    help = "Update the profiles of all active accounts"

    def handle(self, *args, **options):
        account_objects = get_active_accounts()
        for account in account_objects:
            host = getattr(account, "host")
            params = dict(
                access_token=getattr(account, "access_token"),
                display_name=getattr(account, "display_name"),
                fields=getattr(account, "fields"),
            )
            # update account
            if host and host.lower() == "bluesky":
                params.update(dict(
                    account_id="%s.%s" % (getattr(account, "uid"), get_domain(getattr(account, "api_base_url"))),
                    description=getattr(account, "note"),
                ))
                account = update_bluesky_account(**params)
            else:
                params.update(dict(
                    api_base_url=getattr(account, "api_base_url"),
                    bot=getattr(account, "is_bot"),
                    discoverable=getattr(account, "is_discoverable"),
                    locked=getattr(account, "is_locked"),
                    note=getattr(account, "note"),
                ))
                account = update_mastodon_account(**params)
            if not account:
                verbose_warning = 'Account "%s" failed to be updated' % account.pk
                self.stdout.write(self.style.WARNING(verbose_warning))
                log_message = message("LOG_EXCEPT", exception=None, verbose=verbose_warning, object=account)
                logger.warning(log_message)
