"""
Unit tests for durability service

Tests item durability, tool efficiency, and item breakage.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch
from game.models import Player, Material, Inventory, EquippedItem
from game.services.durability_service import DurabilityService
from game.exceptions import GameException


class DurabilityInitializationTests(TestCase):
    """Test durability initialization"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

    def test_initialize_durable_item(self):
        """Test initialize durability for tools"""
        pickaxe = Material.objects.create(
            name='Pioche',
            category='tool',
            max_durability=100
        )

        inventory = Inventory.objects.create(
            player=self.player,
            material=pickaxe,
            quantity=1
        )

        DurabilityService.initialize_durability(inventory, pickaxe)

        self.assertEqual(inventory.durability_max, 100)
        self.assertEqual(inventory.durability_current, 100)

    def test_initialize_non_durable_item(self):
        """Test initialize durability for non-durable items"""
        wood = Material.objects.create(
            name='Bois',
            category='resource',
            max_durability=0
        )

        inventory = Inventory.objects.create(
            player=self.player,
            material=wood,
            quantity=10
        )

        DurabilityService.initialize_durability(inventory, wood)

        self.assertEqual(inventory.durability_max, 0)
        self.assertEqual(inventory.durability_current, 0)


class DurabilityConsumptionTests(TestCase):
    """Test durability consumption"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

        self.pickaxe = Material.objects.create(
            name='Pioche',
            category='tool',
            max_durability=100
        )

        self.inventory = Inventory.objects.create(
            player=self.player,
            material=self.pickaxe,
            quantity=1,
            durability_max=100,
            durability_current=100
        )

    def test_consume_durability_normal(self):
        """Test normal durability consumption"""
        broke, remaining = DurabilityService.consume_durability(self.inventory, amount=10)

        self.assertFalse(broke)
        self.assertEqual(remaining, 90)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.durability_current, 90)

    def test_consume_durability_until_break(self):
        """Test tool breaks when durability reaches 0"""
        self.inventory.durability_current = 5
        self.inventory.save()

        broke, remaining = DurabilityService.consume_durability(self.inventory, amount=10)

        self.assertTrue(broke)
        # Item should be deleted
        self.assertFalse(Inventory.objects.filter(id=self.inventory.id).exists())

    def test_consume_durability_with_multiple_items(self):
        """Test when player has multiple of same tool"""
        self.inventory.quantity = 3
        self.inventory.durability_current = 5
        self.inventory.save()

        broke, remaining = DurabilityService.consume_durability(self.inventory, amount=10)

        self.assertTrue(broke)
        self.inventory.refresh_from_db()

        # Should reduce quantity and reset durability for next item
        self.assertEqual(self.inventory.quantity, 2)
        self.assertEqual(self.inventory.durability_current, 100)

    def test_consume_durability_infinite(self):
        """Test infinite durability items don't degrade"""
        wood = Material.objects.create(name='Bois', category='resource', max_durability=0)
        inventory = Inventory.objects.create(
            player=self.player,
            material=wood,
            quantity=10,
            durability_max=0,
            durability_current=0
        )

        broke, remaining = DurabilityService.consume_durability(inventory, amount=5)

        self.assertFalse(broke)
        self.assertEqual(remaining, 0)

    def test_cannot_use_broken_tool(self):
        """Test cannot consume durability from already broken tool"""
        self.inventory.durability_current = 0
        self.inventory.save()

        with self.assertRaises(GameException) as context:
            DurabilityService.consume_durability(self.inventory)

        self.assertIn('cassé', str(context.exception))


class ToolEfficiencyTests(TestCase):
    """Test tool efficiency calculations"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

        self.axe = Material.objects.create(
            name='Hache',
            category='tool',
            max_durability=100
        )

        self.inventory = Inventory.objects.create(
            player=self.player,
            material=self.axe,
            quantity=1,
            durability_max=100,
            durability_current=100
        )

    def test_full_durability_full_efficiency(self):
        """Test 100% efficiency at high durability"""
        efficiency = DurabilityService.get_tool_efficiency(self.inventory)
        self.assertEqual(efficiency, 1.0)

    def test_medium_durability_reduced_efficiency(self):
        """Test 80% efficiency at medium durability"""
        self.inventory.durability_current = 40  # 40%
        self.inventory.save()

        efficiency = DurabilityService.get_tool_efficiency(self.inventory)
        self.assertEqual(efficiency, 0.8)

    def test_low_durability_low_efficiency(self):
        """Test 60% efficiency at low durability"""
        self.inventory.durability_current = 20  # 20%
        self.inventory.save()

        efficiency = DurabilityService.get_tool_efficiency(self.inventory)
        self.assertEqual(efficiency, 0.6)

    def test_very_low_durability_minimum_efficiency(self):
        """Test 40% efficiency at very low durability"""
        self.inventory.durability_current = 5  # 5%
        self.inventory.save()

        efficiency = DurabilityService.get_tool_efficiency(self.inventory)
        self.assertEqual(efficiency, 0.4)

    def test_infinite_durability_always_full(self):
        """Test infinite durability items always 100% efficient"""
        self.inventory.durability_max = 0
        self.inventory.durability_current = 0
        self.inventory.save()

        efficiency = DurabilityService.get_tool_efficiency(self.inventory)
        self.assertEqual(efficiency, 1.0)


class DurabilityPercentageTests(TestCase):
    """Test durability percentage calculations"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

        self.tool = Material.objects.create(
            name='Outil',
            category='tool',
            max_durability=100
        )

        self.inventory = Inventory.objects.create(
            player=self.player,
            material=self.tool,
            quantity=1,
            durability_max=100,
            durability_current=75
        )

    def test_get_durability_percentage(self):
        """Test getting durability as percentage"""
        percentage = DurabilityService.get_durability_percentage(self.inventory)
        self.assertEqual(percentage, 75)

    def test_durability_percentage_at_full(self):
        """Test 100% durability"""
        self.inventory.durability_current = 100
        self.inventory.save()

        percentage = DurabilityService.get_durability_percentage(self.inventory)
        self.assertEqual(percentage, 100)

    def test_durability_percentage_at_zero(self):
        """Test 0% durability"""
        self.inventory.durability_current = 0
        self.inventory.save()

        percentage = DurabilityService.get_durability_percentage(self.inventory)
        self.assertEqual(percentage, 0)

    def test_infinite_durability_percentage(self):
        """Test infinite durability shows 100%"""
        self.inventory.durability_max = 0
        self.inventory.durability_current = 0
        self.inventory.save()

        percentage = DurabilityService.get_durability_percentage(self.inventory)
        self.assertEqual(percentage, 100)


class ToolGatheringBonusTests(TestCase):
    """Test tool bonuses for gathering"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

    def test_no_tool_equipped(self):
        """Test gathering without tool"""
        has_tool, efficiency, tool_name = DurabilityService.check_tool_for_gathering(
            self.player,
            'forest'
        )

        self.assertFalse(has_tool)
        self.assertEqual(efficiency, 1.0)
        self.assertIsNone(tool_name)

    def test_correct_tool_for_biome(self):
        """Test using correct tool gives bonus"""
        axe = Material.objects.create(
            name='Hache',
            category='tool',
            max_durability=100
        )

        inventory = Inventory.objects.create(
            player=self.player,
            material=axe,
            quantity=1,
            durability_max=100,
            durability_current=100
        )

        EquippedItem.objects.create(
            player=self.player,
            material=axe,
            slot='main_hand'
        )

        has_tool, efficiency, tool_name = DurabilityService.check_tool_for_gathering(
            self.player,
            'forest'
        )

        self.assertTrue(has_tool)
        self.assertEqual(efficiency, 1.5)  # Axe in forest = 1.5x
        self.assertEqual(tool_name, 'Hache')

    def test_wrong_tool_for_biome(self):
        """Test using wrong tool gives no bonus"""
        axe = Material.objects.create(
            name='Hache',
            category='tool',
            max_durability=100
        )

        inventory = Inventory.objects.create(
            player=self.player,
            material=axe,
            quantity=1,
            durability_max=100,
            durability_current=100
        )

        EquippedItem.objects.create(
            player=self.player,
            material=axe,
            slot='main_hand'
        )

        has_tool, efficiency, tool_name = DurabilityService.check_tool_for_gathering(
            self.player,
            'desert'
        )

        self.assertTrue(has_tool)
        self.assertEqual(efficiency, 1.0)  # No bonus for axe in desert

    def test_damaged_tool_reduced_efficiency(self):
        """Test damaged tool has reduced efficiency"""
        pickaxe = Material.objects.create(
            name='Pioche',
            category='tool',
            max_durability=100
        )

        inventory = Inventory.objects.create(
            player=self.player,
            material=pickaxe,
            quantity=1,
            durability_max=100,
            durability_current=30  # 30% durability
        )

        EquippedItem.objects.create(
            player=self.player,
            material=pickaxe,
            slot='main_hand'
        )

        has_tool, efficiency, tool_name = DurabilityService.check_tool_for_gathering(
            self.player,
            'mountain'
        )

        self.assertTrue(has_tool)
        # Mountain bonus (1.5) * durability penalty (0.8) = 1.2
        self.assertAlmostEqual(efficiency, 1.2, places=2)


class ToolDurabilityConsumptionTests(TestCase):
    """Test tool durability consumption during actions"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

        self.pickaxe = Material.objects.create(
            name='Pioche',
            category='tool',
            max_durability=100
        )

        self.inventory = Inventory.objects.create(
            player=self.player,
            material=self.pickaxe,
            quantity=1,
            durability_max=100,
            durability_current=100
        )

        EquippedItem.objects.create(
            player=self.player,
            material=self.pickaxe,
            slot='main_hand'
        )

    @patch('random.random', return_value=0.5)  # Mock to ensure durability is consumed
    def test_consume_tool_during_gathering(self, mock_random):
        """Test tool durability decreases during gathering"""
        tool_name, broke, remaining = DurabilityService.consume_tool_durability(
            self.player,
            action_type='gather'
        )

        self.assertEqual(tool_name, 'Pioche')
        self.assertFalse(broke)
        self.assertEqual(remaining, 99)

    @patch('random.random', return_value=0.5)
    def test_mining_consumes_more_durability(self, mock_random):
        """Test mining consumes more durability than gathering"""
        tool_name, broke, remaining = DurabilityService.consume_tool_durability(
            self.player,
            action_type='mine'
        )

        self.assertEqual(remaining, 98)  # Mine costs 2

    @patch('random.random', return_value=0.1)  # Lucky roll
    def test_lucky_no_durability_consumption(self, mock_random):
        """Test 20% chance to not consume durability"""
        initial = self.inventory.durability_current

        tool_name, broke, remaining = DurabilityService.consume_tool_durability(
            self.player,
            action_type='gather'
        )

        # Should not consume durability
        self.assertEqual(remaining, initial)

    def test_crafting_doesnt_consume_durability(self):
        """Test crafting doesn't consume tool durability"""
        initial = self.inventory.durability_current

        tool_name, broke, remaining = DurabilityService.consume_tool_durability(
            self.player,
            action_type='craft'
        )

        self.assertEqual(remaining, initial)


class RepairTests(TestCase):
    """Test item repair functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

        self.tool = Material.objects.create(
            name='Outil',
            category='tool',
            max_durability=100
        )

        self.inventory = Inventory.objects.create(
            player=self.player,
            material=self.tool,
            quantity=1,
            durability_max=100,
            durability_current=30
        )

    def test_repair_damaged_item(self):
        """Test repairing a damaged item"""
        new_durability = DurabilityService.repair_item(self.inventory)

        self.assertEqual(new_durability, 100)
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.durability_current, 100)

    def test_cannot_repair_infinite_durability(self):
        """Test cannot repair items with infinite durability"""
        self.inventory.durability_max = 0
        self.inventory.save()

        with self.assertRaises(GameException) as context:
            DurabilityService.repair_item(self.inventory)

        self.assertIn('réparation', str(context.exception))
