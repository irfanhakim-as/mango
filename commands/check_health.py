from django.core.management.base import BaseCommand
from base.methods import check_mastodon_health

class Command(BaseCommand):
    help = "Checks the health of the Mastodon bot by sending an unlisted test post"

    def handle(self, *args, **options):
        check_mastodon_health()
