from django.core.management.base import BaseCommand
from lib.scheduler import post_scheduler

class Command(BaseCommand):
    help = "Runs the post scheduler"

    def handle(self, *args, **options):
        post_scheduler()
