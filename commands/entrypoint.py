from django.core.management.base import BaseCommand
from base.methods import sync_data
from lib.bluesky import check_health as check_bluesky_health
from lib.mastodon import check_health as check_mastodon_health

class Command(BaseCommand):
    help = "Entrypoint script"

    def handle(self, *args, **options):
        sync_data()
        check_bluesky_health()
        check_mastodon_health()
