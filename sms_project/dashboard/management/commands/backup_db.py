"""Dumps the full database to a timestamped JSON file (Module: Backup/Restore).
Run with: python manage.py backup_db
"""
import datetime
from pathlib import Path
from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Back up the entire database to backups/backup_<timestamp>.json"

    def handle(self, *args, **options):
        Path(settings.BACKUP_ROOT).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = Path(settings.BACKUP_ROOT) / f"backup_{timestamp}.json"
        with open(filepath, 'w') as f:
            management.call_command(
                'dumpdata', exclude=['contenttypes', 'auth.permission', 'sessions.session'],
                indent=2, stdout=f,
            )
        self.stdout.write(self.style.SUCCESS(f"Backup written to {filepath}"))
