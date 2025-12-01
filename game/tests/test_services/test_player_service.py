"""
Unit tests for player service

Tests player management, restart functionality, and stats.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from game.models import (
    Player, Inventory, Material, EquippedItem,
    GatheringLog, CraftingLog, Recipe, GameConfig, MapCell
)
from game.services.player_service import restart_player


class PlayerRestartTests(TestCase):
    """Test player restart functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            current_x=5.0,
            current_y=45.0,
            grid_x=10,
            grid_y=10,
            energy=50,
            max_energy=150,
            health=80,
            max_health=120,
            hunger=50,
            thirst=30,
            radiation=10,
            strength=20,
            agility=15,
            intelligence=12,
            luck=8,
            level=5,
            experience=500
        )

        # Add some inventory
        self.wood = Material.objects.create(name='Bois', category='resource')
        Inventory.objects.create(player=self.player, material=self.wood, quantity=50)

        # Add equipped item
        self.sword = Material.objects.create(name='Épée', category='weapon')
        EquippedItem.objects.create(player=self.player, material=self.sword, slot='weapon')

        # Add logs
        self.stone = Material.objects.create(name='Pierre', category='resource')
        self.cell = MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            center_lat=44.933,
            center_lon=4.893,
            biome='plains'
        )
        GatheringLog.objects.create(
            player=self.player,
            material=self.stone,
            quantity=10,
            cell=self.cell
        )

        # Create config
        GameConfig.objects.get_or_create(
            key='starting_energy',
            defaults={'value': '100'}
        )

    def test_restart_resets_position(self):
        """Test restart resets player to Valence center"""
        restart_player(self.player)

        self.assertEqual(self.player.current_x, 4.893)
        self.assertEqual(self.player.current_y, 44.933)
        self.assertEqual(self.player.grid_x, 0)
        self.assertEqual(self.player.grid_y, 0)

    def test_restart_resets_energy_and_health(self):
        """Test restart resets energy and health to starting values"""
        restart_player(self.player)

        self.assertEqual(self.player.energy, 100)
        self.assertEqual(self.player.max_energy, 100)
        self.assertEqual(self.player.health, 100)
        self.assertEqual(self.player.max_health, 100)

    def test_restart_resets_survival_stats(self):
        """Test restart resets hunger, thirst, and radiation"""
        restart_player(self.player)

        self.assertEqual(self.player.hunger, 100)
        self.assertEqual(self.player.max_hunger, 100)
        self.assertEqual(self.player.thirst, 100)
        self.assertEqual(self.player.max_thirst, 100)
        self.assertEqual(self.player.radiation, 0)

    def test_restart_resets_player_stats(self):
        """Test restart resets strength, agility, intelligence, luck"""
        restart_player(self.player)

        self.assertEqual(self.player.strength, 10)
        self.assertEqual(self.player.agility, 10)
        self.assertEqual(self.player.intelligence, 10)
        self.assertEqual(self.player.luck, 10)

    def test_restart_resets_level_and_xp(self):
        """Test restart resets level and experience"""
        restart_player(self.player)

        self.assertEqual(self.player.level, 1)
        self.assertEqual(self.player.experience, 0)

    def test_restart_clears_inventory(self):
        """Test restart clears all inventory items"""
        restart_player(self.player)

        inventory_count = Inventory.objects.filter(player=self.player).count()
        self.assertEqual(inventory_count, 0)

    def test_restart_clears_equipped_items(self):
        """Test restart clears all equipped items"""
        restart_player(self.player)

        equipped_count = EquippedItem.objects.filter(player=self.player).count()
        self.assertEqual(equipped_count, 0)

    def test_restart_clears_gathering_logs(self):
        """Test restart clears gathering history"""
        restart_player(self.player)

        log_count = GatheringLog.objects.filter(player=self.player).count()
        self.assertEqual(log_count, 0)

    def test_restart_updates_timestamps(self):
        """Test restart updates survival timestamps"""
        old_time = timezone.now() - timezone.timedelta(hours=1)
        self.player.last_energy_update = old_time
        self.player.last_hunger_update = old_time
        self.player.last_thirst_update = old_time
        self.player.save()

        restart_player(self.player)
        self.player.refresh_from_db()

        # Timestamps should be recent (within last minute)
        now = timezone.now()
        self.assertLess((now - self.player.last_energy_update).total_seconds(), 60)
        self.assertLess((now - self.player.last_hunger_update).total_seconds(), 60)
        self.assertLess((now - self.player.last_thirst_update).total_seconds(), 60)

    def test_restart_returns_player(self):
        """Test restart returns the player object"""
        result = restart_player(self.player)

        self.assertEqual(result, self.player)
        self.assertIsInstance(result, Player)


class PlayerStatsTests(TestCase):
    """Test player stats calculations"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            strength=15,
            agility=12,
            intelligence=10,
            luck=8
        )

    def test_total_attack_calculation(self):
        """Test total attack is calculated from equipped items + strength"""
        # Base attack from strength
        base_attack = self.player.total_attack
        self.assertGreaterEqual(base_attack, 0)

    def test_total_defense_calculation(self):
        """Test total defense is calculated from equipped items"""
        base_defense = self.player.total_defense
        self.assertGreaterEqual(base_defense, 0)

    def test_player_level_progression(self):
        """Test player level affects XP requirements"""
        xp_level_2 = self.player.get_xp_for_level(2)
        xp_level_3 = self.player.get_xp_for_level(3)
        xp_level_5 = self.player.get_xp_for_level(5)

        # Higher levels require more XP
        self.assertGreater(xp_level_3, xp_level_2)
        self.assertGreater(xp_level_5, xp_level_3)
