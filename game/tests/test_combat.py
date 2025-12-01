"""
Unit tests for combat system
Tests all combat mechanics including damage, hit chance, rounds, victory/defeat
"""
from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Player, Mob, Material, Inventory, MapCell
from game.services import combat_service
from unittest.mock import patch
import random


class CombatDamageTests(TestCase):
    """Test damage calculation mechanics"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            strength=15,
            agility=12,
            luck=10
        )
    
    def test_base_damage_calculation(self):
        """Test basic damage calculation"""
        damage, is_crit = combat_service.calculate_damage(
            attacker_attack=20,
            defender_defense=5,
            attacker_strength=0,
            luck=0,
            is_heavy_attack=False
        )
        self.assertEqual(damage, 15)  # 20 - 5
        self.assertFalse(is_crit)
    
    def test_strength_bonus(self):
        """Test that strength adds bonus damage"""
        damage, _ = combat_service.calculate_damage(
            attacker_attack=20,
            defender_defense=5,
            attacker_strength=15,  # Should add 3 damage (15 // 5)
            luck=0,
            is_heavy_attack=False
        )
        self.assertEqual(damage, 18)  # 15 base + 3 strength bonus
    
    def test_heavy_attack_multiplier(self):
        """Test heavy attack deals 1.5x damage"""
        normal_damage, _ = combat_service.calculate_damage(
            attacker_attack=20,
            defender_defense=5,
            attacker_strength=0,
            luck=0,
            is_heavy_attack=False
        )
        heavy_damage, _ = combat_service.calculate_damage(
            attacker_attack=20,
            defender_defense=5,
            attacker_strength=0,
            luck=0,
            is_heavy_attack=True
        )
        self.assertEqual(heavy_damage, int(normal_damage * 1.5))
    
    @patch('random.random')
    def test_critical_hit(self, mock_random):
        """Test critical hits based on luck"""
        mock_random.return_value = 0.05  # Below 10% luck threshold
        damage, is_crit = combat_service.calculate_damage(
            attacker_attack=20,
            defender_defense=5,
            attacker_strength=0,
            luck=10,  # 10% crit chance
            is_heavy_attack=False
        )
        self.assertTrue(is_crit)
        self.assertEqual(damage, int(15 * 1.5))  # Critical multiplier
    
    def test_minimum_damage(self):
        """Test that damage is at least 1"""
        damage, _ = combat_service.calculate_damage(
            attacker_attack=5,
            defender_defense=10,  # Defense higher than attack
            attacker_strength=0,
            luck=0,
            is_heavy_attack=False
        )
        self.assertGreaterEqual(damage, 1)


class CombatHitChanceTests(TestCase):
    """Test hit chance calculation"""
    
    def test_base_accuracy(self):
        """Test base hit chance is 85%"""
        hit_chance = combat_service.calculate_hit_chance(
            attacker_agility=10,
            is_heavy_attack=False
        )
        self.assertEqual(hit_chance, 0.85)
    
    def test_agility_bonus(self):
        """Test agility adds +1% per point above 10"""
        hit_chance = combat_service.calculate_hit_chance(
            attacker_agility=15,  # 5 points above 10
            is_heavy_attack=False
        )
        self.assertEqual(hit_chance, 0.90)  # 85% + 5%
    
    def test_heavy_attack_penalty(self):
        """Test heavy attacks have 30% accuracy penalty"""
        normal_chance = combat_service.calculate_hit_chance(
            attacker_agility=10,
            is_heavy_attack=False
        )
        heavy_chance = combat_service.calculate_hit_chance(
            attacker_agility=10,
            is_heavy_attack=True
        )
        self.assertEqual(heavy_chance, normal_chance * 0.7)
    
    def test_max_hit_chance_cap(self):
        """Test hit chance is capped at 95%"""
        hit_chance = combat_service.calculate_hit_chance(
            attacker_agility=100,  # Very high agility
            is_heavy_attack=False
        )
        self.assertLessEqual(hit_chance, 0.95)
    
    def test_min_hit_chance_floor(self):
        """Test hit chance has minimum of 50%"""
        hit_chance = combat_service.calculate_hit_chance(
            attacker_agility=0,  # Very low agility
            is_heavy_attack=True  # With penalty
        )
        self.assertGreaterEqual(hit_chance, 0.50)


class CombatRoundTests(TestCase):
    """Test combat round execution"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            health=100,
            max_health=100,
            strength=15,
            agility=12,
            luck=10
        )
        self.mob = Mob.objects.create(
            name='Test Wolf',
            health=50,
            attack=10,
            defense=2
        )
    
    @patch('random.random')
    def test_successful_attack(self, mock_random):
        """Test successful player attack"""
        mock_random.return_value = 0.5  # Hit succeeds
        
        player_dmg, mob_dmg, is_crit, log, fled = combat_service.execute_combat_round(
            self.player,
            self.mob,
            'attack'
        )
        
        self.assertGreater(player_dmg, 0)
        self.assertGreater(mob_dmg, 0)
        self.assertFalse(fled)
        self.assertTrue(any('attaquez' in msg.lower() for msg in log))
    
    @patch('random.random')
    def test_missed_attack(self, mock_random):
        """Test missed attack"""
        mock_random.return_value = 0.99  # Miss
        
        player_dmg, mob_dmg, is_crit, log, fled = combat_service.execute_combat_round(
            self.player,
            self.mob,
            'attack'
        )
        
        self.assertEqual(player_dmg, 0)
        self.assertTrue(any('manquée' in msg.lower() for msg in log))
    
    def test_defend_action(self):
        """Test defend action reduces damage"""
        _, mob_dmg_defend, _, log_defend, _ = combat_service.execute_combat_round(
            self.player,
            self.mob,
            'defend'
        )
        
        _, mob_dmg_normal, _, log_normal, _ = combat_service.execute_combat_round(
            self.player,
            self.mob,
            'attack'
        )
        
        # Defend should reduce damage by 50%
        self.assertLess(mob_dmg_defend, mob_dmg_normal)
        self.assertTrue(any('défendez' in msg.lower() for msg in log_defend))
    
    @patch('random.random')
    def test_successful_flee(self, mock_random):
        """Test successful flee attempt"""
        mock_random.return_value = 0.1  # Flee succeeds
        
        _, _, _, log, fled = combat_service.execute_combat_round(
            self.player,
            self.mob,
            'flee'
        )
        
        self.assertTrue(fled)
        self.assertTrue(any('fuir' in msg.lower() for msg in log))
    
    @patch('random.random')
    def test_failed_flee(self, mock_random):
        """Test failed flee attempt"""
        mock_random.return_value = 0.9  # Flee fails
        
        _, mob_dmg, _, log, fled = combat_service.execute_combat_round(
            self.player,
            self.mob,
            'flee'
        )
        
        self.assertFalse(fled)
        self.assertGreater(mob_dmg, 0)  # Mob still attacks
        self.assertTrue(any('échec' in msg.lower() for msg in log))


class CombatVictoryTests(TestCase):
    """Test victory resolution and rewards"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            level=1,
            experience=0,
            energy=50,
            max_energy=100,
            health=80,
            max_health=100,
            luck=10
        )
        self.cell = MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            center_lat=44.933,
            center_lon=4.893,
            biome='plains'
        )
        self.mob = Mob.objects.create(
            name='Test Rabbit',
            health=20,
            xp_reward=10,
            loot_table_json='{"Viande": {"min": 1, "max": 2, "chance": 1.0}}'
        )
        # Create material for loot
        self.meat = Material.objects.create(
            name='Viande',
            icon='🥩',
            category='food'
        )
        self.player.grid_x = 0
        self.player.grid_y = 0
        self.player.save()
    
    def test_base_xp_reward(self):
        """Test base XP is awarded"""
        initial_xp = self.player.experience
        combat_state = {
            'mob_health': 0,
            'player_health': 80,
            'total_damage_dealt': 20,
            'total_damage_taken': 0,
            'rounds': 5,
            'combat_log': []
        }
        
        combat_service.resolve_combat_victory(self.player, self.mob, combat_state)
        self.player.refresh_from_db()
        
        self.assertGreater(self.player.experience, initial_xp)
    
    def test_perfect_victory_bonus(self):
        """Test perfect victory (no damage) gives bonus XP"""
        combat_state = {
            'mob_health': 0,
            'player_health': 100,
            'total_damage_dealt': 20,
            'total_damage_taken': 0,  # Perfect!
            'rounds': 5,
            'combat_log': []
        }
        
        combat_service.resolve_combat_victory(self.player, self.mob, combat_state)
        
        self.assertIn('bonus_xp', combat_state)
        self.assertGreater(combat_state['bonus_xp'], 0)
    
    def test_quick_victory_bonus(self):
        """Test quick victory (≤3 rounds) gives bonus XP"""
        combat_state = {
            'mob_health': 0,
            'player_health': 80,
            'total_damage_dealt': 20,
            'total_damage_taken': 20,
            'rounds': 3,  # Quick!
            'combat_log': []
        }
        
        combat_service.resolve_combat_victory(self.player, self.mob, combat_state)
        
        self.assertIn('bonus_xp', combat_state)
        self.assertGreater(combat_state['bonus_xp'], 0)
    
    def test_loot_generation(self):
        """Test loot is generated and added to inventory"""
        combat_state = {
            'mob_health': 0,
            'player_health': 80,
            'total_damage_dealt': 20,
            'total_damage_taken': 0,
            'rounds': 5,
            'combat_log': []
        }
        
        combat_service.resolve_combat_victory(self.player, self.mob, combat_state)
        
        # Check loot was generated
        self.assertIn('loot', combat_state)
        self.assertGreater(len(combat_state['loot']), 0)
        
        # Check inventory was updated
        inventory = Inventory.objects.filter(player=self.player, material=self.meat).first()
        self.assertIsNotNone(inventory)
        self.assertGreater(inventory.quantity, 0)


class CombatDefeatTests(TestCase):
    """Test defeat resolution"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            health=0,  # Defeated
            energy=50
        )
        self.cell = MapCell.objects.create(grid_x=0, grid_y=0, center_lat=44.933, center_lon=4.893, biome='plains')
        self.mob = Mob.objects.create(name='Test Wolf', health=50)
        self.player.grid_x = 0
        self.player.grid_y = 0
        self.player.save()
    
    def test_health_restoration_on_defeat(self):
        """Test player gets minimum health on defeat"""
        combat_state = {
            'mob_health': 50,
            'player_health': 0,
            'total_damage_dealt': 10,
            'total_damage_taken': 100,
            'rounds': 3,
            'combat_log': []
        }
        
        combat_service.resolve_combat_defeat(self.player, self.mob, combat_state)
        self.player.refresh_from_db()
        
        self.assertGreater(self.player.health, 0)
    
    def test_energy_penalty_on_defeat(self):
        """Test energy is reduced on defeat"""
        initial_energy = self.player.energy
        combat_state = {
            'mob_health': 50,
            'player_health': 0,
            'total_damage_dealt': 10,
            'total_damage_taken': 100,
            'rounds': 3,
            'combat_log': []
        }
        
        combat_service.resolve_combat_defeat(self.player, self.mob, combat_state)
        self.player.refresh_from_db()
        
        self.assertLess(self.player.energy, initial_energy)
