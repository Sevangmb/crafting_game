"""
Unit tests for movement service
"""
from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Player, MapCell
from game.services import movement_service
from decimal import Decimal


class MovementServiceTest(TestCase):
    def setUp(self):
        """Set up test user and player"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            grid_x=0,
            grid_y=0,
            current_x=44.933,
            current_y=4.893,
            energy=100,
            health=100,
            hunger=100,
            thirst=100
        )
        # Create starting cell
        MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            center_lat=44.933,
            center_lon=4.893,
            biome='urban'
        )

    def test_move_north(self):
        """Test moving north increases grid_y"""
        initial_y = self.player.grid_y
        result, status_code, *_ = movement_service.move_player(self.player, 'north')

        self.player.refresh_from_db()
        self.assertEqual(status_code, 200)
        self.assertEqual(self.player.grid_y, initial_y + 1)
        self.assertIsInstance(result, Player)

    def test_move_south(self):
        """Test moving south decreases grid_y"""
        # Move north first so we can move south
        movement_service.move_player(self.player, 'north')
        self.player.refresh_from_db()

        initial_y = self.player.grid_y
        result, status_code, *_ = movement_service.move_player(self.player, 'south')

        self.player.refresh_from_db()
        self.assertEqual(status_code, 200)
        self.assertEqual(self.player.grid_y, initial_y - 1)

    def test_move_east(self):
        """Test moving east increases grid_x"""
        initial_x = self.player.grid_x
        result, status_code, *_ = movement_service.move_player(self.player, 'east')

        self.player.refresh_from_db()
        self.assertEqual(status_code, 200)
        self.assertEqual(self.player.grid_x, initial_x + 1)

    def test_move_west(self):
        """Test moving west decreases grid_x"""
        # Move east first so we can move west
        movement_service.move_player(self.player, 'east')
        self.player.refresh_from_db()

        initial_x = self.player.grid_x
        result, status_code, *_ = movement_service.move_player(self.player, 'west')

        self.player.refresh_from_db()
        self.assertEqual(status_code, 200)
        self.assertEqual(self.player.grid_x, initial_x - 1)

    def test_consecutive_moves_same_direction(self):
        """Test multiple consecutive moves in the same direction"""
        initial_x = self.player.grid_x

        # Move east 3 times
        for i in range(3):
            result, status_code, *_ = movement_service.move_player(self.player, 'east')
            self.player.refresh_from_db()
            self.assertEqual(status_code, 200, f"Move {i+1} failed")
            self.assertEqual(self.player.grid_x, initial_x + i + 1, f"Grid X incorrect after move {i+1}")

    def test_movement_consumes_energy(self):
        """Test that movement consumes energy"""
        initial_energy = self.player.energy
        movement_service.move_player(self.player, 'north')

        self.player.refresh_from_db()
        self.assertLess(self.player.energy, initial_energy)

    def test_cannot_move_without_energy(self):
        """Test that player cannot move without enough energy"""
        self.player.energy = 0
        self.player.save()

        result, status_code = movement_service.move_player(self.player, 'north')

        self.assertEqual(status_code, 400)
        self.assertIn('error', result)

    def test_invalid_direction(self):
        """Test that invalid direction returns error"""
        result, status_code = movement_service.move_player(self.player, 'invalid')

        self.assertEqual(status_code, 400)
        self.assertIn('error', result)

    def test_movement_creates_new_cell(self):
        """Test that moving to new coordinates creates a new cell"""
        initial_cell_count = MapCell.objects.count()

        movement_service.move_player(self.player, 'north')

        new_cell_count = MapCell.objects.count()
        self.assertGreater(new_cell_count, initial_cell_count)

    def test_grid_coordinates_consistency(self):
        """Test that grid coordinates remain consistent after multiple moves"""
        # Move in a square: north -> east -> south -> west
        movement_service.move_player(self.player, 'north')
        self.player.refresh_from_db()

        movement_service.move_player(self.player, 'east')
        self.player.refresh_from_db()

        movement_service.move_player(self.player, 'south')
        self.player.refresh_from_db()

        movement_service.move_player(self.player, 'west')
        self.player.refresh_from_db()

        # Should be back at starting position
        self.assertEqual(self.player.grid_x, 0)
        self.assertEqual(self.player.grid_y, 0)

    def test_rapid_consecutive_moves(self):
        """Test rapid consecutive moves in same direction (simulates quick clicks)"""
        self.player.energy = 1000  # Ensure enough energy
        self.player.save()

        initial_x = self.player.grid_x
        moves = 5

        for i in range(moves):
            result, status_code, *_ = movement_service.move_player(self.player, 'east')
            self.player.refresh_from_db()

            self.assertEqual(status_code, 200, f"Rapid move {i+1} failed with status {status_code}")
            self.assertEqual(self.player.grid_x, initial_x + i + 1,
                           f"After rapid move {i+1}, expected grid_x={initial_x + i + 1}, got {self.player.grid_x}")
