from django.core.management.base import BaseCommand
from lib.mastodon import check_mastodon_health

class Command(BaseCommand):
    help = "Checks the health of the Mastodon bot by sending a test post"

    def handle(self, *args, **options):
        check_mastodon_health()
