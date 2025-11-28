"""
Management command to spawn dynamic events on the map
"""
from django.core.management.base import BaseCommand
from game.services.event_spawner_service import EventSpawnerService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Spawn random dynamic events on the map'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of events to spawn (default: 5)'
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Cleanup expired events before spawning new ones'
        )

    def handle(self, *args, **options):
        count = options['count']
        cleanup = options['cleanup']

        self.stdout.write(f'Spawning {count} dynamic events...')

        # Cleanup expired events if requested
        if cleanup:
            cleaned = EventSpawnerService.cleanup_expired_events()
            self.stdout.write(self.style.WARNING(f'  Cleaned up {cleaned} expired events'))

        # Spawn new events
        events = EventSpawnerService.spawn_random_events(count=count)

        if not events:
            self.stdout.write(self.style.ERROR('  No events spawned (no map cells available)'))
            return

        # Display spawned events
        for event in events:
            self.stdout.write(
                self.style.SUCCESS(
                    f'  [+] {event.icon} {event.name} at ({event.cell.grid_x}, {event.cell.grid_y}) - '
                    f'Expires in {event.expires_at.strftime("%H:%M")}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully spawned {len(events)} events!')
        )

        # Show active events count
        active_count = EventSpawnerService.get_active_events().count()
        self.stdout.write(f'Total active events: {active_count}')
