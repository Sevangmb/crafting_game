"""
Script to populate the database with random enemies
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from game.models import RandomEnemy

def populate_enemies():
    """Create various types of random enemies"""

    enemies_data = [
        # Low-level enemies
        {
            'name': 'Vagabond Affamé',
            'description': 'Un vagabond désespéré cherchant de la nourriture',
            'icon': '🤷',
            'level': 1,
            'health': 25,
            'attack': 5,
            'defense': 0,
            'xp_reward': 10,
            'encounter_rate': 0.15,
            'aggression_level': 'defensive',
            'money_min': 2,
            'money_max': 10,
            'biomes': ['plains', 'forest', 'city'],
            'equipment': {
                'Couteau Rouillé': {'chance': 0.3, 'quantity': 1}
            },
            'inventory': {
                'Pain': {'chance': 0.5, 'min': 1, 'max': 2},
                'Eau Purifiée': {'chance': 0.3, 'min': 1, 'max': 1}
            },
            'min_level_required': 1,
            'time_of_day': 'any'
        },
        {
            'name': 'Pillard Solitaire',
            'description': 'Un pillard opportuniste à la recherche de cibles faciles',
            'icon': '🗡️',
            'level': 2,
            'health': 35,
            'attack': 8,
            'defense': 2,
            'xp_reward': 15,
            'encounter_rate': 0.12,
            'aggression_level': 'neutral',
            'money_min': 5,
            'money_max': 20,
            'biomes': ['plains', 'forest', 'city'],
            'equipment': {
                'Couteau': {'chance': 0.5, 'quantity': 1},
                'Jean': {'chance': 0.4, 'quantity': 1},
                'T-shirt Coton': {'chance': 0.6, 'quantity': 1}
            },
            'inventory': {
                'Bandage': {'chance': 0.3, 'min': 1, 'max': 2},
                'Viande Crue': {'chance': 0.4, 'min': 1, 'max': 3}
            },
            'min_level_required': 1,
            'time_of_day': 'any'
        },
        # Mid-level enemies
        {
            'name': 'Bandit Armé',
            'description': 'Un bandit bien équipé et dangereux',
            'icon': '🔫',
            'level': 4,
            'health': 50,
            'attack': 12,
            'defense': 5,
            'xp_reward': 25,
            'encounter_rate': 0.10,
            'aggression_level': 'aggressive',
            'money_min': 15,
            'money_max': 40,
            'biomes': ['plains', 'forest', 'mountain', 'city'],
            'equipment': {
                'Pistolet': {'chance': 0.3, 'quantity': 1},
                'Couteau de Chasse': {'chance': 0.6, 'quantity': 1},
                'Hoodie': {'chance': 0.5, 'quantity': 1},
                'Jean': {'chance': 0.7, 'quantity': 1},
                'Baskets': {'chance': 0.6, 'quantity': 1}
            },
            'inventory': {
                'Bandage': {'chance': 0.6, 'min': 2, 'max': 4},
                'Pain': {'chance': 0.5, 'min': 1, 'max': 3},
                'Eau Purifiée': {'chance': 0.5, 'min': 1, 'max': 2},
                'Stimulant': {'chance': 0.2, 'min': 1, 'max': 1}
            },
            'min_level_required': 3,
            'time_of_day': 'any'
        },
        {
            'name': 'Maraudeur',
            'description': 'Un survivant agressif qui attaque pour survivre',
            'icon': '⚔️',
            'level': 5,
            'health': 60,
            'attack': 15,
            'defense': 7,
            'xp_reward': 30,
            'encounter_rate': 0.08,
            'aggression_level': 'aggressive',
            'money_min': 20,
            'money_max': 50,
            'biomes': ['plains', 'forest', 'mountain', 'desert'],
            'equipment': {
                'Machete': {'chance': 0.4, 'quantity': 1},
                'Hache': {'chance': 0.3, 'quantity': 1},
                'Blouson Denim': {'chance': 0.4, 'quantity': 1},
                'Gants Laine': {'chance': 0.5, 'quantity': 1},
                'Chaussures Randonnee': {'chance': 0.3, 'quantity': 1}
            },
            'inventory': {
                'Bandage': {'chance': 0.7, 'min': 2, 'max': 5},
                'Viande Cuite': {'chance': 0.6, 'min': 1, 'max': 3},
                'Eau Purifiée': {'chance': 0.6, 'min': 1, 'max': 3},
                'Corde': {'chance': 0.4, 'min': 1, 'max': 2}
            },
            'min_level_required': 4,
            'time_of_day': 'any'
        },
        # High-level enemies
        {
            'name': 'Chef de Gang',
            'description': 'Un leader de gang dangereux et bien équipé',
            'icon': '👹',
            'level': 8,
            'health': 80,
            'attack': 20,
            'defense': 12,
            'xp_reward': 50,
            'encounter_rate': 0.05,
            'aggression_level': 'very_aggressive',
            'money_min': 40,
            'money_max': 100,
            'biomes': ['city', 'plains'],
            'equipment': {
                'Fusil d\'Assaut': {'chance': 0.25, 'quantity': 1},
                'Pistolet': {'chance': 0.5, 'quantity': 1},
                'Couteau de Combat': {'chance': 0.6, 'quantity': 1},
                'Parka': {'chance': 0.4, 'quantity': 1},
                'Gilet Pare-Balles Léger': {'chance': 0.3, 'quantity': 1},
                'Gants Tactiques': {'chance': 0.5, 'quantity': 1}
            },
            'inventory': {
                'Bandage': {'chance': 0.8, 'min': 3, 'max': 6},
                'Stimulant': {'chance': 0.5, 'min': 1, 'max': 2},
                'Anti-Radiation': {'chance': 0.3, 'min': 1, 'max': 1},
                'Viande Cuite': {'chance': 0.7, 'min': 2, 'max': 4},
                'Eau Purifiée': {'chance': 0.7, 'min': 2, 'max': 4}
            },
            'min_level_required': 6,
            'time_of_day': 'any'
        },
        {
            'name': 'Mercenaire',
            'description': 'Un mercenaire professionnel lourdement armé',
            'icon': '💀',
            'level': 10,
            'health': 100,
            'attack': 25,
            'defense': 15,
            'xp_reward': 75,
            'encounter_rate': 0.04,
            'aggression_level': 'aggressive',
            'money_min': 60,
            'money_max': 150,
            'biomes': ['city', 'mountain', 'plains'],
            'equipment': {
                'Fusil de Sniper': {'chance': 0.2, 'quantity': 1},
                'Fusil d\'Assaut': {'chance': 0.4, 'quantity': 1},
                'Pistolet': {'chance': 0.7, 'quantity': 1},
                'Gilet Pare-Balles Lourd': {'chance': 0.4, 'quantity': 1},
                'Casque Balistique': {'chance': 0.3, 'quantity': 1},
                'Gants Tactiques': {'chance': 0.6, 'quantity': 1},
                'Chaussures Securite S3': {'chance': 0.5, 'quantity': 1}
            },
            'inventory': {
                'Bandage': {'chance': 0.9, 'min': 4, 'max': 8},
                'Stimulant': {'chance': 0.7, 'min': 2, 'max': 3},
                'Anti-Radiation': {'chance': 0.5, 'min': 1, 'max': 2},
                'Viande Cuite': {'chance': 0.8, 'min': 3, 'max': 5},
                'Eau Purifiée': {'chance': 0.8, 'min': 3, 'max': 5},
                'Corde': {'chance': 0.5, 'min': 2, 'max': 3}
            },
            'min_level_required': 8,
            'time_of_day': 'any'
        },
        # Night-specific enemies
        {
            'name': 'Rôdeur Nocturne',
            'description': 'Un criminel qui opère sous le couvert de la nuit',
            'icon': '🌙',
            'level': 6,
            'health': 55,
            'attack': 18,
            'defense': 8,
            'xp_reward': 35,
            'encounter_rate': 0.12,
            'aggression_level': 'very_aggressive',
            'money_min': 25,
            'money_max': 60,
            'biomes': ['city', 'plains', 'forest'],
            'equipment': {
                'Couteau de Combat': {'chance': 0.6, 'quantity': 1},
                'Pistolet': {'chance': 0.4, 'quantity': 1},
                'Sweat à Capuche Discret': {'chance': 0.5, 'quantity': 1},
                'Jean': {'chance': 0.6, 'quantity': 1},
                'Gants Discrets': {'chance': 0.4, 'quantity': 1}
            },
            'inventory': {
                'Bandage': {'chance': 0.6, 'min': 2, 'max': 4},
                'Stimulant': {'chance': 0.3, 'min': 1, 'max': 1},
                'Pain': {'chance': 0.5, 'min': 1, 'max': 2},
                'Eau Purifiée': {'chance': 0.5, 'min': 1, 'max': 2}
            },
            'min_level_required': 5,
            'time_of_day': 'night'
        },
        # Passive/Defensive enemies
        {
            'name': 'Survivant Méfiant',
            'description': 'Un survivant qui se défend uniquement si provoqué',
            'icon': '😰',
            'level': 3,
            'health': 40,
            'attack': 10,
            'defense': 3,
            'xp_reward': 20,
            'encounter_rate': 0.08,
            'aggression_level': 'passive',
            'money_min': 10,
            'money_max': 30,
            'biomes': ['plains', 'forest', 'city'],
            'equipment': {
                'Bâton': {'chance': 0.7, 'quantity': 1},
                'T-shirt Coton': {'chance': 0.8, 'quantity': 1},
                'Jean': {'chance': 0.7, 'quantity': 1}
            },
            'inventory': {
                'Bandage': {'chance': 0.8, 'min': 3, 'max': 5},
                'Pain': {'chance': 0.9, 'min': 2, 'max': 4},
                'Eau Purifiée': {'chance': 0.9, 'min': 2, 'max': 4},
                'Baie': {'chance': 0.6, 'min': 1, 'max': 3}
            },
            'min_level_required': 1,
            'time_of_day': 'any'
        }
    ]

    created_count = 0
    updated_count = 0

    for enemy_data in enemies_data:
        # Extract lists for JSON fields
        biomes = enemy_data.pop('biomes')
        equipment = enemy_data.pop('equipment')
        inventory = enemy_data.pop('inventory')

        # Create or update enemy
        enemy, created = RandomEnemy.objects.update_or_create(
            name=enemy_data['name'],
            defaults={
                **enemy_data,
                'biomes_json': json.dumps(biomes),
                'equipment_json': json.dumps(equipment),
                'inventory_json': json.dumps(inventory)
            }
        )

        if created:
            created_count += 1
            print(f"✅ Created enemy: {enemy.name} (Level {enemy.level})")
        else:
            updated_count += 1
            print(f"🔄 Updated enemy: {enemy.name} (Level {enemy.level})")

    print(f"\n📊 Summary:")
    print(f"   - Created: {created_count} enemies")
    print(f"   - Updated: {updated_count} enemies")
    print(f"   - Total: {created_count + updated_count} enemies in database")

if __name__ == '__main__':
    # Fix encoding for Windows console
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("🎮 Populating database with random enemies...")
    print("=" * 50)
    populate_enemies()
    print("=" * 50)
    print("✅ Done!")
