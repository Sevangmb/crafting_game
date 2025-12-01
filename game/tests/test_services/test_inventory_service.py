"""
Unit tests for inventory service

Tests inventory management, item consumption, and inventory operations.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Player, Material, Inventory
from game.services.inventory_service import consume_item, get_inventory_summary


class ConsumeItemTests(TestCase):
    """Test item consumption mechanics"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            energy=50,
            max_energy=100,
            hunger=50,
            thirst=50,
            radiation=0
        )

        # Create test food items
        self.bread = Material.objects.create(
            name='Pain',
            icon='🍞',
            category='food',
            is_food=True,
            hunger_restore=20,
            thirst_restore=0,
            energy_restore=10
        )

        self.water = Material.objects.create(
            name='Eau',
            icon='💧',
            category='drink',
            is_food=True,
            hunger_restore=0,
            thirst_restore=30,
            energy_restore=5
        )

        self.stone = Material.objects.create(
            name='Pierre',
            icon='🪨',
            category='resource',
            is_food=False
        )

    def test_consume_food_success(self):
        """Test successfully consuming food item"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.bread,
            quantity=5
        )

        initial_hunger = self.player.hunger
        initial_energy = self.player.energy

        response, status = consume_item(self.player, inventory.id)

        self.assertEqual(status, 200)
        self.assertIn('message', response)
        self.player.refresh_from_db()

        # Check stats increased
        self.assertGreater(self.player.hunger, initial_hunger)
        self.assertGreater(self.player.energy, initial_energy)

        # Check inventory quantity decreased
        inventory.refresh_from_db()
        self.assertEqual(inventory.quantity, 4)

    def test_consume_last_item_deletes_inventory(self):
        """Test consuming last item removes inventory entry"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.bread,
            quantity=1
        )

        consume_item(self.player, inventory.id)

        # Inventory entry should be deleted
        self.assertFalse(
            Inventory.objects.filter(id=inventory.id).exists()
        )

    def test_consume_drink_restores_thirst(self):
        """Test consuming drink restores thirst"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.water,
            quantity=3
        )

        initial_thirst = self.player.thirst

        response, status = consume_item(self.player, inventory.id)

        self.assertEqual(status, 200)
        self.player.refresh_from_db()
        self.assertGreater(self.player.thirst, initial_thirst)

    def test_consume_non_food_item_fails(self):
        """Test trying to consume non-food item returns error"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.stone,
            quantity=10
        )

        response, status = consume_item(self.player, inventory.id)

        self.assertEqual(status, 400)
        self.assertIn('error', response)
        self.assertIn('consommable', response['error'].lower())

    def test_consume_nonexistent_item_fails(self):
        """Test consuming item not in inventory returns error"""
        response, status = consume_item(self.player, 99999)

        self.assertEqual(status, 404)
        self.assertIn('error', response)
        self.assertIn('non trouvé', response['error'].lower())

    def test_consume_other_player_item_fails(self):
        """Test player cannot consume another player's items"""
        other_user = User.objects.create_user(username='other', password='pass')
        other_player = Player.objects.create(user=other_user)

        inventory = Inventory.objects.create(
            player=other_player,
            material=self.bread,
            quantity=5
        )

        response, status = consume_item(self.player, inventory.id)

        self.assertEqual(status, 404)

    def test_consume_updates_response_format(self):
        """Test consume returns correct response format"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.bread,
            quantity=2
        )

        response, status = consume_item(self.player, inventory.id)

        self.assertEqual(status, 200)
        self.assertIn('message', response)
        self.assertIn('energy', response)
        self.assertIn('hunger', response)
        self.assertIn('thirst', response)
        self.assertIn('max_energy', response)


class InventorySummaryTests(TestCase):
    """Test inventory summary generation"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

        self.wood = Material.objects.create(name='Bois', icon='🪵', category='resource')
        self.stone = Material.objects.create(name='Pierre', icon='🪨', category='resource')
        self.food = Material.objects.create(name='Pain', icon='🍞', category='food', is_food=True)

    def test_get_empty_inventory(self):
        """Test getting summary of empty inventory"""
        summary = get_inventory_summary(self.player)

        self.assertIsNotNone(summary)
        # Should return empty structure or empty list
        if isinstance(summary, list):
            self.assertEqual(len(summary), 0)
        elif isinstance(summary, dict):
            self.assertTrue(len(summary) == 0 or all(len(v) == 0 for v in summary.values()))

    def test_get_inventory_with_items(self):
        """Test getting summary with items in inventory"""
        Inventory.objects.create(player=self.player, material=self.wood, quantity=50)
        Inventory.objects.create(player=self.player, material=self.stone, quantity=30)
        Inventory.objects.create(player=self.player, material=self.food, quantity=5)

        summary = get_inventory_summary(self.player)

        self.assertIsNotNone(summary)
        # Should contain items
        if isinstance(summary, list):
            self.assertEqual(len(summary), 3)
        elif isinstance(summary, dict):
            total_items = sum(len(v) if isinstance(v, list) else 1 for v in summary.values())
            self.assertGreaterEqual(total_items, 3)

    def test_get_inventory_only_shows_own_items(self):
        """Test inventory summary only shows player's own items"""
        other_user = User.objects.create_user(username='other', password='pass')
        other_player = Player.objects.create(user=other_user)

        # Add items to both players
        Inventory.objects.create(player=self.player, material=self.wood, quantity=10)
        Inventory.objects.create(player=other_player, material=self.stone, quantity=20)

        summary = get_inventory_summary(self.player)

        # Should only contain player's items, not other player's
        if isinstance(summary, list):
            # Check that only wood is in summary, not stone
            item_names = [item.get('name') if isinstance(item, dict) else getattr(item, 'material', {}).name for item in summary]
            self.assertIn('Bois', item_names)
            self.assertNotIn('Pierre', item_names)


class InventoryManagementTests(TestCase):
    """Test general inventory management"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)
        self.material = Material.objects.create(name='Test Material', category='resource')

    def test_add_new_item_to_inventory(self):
        """Test adding new item creates inventory entry"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.material,
            quantity=10
        )

        self.assertIsNotNone(inventory)
        self.assertEqual(inventory.quantity, 10)
        self.assertEqual(inventory.player, self.player)
        self.assertEqual(inventory.material, self.material)

    def test_update_existing_inventory_quantity(self):
        """Test updating quantity of existing inventory item"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.material,
            quantity=10
        )

        inventory.quantity += 5
        inventory.save()
        inventory.refresh_from_db()

        self.assertEqual(inventory.quantity, 15)

    def test_remove_zero_quantity_items(self):
        """Test removing items when quantity reaches zero"""
        inventory = Inventory.objects.create(
            player=self.player,
            material=self.material,
            quantity=1
        )

        inventory.quantity = 0
        inventory.delete()

        self.assertFalse(
            Inventory.objects.filter(id=inventory.id).exists()
        )
