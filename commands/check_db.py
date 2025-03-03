from django.db import connection
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Check database connection"

    def handle(self, *args, **options):
        try:
            connection.ensure_connection()
            self.stdout.write(self.style.SUCCESS("Database connection successful."))
        except Exception as e:
            self.stdout.write(self.style.ERROR("Database connection failed."))
            exit(1)
