"""
Unit tests for building service

Tests building construction, completion, and bonuses.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from game.models import (
    Player, Building, BuildingType, BuildingRecipe,
    Material, Inventory, MapCell
)
from game.services.building_service import (
    get_available_building_types,
    check_can_build,
    calculate_player_bonuses
)
from game.exceptions import (
    InsufficientMaterialsError,
    InvalidActionError,
    NotFoundError
)


class AvailableBuildingTypesTests(TestCase):
    """Test getting available building types"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, level=1)

        # Create building types
        self.tent = BuildingType.objects.create(
            name='Tente',
            description='Abri simple',
            category='shelter',
            required_level=1,
            construction_time=60
        )

        self.house = BuildingType.objects.create(
            name='Maison',
            description='Maison en bois',
            category='shelter',
            required_level=5,
            construction_time=300
        )

        # Create materials
        self.wood = Material.objects.create(name='Bois', category='resource')
        self.stone = Material.objects.create(name='Pierre', category='resource')

        # Create recipes
        BuildingRecipe.objects.create(
            building_type=self.tent,
            material=self.wood,
            quantity=10
        )

    def test_get_available_types_filters_by_level(self):
        """Test only buildings at or below player level are shown"""
        available = get_available_building_types(self.player)

        # Player is level 1, should only see tent
        names = [bt['name'] for bt in available]
        self.assertIn('Tente', names)
        self.assertNotIn('Maison', names)

    def test_higher_level_sees_more_buildings(self):
        """Test higher level player sees more buildings"""
        self.player.level = 5
        self.player.save()

        available = get_available_building_types(self.player)

        names = [bt['name'] for bt in available]
        self.assertIn('Tente', names)
        self.assertIn('Maison', names)

    def test_available_types_include_materials(self):
        """Test available types include required materials"""
        available = get_available_building_types(self.player)

        tent_data = next(bt for bt in available if bt['name'] == 'Tente')
        self.assertIn('materials', tent_data)
        self.assertGreater(len(tent_data['materials']), 0)

        material = tent_data['materials'][0]
        self.assertEqual(material['material_name'], 'Bois')
        self.assertEqual(material['quantity'], 10)

    def test_available_types_include_bonuses(self):
        """Test available types include bonus information"""
        available = get_available_building_types(self.player)

        tent_data = next(bt for bt in available if bt['name'] == 'Tente')
        self.assertIn('energy_regeneration_bonus', tent_data)
        self.assertIn('storage_bonus', tent_data)
        self.assertIn('defense_bonus', tent_data)
        self.assertIn('production_bonus', tent_data)


class CheckCanBuildTests(TestCase):
    """Test building eligibility checks"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, level=5, grid_x=0, grid_y=0)

        self.cell = MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            center_lat=44.933,
            center_lon=4.893,
            biome='plains'
        )

        # Create building type
        self.shelter = BuildingType.objects.create(
            name='Abri',
            category='shelter',
            required_level=3,
            construction_time=120
        )

        # Create materials
        self.wood = Material.objects.create(name='Bois', category='resource')
        self.stone = Material.objects.create(name='Pierre', category='resource')

        # Create recipe
        BuildingRecipe.objects.create(
            building_type=self.shelter,
            material=self.wood,
            quantity=20
        )
        BuildingRecipe.objects.create(
            building_type=self.shelter,
            material=self.stone,
            quantity=10
        )

    def test_can_build_with_sufficient_materials(self):
        """Test can build when all requirements met"""
        # Add materials to inventory
        Inventory.objects.create(player=self.player, material=self.wood, quantity=30)
        Inventory.objects.create(player=self.player, material=self.stone, quantity=15)

        can_build, building_type, recipes = check_can_build(
            self.player,
            self.shelter.id,
            self.cell
        )

        self.assertTrue(can_build)
        self.assertEqual(building_type, self.shelter)
        self.assertGreater(len(list(recipes)), 0)

    def test_cannot_build_insufficient_materials(self):
        """Test cannot build without enough materials"""
        # Add insufficient materials
        Inventory.objects.create(player=self.player, material=self.wood, quantity=5)

        with self.assertRaises(InsufficientMaterialsError):
            check_can_build(self.player, self.shelter.id, self.cell)

    def test_cannot_build_below_required_level(self):
        """Test cannot build if below required level"""
        self.player.level = 1
        self.player.save()

        with self.assertRaises(InvalidActionError) as context:
            check_can_build(self.player, self.shelter.id, self.cell)

        self.assertIn('Niveau', str(context.exception))

    def test_cannot_build_if_building_exists(self):
        """Test cannot build if already have building on cell"""
        # Add materials
        Inventory.objects.create(player=self.player, material=self.wood, quantity=30)
        Inventory.objects.create(player=self.player, material=self.stone, quantity=15)

        # Create existing building
        Building.objects.create(
            player=self.player,
            cell=self.cell,
            building_type=self.shelter,
            status='completed'
        )

        with self.assertRaises(InvalidActionError) as context:
            check_can_build(self.player, self.shelter.id, self.cell)

        self.assertIn('déjà un bâtiment', str(context.exception))

    def test_cannot_build_invalid_building_type(self):
        """Test error for non-existent building type"""
        with self.assertRaises(NotFoundError):
            check_can_build(self.player, 99999, self.cell)


class CalculatePlayerBonusesTests(TestCase):
    """Test building bonus calculations"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, grid_x=0, grid_y=0)

        self.cell = MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            center_lat=44.933,
            center_lon=4.893,
            biome='plains'
        )

    def test_no_bonuses_without_buildings(self):
        """Test bonuses are zero without buildings"""
        bonuses = calculate_player_bonuses(self.player)

        self.assertEqual(bonuses.get('energy_regeneration', 0), 0)
        self.assertEqual(bonuses.get('storage', 0), 0)
        self.assertEqual(bonuses.get('defense', 0), 0)
        self.assertEqual(bonuses.get('production', 0), 0)

    def test_bonuses_from_completed_buildings(self):
        """Test bonuses accumulate from completed buildings"""
        # Create building type with bonuses
        shelter = BuildingType.objects.create(
            name='Shelter',
            category='shelter',
            energy_regeneration_bonus=2.0,
            storage_bonus=50,
            construction_time=60
        )

        # Create completed building
        Building.objects.create(
            player=self.player,
            cell=self.cell,
            building_type=shelter,
            status='completed',
            construction_completed_at=timezone.now()
        )

        bonuses = calculate_player_bonuses(self.player)

        self.assertEqual(bonuses['energy_regeneration'], 2.0)
        self.assertEqual(bonuses['storage'], 50)

    def test_under_construction_buildings_not_counted(self):
        """Test buildings under construction don't give bonuses"""
        shelter = BuildingType.objects.create(
            name='Shelter',
            category='shelter',
            energy_regeneration_bonus=2.0,
            construction_time=60
        )

        # Create building under construction
        Building.objects.create(
            player=self.player,
            cell=self.cell,
            building_type=shelter,
            status='under_construction',
            construction_started_at=timezone.now()
        )

        bonuses = calculate_player_bonuses(self.player)

        # Should not get bonuses from incomplete building
        self.assertEqual(bonuses.get('energy_regeneration', 0), 0)

    def test_multiple_buildings_stack_bonuses(self):
        """Test multiple buildings stack their bonuses"""
        shelter1 = BuildingType.objects.create(
            name='Shelter 1',
            category='shelter',
            energy_regeneration_bonus=2.0,
            construction_time=60
        )

        shelter2 = BuildingType.objects.create(
            name='Shelter 2',
            category='shelter',
            energy_regeneration_bonus=3.0,
            construction_time=60
        )

        cell2 = MapCell.objects.create(
            grid_x=1,
            grid_y=0,
            center_lat=44.934,
            center_lon=4.894,
            biome='plains'
        )

        # Create two completed buildings
        Building.objects.create(
            player=self.player,
            cell=self.cell,
            building_type=shelter1,
            status='completed',
            construction_completed_at=timezone.now()
        )

        Building.objects.create(
            player=self.player,
            cell=cell2,
            building_type=shelter2,
            status='completed',
            construction_completed_at=timezone.now()
        )

        bonuses = calculate_player_bonuses(self.player)

        # Bonuses should stack
        self.assertEqual(bonuses['energy_regeneration'], 5.0)
