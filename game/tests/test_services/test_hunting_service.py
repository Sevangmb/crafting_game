from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch
from game.models import Player, MapCell, Mob, Material, Inventory
from game.services import hunting_service

class HuntingServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.player = Player.objects.create(
            user=self.user, 
            money=100,
            energy=100,
            health=100,
            max_health=100,
            grid_x=0,
            grid_y=0
        )
        
        # Setup map cell
        self.cell = MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            biome='forest',
            name='Test Forest'
        )
        
        # Setup Mob
        self.mob = Mob.objects.create(
            name='Wolf',
            level=1,
            health=50,
            attack=10,
            defense=2,
            xp_reward=20,
            biomes=['forest'], # Store as list in JSONField usually, but here simplified
            loot_table={'Meat': {'chance': 1.0, 'min': 1, 'max': 1}}
        )
        
        # Setup Material
        self.meat = Material.objects.create(name='Meat')

    def tearDown(self):
        """Clean up after each test"""
        # Stop all patches
        from unittest.mock import patch
        patch.stopall()
        
        # Clean up database objects
        Inventory.objects.all().delete()
        Mob.objects.all().delete()
        Material.objects.all().delete()
        MapCell.objects.all().delete()
        Player.objects.all().delete()
        User.objects.all().delete()


    def test_hunt_success(self):
        # Mock random to ensure mob is found and player wins
        with patch('random.choice', return_value=self.mob), \
             patch('random.random', return_value=0.0), \
             patch('random.randint', return_value=1):
            
            result, status = hunting_service.hunt_at_location(self.player)
            
            self.assertEqual(status, 200)
            self.assertEqual(result['result'], 'success')
            self.assertEqual(result['mob'], 'Wolf')
            
            # Check XP
            self.player.refresh_from_db()
            self.assertEqual(self.player.experience, 20)
            
            # Check Loot
            inv = Inventory.objects.filter(player=self.player, material=self.meat).first()
            self.assertIsNotNone(inv)
            self.assertEqual(inv.quantity, 1)

    def test_hunt_no_energy(self):
        self.player.energy = 0
        self.player.save()
        
        result, status = hunting_service.hunt_at_location(self.player)
        self.assertEqual(status, 400)
        self.assertIn('énergie', result['error'])

    def test_hunt_wrong_biome(self):
        # Change cell biome to something where wolf doesn't spawn
        self.cell.biome = 'desert'
        self.cell.save()
        
        result, status = hunting_service.hunt_at_location(self.player)
        self.assertEqual(status, 200)
        self.assertEqual(result['result'], 'nothing')

    def test_hunt_flee(self):
        # Make mob very strong
        self.mob.attack = 200
        self.mob.save()
        
        with patch('random.choice', return_value=self.mob):
            result, status = hunting_service.hunt_at_location(self.player)
            
            self.assertEqual(status, 200)
            self.assertEqual(result['result'], 'fled')
            
            self.player.refresh_from_db()
            self.assertEqual(self.player.health, 1) # Should survive with 1 HP

    def test_hunt_invalid_location(self):
        self.player.grid_x = 999
        self.player.save()
        
        result, status = hunting_service.hunt_at_location(self.player)
        self.assertEqual(status, 400)
        self.assertIn('invalide', result['error'])
