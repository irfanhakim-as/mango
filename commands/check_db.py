import sys
from django.db import connection
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Check database connection"

    def handle(self, *args, **options):
        try:
            connection.ensure_connection()
        except Exception as e:
            self.stderr.write(self.style.ERROR("Database connection failed."))
            sys.exit(1)
        self.stdout.write(self.style.SUCCESS("Database connection successful."))
