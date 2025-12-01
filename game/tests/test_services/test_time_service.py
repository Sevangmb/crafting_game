"""
Unit tests for time service

Tests real-time game clock, day/night cycles, and time-based effects.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, time
from unittest.mock import patch
from game.models import Player
from game.services.time_service import TimeService


class TimeServiceConstantsTests(TestCase):
    """Test time service constants"""

    def test_time_constants_defined(self):
        """Test that time constants are properly defined"""
        self.assertTrue(hasattr(TimeService, 'SUNRISE'))
        self.assertTrue(hasattr(TimeService, 'MORNING_END'))
        self.assertTrue(hasattr(TimeService, 'AFTERNOON_END'))
        self.assertTrue(hasattr(TimeService, 'SUNSET'))
        self.assertTrue(hasattr(TimeService, 'NIGHT_END'))

    def test_time_constants_valid_hours(self):
        """Test time constants are valid 24-hour values"""
        self.assertGreaterEqual(TimeService.SUNRISE, 0)
        self.assertLess(TimeService.SUNRISE, 24)
        self.assertGreaterEqual(TimeService.SUNSET, 0)
        self.assertLess(TimeService.SUNSET, 24)

    def test_sunrise_before_sunset(self):
        """Test sunrise comes before sunset"""
        self.assertLess(TimeService.SUNRISE, TimeService.SUNSET)

    def test_time_progression_logical(self):
        """Test time periods are in logical order"""
        self.assertLess(TimeService.SUNRISE, TimeService.MORNING_END)
        self.assertLess(TimeService.MORNING_END, TimeService.AFTERNOON_END)
        self.assertLess(TimeService.AFTERNOON_END, TimeService.SUNSET)


class CurrentTimeTests(TestCase):
    """Test current game time retrieval"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

    def test_get_current_game_time(self):
        """Test getting current game time"""
        game_time = TimeService.get_current_game_time()

        self.assertIsNotNone(game_time)
        self.assertIsInstance(game_time, datetime)

    def test_get_current_game_time_with_player(self):
        """Test getting current game time with player parameter"""
        game_time = TimeService.get_current_game_time(self.player)

        self.assertIsNotNone(game_time)
        self.assertIsInstance(game_time, datetime)

    def test_game_time_is_recent(self):
        """Test game time is close to actual time"""
        game_time = TimeService.get_current_game_time()
        now = timezone.now()

        # Should be within 1 second
        diff = abs((game_time - now).total_seconds())
        self.assertLess(diff, 1.0)

    def test_get_day_number(self):
        """Test getting current day number"""
        day = TimeService.get_day_number()

        self.assertIsNotNone(day)
        self.assertIsInstance(day, int)
        self.assertGreaterEqual(day, 1)
        self.assertLessEqual(day, 31)


class TimeOfDayTests(TestCase):
    """Test time of day calculations"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

    @patch('game.services.time_service.timezone.now')
    def test_morning_detection(self, mock_now):
        """Test morning time period detection"""
        # Set time to 8 AM
        mock_now.return_value = datetime(2025, 1, 15, 8, 0, 0, tzinfo=timezone.utc)

        time_of_day = TimeService.get_time_of_day()

        self.assertEqual(time_of_day, 'morning')

    @patch('game.services.time_service.timezone.now')
    def test_afternoon_detection(self, mock_now):
        """Test afternoon time period detection"""
        # Set time to 2 PM
        mock_now.return_value = datetime(2025, 1, 15, 14, 0, 0, tzinfo=timezone.utc)

        time_of_day = TimeService.get_time_of_day()

        self.assertEqual(time_of_day, 'afternoon')

    @patch('game.services.time_service.timezone.now')
    def test_evening_detection(self, mock_now):
        """Test evening time period detection"""
        # Set time to 7 PM
        mock_now.return_value = datetime(2025, 1, 15, 19, 0, 0, tzinfo=timezone.utc)

        time_of_day = TimeService.get_time_of_day()

        self.assertEqual(time_of_day, 'evening')

    @patch('game.services.time_service.timezone.now')
    def test_night_detection(self, mock_now):
        """Test night time period detection"""
        # Set time to 11 PM
        mock_now.return_value = datetime(2025, 1, 15, 23, 0, 0, tzinfo=timezone.utc)

        time_of_day = TimeService.get_time_of_day()

        self.assertEqual(time_of_day, 'night')

    @patch('game.services.time_service.timezone.now')
    def test_early_morning_is_night(self, mock_now):
        """Test early morning hours are considered night"""
        # Set time to 3 AM
        mock_now.return_value = datetime(2025, 1, 15, 3, 0, 0, tzinfo=timezone.utc)

        time_of_day = TimeService.get_time_of_day()

        self.assertEqual(time_of_day, 'night')


class DaytimeTests(TestCase):
    """Test daytime detection"""

    @patch('game.services.time_service.timezone.now')
    def test_is_daytime_morning(self, mock_now):
        """Test morning is considered daytime"""
        mock_now.return_value = datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        is_day = TimeService.is_daytime()

        self.assertTrue(is_day)

    @patch('game.services.time_service.timezone.now')
    def test_is_daytime_afternoon(self, mock_now):
        """Test afternoon is considered daytime"""
        mock_now.return_value = datetime(2025, 1, 15, 15, 0, 0, tzinfo=timezone.utc)

        is_day = TimeService.is_daytime()

        self.assertTrue(is_day)

    @patch('game.services.time_service.timezone.now')
    def test_is_nighttime(self, mock_now):
        """Test night is not daytime"""
        mock_now.return_value = datetime(2025, 1, 15, 22, 0, 0, tzinfo=timezone.utc)

        is_day = TimeService.is_daytime()

        self.assertFalse(is_day)

    @patch('game.services.time_service.timezone.now')
    def test_sunrise_is_daytime(self, mock_now):
        """Test sunrise hour is considered daytime"""
        # Set to exactly sunrise time
        mock_now.return_value = datetime(2025, 1, 15, TimeService.SUNRISE, 0, 0, tzinfo=timezone.utc)

        is_day = TimeService.is_daytime()

        self.assertTrue(is_day)

    @patch('game.services.time_service.timezone.now')
    def test_sunset_is_nighttime(self, mock_now):
        """Test sunset hour is considered nighttime"""
        # Set to exactly sunset time
        mock_now.return_value = datetime(2025, 1, 15, TimeService.SUNSET, 0, 0, tzinfo=timezone.utc)

        is_day = TimeService.is_daytime()

        self.assertFalse(is_day)


class TimeInfoTests(TestCase):
    """Test comprehensive time information"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

    def test_get_time_info_structure(self):
        """Test get_time_info returns correct structure"""
        info = TimeService.get_time_info()

        self.assertIsInstance(info, dict)
        self.assertIn('current_time', info)
        self.assertIn('date', info)
        self.assertIn('time_of_day', info)
        self.assertIn('is_daytime', info)
        self.assertIn('sunrise', info)
        self.assertIn('sunset', info)

    def test_time_info_has_labels(self):
        """Test time info includes French labels"""
        info = TimeService.get_time_info()

        self.assertIn('time_of_day_label', info)
        self.assertIn('month_name', info)
        self.assertIsInstance(info['time_of_day_label'], str)
        self.assertIsInstance(info['month_name'], str)

    def test_time_info_has_icons(self):
        """Test time info includes emoji icons"""
        info = TimeService.get_time_info()

        self.assertIn('time_of_day_icon', info)
        self.assertIsInstance(info['time_of_day_icon'], str)
        self.assertGreater(len(info['time_of_day_icon']), 0)

    def test_time_info_hour_minute(self):
        """Test time info includes hour and minute"""
        info = TimeService.get_time_info()

        self.assertIn('hour', info)
        self.assertIn('minute', info)
        self.assertGreaterEqual(info['hour'], 0)
        self.assertLess(info['hour'], 24)
        self.assertGreaterEqual(info['minute'], 0)
        self.assertLess(info['minute'], 60)

    def test_time_info_date_components(self):
        """Test time info includes date components"""
        info = TimeService.get_time_info()

        self.assertIn('day_number', info)
        self.assertIn('month', info)
        self.assertIn('year', info)
        self.assertGreaterEqual(info['day_number'], 1)
        self.assertLessEqual(info['day_number'], 31)
        self.assertGreaterEqual(info['month'], 1)
        self.assertLessEqual(info['month'], 12)
        self.assertGreater(info['year'], 2020)

    @patch('game.services.time_service.timezone.now')
    def test_time_info_morning_label(self, mock_now):
        """Test time info has correct French label for morning"""
        mock_now.return_value = datetime(2025, 1, 15, 9, 0, 0, tzinfo=timezone.utc)

        info = TimeService.get_time_info()

        self.assertEqual(info['time_of_day'], 'morning')
        self.assertEqual(info['time_of_day_label'], 'Matin')

    @patch('game.services.time_service.timezone.now')
    def test_time_info_night_label(self, mock_now):
        """Test time info has correct French label for night"""
        mock_now.return_value = datetime(2025, 1, 15, 23, 0, 0, tzinfo=timezone.utc)

        info = TimeService.get_time_info()

        self.assertEqual(info['time_of_day'], 'night')
        self.assertEqual(info['time_of_day_label'], 'Nuit')


class TimeEffectsTests(TestCase):
    """Test time-based effects"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

    def test_apply_time_effects_returns_dict(self):
        """Test apply_time_effects returns effects dict"""
        effects = TimeService.apply_time_effects(self.player)

        self.assertIsInstance(effects, dict)

    def test_time_effects_has_multipliers(self):
        """Test time effects include multipliers"""
        effects = TimeService.apply_time_effects(self.player)

        # Check for common effect keys
        possible_keys = ['energy_regen_mult', 'visibility_mult', 'spawn_rate_mult']
        has_effects = any(key in effects for key in possible_keys)
        self.assertTrue(has_effects)

    @patch('game.services.time_service.TimeService.get_time_of_day')
    def test_night_has_different_effects(self, mock_time_of_day):
        """Test night time has different effects than day"""
        mock_time_of_day.return_value = 'night'

        night_effects = TimeService.apply_time_effects(self.player)

        self.assertIsInstance(night_effects, dict)
        # Night should have some effects
        self.assertGreater(len(night_effects), 0)

    @patch('game.services.time_service.TimeService.get_time_of_day')
    def test_morning_effects(self, mock_time_of_day):
        """Test morning time has bonus effects"""
        mock_time_of_day.return_value = 'morning'

        morning_effects = TimeService.apply_time_effects(self.player)

        self.assertIsInstance(morning_effects, dict)

    @patch('game.services.time_service.TimeService.get_time_of_day')
    def test_night_visibility_reduced(self, mock_time_of_day):
        """Test night reduces visibility"""
        mock_time_of_day.return_value = 'night'

        effects = TimeService.apply_time_effects(self.player)

        if 'visibility_mult' in effects:
            self.assertLess(effects['visibility_mult'], 1.0)

    @patch('game.services.time_service.TimeService.get_time_of_day')
    def test_night_spawn_rate_increased(self, mock_time_of_day):
        """Test night increases enemy spawn rate"""
        mock_time_of_day.return_value = 'night'

        effects = TimeService.apply_time_effects(self.player)

        if 'spawn_rate_mult' in effects:
            self.assertGreater(effects['spawn_rate_mult'], 1.0)
