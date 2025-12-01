"""
Unit tests for basic service validations

Tests that services are importable and basic functionality.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Player, Material, Inventory, MapCell


class ServiceImportTests(TestCase):
    """Test that all services can be imported"""

    def test_import_achievement_service(self):
        """Test achievement service imports"""
        from game.services import achievement_service
        self.assertIsNotNone(achievement_service)

    def test_import_crafting_service(self):
        """Test crafting service imports"""
        from game.services import crafting_service
        self.assertIsNotNone(crafting_service)

    def test_import_gathering_service(self):
        """Test gathering service imports"""
        from game.services import gathering_service
        self.assertIsNotNone(gathering_service)

    def test_import_inventory_service(self):
        """Test inventory service imports"""
        from game.services import inventory_service
        self.assertIsNotNone(inventory_service)

    def test_import_player_service(self):
        """Test player service imports"""
        from game.services import player_service
        self.assertIsNotNone(player_service)

    def test_import_skills_service(self):
        """Test skills service imports"""
        from game.services import skills_service
        self.assertIsNotNone(skills_service)

    def test_import_energy_service(self):
        """Test energy service imports"""
        from game.services import energy_service
        self.assertIsNotNone(energy_service)

    def test_import_building_service(self):
        """Test building service imports"""
        from game.services import building_service
        self.assertIsNotNone(building_service)

    def test_import_durability_service(self):
        """Test durability service imports"""
        from game.services import durability_service
        self.assertIsNotNone(durability_service)

    def test_import_health_service(self):
        """Test health service imports"""
        from game.services import health_service
        self.assertIsNotNone(health_service)

    def test_import_metabolism_service(self):
        """Test metabolism service imports"""
        from game.services import metabolism_service
        self.assertIsNotNone(metabolism_service)

    def test_import_quest_service(self):
        """Test quest service imports"""
        from game.services import quest_service
        self.assertIsNotNone(quest_service)

    def test_import_combat_service(self):
        """Test combat service imports"""
        from game.services import combat_service
        self.assertIsNotNone(combat_service)

    def test_import_encounter_service(self):
        """Test encounter service imports"""
        from game.services import encounter_service
        self.assertIsNotNone(encounter_service)

    def test_import_equipment_service(self):
        """Test equipment service imports"""
        from game.services import equipment_service
        self.assertIsNotNone(equipment_service)

    def test_import_map_service(self):
        """Test map service imports"""
        from game.services import map_service
        self.assertIsNotNone(map_service)

    def test_import_poi_service(self):
        """Test poi service imports"""
        from game.services import poi_service
        self.assertIsNotNone(poi_service)

    def test_import_time_service(self):
        """Test time service imports"""
        from game.services import time_service
        self.assertIsNotNone(time_service)


class PlayerBasicTests(TestCase):
    """Test basic player operations"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_player(self):
        """Test creating a player"""
        player = Player.objects.create(user=self.user)

        self.assertIsNotNone(player)
        self.assertEqual(player.user, self.user)

    def test_player_has_default_stats(self):
        """Test player has default stats"""
        player = Player.objects.create(user=self.user)

        self.assertGreaterEqual(player.health, 0)
        self.assertGreaterEqual(player.energy, 0)
        self.assertGreaterEqual(player.level, 1)

    def test_player_can_level_up(self):
        """Test player level can be incremented"""
        player = Player.objects.create(user=self.user, level=1)

        player.level += 1
        player.save()

        player.refresh_from_db()
        self.assertEqual(player.level, 2)


class MaterialBasicTests(TestCase):
    """Test basic material operations"""

    def test_create_material(self):
        """Test creating a material"""
        material = Material.objects.create(
            name='Test Material',
            category='resource'
        )

        self.assertIsNotNone(material)
        self.assertEqual(material.name, 'Test Material')

    def test_material_categories_exist(self):
        """Test different material categories"""
        categories = ['resource', 'tool', 'weapon', 'food', 'crafted']

        for category in categories:
            material = Material.objects.create(
                name=f'Test {category}',
                category=category
            )
            self.assertEqual(material.category, category)


class InventoryBasicTests(TestCase):
    """Test basic inventory operations"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)
        self.material = Material.objects.create(name='Wood', category='resource')

    def test_add_to_inventory(self):
        """Test adding items to inventory"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.material,
            quantity=10
        )

        self.assertEqual(inventory.quantity, 10)

    def test_update_inventory_quantity(self):
        """Test updating inventory quantity"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.material,
            quantity=10
        )

        inventory.quantity += 5
        inventory.save()

        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 15)

    def test_remove_from_inventory(self):
        """Test removing items from inventory"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.material,
            quantity=10
        )

        inventory.quantity -= 3
        inventory.save()

        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 7)
