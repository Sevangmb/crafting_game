"""
Management command to reset daily quests
This should be run daily at midnight via cron job
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from game.models import Quest, PlayerQuest
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Reset daily quests for all players'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be reset without actually resetting'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        self.stdout.write('Resetting daily quests...')

        # Get all daily quests
        daily_quests = Quest.objects.filter(is_daily=True, is_active=True)

        if not daily_quests.exists():
            self.stdout.write(self.style.WARNING('  No daily quests found'))
            return

        self.stdout.write(f'  Found {daily_quests.count()} daily quests')

        # Reset completed daily quests for all players
        reset_count = 0
        for quest in daily_quests:
            # Find all completed instances of this quest
            completed_instances = PlayerQuest.objects.filter(
                quest=quest,
                status='completed'
            )

            count = completed_instances.count()
            if count > 0:
                self.stdout.write(f'  [{quest.icon} {quest.name}]: {count} instances to reset')
                
                if not dry_run:
                    # Reset to available (delete the PlayerQuest entry)
                    # This allows players to accept the quest again
                    completed_instances.delete()
                    reset_count += count

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\n[DRY RUN] Would reset {reset_count} quest instances')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nSuccessfully reset {reset_count} daily quest instances!')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Daily quests are now available for all players')
        )
