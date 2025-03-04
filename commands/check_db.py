import sys
from django.core.management.base import BaseCommand
from base.methods import check_db

class Command(BaseCommand):
    help = "Check database connection"

    def handle(self, *args, **options):
        response = check_db()
        if response.status_code != 200:
            self.stderr.write(self.style.ERROR(response.content.decode()))
            sys.exit(1)
        self.stdout.write(self.style.SUCCESS(response.content.decode()))
