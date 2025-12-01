"""
Unit tests for achievement service

Tests achievement tracking, unlocking, and progress.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from game.models import (
    Player, Achievement, PlayerAchievement,
    Material, GatheringLog, CraftingLog, Recipe,
    MapCell, Building, BuildingType
)
from game.services.achievement_service import (
    AchievementService,
    check_achievements
)


class AchievementUnlockingTests(TestCase):
    """Test achievement unlocking mechanics"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            level=1,
            experience=0,
            total_moves=0
        )

        # Create test cell
        self.cell = MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            center_lat=44.933,
            center_lon=4.893,
            biome='plains'
        )

        # Create achievements
        self.gather_achievement = Achievement.objects.create(
            name='First Gatherer',
            description='Gather 10 times',
            requirement_type='gather_count',
            requirement_value=10,
            reward_xp=50
        )

        self.level_achievement = Achievement.objects.create(
            name='Level 5',
            description='Reach level 5',
            requirement_type='level_reached',
            requirement_value=5,
            reward_xp=100
        )

    def test_achievement_unlocks_on_completion(self):
        """Test achievement unlocks when requirement is met"""
        # Create 10 gathering logs
        wood = Material.objects.create(name='Bois', category='resource')
        for i in range(10):
            GatheringLog.objects.create(
                player=self.player,
                material=wood,
                quantity=1,
                cell=self.cell
            )

        # Check achievements
        completed = check_achievements(self.player, 'gather')

        # Should have unlocked the achievement
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0], self.gather_achievement)

        # Check player achievement record
        pa = PlayerAchievement.objects.get(
            player=self.player,
            achievement=self.gather_achievement
        )
        self.assertTrue(pa.completed)
        self.assertIsNotNone(pa.completed_at)
        self.assertEqual(pa.progress, 10)

    def test_xp_awarded_on_achievement(self):
        """Test XP is awarded when achievement unlocks"""
        initial_xp = self.player.experience

        # Create 10 gathering logs
        wood = Material.objects.create(name='Bois', category='resource')
        for i in range(10):
            GatheringLog.objects.create(
                player=self.player,
                material=wood,
                quantity=1,
                cell=self.cell
            )

        check_achievements(self.player, 'gather')
        self.player.refresh_from_db()

        # Should have gained XP
        self.assertEqual(self.player.experience, initial_xp + 50)

    def test_achievement_not_unlocked_if_incomplete(self):
        """Test achievement doesn't unlock if progress insufficient"""
        # Only 5 gatherings (need 10)
        wood = Material.objects.create(name='Bois', category='resource')
        for i in range(5):
            GatheringLog.objects.create(
                player=self.player,
                material=wood,
                quantity=1,
                cell=self.cell
            )

        completed = check_achievements(self.player, 'gather')

        # Should not have unlocked
        self.assertEqual(len(completed), 0)

        # Progress should be tracked
        pa = PlayerAchievement.objects.get(
            player=self.player,
            achievement=self.gather_achievement
        )
        self.assertFalse(pa.completed)
        self.assertEqual(pa.progress, 5)

    def test_achievement_not_unlocked_twice(self):
        """Test already completed achievement is not re-awarded"""
        # Mark achievement as completed
        PlayerAchievement.objects.create(
            player=self.player,
            achievement=self.gather_achievement,
            progress=10,
            completed=True,
            completed_at=timezone.now()
        )

        initial_xp = self.player.experience

        # Try to trigger again
        wood = Material.objects.create(name='Bois', category='resource')
        for i in range(15):
            GatheringLog.objects.create(
                player=self.player,
                material=wood,
                quantity=1,
                cell=self.cell
            )

        completed = check_achievements(self.player, 'gather')

        # Should not unlock again
        self.assertEqual(len(completed), 0)
        self.player.refresh_from_db()
        self.assertEqual(self.player.experience, initial_xp)


class AchievementProgressTrackingTests(TestCase):
    """Test achievement progress tracking"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, total_moves=0)

        self.cell = MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            center_lat=44.933,
            center_lon=4.893,
            biome='plains'
        )

    def test_gather_count_tracking(self):
        """Test gather_count type tracks total gatherings"""
        achievement = Achievement.objects.create(
            name='Gatherer',
            requirement_type='gather_count',
            requirement_value=20
        )

        wood = Material.objects.create(name='Bois', category='resource')

        # Create 5 logs
        for i in range(5):
            GatheringLog.objects.create(
                player=self.player,
                material=wood,
                quantity=1,
                cell=self.cell
            )

        check_achievements(self.player, 'gather')

        pa = PlayerAchievement.objects.get(player=self.player, achievement=achievement)
        self.assertEqual(pa.progress, 5)

    def test_craft_count_tracking(self):
        """Test craft_count type tracks total crafts"""
        achievement = Achievement.objects.create(
            name='Crafter',
            requirement_type='craft_count',
            requirement_value=15
        )

        plank = Material.objects.create(name='Planche', category='crafted')
        recipe = Recipe.objects.create(result_material=plank, result_quantity=1)

        # Create 3 craft logs
        for i in range(3):
            CraftingLog.objects.create(
                player=self.player,
                recipe=recipe,
                quantity=1
            )

        check_achievements(self.player, 'craft')

        pa = PlayerAchievement.objects.get(player=self.player, achievement=achievement)
        self.assertEqual(pa.progress, 3)

    def test_move_count_tracking(self):
        """Test move_count type tracks player movements"""
        achievement = Achievement.objects.create(
            name='Explorer',
            requirement_type='move_count',
            requirement_value=100
        )

        self.player.total_moves = 50
        self.player.save()

        check_achievements(self.player, 'move')

        pa = PlayerAchievement.objects.get(player=self.player, achievement=achievement)
        self.assertEqual(pa.progress, 50)

    def test_level_reached_tracking(self):
        """Test level_reached type checks player level"""
        achievement = Achievement.objects.create(
            name='Level 10',
            requirement_type='level_reached',
            requirement_value=10
        )

        self.player.level = 8
        self.player.save()

        check_achievements(self.player, 'level_up')

        pa = PlayerAchievement.objects.get(player=self.player, achievement=achievement)
        self.assertEqual(pa.progress, 8)

    def test_material_collected_tracking(self):
        """Test material_collected type tracks specific materials"""
        achievement = Achievement.objects.create(
            name='Stone Collector',
            requirement_type='material_collected',
            requirement_target='Pierre',
            requirement_value=50
        )

        stone = Material.objects.create(name='Pierre', category='resource')

        # Gather stone 10 times
        for i in range(10):
            GatheringLog.objects.create(
                player=self.player,
                material=stone,
                quantity=5,
                cell=self.cell
            )

        check_achievements(self.player, 'gather', material_name='Pierre')

        pa = PlayerAchievement.objects.get(player=self.player, achievement=achievement)
        self.assertEqual(pa.progress, 10)


class AchievementListingTests(TestCase):
    """Test achievement listing functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)

        # Create visible achievement
        self.visible_achievement = Achievement.objects.create(
            name='Visible Achievement',
            requirement_type='gather_count',
            requirement_value=10,
            hidden=False
        )

        # Create hidden achievement
        self.hidden_achievement = Achievement.objects.create(
            name='Secret Achievement',
            requirement_type='craft_count',
            requirement_value=100,
            hidden=True
        )

        # Complete one achievement
        PlayerAchievement.objects.create(
            player=self.player,
            achievement=self.visible_achievement,
            progress=10,
            completed=True,
            completed_at=timezone.now()
        )

        # In progress achievement
        self.progress_achievement = Achievement.objects.create(
            name='In Progress',
            requirement_type='move_count',
            requirement_value=50,
            hidden=False
        )
        PlayerAchievement.objects.create(
            player=self.player,
            achievement=self.progress_achievement,
            progress=25,
            completed=False
        )

    def test_get_completed_achievements(self):
        """Test listing completed achievements"""
        result = AchievementService.get_player_achievements(self.player)

        completed = result['completed']
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0]['achievement'], self.visible_achievement)
        self.assertEqual(completed[0]['progress'], 10)
        self.assertIsNotNone(completed[0]['completed_at'])

    def test_get_in_progress_achievements(self):
        """Test listing in-progress achievements"""
        result = AchievementService.get_player_achievements(self.player)

        in_progress = result['in_progress']

        # Should have progress_achievement
        progress_names = [item['achievement'].name for item in in_progress]
        self.assertIn('In Progress', progress_names)

        # Find the specific one
        progress_item = next(
            item for item in in_progress
            if item['achievement'].name == 'In Progress'
        )
        self.assertEqual(progress_item['progress'], 25)
        self.assertEqual(progress_item['max_progress'], 50)

    def test_hidden_achievements_not_shown(self):
        """Test hidden achievements don't appear until started"""
        result = AchievementService.get_player_achievements(
            self.player,
            include_hidden=False
        )

        all_achievements = result['completed'] + result['in_progress']
        achievement_names = [item['achievement'].name for item in all_achievements]

        # Secret achievement shouldn't be visible
        self.assertNotIn('Secret Achievement', achievement_names)

    def test_include_hidden_shows_all(self):
        """Test include_hidden flag shows hidden achievements"""
        result = AchievementService.get_player_achievements(
            self.player,
            include_hidden=True
        )

        all_achievements = result['completed'] + result['in_progress']
        achievement_names = [item['achievement'].name for item in all_achievements]

        # Should include hidden achievement
        self.assertIn('Secret Achievement', achievement_names)


class BuildingAchievementsTests(TestCase):
    """Test building-related achievements"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, grid_x=0, grid_y=0)

        self.cell = MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            center_lat=44.933,
            center_lon=4.893,
            biome='plains'
        )

        self.shelter_type = BuildingType.objects.create(
            name='Shelter',
            category='housing',
            construction_time=60
        )

    def test_building_count_achievement(self):
        """Test building_count type counts total buildings"""
        achievement = Achievement.objects.create(
            name='Builder',
            requirement_type='building_count',
            requirement_value=5
        )

        # Create 3 buildings
        for i in range(1, 4):  # Start from 1 to avoid conflict with self.cell at (0,0)
            cell = MapCell.objects.create(
                grid_x=i,
                grid_y=0,
                center_lat=44.933 + i * 0.001,
                center_lon=4.893,
                biome='plains'
            )
            Building.objects.create(
                player=self.player,
                cell=cell,
                building_type=self.shelter_type,
                status='completed'
            )

        check_achievements(self.player, 'building_count')

        pa = PlayerAchievement.objects.get(player=self.player, achievement=achievement)
        self.assertEqual(pa.progress, 3)

    def test_specific_building_constructed(self):
        """Test building_constructed type tracks specific buildings"""
        achievement = Achievement.objects.create(
            name='Shelter Builder',
            requirement_type='building_constructed',
            requirement_target='Shelter',
            requirement_value=2
        )

        # Build 1 shelter
        Building.objects.create(
            player=self.player,
            cell=self.cell,
            building_type=self.shelter_type,
            status='completed'
        )

        check_achievements(
            self.player,
            'building_constructed',
            building_name='Shelter'
        )

        pa = PlayerAchievement.objects.get(player=self.player, achievement=achievement)
        self.assertEqual(pa.progress, 1)
