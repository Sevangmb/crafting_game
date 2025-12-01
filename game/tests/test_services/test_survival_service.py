from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from game.models import Player, Material
from game.services.survival_service import SurvivalService

class SurvivalServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.player = Player.objects.create(
            user=self.user,
            hunger=50,
            thirst=50,
            health=50,
            max_health=100,
            max_energy=100
        )
        
        self.food = Material.objects.create(
            name='Apple',
            is_food=True,
            hunger_restore=10,
            thirst_restore=5,
            health_restore=2,
            energy_restore=5
        )

    def tearDown(self):
        """Clean up after each test"""
        # Clean up database objects
        Material.objects.all().delete()
        Player.objects.all().delete()
        User.objects.all().delete()


    def test_update_survival_stats(self):
        # Simulate time passing
        now = timezone.now()
        self.player.last_hunger_update = now - timedelta(minutes=60)
        self.player.last_thirst_update = now - timedelta(minutes=60)
        self.player.save()
        
        result = SurvivalService.update_survival_stats(self.player, activity='walking')
        
        self.player.refresh_from_db()
        # Stats should decrease
        self.assertLess(self.player.hunger, 50)
        self.assertLess(self.player.thirst, 50)
        
        # Check result structure
        self.assertIn('hunger', result)
        self.assertIn('thirst', result)
        self.assertIn('health', result)

    def test_consume_food(self):
        result = SurvivalService.consume_food(self.player, self.food)
        
        self.player.refresh_from_db()
        self.assertEqual(self.player.hunger, 60) # 50 + 10
        self.assertEqual(self.player.thirst, 55) # 50 + 5
        self.assertEqual(self.player.health, 52) # 50 + 2
        
        self.assertIn('hunger_restored', result)
        self.assertEqual(result['hunger_restored'], 10)

    def test_regenerate_health(self):
        # Set conditions for regen (well fed/hydrated)
        self.player.hunger = 90
        self.player.thirst = 90
        self.player.save()
        
        regen = SurvivalService.regenerate_health(self.player, minutes_passed=10)
        
        self.assertGreater(regen, 0)
        self.player.refresh_from_db()
        self.assertGreater(self.player.health, 50)

    def test_starvation_damage(self):
        # Set starving
        self.player.hunger = 0
        self.player.save()
        
        effects = SurvivalService.apply_survival_effects(self.player, minutes_passed=60)
        
        self.player.refresh_from_db()
        self.assertLess(self.player.health, 50)
        self.assertTrue(any('Famine' in e for e in effects))

    def test_check_can_act(self):
        # Normal state
        can_act, msg = SurvivalService.check_can_act(self.player)
        self.assertTrue(can_act)
        
        # Dead state
        self.player.health = 0
        self.player.save()
        can_act, msg = SurvivalService.check_can_act(self.player)
        self.assertFalse(can_act)
        self.assertIn('mort', msg)

    def test_environment_effects(self):
        # Test winter cold
        initial_hunger = self.player.hunger
        SurvivalService.adjust_survival_for_environment(
            self.player, 
            season='winter', 
            biome='plains', 
            weather='clear', 
            time_of_day='day'
        )
        
        self.player.refresh_from_db()
        self.assertLess(self.player.hunger, initial_hunger)

    def test_get_survival_status(self):
        status = SurvivalService.get_survival_status(self.player)
        self.assertIsInstance(status, list)
        self.assertTrue(len(status) > 0)
