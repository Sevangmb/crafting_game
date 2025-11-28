from django.core.management.base import BaseCommand
from game.models import BuildingType, BuildingRecipe, Material


class Command(BaseCommand):
    help = 'Populate initial building types and their recipes'

    def handle(self, *args, **options):
        self.stdout.write('Populating building types...')

        # Define building types with their recipes
        buildings_data = [
            {
                'name': 'Cabane en Bois',
                'description': 'Une petite cabane pour se reposer. Augmente la régénération d\'énergie.',
                'icon': '🏚️',
                'category': 'housing',
                'energy_regeneration_bonus': 5,
                'storage_bonus': 10,
                'defense_bonus': 0,
                'production_bonus': 0.0,
                'construction_time': 30,
                'required_level': 1,
                'materials': [
                    {'name': 'Bois', 'quantity': 20},
                    {'name': 'Pierre', 'quantity': 10},
                ]
            },
            {
                'name': 'Maison en Pierre',
                'description': 'Une maison solide en pierre. Offre plus d\'espace de stockage et meilleure défense.',
                'icon': '🏠',
                'category': 'housing',
                'energy_regeneration_bonus': 10,
                'storage_bonus': 25,
                'defense_bonus': 5,
                'production_bonus': 0.0,
                'construction_time': 120,
                'required_level': 5,
                'materials': [
                    {'name': 'Pierre', 'quantity': 50},
                    {'name': 'Bois', 'quantity': 30},
                    {'name': 'Minerai de Fer', 'quantity': 10},
                ]
            },
            {
                'name': 'Manoir',
                'description': 'Un grand manoir luxueux. Excellente régénération d\'énergie et stockage massif.',
                'icon': '🏰',
                'category': 'housing',
                'energy_regeneration_bonus': 20,
                'storage_bonus': 50,
                'defense_bonus': 10,
                'production_bonus': 0.05,
                'construction_time': 300,
                'required_level': 15,
                'materials': [
                    {'name': 'Pierre', 'quantity': 100},
                    {'name': 'Bois', 'quantity': 80},
                    {'name': 'Minerai de Fer', 'quantity': 50},
                    {'name': "Minerai d'Or", 'quantity': 20},
                ]
            },
            {
                'name': 'Atelier',
                'description': 'Un atelier de production. Améliore la vitesse de fabrication.',
                'icon': '🏭',
                'category': 'production',
                'energy_regeneration_bonus': 0,
                'storage_bonus': 20,
                'defense_bonus': 0,
                'production_bonus': 0.15,
                'construction_time': 90,
                'required_level': 8,
                'materials': [
                    {'name': 'Bois', 'quantity': 40},
                    {'name': 'Pierre', 'quantity': 30},
                    {'name': 'Minerai de Fer', 'quantity': 25},
                ]
            },
            {
                'name': 'Entrepôt',
                'description': 'Un grand entrepôt pour stocker plus de matériaux.',
                'icon': '🏢',
                'category': 'storage',
                'energy_regeneration_bonus': 0,
                'storage_bonus': 100,
                'defense_bonus': 2,
                'production_bonus': 0.0,
                'construction_time': 60,
                'required_level': 10,
                'materials': [
                    {'name': 'Bois', 'quantity': 60},
                    {'name': 'Pierre', 'quantity': 40},
                ]
            },
            {
                'name': 'Tour de Guet',
                'description': 'Une tour défensive pour protéger vos bâtiments.',
                'icon': '🗼',
                'category': 'defense',
                'energy_regeneration_bonus': 0,
                'storage_bonus': 0,
                'defense_bonus': 20,
                'production_bonus': 0.0,
                'construction_time': 180,
                'required_level': 12,
                'materials': [
                    {'name': 'Pierre', 'quantity': 80},
                    {'name': 'Minerai de Fer', 'quantity': 40},
                    {'name': 'Bois', 'quantity': 20},
                ]
            },
            {
                'name': 'Jardin',
                'description': 'Un beau jardin décoratif. Apporte un petit bonus de production.',
                'icon': '🌳',
                'category': 'decoration',
                'energy_regeneration_bonus': 2,
                'storage_bonus': 0,
                'defense_bonus': 0,
                'production_bonus': 0.05,
                'construction_time': 45,
                'required_level': 3,
                'materials': [
                    {'name': 'Bois', 'quantity': 15},
                    {'name': 'Pierre', 'quantity': 10},
                ]
            },
        ]

        for building_data in buildings_data:
            # Extract materials before creating building
            materials_data = building_data.pop('materials')

            # Create or update building type
            building_type, created = BuildingType.objects.update_or_create(
                name=building_data['name'],
                defaults=building_data
            )

            action = 'Created' if created else 'Updated'
            try:
                self.stdout.write(self.style.SUCCESS(f'{action} building type: {building_type.icon} {building_type.name}'))
            except UnicodeEncodeError:
                self.stdout.write(self.style.SUCCESS(f'{action} building type: {building_type.name}'))

            # Create building recipes
            for mat_data in materials_data:
                try:
                    material = Material.objects.get(name=mat_data['name'])
                    BuildingRecipe.objects.update_or_create(
                        building_type=building_type,
                        material=material,
                        defaults={'quantity': mat_data['quantity']}
                    )
                except Material.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'  Material not found: {mat_data["name"]}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully populated {len(buildings_data)} building types'))
