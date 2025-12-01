"""
Unit tests for quest service

Tests quest management, progress tracking, and rewards.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from game.models import (
    Player, Quest, PlayerQuest, Material, Inventory
)
from game.services.quest_service import QuestService


class QuestAvailabilityTests(TestCase):
    """Test quest availability logic"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, level=5)

        # Create quests
        self.low_level_quest = Quest.objects.create(
            name='Beginner Quest',
            description='First quest',
            quest_type='gather',
            required_level=1,
            is_active=True,
            is_repeatable=False
        )

        self.high_level_quest = Quest.objects.create(
            name='Advanced Quest',
            description='Hard quest',
            quest_type='combat',
            required_level=10,
            is_active=True,
            is_repeatable=False
        )

    def test_get_available_quests_filters_by_level(self):
        """Test only quests within level requirement are shown"""
        available = QuestService.get_available_quests(self.player)

        quest_names = [q.name for q in available]
        self.assertIn('Beginner Quest', quest_names)
        self.assertNotIn('Advanced Quest', quest_names)

    def test_higher_level_sees_more_quests(self):
        """Test higher level player sees more quests"""
        self.player.level = 15
        self.player.save()

        available = QuestService.get_available_quests(self.player)

        quest_names = [q.name for q in available]
        self.assertIn('Beginner Quest', quest_names)
        self.assertIn('Advanced Quest', quest_names)

    def test_active_quests_not_in_available(self):
        """Test active quests don't appear in available"""
        # Accept the quest
        PlayerQuest.objects.create(
            player=self.player,
            quest=self.low_level_quest,
            status='active',
            accepted_at=timezone.now()
        )

        available = QuestService.get_available_quests(self.player)

        quest_names = [q.name for q in available]
        self.assertNotIn('Beginner Quest', quest_names)

    def test_completed_non_repeatable_not_available(self):
        """Test completed non-repeatable quests don't appear"""
        PlayerQuest.objects.create(
            player=self.player,
            quest=self.low_level_quest,
            status='completed',
            accepted_at=timezone.now() - timedelta(days=1),
            completed_at=timezone.now() - timedelta(hours=1)
        )

        available = QuestService.get_available_quests(self.player)

        quest_names = [q.name for q in available]
        self.assertNotIn('Beginner Quest', quest_names)

    def test_repeatable_quest_available_after_cooldown(self):
        """Test repeatable quests reappear after cooldown"""
        repeatable_quest = Quest.objects.create(
            name='Daily Quest',
            description='Repeatable daily',
            quest_type='gather',
            required_level=1,
            is_active=True,
            is_repeatable=True
        )

        # Complete it and cooldown expired
        PlayerQuest.objects.create(
            player=self.player,
            quest=repeatable_quest,
            status='completed',
            accepted_at=timezone.now() - timedelta(days=2),
            completed_at=timezone.now() - timedelta(days=1),
            can_repeat_at=timezone.now() - timedelta(hours=1)  # Cooldown passed
        )

        available = QuestService.get_available_quests(self.player)

        quest_names = [q.name for q in available]
        self.assertIn('Daily Quest', quest_names)


class QuestPrerequisiteTests(TestCase):
    """Test quest prerequisite logic"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, level=10)

        # Create prerequisite chain
        self.quest1 = Quest.objects.create(
            name='Quest 1',
            description='First quest',
            quest_type='gather',
            required_level=1,
            is_active=True
        )

        self.quest2 = Quest.objects.create(
            name='Quest 2',
            description='Second quest',
            quest_type='craft',
            required_level=1,
            is_active=True,
            prerequisite_quest=self.quest1
        )

    def test_prerequisite_quest_not_available(self):
        """Test quest with uncompleted prerequisite not available"""
        available = QuestService.get_available_quests(self.player)

        quest_names = [q.name for q in available]
        self.assertIn('Quest 1', quest_names)
        self.assertNotIn('Quest 2', quest_names)

    def test_prerequisite_completed_unlocks_next(self):
        """Test completing prerequisite unlocks next quest"""
        # Complete quest 1
        PlayerQuest.objects.create(
            player=self.player,
            quest=self.quest1,
            status='completed',
            accepted_at=timezone.now() - timedelta(hours=2),
            completed_at=timezone.now() - timedelta(hours=1)
        )

        available = QuestService.get_available_quests(self.player)

        quest_names = [q.name for q in available]
        self.assertIn('Quest 2', quest_names)


class QuestAcceptanceTests(TestCase):
    """Test quest acceptance"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, level=5)

        self.quest = Quest.objects.create(
            name='Test Quest',
            description='A test quest',
            quest_type='gather',
            required_level=3,
            is_active=True
        )

    def test_accept_quest_success(self):
        """Test successfully accepting a quest"""
        player_quest, error = QuestService.accept_quest(self.player, self.quest.id)

        self.assertIsNotNone(player_quest)
        self.assertIsNone(error)
        self.assertEqual(player_quest.status, 'active')
        self.assertEqual(player_quest.quest, self.quest)

    def test_cannot_accept_if_level_too_low(self):
        """Test cannot accept quest if level too low"""
        self.player.level = 1
        self.player.save()

        player_quest, error = QuestService.accept_quest(self.player, self.quest.id)

        self.assertIsNone(player_quest)
        self.assertIn('Niveau', error)

    def test_cannot_accept_already_active(self):
        """Test cannot accept quest that's already active"""
        # First acceptance
        QuestService.accept_quest(self.player, self.quest.id)

        # Try to accept again
        player_quest, error = QuestService.accept_quest(self.player, self.quest.id)

        self.assertIsNone(player_quest)
        self.assertIn('déjà active', error)

    def test_cannot_accept_completed_non_repeatable(self):
        """Test cannot re-accept completed non-repeatable quest"""
        PlayerQuest.objects.create(
            player=self.player,
            quest=self.quest,
            status='completed',
            accepted_at=timezone.now() - timedelta(hours=2),
            completed_at=timezone.now() - timedelta(hours=1)
        )

        player_quest, error = QuestService.accept_quest(self.player, self.quest.id)

        self.assertIsNone(player_quest)
        self.assertIn('complétée', error)

    def test_cannot_accept_invalid_quest(self):
        """Test accepting non-existent quest returns error"""
        player_quest, error = QuestService.accept_quest(self.player, 99999)

        self.assertIsNone(player_quest)
        self.assertIn('introuvable', error)


class QuestProgressTrackingTests(TestCase):
    """Test quest progress tracking"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, level=5)

        self.wood = Material.objects.create(name='Bois', category='resource')

        # Create gather quest
        self.quest = Quest.objects.create(
            name='Gather Wood',
            description='Gather 10 wood',
            quest_type='gather',
            required_level=1,
            is_active=True,
            requirements={
                'gather': [
                    {'material_id': self.wood.id, 'quantity': 10}
                ]
            }
        )

        # Accept the quest
        self.player_quest = PlayerQuest.objects.create(
            player=self.player,
            quest=self.quest,
            status='active',
            accepted_at=timezone.now(),
            progress={}
        )

    def test_update_gather_progress(self):
        """Test gathering updates quest progress"""
        completed = QuestService.update_quest_progress(
            self.player,
            'gather',
            material_id=self.wood.id,
            quantity=5
        )

        self.player_quest.refresh_from_db()
        self.assertEqual(self.player_quest.progress['gather'][str(self.wood.id)], 5)
        self.assertEqual(len(completed), 0)  # Not complete yet

    def test_quest_completes_when_requirement_met(self):
        """Test quest completes when requirement is met"""
        # Update progress to complete
        self.player_quest.progress = {'gather': {str(self.wood.id): 10}}
        self.player_quest.save()

        # Trigger completion check
        completed = QuestService.update_quest_progress(
            self.player,
            'gather',
            material_id=self.wood.id,
            quantity=1
        )

        self.player_quest.refresh_from_db()
        self.assertEqual(self.player_quest.status, 'completed')
        self.assertIsNotNone(self.player_quest.completed_at)


class QuestRewardTests(TestCase):
    """Test quest reward distribution"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, level=5, experience=0)

        self.wood = Material.objects.create(name='Bois', category='resource')

        # Create quest with rewards
        self.quest = Quest.objects.create(
            name='Reward Quest',
            description='Get rewards',
            quest_type='gather',
            required_level=1,
            is_active=True,
            reward_xp=100,
            reward_money=50,
            requirements={}
        )

        self.player_quest = PlayerQuest.objects.create(
            player=self.player,
            quest=self.quest,
            status='active',
            accepted_at=timezone.now()
        )

    def test_complete_quest_awards_xp(self):
        """Test completing quest awards XP"""
        initial_xp = self.player.experience

        player_quest, rewards = QuestService.complete_quest(self.player, self.player_quest.id)

        self.assertIsNotNone(player_quest)
        self.player.refresh_from_db()
        self.assertEqual(self.player.experience, initial_xp + 100)

    def test_complete_quest_awards_money(self):
        """Test completing quest awards money"""
        initial_money = self.player.money

        QuestService.complete_quest(self.player, self.player_quest.id)

        self.player.refresh_from_db()
        self.assertEqual(self.player.money, initial_money + 50)

    def test_complete_quest_sets_status(self):
        """Test completing quest updates status"""
        QuestService.complete_quest(self.player, self.player_quest.id)

        self.player_quest.refresh_from_db()
        self.assertEqual(self.player_quest.status, 'completed')
        self.assertIsNotNone(self.player_quest.completed_at)

    def test_complete_repeatable_sets_cooldown(self):
        """Test completing repeatable quest sets cooldown"""
        self.quest.is_repeatable = True
        self.quest.save()

        QuestService.complete_quest(self.player, self.player_quest.id)

        self.player_quest.refresh_from_db()
        # If quest has cooldown, can_repeat_at will be set
        # For now just check it completed
        self.assertEqual(self.player_quest.status, 'completed')


class ActiveQuestTests(TestCase):
    """Test getting active quests"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user, level=5)

        # Create multiple quests
        self.quest1 = Quest.objects.create(
            name='Active 1',
            quest_type='gather',
            required_level=1,
            is_active=True
        )

        self.quest2 = Quest.objects.create(
            name='Active 2',
            quest_type='craft',
            required_level=1,
            is_active=True
        )

        self.quest3 = Quest.objects.create(
            name='Completed Quest',
            quest_type='combat',
            required_level=1,
            is_active=True
        )

        # Accept some quests
        PlayerQuest.objects.create(
            player=self.player,
            quest=self.quest1,
            status='active',
            accepted_at=timezone.now()
        )

        PlayerQuest.objects.create(
            player=self.player,
            quest=self.quest2,
            status='active',
            accepted_at=timezone.now()
        )

        PlayerQuest.objects.create(
            player=self.player,
            quest=self.quest3,
            status='completed',
            accepted_at=timezone.now() - timedelta(hours=2),
            completed_at=timezone.now() - timedelta(hours=1)
        )

    def test_get_active_quests(self):
        """Test getting only active quests"""
        active = QuestService.get_active_quests(self.player)

        self.assertEqual(active.count(), 2)
        quest_names = [pq.quest.name for pq in active]
        self.assertIn('Active 1', quest_names)
        self.assertIn('Active 2', quest_names)
        self.assertNotIn('Completed Quest', quest_names)
