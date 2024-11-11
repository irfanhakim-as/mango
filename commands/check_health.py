from django.core.management.base import BaseCommand
from lib.bluesky import check_health as check_bluesky_health
from lib.mastodon import check_health as check_mastodon_health

class Command(BaseCommand):
    help = "Checks the health of the bot by sending a test post"

    def handle(self, *args, **options):
        check_bluesky_health()
        check_mastodon_health()
