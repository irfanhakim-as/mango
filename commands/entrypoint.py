from django.core.management.base import BaseCommand
from lib.mastodon import check_mastodon_health

class Command(BaseCommand):
    help = "Entrypoint script"

    def handle(self, *args, **options):
        check_mastodon_health()
