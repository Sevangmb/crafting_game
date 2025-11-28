"""
Management command to populate initial event templates
This is mainly for documentation/testing - events are spawned via spawn_events.py
"""
from django.core.management.base import BaseCommand
from game.services.event_spawner_service import EventSpawnerService


class Command(BaseCommand):
    help = 'Display available event templates and spawn some test events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--spawn',
            action='store_true',
            help='Actually spawn test events (default: just display templates)'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=3,
            help='Number of test events to spawn (default: 3)'
        )

    def handle(self, *args, **options):
        spawn = options['spawn']
        count = options['count']

        self.stdout.write(self.style.SUCCESS('=== Available Event Templates ===\n'))

        # Display all event templates
        for event_type, templates in EventSpawnerService.EVENT_TEMPLATES.items():
            self.stdout.write(self.style.WARNING(f'\n{event_type.upper()}:'))
            for template in templates:
                self.stdout.write(f"  {template['icon']} {template['name']}")
                self.stdout.write(f"     {template['description']}")
                self.stdout.write(f"     Duration: {template['duration_hours']}h")
                self.stdout.write(f"     Max participants: {template['max_participants']}")
                
                # Show rewards
                reward_str = []
                for key in template['rewards'].keys():
                    if key == 'gather_multiplier':
                        reward_str.append(f'{key}')
                    else:
                        reward_str.append(key)
                self.stdout.write(f"     Rewards: {', '.join(reward_str)}\n")

        # Count templates
        total_templates = sum(len(templates) for templates in EventSpawnerService.EVENT_TEMPLATES.values())
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {total_templates} event templates across {len(EventSpawnerService.EVENT_TEMPLATES)} types')
        )

        # Spawn test events if requested
        if spawn:
            self.stdout.write(self.style.WARNING(f'\n=== Spawning {count} Test Events ===\n'))
            events = EventSpawnerService.spawn_random_events(count=count)
            
            for event in events:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  [+] {event.icon} {event.name} at ({event.cell.grid_x}, {event.cell.grid_y})'
                    )
                )
            
            self.stdout.write(self.style.SUCCESS(f'\nSpawned {len(events)} test events!'))
        else:
            self.stdout.write(
                self.style.WARNING('\nTo spawn test events, run: python manage.py populate_events --spawn')
            )
