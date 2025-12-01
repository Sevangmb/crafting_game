from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch
from game.models import Player, MapCell, Material, Inventory
from game.services import scavenging_service

class ScavengingServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.player = Player.objects.create(
            user=self.user,
            energy=100,
            luck=0,
            grid_x=0,
            grid_y=0
        )
        
        self.cell = MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            biome='urban',
            name='City'
        )
        
        self.scrap = Material.objects.create(name='Ferraille')

    def tearDown(self):
        """Clean up after each test"""
        # Stop all patches
        from unittest.mock import patch
        patch.stopall()
        
        # Clean up database objects
        Inventory.objects.all().delete()
        Material.objects.all().delete()
        MapCell.objects.all().delete()
        Player.objects.all().delete()
        User.objects.all().delete()


    def test_scavenge_success(self):
        # Mock random to ensure finding items
        with patch('random.random', return_value=0.0), \
             patch('random.randint', return_value=1):
            
            result, status = scavenging_service.scavenge_location(self.player)
            
            self.assertEqual(status, 200)
            self.assertEqual(result['result'], 'success')
            
            # Check XP
            self.player.refresh_from_db()
            self.assertGreater(self.player.experience, 0)
            
            # Check Loot
            inv = Inventory.objects.filter(player=self.player, material=self.scrap).first()
            self.assertIsNotNone(inv)
            self.assertEqual(inv.quantity, 1)

    def test_scavenge_wrong_biome(self):
        self.cell.biome = 'forest'
        self.cell.save()
        
        result, status = scavenging_service.scavenge_location(self.player)
        self.assertEqual(status, 400)
        self.assertIn('urbaines', result['error'])

    def test_scavenge_no_energy(self):
        self.player.energy = 0
        self.player.save()
        
        result, status = scavenging_service.scavenge_location(self.player)
        self.assertEqual(status, 400)
        self.assertIn('énergie', result['error'])

    def test_scavenge_nothing_found(self):
        # Mock random to find nothing
        with patch('random.random', return_value=1.0):
            result, status = scavenging_service.scavenge_location(self.player)
            
            self.assertEqual(status, 200)
            self.assertEqual(result['result'], 'nothing')
