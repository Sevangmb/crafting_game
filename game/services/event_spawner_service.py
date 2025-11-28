"""
Event Spawner Service - Automatically generates dynamic events on the map
"""
from django.utils import timezone
from datetime import timedelta
import random
from game.models import DynamicEvent, MapCell, Material, Player
import logging

logger = logging.getLogger(__name__)


class EventSpawnerService:
    """Service for spawning dynamic events"""

    # Event templates
    EVENT_TEMPLATES = {
        'treasure': [
            {
                'name': 'Coffre au Trésor',
                'description': 'Un coffre mystérieux contenant des ressources précieuses!',
                'icon': '💎',
                'rewards': {
                    'money': lambda: random.randint(100, 500),
                    'items': lambda: [
                        {'material_id': random.choice([1, 2, 3, 4, 5]), 'quantity': random.randint(10, 30)}
                    ]
                },
                'duration_hours': 2,
                'max_participants': 1
            },
            {
                'name': 'Cache Secrète',
                'description': 'Quelqu\'un a caché des ressources ici!',
                'icon': '🎁',
                'rewards': {
                    'xp': lambda: random.randint(50, 200),
                    'money': lambda: random.randint(50, 200),
                },
                'duration_hours': 3,
                'max_participants': 3
            }
        ],
        'merchant': [
            {
                'name': 'Marchand Ambulant',
                'description': 'Un marchand mystérieux propose des échanges intéressants.',
                'icon': '🧙',
                'rewards': {
                    'money': lambda: random.randint(20, 100),
                },
                'duration_hours': 4,
                'max_participants': -1  # Unlimited
            }
        ],
        'resource': [
            {
                'name': 'Filon de Ressources',
                'description': 'Un filon riche en ressources! Récolte multipliée par 2!',
                'icon': '⛏️',
                'rewards': {
                    'gather_multiplier': lambda: 2.0
                },
                'duration_hours': 6,
                'max_participants': -1
            },
            {
                'name': 'Abondance Naturelle',
                'description': 'La nature est généreuse ici. Récolte multipliée par 1.5!',
                'icon': '🌿',
                'rewards': {
                    'gather_multiplier': lambda: 1.5
                },
                'duration_hours': 8,
                'max_participants': -1
            }
        ],
        'weather': [
            {
                'name': 'Pluie de Météores',
                'description': 'Des météores tombent! Récoltez des minerais rares!',
                'icon': '☄️',
                'rewards': {
                    'xp': lambda: random.randint(100, 300),
                    'items': lambda: [
                        {'material_id': random.choice([4, 5]), 'quantity': random.randint(5, 15)}
                    ]
                },
                'duration_hours': 1,
                'max_participants': 5
            }
        ]
    }

    @staticmethod
    def _process_rewards(template):
        """Process reward lambdas into actual values"""
        processed = {}
        for key, value in template['rewards'].items():
            processed[key] = value() if callable(value) else value
        return processed

    @staticmethod
    def _create_event(cell, event_type, template):
        """Create a DynamicEvent from template"""
        expires_at = timezone.now() + timedelta(hours=template['duration_hours'])
        return DynamicEvent.objects.create(
            name=template['name'],
            description=template['description'],
            icon=template['icon'],
            event_type=event_type,
            cell=cell,
            rewards=EventSpawnerService._process_rewards(template),
            expires_at=expires_at,
            max_participants=template['max_participants']
        )

    @staticmethod
    def spawn_random_events(count=5):
        """Spawn random events on the map"""
        spawned = []

        # Get random cells (prefer populated areas)
        cells = list(MapCell.objects.all().order_by('?')[:count * 3])

        if not cells:
            logger.warning("No map cells available for event spawning")
            return spawned

        for i in range(min(count, len(cells))):
            cell = cells[i]

            # Choose random event type and template
            event_type = random.choice(list(EventSpawnerService.EVENT_TEMPLATES.keys()))
            template = random.choice(EventSpawnerService.EVENT_TEMPLATES[event_type])

            # Create event using helper
            event = EventSpawnerService._create_event(cell, event_type, template)

            spawned.append(event)
            logger.info(f"Spawned event '{event.name}' at ({cell.grid_x}, {cell.grid_y})")

        return spawned

    @staticmethod
    def spawn_event_near_player(player, event_type=None, radius=5):
        """Spawn an event near a player"""
        # Find cells near player
        cells = MapCell.objects.filter(
            grid_x__gte=player.grid_x - radius,
            grid_x__lte=player.grid_x + radius,
            grid_y__gte=player.grid_y - radius,
            grid_y__lte=player.grid_y + radius
        ).exclude(
            grid_x=player.grid_x,
            grid_y=player.grid_y
        )

        if not cells.exists():
            return None

        cell = random.choice(list(cells))

        # Choose event type and template
        if not event_type:
            event_type = random.choice(list(EventSpawnerService.EVENT_TEMPLATES.keys()))

        template = random.choice(EventSpawnerService.EVENT_TEMPLATES[event_type])

        # Create event using helper
        event = EventSpawnerService._create_event(cell, event_type, template)

        logger.info(f"Spawned {event_type} event near player {player.user.username}")
        return event

    @staticmethod
    def cleanup_expired_events():
        """Remove expired events"""
        expired = DynamicEvent.objects.filter(
            expires_at__lt=timezone.now()
        )

        count = expired.count()
        expired.delete()

        if count > 0:
            logger.info(f"Cleaned up {count} expired events")

        return count

    @staticmethod
    def get_active_events():
        """Get all active events"""
        return DynamicEvent.objects.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).select_related('cell')

    @staticmethod
    def get_events_near_player(player, radius=10):
        """Get events near a player"""
        return DynamicEvent.objects.filter(
            is_active=True,
            expires_at__gt=timezone.now(),
            cell__grid_x__gte=player.grid_x - radius,
            cell__grid_x__lte=player.grid_x + radius,
            cell__grid_y__gte=player.grid_y - radius,
            cell__grid_y__lte=player.grid_y + radius
        ).select_related('cell')
