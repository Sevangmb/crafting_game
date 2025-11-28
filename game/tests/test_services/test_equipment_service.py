"""
Test Equipment Service

Tests for equipping and unequipping items.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Player, Material, Inventory, EquippedItem
from game.services.equipment_service import equip_item, unequip_item


class EquipmentServiceTestCase(TestCase):
    """Test suite for equipment service functions"""
    
    def setUp(self):
        """Create test data before each test"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)
        
        # Create test equipment
        self.helmet = Material.objects.create(
            name='Iron Helmet',
            description='A sturdy helmet',
            is_equipment=True,
            equipment_slot='head',
            defense=5
        )
        
        self.sword = Material.objects.create(
            name='Iron Sword',
            description='A sharp sword',
            is_equipment=True,
            equipment_slot='main_hand',
            attack=10
        )
        
        self.food = Material.objects.create(
            name='Bread',
            description='Tasty bread',
            is_food=True,
            hunger_restore=20
        )
    
    def test_equip_item_success(self):
        """Test successfully equipping an item"""
        # Add helmet to inventory
        inv = Inventory.objects.create(
            player=self.player,
            material=self.helmet,
            quantity=1
        )
        
        response, status = equip_item(self.player, inv.id)
        
        self.assertEqual(status, 200)
        self.assertIn('équipé avec succès', response['message'])
        
        # Check that item is equipped
        self.assertTrue(
            EquippedItem.objects.filter(
                player=self.player,
                material=self.helmet,
                slot='head'
            ).exists()
        )
        
        # Check that item was removed from inventory
        self.assertFalse(Inventory.objects.filter(id=inv.id).exists())
    
    def test_equip_item_reduces_inventory_quantity(self):
        """Test that equipping reduces inventory quantity for stackable items"""
        # Add multiple helmets to inventory
        inv = Inventory.objects.create(
            player=self.player,
            material=self.helmet,
            quantity=3
        )
        
        response, status = equip_item(self.player, inv.id)
        
        self.assertEqual(status, 200)
        
        # Check that quantity was reduced
        inv.refresh_from_db()
        self.assertEqual(inv.quantity, 2)
    
    def test_equip_item_replaces_existing_in_slot(self):
        """Test that equipping replaces existing item in the same slot"""
        # Create another helmet
        better_helmet = Material.objects.create(
            name='Steel Helmet',
            description='A better helmet',
            is_equipment=True,
            equipment_slot='head',
            defense=10
        )
        
        # Equip first helmet
        inv1 = Inventory.objects.create(player=self.player, material=self.helmet, quantity=1)
        equip_item(self.player, inv1.id)
        
        # Equip second helmet
        inv2 = Inventory.objects.create(player=self.player, material=better_helmet, quantity=1)
        response, status = equip_item(self.player, inv2.id)
        
        self.assertEqual(status, 200)
        
        # Check that only the new helmet is equipped
        self.assertFalse(
            EquippedItem.objects.filter(player=self.player, material=self.helmet).exists()
        )
        self.assertTrue(
            EquippedItem.objects.filter(player=self.player, material=better_helmet).exists()
        )
        
        # Check that first helmet was returned to inventory
        self.assertTrue(
            Inventory.objects.filter(player=self.player, material=self.helmet).exists()
        )
    
    def test_equip_item_not_found(self):
        """Test equipping an item that doesn't exist in inventory"""
        response, status = equip_item(self.player, 99999)
        
        self.assertEqual(status, 404)
        self.assertIn('non trouvé', response['error'])
    
    def test_equip_item_not_equipment(self):
        """Test trying to equip a non-equipment item"""
        inv = Inventory.objects.create(player=self.player, material=self.food, quantity=1)
        
        response, status = equip_item(self.player, inv.id)
        
        self.assertEqual(status, 400)
        self.assertIn('ne peut pas être équipé', response['error'])
    
    def test_unequip_item_success(self):
        """Test successfully unequipping an item"""
        # Equip an item first
        EquippedItem.objects.create(
            player=self.player,
            material=self.helmet,
            slot='head'
        )
        
        response, status = unequip_item(self.player, 'head')
        
        self.assertEqual(status, 200)
        self.assertIn('déséquipé', response['message'])
        
        # Check that item is no longer equipped
        self.assertFalse(
            EquippedItem.objects.filter(player=self.player, slot='head').exists()
        )
        
        # Check that item was added to inventory
        self.assertTrue(
            Inventory.objects.filter(player=self.player, material=self.helmet).exists()
        )
    
    def test_unequip_item_adds_to_existing_inventory(self):
        """Test that unequipping adds to existing inventory stack"""
        # Add helmet to inventory
        inv = Inventory.objects.create(player=self.player, material=self.helmet, quantity=2)
        
        # Equip another helmet
        EquippedItem.objects.create(player=self.player, material=self.helmet, slot='head')
        
        unequip_item(self.player, 'head')
        
        # Check that quantity increased
        inv.refresh_from_db()
        self.assertEqual(inv.quantity, 3)
    
    def test_unequip_item_not_found(self):
        """Test unequipping from an empty slot"""
        response, status = unequip_item(self.player, 'head')
        
        self.assertEqual(status, 404)
        self.assertIn('Aucun objet équipé', response['error'])
    
    def test_equip_multiple_different_slots(self):
        """Test equipping items in different slots"""
        # Add items to inventory
        inv_helmet = Inventory.objects.create(player=self.player, material=self.helmet, quantity=1)
        inv_sword = Inventory.objects.create(player=self.player, material=self.sword, quantity=1)
        
        # Equip both
        equip_item(self.player, inv_helmet.id)
        equip_item(self.player, inv_sword.id)
        
        # Check both are equipped
        self.assertEqual(EquippedItem.objects.filter(player=self.player).count(), 2)
        self.assertTrue(
            EquippedItem.objects.filter(player=self.player, slot='head').exists()
        )
        self.assertTrue(
            EquippedItem.objects.filter(player=self.player, slot='main_hand').exists()
        )
