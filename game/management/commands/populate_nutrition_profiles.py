"""
Management command to populate nutritional profiles for existing foods
Based on real-world nutritional data
"""
from django.core.management.base import BaseCommand
from game.models import Material, NutritionalProfile


class Command(BaseCommand):
    help = 'Populate nutritional profiles for food items with realistic values'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating nutritional profiles for foods...'))

        # Realistic nutritional data per 100g
        nutrition_data = {
            # FRUITS
            'Pomme': {
                'proteins': 0.3, 'carbohydrates': 14, 'fats': 0.2, 'fiber': 2.4, 'water': 86,
                'calories': 52,
                'vitamin_a': 0.003, 'vitamin_c': 4.6, 'potassium': 107,
                'digestion_time': 30, 'is_perishable': True
            },
            'Orange': {
                'proteins': 0.9, 'carbohydrates': 12, 'fats': 0.1, 'fiber': 2.4, 'water': 87,
                'calories': 47,
                'vitamin_a': 0.011, 'vitamin_c': 53, 'calcium': 40, 'potassium': 181,
                'digestion_time': 30, 'is_perishable': True
            },
            'Pastèque': {
                'proteins': 0.6, 'carbohydrates': 8, 'fats': 0.2, 'fiber': 0.4, 'water': 92,
                'calories': 30,
                'vitamin_a': 0.028, 'vitamin_c': 8, 'potassium': 112,
                'digestion_time': 20, 'is_perishable': True
            },
            'Baies': {
                'proteins': 1.4, 'carbohydrates': 14, 'fats': 0.5, 'fiber': 2.4, 'water': 85,
                'calories': 57,
                'vitamin_c': 10, 'vitamin_k': 0.019,
                'digestion_time': 25, 'is_perishable': True
            },

            # VIANDES
            'Viande crue': {
                'proteins': 20, 'carbohydrates': 0, 'fats': 15, 'fiber': 0, 'water': 65,
                'calories': 250,
                'vitamin_b12': 0.002, 'iron': 2.6, 'zinc': 4.5,
                'digestion_time': 180, 'is_toxic': True, 'toxicity_level': 20,
                'is_perishable': True, 'freshness_decay_rate': 2.0
            },
            'Viande cuite': {
                'proteins': 26, 'carbohydrates': 0, 'fats': 15, 'fiber': 0, 'water': 60,
                'calories': 250,
                'vitamin_b3': 5.5, 'vitamin_b6': 0.5, 'vitamin_b12': 0.002,
                'iron': 2.6, 'zinc': 5.8, 'phosphorus': 200,
                'digestion_time': 240, 'is_perishable': True
            },
            'Poisson cuit': {
                'proteins': 22, 'carbohydrates': 0, 'fats': 12, 'fiber': 0, 'water': 65,
                'calories': 206,
                'vitamin_d': 0.011, 'vitamin_b12': 0.003, 'vitamin_b6': 0.4,
                'calcium': 15, 'iron': 0.8, 'magnesium': 29,
                'digestion_time': 120, 'is_perishable': True
            },
            'Poulet rôti': {
                'proteins': 27, 'carbohydrates': 0, 'fats': 14, 'fiber': 0, 'water': 59,
                'calories': 239,
                'vitamin_b3': 10, 'vitamin_b6': 0.6, 'vitamin_b12': 0.0003,
                'phosphorus': 200, 'zinc': 2,
                'digestion_time': 180, 'is_perishable': True
            },

            # LÉGUMES
            'Carotte': {
                'proteins': 0.9, 'carbohydrates': 10, 'fats': 0.2, 'fiber': 2.8, 'water': 88,
                'calories': 41,
                'vitamin_a': 0.835, 'vitamin_c': 6, 'vitamin_k': 0.013, 'potassium': 320,
                'digestion_time': 60, 'is_perishable': True
            },
            'Champignon': {
                'proteins': 3, 'carbohydrates': 3, 'fats': 0.3, 'fiber': 1, 'water': 92,
                'calories': 22,
                'vitamin_d': 0.002, 'vitamin_b2': 0.4, 'vitamin_b3': 3.6, 'potassium': 318,
                'digestion_time': 90, 'is_perishable': True
            },

            # REPAS CUISINÉS
            'Soupe': {
                'proteins': 3, 'carbohydrates': 8, 'fats': 2, 'fiber': 1.5, 'water': 85,
                'calories': 65,
                'vitamin_a': 0.05, 'vitamin_c': 5, 'sodium': 400,
                'digestion_time': 90, 'is_perishable': True
            },
            'Ragoût': {
                'proteins': 15, 'carbohydrates': 12, 'fats': 8, 'fiber': 2, 'water': 65,
                'calories': 180,
                'vitamin_a': 0.1, 'vitamin_b12': 0.001, 'iron': 3,
                'digestion_time': 150, 'is_perishable': True
            },
            'Pain': {
                'proteins': 9, 'carbohydrates': 49, 'fats': 3.2, 'fiber': 2.7, 'water': 36,
                'calories': 265,
                'vitamin_b1': 0.5, 'vitamin_b3': 4.7, 'iron': 3.6,
                'magnesium': 25,
                'digestion_time': 180, 'is_perishable': True, 'freshness_decay_rate': 0.5
            },
            'Sandwich': {
                'proteins': 12, 'carbohydrates': 35, 'fats': 8, 'fiber': 3, 'water': 45,
                'calories': 250,
                'vitamin_c': 3, 'calcium': 80, 'iron': 2,
                'digestion_time': 150, 'is_perishable': True
            },
            'Pizza': {
                'proteins': 11, 'carbohydrates': 33, 'fats': 10, 'fiber': 2, 'water': 45,
                'calories': 266,
                'calcium': 200, 'vitamin_a': 0.05, 'sodium': 600,
                'digestion_time': 180, 'is_perishable': True
            },

            # SNACKS
            'Noix': {
                'proteins': 20, 'carbohydrates': 21, 'fats': 54, 'fiber': 7, 'water': 5,
                'calories': 607,
                'vitamin_e': 7.4, 'magnesium': 168, 'zinc': 3,
                'digestion_time': 180, 'is_perishable': False
            },
            'Barre énergétique': {
                'proteins': 10, 'carbohydrates': 60, 'fats': 8, 'fiber': 4, 'water': 18,
                'calories': 400,
                'vitamin_b6': 0.7, 'iron': 4, 'magnesium': 50,
                'digestion_time': 120, 'is_perishable': False
            },

            # BOISSONS
            'Eau': {
                'proteins': 0, 'carbohydrates': 0, 'fats': 0, 'fiber': 0, 'water': 100,
                'calories': 0,
                'digestion_time': 5, 'absorption_rate': 1.0, 'is_perishable': False
            },
            'Eau purifiée': {
                'proteins': 0, 'carbohydrates': 0, 'fats': 0, 'fiber': 0, 'water': 100,
                'calories': 0,
                'sodium': 5, 'potassium': 5,  # Added minerals
                'digestion_time': 5, 'absorption_rate': 1.0, 'is_perishable': False
            },
            'Jus de fruit': {
                'proteins': 0.7, 'carbohydrates': 11, 'fats': 0.2, 'fiber': 0.2, 'water': 88,
                'calories': 45,
                'vitamin_c': 50, 'potassium': 200,
                'digestion_time': 30, 'is_perishable': True
            },
            'Lait': {
                'proteins': 3.4, 'carbohydrates': 5, 'fats': 3.6, 'fiber': 0, 'water': 88,
                'calories': 61,
                'vitamin_d': 0.001, 'vitamin_b12': 0.00045, 'calcium': 113,
                'phosphorus': 84,
                'digestion_time': 90, 'is_perishable': True, 'freshness_decay_rate': 1.5
            },
            'Café': {
                'proteins': 0.3, 'carbohydrates': 0, 'fats': 0, 'fiber': 0, 'water': 99,
                'calories': 2,
                'vitamin_b2': 0.01, 'magnesium': 8,
                'digestion_time': 30, 'is_perishable': False
            },
            'Boisson énergétique': {
                'proteins': 0, 'carbohydrates': 11, 'fats': 0, 'fiber': 0, 'water': 89,
                'calories': 45,
                'vitamin_b3': 8, 'vitamin_b6': 2, 'sodium': 100,
                'digestion_time': 20, 'is_perishable': False
            },

            # ITEMS MÉDICAUX
            'Herbes médicinales': {
                'proteins': 2, 'carbohydrates': 5, 'fats': 0.5, 'fiber': 3, 'water': 85,
                'calories': 30,
                'vitamin_c': 20, 'vitamin_k': 0.1, 'iron': 2,
                'digestion_time': 60, 'is_perishable': True
            },
            'Potion de soin': {
                'proteins': 0, 'carbohydrates': 15, 'fats': 0, 'fiber': 0, 'water': 85,
                'calories': 60,
                'vitamin_c': 100, 'vitamin_e': 15,  # High vitamins
                'digestion_time': 15, 'absorption_rate': 0.95,
                'is_perishable': False
            },
            'Anti-radiation': {
                'proteins': 0, 'carbohydrates': 5, 'fats': 0, 'fiber': 0, 'water': 95,
                'calories': 20,
                'vitamin_e': 50, 'zinc': 10,  # Antioxidants
                'digestion_time': 10, 'absorption_rate': 0.98,
                'is_perishable': False
            },

            # ITEMS DANGEREUX
            'Eau contaminée': {
                'proteins': 0, 'carbohydrates': 0, 'fats': 0, 'fiber': 0, 'water': 100,
                'calories': 0,
                'digestion_time': 5, 'is_toxic': True, 'toxicity_level': 40,
                'is_perishable': False
            },
            'Champignon toxique': {
                'proteins': 3, 'carbohydrates': 3, 'fats': 0.3, 'fiber': 1, 'water': 92,
                'calories': 22,
                'digestion_time': 90, 'is_toxic': True, 'toxicity_level': 60,
                'is_perishable': True
            },
        }

        created = 0
        updated = 0
        skipped = 0

        for food_name, nutrition_values in nutrition_data.items():
            try:
                material = Material.objects.get(name=food_name)

                # Create or update nutritional profile
                profile, created_flag = NutritionalProfile.objects.update_or_create(
                    material=material,
                    defaults=nutrition_values
                )

                if created_flag:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f'  + Created profile: {food_name}'))
                else:
                    updated += 1
                    self.stdout.write(self.style.WARNING(f'  * Updated profile: {food_name}'))

            except Material.DoesNotExist:
                skipped += 1
                self.stdout.write(self.style.ERROR(f'  ! Skipped (material not found): {food_name}'))

        self.stdout.write(self.style.SUCCESS(f'\nNutritional profiles population complete!'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {created} profiles'))
        self.stdout.write(self.style.SUCCESS(f'   Updated: {updated} profiles'))
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'   Skipped: {skipped} items'))
        self.stdout.write(self.style.SUCCESS(f'   Total: {created + updated} food items with nutrition data'))
