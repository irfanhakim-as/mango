from django.core.management.base import BaseCommand
from base.methods import sync_data

class Command(BaseCommand):
    help = "Sync essential models with data from JSON files."

    def handle(self, *args, **options):
        sync_data()
