"""
Management command to populate the database with realistic food and drinks
"""
from django.core.management.base import BaseCommand
from game.models import Material


class Command(BaseCommand):
    help = 'Populate database with realistic food and drink items'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating realistic food and drink items...'))

        # Food items with realistic nutritional values
        foods = [
            # === FRUITS (Hydratation + Faim légère) ===
            {
                'name': 'Pomme',
                'description': 'Une pomme fraîche et juteuse. Bonne source d\'hydratation.',
                'category': 'nourriture',
                'icon': '🍎',
                'is_food': True,
                'hunger_restore': 15,
                'thirst_restore': 20,
                'energy_restore': 5,
                'health_restore': 0,
                'radiation_change': 0,
                'weight': 0.2,
                'rarity': 'common'
            },
            {
                'name': 'Orange',
                'description': 'Une orange juteuse riche en vitamine C.',
                'category': 'nourriture',
                'icon': '🍊',
                'is_food': True,
                'hunger_restore': 12,
                'thirst_restore': 25,
                'energy_restore': 8,
                'health_restore': 2,
                'radiation_change': 0,
                'weight': 0.25,
                'rarity': 'common'
            },
            {
                'name': 'Pastèque',
                'description': 'Tranche de pastèque très hydratante.',
                'category': 'nourriture',
                'icon': '🍉',
                'is_food': True,
                'hunger_restore': 10,
                'thirst_restore': 40,
                'energy_restore': 5,
                'health_restore': 0,
                'radiation_change': 0,
                'weight': 0.5,
                'rarity': 'uncommon'
            },
            {
                'name': 'Baies',
                'description': 'Poignée de baies sauvages.',
                'category': 'nourriture',
                'icon': '🫐',
                'is_food': True,
                'hunger_restore': 8,
                'thirst_restore': 10,
                'energy_restore': 10,
                'health_restore': 1,
                'radiation_change': 0,
                'weight': 0.1,
                'rarity': 'common'
            },

            # === VIANDES (Beaucoup de faim, peu d'hydratation) ===
            {
                'name': 'Viande crue',
                'description': 'Viande crue, mieux vaut la cuire.',
                'category': 'nourriture',
                'icon': '🥩',
                'is_food': True,
                'hunger_restore': 15,
                'thirst_restore': 0,
                'energy_restore': 5,
                'health_restore': -5,
                'radiation_change': 0,
                'weight': 0.5,
                'rarity': 'common'
            },
            {
                'name': 'Viande cuite',
                'description': 'Viande bien cuite, nourrissante et sûre.',
                'category': 'nourriture',
                'icon': '🍖',
                'is_food': True,
                'hunger_restore': 35,
                'thirst_restore': 0,
                'energy_restore': 15,
                'health_restore': 5,
                'radiation_change': 0,
                'weight': 0.5,
                'rarity': 'common'
            },
            {
                'name': 'Poisson cuit',
                'description': 'Poisson grillé, léger et nutritif.',
                'category': 'nourriture',
                'icon': '🐟',
                'is_food': True,
                'hunger_restore': 30,
                'thirst_restore': 5,
                'energy_restore': 12,
                'health_restore': 3,
                'radiation_change': 0,
                'weight': 0.4,
                'rarity': 'uncommon'
            },
            {
                'name': 'Poulet rôti',
                'description': 'Poulet rôti parfaitement cuit.',
                'category': 'nourriture',
                'icon': '🍗',
                'is_food': True,
                'hunger_restore': 40,
                'thirst_restore': 0,
                'energy_restore': 20,
                'health_restore': 5,
                'radiation_change': 0,
                'weight': 0.6,
                'rarity': 'uncommon'
            },

            # === LÉGUMES ===
            {
                'name': 'Carotte',
                'description': 'Carotte croquante et saine.',
                'category': 'nourriture',
                'icon': '🥕',
                'is_food': True,
                'hunger_restore': 10,
                'thirst_restore': 15,
                'energy_restore': 5,
                'health_restore': 2,
                'radiation_change': 0,
                'weight': 0.15,
                'rarity': 'common'
            },
            {
                'name': 'Champignon',
                'description': 'Champignon comestible trouvé en forêt.',
                'category': 'nourriture',
                'icon': '🍄',
                'is_food': True,
                'hunger_restore': 12,
                'thirst_restore': 8,
                'energy_restore': 8,
                'health_restore': 0,
                'radiation_change': -2,
                'weight': 0.1,
                'rarity': 'uncommon'
            },

            # === REPAS CUISINÉS (Bonus de satiété) ===
            {
                'name': 'Soupe',
                'description': 'Soupe chaude et réconfortante. Très hydratante.',
                'category': 'nourriture',
                'icon': '🍲',
                'is_food': True,
                'hunger_restore': 30,
                'thirst_restore': 35,
                'energy_restore': 15,
                'health_restore': 8,
                'radiation_change': 0,
                'weight': 0.5,
                'rarity': 'uncommon'
            },
            {
                'name': 'Ragoût',
                'description': 'Ragoût copieux avec viande et légumes.',
                'category': 'nourriture',
                'icon': '🥘',
                'is_food': True,
                'hunger_restore': 45,
                'thirst_restore': 20,
                'energy_restore': 25,
                'health_restore': 10,
                'radiation_change': 0,
                'weight': 0.7,
                'rarity': 'rare'
            },
            {
                'name': 'Pain',
                'description': 'Pain frais, nourrissant.',
                'category': 'nourriture',
                'icon': '🍞',
                'is_food': True,
                'hunger_restore': 25,
                'thirst_restore': 0,
                'energy_restore': 12,
                'health_restore': 0,
                'radiation_change': 0,
                'weight': 0.3,
                'rarity': 'common'
            },
            {
                'name': 'Sandwich',
                'description': 'Sandwich bien garni.',
                'category': 'nourriture',
                'icon': '🥪',
                'is_food': True,
                'hunger_restore': 35,
                'thirst_restore': 5,
                'energy_restore': 20,
                'health_restore': 5,
                'radiation_change': 0,
                'weight': 0.4,
                'rarity': 'uncommon'
            },
            {
                'name': 'Pizza',
                'description': 'Part de pizza. Très calorique.',
                'category': 'nourriture',
                'icon': '🍕',
                'is_food': True,
                'hunger_restore': 40,
                'thirst_restore': 0,
                'energy_restore': 25,
                'health_restore': 3,
                'radiation_change': 0,
                'weight': 0.5,
                'rarity': 'rare'
            },

            # === SNACKS ===
            {
                'name': 'Noix',
                'description': 'Poignée de noix, riche en énergie.',
                'category': 'nourriture',
                'icon': '🥜',
                'is_food': True,
                'hunger_restore': 15,
                'thirst_restore': -5,
                'energy_restore': 20,
                'health_restore': 2,
                'radiation_change': 0,
                'weight': 0.1,
                'rarity': 'common'
            },
            {
                'name': 'Barre énergétique',
                'description': 'Barre compacte, parfaite pour l\'aventure.',
                'category': 'nourriture',
                'icon': '🍫',
                'is_food': True,
                'hunger_restore': 20,
                'thirst_restore': -10,
                'energy_restore': 30,
                'health_restore': 0,
                'radiation_change': 0,
                'weight': 0.1,
                'rarity': 'uncommon'
            },

            # === BOISSONS (Hydratation principalement) ===
            {
                'name': 'Eau',
                'description': 'Eau fraîche et pure. Essentielle à la survie.',
                'category': 'nourriture',
                'icon': '💧',
                'is_food': True,
                'hunger_restore': 0,
                'thirst_restore': 50,
                'energy_restore': 0,
                'health_restore': 0,
                'radiation_change': 0,
                'weight': 0.5,
                'rarity': 'common'
            },
            {
                'name': 'Eau purifiée',
                'description': 'Eau purifiée, élimine la radiation.',
                'category': 'nourriture',
                'icon': '💦',
                'is_food': True,
                'hunger_restore': 0,
                'thirst_restore': 60,
                'energy_restore': 5,
                'health_restore': 5,
                'radiation_change': -10,
                'weight': 0.5,
                'rarity': 'uncommon'
            },
            {
                'name': 'Jus de fruit',
                'description': 'Jus de fruit naturel, sucré et désaltérant.',
                'category': 'nourriture',
                'icon': '🧃',
                'is_food': True,
                'hunger_restore': 10,
                'thirst_restore': 40,
                'energy_restore': 15,
                'health_restore': 3,
                'radiation_change': 0,
                'weight': 0.4,
                'rarity': 'uncommon'
            },
            {
                'name': 'Lait',
                'description': 'Lait frais, nutritif.',
                'category': 'nourriture',
                'icon': '🥛',
                'is_food': True,
                'hunger_restore': 15,
                'thirst_restore': 35,
                'energy_restore': 10,
                'health_restore': 5,
                'radiation_change': -5,
                'weight': 0.5,
                'rarity': 'uncommon'
            },
            {
                'name': 'Café',
                'description': 'Café chaud. Boost d\'énergie temporaire.',
                'category': 'nourriture',
                'icon': '☕',
                'is_food': True,
                'hunger_restore': 0,
                'thirst_restore': 20,
                'energy_restore': 40,
                'health_restore': 0,
                'radiation_change': 0,
                'weight': 0.3,
                'rarity': 'common'
            },
            {
                'name': 'Boisson énergétique',
                'description': 'Boisson énergétique puissante.',
                'category': 'nourriture',
                'icon': '🥤',
                'is_food': True,
                'hunger_restore': 5,
                'thirst_restore': 30,
                'energy_restore': 50,
                'health_restore': 0,
                'radiation_change': 0,
                'weight': 0.3,
                'rarity': 'rare'
            },

            # === ITEMS MÉDICAUX ===
            {
                'name': 'Herbes médicinales',
                'description': 'Herbes qui soignent les blessures.',
                'category': 'nourriture',
                'icon': '🌿',
                'is_food': True,
                'hunger_restore': 0,
                'thirst_restore': 0,
                'energy_restore': 0,
                'health_restore': 15,
                'radiation_change': -5,
                'weight': 0.1,
                'rarity': 'uncommon'
            },
            {
                'name': 'Potion de soin',
                'description': 'Potion magique qui restaure la santé.',
                'category': 'magie',
                'icon': '🧪',
                'is_food': True,
                'hunger_restore': 0,
                'thirst_restore': 10,
                'energy_restore': 10,
                'health_restore': 30,
                'radiation_change': -15,
                'weight': 0.2,
                'rarity': 'rare'
            },
            {
                'name': 'Anti-radiation',
                'description': 'Pilule anti-radiation puissante.',
                'category': 'divers',
                'icon': '💊',
                'is_food': True,
                'hunger_restore': 0,
                'thirst_restore': 0,
                'energy_restore': 0,
                'health_restore': 10,
                'radiation_change': -30,
                'weight': 0.05,
                'rarity': 'epic'
            },

            # === ITEMS DANGEREUX (Radiation) ===
            {
                'name': 'Eau contaminée',
                'description': 'Eau contaminée. Désaltère mais irradie.',
                'category': 'nourriture',
                'icon': '☢️',
                'is_food': True,
                'hunger_restore': 0,
                'thirst_restore': 40,
                'energy_restore': 0,
                'health_restore': -10,
                'radiation_change': 15,
                'weight': 0.5,
                'rarity': 'common'
            },
            {
                'name': 'Champignon toxique',
                'description': 'Champignon vénéneux. À éviter.',
                'category': 'nourriture',
                'icon': '🍄‍🟫',
                'is_food': True,
                'hunger_restore': 5,
                'thirst_restore': 0,
                'energy_restore': 0,
                'health_restore': -20,
                'radiation_change': 10,
                'weight': 0.1,
                'rarity': 'common'
            },
        ]

        created = 0
        updated = 0

        for food_data in foods:
            material, created_flag = Material.objects.update_or_create(
                name=food_data['name'],
                defaults=food_data
            )
            if created_flag:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'  + Created: {material.name}'))
            else:
                updated += 1
                self.stdout.write(self.style.WARNING(f'  * Updated: {material.name}'))

        self.stdout.write(self.style.SUCCESS(f'\nFood population complete!'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {created} items'))
        self.stdout.write(self.style.SUCCESS(f'   Updated: {updated} items'))
        self.stdout.write(self.style.SUCCESS(f'   Total: {created + updated} food/drink items'))
