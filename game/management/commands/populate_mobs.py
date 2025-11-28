# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from game.models import Mob, Material
import json

class Command(BaseCommand):
    help = 'Populate mobs'

    def handle(self, *args, **options):
        self.stdout.write('Populating mobs...')

        # Ensure loot materials exist
        viande, _ = Material.objects.get_or_create(name='Viande')
        cuir, _ = Material.objects.get_or_create(name='Cuir brut')
        os_mat, _ = Material.objects.get_or_create(name='Os', defaults={'description': 'Os d\'animal', 'icon': '🦴'})
        fourrure, _ = Material.objects.get_or_create(name='Fourrure', defaults={'description': 'Fourrure épaisse', 'icon': '🧥', 'rarity': 'uncommon'})
        
        # Plains
        Mob.objects.update_or_create(
            name='Lapin',
            defaults={
                'description': 'Un petit lapin rapide.',
                'icon': '🐇',
                'level': 1,
                'health': 10,
                'attack': 2,
                'defense': 0,
                'xp_reward': 5,
                'spawn_rate': 0.6,
                'aggression_level': 'passive',
                'biomes_json': json.dumps(['plains', 'forest', 'farmland']),
                'loot_table_json': json.dumps({
                    'Viande': {'min': 1, 'max': 2, 'chance': 1.0},
                    'Cuir brut': {'min': 1, 'max': 1, 'chance': 0.5}
                })
            }
        )

        Mob.objects.update_or_create(
            name='Poule',
            defaults={
                'description': 'Une poule sauvage.',
                'icon': '🐔',
                'level': 1,
                'health': 5,
                'attack': 1,
                'defense': 0,
                'xp_reward': 3,
                'spawn_rate': 0.7,
                'aggression_level': 'passive',
                'biomes_json': json.dumps(['plains', 'farmland']),
                'loot_table_json': json.dumps({
                    'Viande': {'min': 1, 'max': 2, 'chance': 1.0}
                })
            }
        )

        # Forest
        Mob.objects.update_or_create(
            name='Sanglier',
            defaults={
                'description': 'Un sanglier agressif.',
                'icon': '🐗',
                'level': 4,
                'health': 35,
                'attack': 8,
                'defense': 3,
                'xp_reward': 30,
                'spawn_rate': 0.3,
                'aggression_level': 'aggressive',
                'biomes_json': json.dumps(['forest']),
                'loot_table_json': json.dumps({
                    'Viande': {'min': 4, 'max': 6, 'chance': 1.0},
                    'Cuir brut': {'min': 2, 'max': 4, 'chance': 0.9},
                    'Os': {'min': 2, 'max': 3, 'chance': 0.8}
                })
            }
        )

        Mob.objects.update_or_create(
            name='Cerf',
            defaults={
                'description': 'Un cerf majestueux.',
                'icon': '🦌',
                'level': 3,
                'health': 25,
                'attack': 4,
                'defense': 2,
                'xp_reward': 20,
                'spawn_rate': 0.35,
                'aggression_level': 'neutral',
                'biomes_json': json.dumps(['forest', 'plains']),
                'loot_table_json': json.dumps({
                    'Viande': {'min': 3, 'max': 5, 'chance': 1.0},
                    'Cuir brut': {'min': 2, 'max': 3, 'chance': 1.0},
                    'Os': {'min': 1, 'max': 2, 'chance': 0.7}
                })
            }
        )

        Mob.objects.update_or_create(
            name='Loup',
            defaults={
                'description': 'Un prédateur dangereux.',
                'icon': '🐺',
                'level': 5,
                'health': 45,
                'attack': 10,
                'defense': 4,
                'xp_reward': 40,
                'spawn_rate': 0.25,
                'aggression_level': 'aggressive',
                'biomes_json': json.dumps(['forest', 'mountain']),
                'loot_table_json': json.dumps({
                    'Viande': {'min': 2, 'max': 4, 'chance': 1.0},
                    'Cuir brut': {'min': 3, 'max': 5, 'chance': 1.0},
                    'Os': {'min': 2, 'max': 4, 'chance': 0.9}
                })
            }
        )

        # Mountain
        Mob.objects.update_or_create(
            name='Ours',
            defaults={
                'description': 'Un ours massif et puissant.',
                'icon': '🐻',
                'level': 8,
                'health': 80,
                'attack': 15,
                'defense': 8,
                'xp_reward': 80,
                'spawn_rate': 0.15,
                'aggression_level': 'aggressive',
                'biomes_json': json.dumps(['mountain', 'forest']),
                'loot_table_json': json.dumps({
                    'Viande': {'min': 6, 'max': 10, 'chance': 1.0},
                    'Cuir brut': {'min': 5, 'max': 8, 'chance': 1.0},
                    'Os': {'min': 4, 'max': 6, 'chance': 1.0}
                })
            }
        )

        Mob.objects.update_or_create(
            name='Chèvre',
            defaults={
                'description': 'Une chèvre de montagne agile.',
                'icon': '🐐',
                'level': 2,
                'health': 15,
                'attack': 3,
                'defense': 1,
                'xp_reward': 10,
                'spawn_rate': 0.4,
                'aggression_level': 'neutral',
                'biomes_json': json.dumps(['mountain']),
                'loot_table_json': json.dumps({
                    'Viande': {'min': 2, 'max': 3, 'chance': 1.0},
                    'Cuir brut': {'min': 1, 'max': 2, 'chance': 0.6}
                })
            }
        )

        self.stdout.write(self.style.SUCCESS('Mobs populated successfully!'))
