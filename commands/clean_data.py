from django.core.management.base import BaseCommand
from lib.post import clean_data

class Command(BaseCommand):
    help = "Update and clean the PostItem model with the latest relevant data"

    def handle(self, *args, **options):
        clean_data()
