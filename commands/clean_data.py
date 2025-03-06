from django.core.management.base import BaseCommand
from base.methods import get_post_model
from lib.post import clean_data
PostModel = get_post_model()

class Command(BaseCommand):
    help = "Update and clean the %s model with the latest relevant data" % PostModel.__name__

    def handle(self, *args, **options):
        clean_data()
