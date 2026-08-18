"""Restores the database from a JSON backup file (Module: Backup/Restore).
Run with: python manage.py restore_db backups/backup_20260101_120000.json
"""
from django.core import management
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Restore the database from a backup JSON file"

    def add_arguments(self, parser):
        parser.add_argument('filepath', type=str)

    def handle(self, *args, **options):
        filepath = options['filepath']
        try:
            management.call_command('loaddata', filepath)
        except Exception as e:
            raise CommandError(f"Restore failed: {e}")
        self.stdout.write(self.style.SUCCESS(f"Database restored from {filepath}"))
