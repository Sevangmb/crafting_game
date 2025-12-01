"""
Unit tests for energy service

Tests energy regeneration and building bonuses.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from game.models import Player, GameConfig
from game.services.energy_service import (
    regenerate_player_energy,
    apply_building_effects_to_action
)


class EnergyRegenerationTests(TestCase):
    """Test energy regeneration mechanics"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            energy=50,
            max_energy=100,
            last_energy_update=timezone.now() - timedelta(minutes=10)
        )

        # Create configs
        GameConfig.objects.get_or_create(
            key='energy_base_regen_per_minute',
            defaults={'value': '1'}
        )

    def test_regenerate_energy_over_time(self):
        """Test energy regenerates based on time passed"""
        # Set last update to 10 minutes ago
        self.player.last_energy_update = timezone.now() - timedelta(minutes=10)
        self.player.save()

        initial_energy = self.player.energy
        restored, minutes = regenerate_player_energy(self.player)
        self.player.refresh_from_db()

        # Should have regenerated some energy
        self.assertGreater(restored, 0)
        self.assertEqual(self.player.energy, initial_energy + restored)
        self.assertGreaterEqual(minutes, 10)

    def test_energy_caps_at_max(self):
        """Test energy doesn't exceed max_energy"""
        self.player.energy = 95
        self.player.max_energy = 100
        self.player.last_energy_update = timezone.now() - timedelta(minutes=60)
        self.player.save()

        regenerate_player_energy(self.player)
        self.player.refresh_from_db()

        # Should be capped at max
        self.assertEqual(self.player.energy, 100)
        self.assertLessEqual(self.player.energy, self.player.max_energy)

    def test_first_time_regeneration(self):
        """Test first regeneration sets timestamp"""
        self.player.last_energy_update = None
        self.player.save()

        restored, minutes = regenerate_player_energy(self.player)
        self.player.refresh_from_db()

        # First time should return 0 energy but set timestamp
        self.assertEqual(restored, 0)
        self.assertEqual(minutes, 0)
        self.assertIsNotNone(self.player.last_energy_update)

    def test_no_regeneration_if_no_time_passed(self):
        """Test no energy if insufficient time passed"""
        self.player.last_energy_update = timezone.now()
        self.player.save()

        initial_energy = self.player.energy
        restored, minutes = regenerate_player_energy(self.player)
        self.player.refresh_from_db()

        # Should restore 0 if almost no time passed
        self.assertEqual(restored, 0)
        self.assertEqual(self.player.energy, initial_energy)

    def test_regeneration_updates_timestamp(self):
        """Test regeneration updates last_energy_update"""
        old_time = timezone.now() - timedelta(minutes=30)
        self.player.last_energy_update = old_time
        self.player.save()

        regenerate_player_energy(self.player)
        self.player.refresh_from_db()

        # Timestamp should be updated to recent time
        self.assertGreater(self.player.last_energy_update, old_time)
        time_diff = (timezone.now() - self.player.last_energy_update).total_seconds()
        self.assertLess(time_diff, 60)  # Within last minute


class BuildingEffectsTests(TestCase):
    """Test building bonuses on action costs"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

    def test_apply_building_effects_no_bonuses(self):
        """Test action cost without any buildings"""
        base_cost = 10
        modified_cost = apply_building_effects_to_action(
            self.player,
            'gather',
            base_cost
        )

        # Without buildings, cost should be unchanged
        self.assertEqual(modified_cost, base_cost)

    def test_apply_building_effects_reduces_cost(self):
        """Test building bonuses reduce action costs"""
        # This test depends on building_service implementation
        # For now, verify it returns a valid cost
        base_cost = 20
        modified_cost = apply_building_effects_to_action(
            self.player,
            'craft',
            base_cost
        )

        # Should return a positive integer
        self.assertGreater(modified_cost, 0)
        self.assertIsInstance(modified_cost, int)
        self.assertLessEqual(modified_cost, base_cost)

    def test_cost_never_below_one(self):
        """Test costs are never reduced below 1"""
        base_cost = 2
        modified_cost = apply_building_effects_to_action(
            self.player,
            'move',
            base_cost
        )

        # Even with high bonuses, cost should be at least 1
        self.assertGreaterEqual(modified_cost, 1)

    def test_different_action_types(self):
        """Test various action types work"""
        for action in ['gather', 'craft', 'move']:
            cost = apply_building_effects_to_action(
                self.player,
                action,
                10
            )
            self.assertGreater(cost, 0)
            self.assertIsInstance(cost, int)


class EnergyEdgeCasesTests(TestCase):
    """Test edge cases for energy system"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            energy=100,
            max_energy=100
        )

        GameConfig.objects.get_or_create(
            key='energy_base_regen_per_minute',
            defaults={'value': '1'}
        )

    def test_regeneration_with_full_energy(self):
        """Test regeneration when already at max energy"""
        self.player.energy = 100
        self.player.max_energy = 100
        self.player.last_energy_update = timezone.now() - timedelta(minutes=20)
        self.player.save()

        initial_energy = self.player.energy
        restored, _ = regenerate_player_energy(self.player)
        self.player.refresh_from_db()

        # Should restore 0 since already at max
        self.assertEqual(restored, 0)
        self.assertEqual(self.player.energy, initial_energy)

    def test_regeneration_with_zero_energy(self):
        """Test regeneration from zero energy"""
        self.player.energy = 0
        self.player.last_energy_update = timezone.now() - timedelta(minutes=30)
        self.player.save()

        restored, minutes = regenerate_player_energy(self.player)
        self.player.refresh_from_db()

        # Should restore energy
        self.assertGreater(restored, 0)
        self.assertGreater(self.player.energy, 0)
        self.assertGreaterEqual(minutes, 30)

    def test_very_long_time_offline(self):
        """Test regeneration after very long offline period"""
        self.player.energy = 10
        self.player.max_energy = 100
        # 24 hours offline
        self.player.last_energy_update = timezone.now() - timedelta(hours=24)
        self.player.save()

        regenerate_player_energy(self.player)
        self.player.refresh_from_db()

        # Should be capped at max, not overflow
        self.assertEqual(self.player.energy, 100)
        self.assertLessEqual(self.player.energy, self.player.max_energy)
