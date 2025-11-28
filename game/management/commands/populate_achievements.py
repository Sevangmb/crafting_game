"""
Populate initial achievements
"""
from django.core.management.base import BaseCommand
from game.models import Achievement


class Command(BaseCommand):
    help = 'Populate initial achievements'

    def handle(self, *args, **kwargs):
        achievements = [
            # Exploration Achievements
            {
                'name': 'Premier Pas',
                'description': 'Effectuez votre premier déplacement',
                'icon': '👣',
                'category': 'exploration',
                'requirement_type': 'move_count',
                'requirement_value': 1,
                'reward_xp': 10,
            },
            {
                'name': 'Explorateur',
                'description': 'Parcourez 100 cases',
                'icon': '🗺️',
                'category': 'exploration',
                'requirement_type': 'move_count',
                'requirement_value': 100,
                'reward_xp': 100,
            },
            {
                'name': 'Grand Voyageur',
                'description': 'Parcourez 1000 cases',
                'icon': '🌍',
                'category': 'exploration',
                'requirement_type': 'move_count',
                'requirement_value': 1000,
                'reward_xp': 500,
            },

            # Gathering Achievements
            {
                'name': 'Première Récolte',
                'description': 'Récoltez votre premier matériau',
                'icon': '🌾',
                'category': 'gathering',
                'requirement_type': 'gather_count',
                'requirement_value': 1,
                'reward_xp': 10,
            },
            {
                'name': 'Collecteur',
                'description': 'Récoltez 50 fois',
                'icon': '🧺',
                'category': 'gathering',
                'requirement_type': 'gather_count',
                'requirement_value': 50,
                'reward_xp': 50,
            },
            {
                'name': 'Maître Collecteur',
                'description': 'Récoltez 500 fois',
                'icon': '👑',
                'category': 'gathering',
                'requirement_type': 'gather_count',
                'requirement_value': 500,
                'reward_xp': 250,
            },

            # Crafting Achievements
            {
                'name': 'Premier Craft',
                'description': 'Craftez votre premier objet',
                'icon': '🔨',
                'category': 'crafting',
                'requirement_type': 'craft_count',
                'requirement_value': 1,
                'reward_xp': 10,
            },
            {
                'name': 'Artisan',
                'description': 'Craftez 25 objets',
                'icon': '⚒️',
                'category': 'crafting',
                'requirement_type': 'craft_count',
                'requirement_value': 25,
                'reward_xp': 50,
            },
            {
                'name': 'Maître Artisan',
                'description': 'Craftez 100 objets',
                'icon': '🏭',
                'category': 'crafting',
                'requirement_type': 'craft_count',
                'requirement_value': 100,
                'reward_xp': 200,
            },

            # Progression Achievements
            {
                'name': 'Niveau 5',
                'description': 'Atteignez le niveau 5',
                'icon': '⭐',
                'category': 'progression',
                'requirement_type': 'level_reached',
                'requirement_value': 5,
                'reward_xp': 50,
            },
            {
                'name': 'Niveau 10',
                'description': 'Atteignez le niveau 10',
                'icon': '⭐⭐',
                'category': 'progression',
                'requirement_type': 'level_reached',
                'requirement_value': 10,
                'reward_xp': 100,
            },
            {
                'name': 'Niveau 20',
                'description': 'Atteignez le niveau 20',
                'icon': '⭐⭐⭐',
                'category': 'progression',
                'requirement_type': 'level_reached',
                'requirement_value': 20,
                'reward_xp': 500,
            },

            # Collection Achievements
            {
                'name': 'Bûcheron',
                'description': 'Récoltez du Bois 10 fois',
                'icon': '🪓',
                'category': 'collection',
                'requirement_type': 'material_collected',
                'requirement_value': 10,
                'requirement_target': 'Bois',
                'reward_xp': 25,
            },
            {
                'name': 'Mineur',
                'description': 'Récoltez de la Pierre 10 fois',
                'icon': '⛏️',
                'category': 'collection',
                'requirement_type': 'material_collected',
                'requirement_value': 10,
                'requirement_target': 'Pierre',
                'reward_xp': 25,
            },
            {
                'name': 'Chercheur de Diamants',
                'description': 'Récoltez un Diamant',
                'icon': '💎',
                'category': 'collection',
                'requirement_type': 'material_collected',
                'requirement_value': 1,
                'requirement_target': 'Diamant',
                'reward_xp': 100,
                'hidden': True,
            },

            # Combat Achievements (for future)
            {
                'name': 'Premier Sang',
                'description': 'Battez votre premier monstre',
                'icon': '⚔️',
                'category': 'combat',
                'requirement_type': 'mob_defeated',
                'requirement_value': 1,
                'reward_xp': 20,
            },
            {
                'name': 'Chasseur',
                'description': 'Battez 10 monstres',
                'icon': '🏹',
                'category': 'combat',
                'requirement_type': 'mob_defeated',
                'requirement_value': 10,
                'reward_xp': 100,
            },
        ]

        created_count = 0
        for achievement_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )
            if created:
                created_count += 1
                # Use ASCII-safe output for Windows console
                try:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created achievement: {achievement.icon} {achievement.name}')
                    )
                except UnicodeEncodeError:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created achievement: {achievement.name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} achievements!')
        )
