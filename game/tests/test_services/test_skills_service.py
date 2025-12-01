"""
Test Skills Service

Tests for skills, XP, and talent management.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Player, Skill, PlayerSkill, TalentNode, PlayerTalent, GameConfig
from game.services.skills_service import (
    ensure_default_skills,
    get_or_create_player_skill,
    award_xp,
    auto_unlock_talents,
    get_active_effects
)


class SkillsServiceTestCase(TestCase):
    """Test suite for skills service functions"""
    
    def setUp(self):
        """Create test data before each test"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(user=self.user)
        
        # Create test skill
        self.skill, _ = Skill.objects.get_or_create(
            code='gathering',
            defaults={
                'name': 'Gathering',
                'description': 'Test gathering skill'
            }
        )
        
        # Set default config
        GameConfig.objects.get_or_create(
            key='default_skill_xp_to_next',
            defaults={'value': '50'}
        )
        GameConfig.objects.get_or_create(
            key='skill_level_multiplier',
            defaults={'value': '50'}
        )
    
    def test_ensure_default_skills_creates_crafting(self):
        """Test that ensure_default_skills creates the crafting skill"""
        ensure_default_skills()
        self.assertTrue(Skill.objects.filter(code='crafting').exists())
    
    def test_get_or_create_player_skill_creates_new(self):
        """Test creating a new PlayerSkill"""
        player_skill = get_or_create_player_skill(self.player, 'gathering')
        
        self.assertIsNotNone(player_skill)
        self.assertEqual(player_skill.player, self.player)
        self.assertEqual(player_skill.skill, self.skill)
        self.assertEqual(player_skill.level, 1)
        self.assertEqual(player_skill.xp, 0)
        self.assertEqual(player_skill.total_xp, 0)
    
    def test_get_or_create_player_skill_returns_existing(self):
        """Test that get_or_create returns existing PlayerSkill"""
        # Create initial skill
        ps1 = get_or_create_player_skill(self.player, 'gathering')
        ps1.xp = 25
        ps1.save()
        
        # Get it again
        ps2 = get_or_create_player_skill(self.player, 'gathering')
        
        self.assertEqual(ps1.id, ps2.id)
        self.assertEqual(ps2.xp, 25)
    
    def test_award_xp_increases_total_xp(self):
        """Test that awarding XP increases total XP"""
        player_skill, leveled = award_xp(self.player, 'gathering', 30)
        
        self.assertEqual(player_skill.xp, 30)
        self.assertEqual(player_skill.total_xp, 30)
        self.assertFalse(leveled)
    
    def test_award_xp_levels_up_when_threshold_reached(self):
        """Test that player levels up when XP threshold is reached"""
        player_skill, leveled = award_xp(self.player, 'gathering', 100)

        self.assertTrue(leveled)
        self.assertEqual(player_skill.level, 2)  # Started at 1, gained 100 XP (50 for first level, 50/100 for next)
        self.assertEqual(player_skill.total_xp, 100)
        self.assertEqual(player_skill.xp, 50)  # 50 XP remaining towards level 3
    
    def test_award_xp_multiple_level_ups(self):
        """Test multiple level ups from single XP award"""
        player_skill, leveled = award_xp(self.player, 'gathering', 250)
        
        self.assertTrue(leveled)
        self.assertGreater(player_skill.level, 1)
        self.assertEqual(player_skill.total_xp, 250)
    
    def test_auto_unlock_talents_with_no_prerequisites(self):
        """Test unlocking talents with no prerequisites"""
        # Create a talent with no prerequisites
        talent = TalentNode.objects.create(
            skill=self.skill,
            code='gather_basic',
            name='Basic Gathering',
            tier=1,
            xp_required=0,
            effect_type='gather_bonus',
            effect_value=5
        )

        # Create PlayerSkill first
        get_or_create_player_skill(self.player, 'gathering')
        auto_unlock_talents(self.player, 'gathering')
        
        self.assertTrue(
            PlayerTalent.objects.filter(player=self.player, talent_node=talent).exists()
        )
    
    def test_auto_unlock_talents_respects_xp_requirement(self):
        """Test that talents are not unlocked without sufficient XP"""
        talent = TalentNode.objects.create(
            skill=self.skill,
            code='gather_advanced',
            name='Advanced Gathering',
            tier=2,
            xp_required=100,
            effect_type='gather_bonus',
            effect_value=10
        )
        
        # Award only 50 XP
        award_xp(self.player, 'gathering', 50)
        
        self.assertFalse(
            PlayerTalent.objects.filter(player=self.player, talent_node=talent).exists()
        )
        
        # Award more XP to reach threshold
        award_xp(self.player, 'gathering', 60)
        
        self.assertTrue(
            PlayerTalent.objects.filter(player=self.player, talent_node=talent).exists()
        )
    
    def test_auto_unlock_talents_respects_prerequisites(self):
        """Test that talents require prerequisites to be unlocked"""
        # Create prerequisite talent
        prereq_talent = TalentNode.objects.create(
            skill=self.skill,
            code='gather_basic',
            name='Basic Gathering',
            tier=1,
            xp_required=0,
            effect_type='gather_bonus',
            effect_value=5
        )
        
        # Create talent with prerequisite
        advanced_talent = TalentNode.objects.create(
            skill=self.skill,
            code='gather_advanced',
            name='Advanced Gathering',
            tier=2,
            xp_required=50,
            prereq_codes=['gather_basic'],
            effect_type='gather_bonus',
            effect_value=10
        )
        
        # Award enough XP but don't unlock prerequisite
        ps = get_or_create_player_skill(self.player, 'gathering')
        ps.total_xp = 100
        ps.save()
        
        auto_unlock_talents(self.player, 'gathering')
        
        # Should have prerequisite but not advanced
        self.assertTrue(
            PlayerTalent.objects.filter(player=self.player, talent_node=prereq_talent).exists()
        )
        self.assertTrue(
            PlayerTalent.objects.filter(player=self.player, talent_node=advanced_talent).exists()
        )
    
    def test_get_active_effects_returns_empty_for_no_talents(self):
        """Test that get_active_effects returns empty dict when no talents"""
        effects = get_active_effects(self.player, 'gathering')
        
        self.assertEqual(effects, {})
    
    def test_get_active_effects_returns_talent_effects(self):
        """Test that get_active_effects returns correct talent effects"""
        # Create and unlock talents
        talent1 = TalentNode.objects.create(
            skill=self.skill,
            code='gather_bonus_1',
            name='Gather Bonus 1',
            tier=1,
            xp_required=0,
            effect_type='gather_bonus',
            effect_value=5
        )
        
        talent2 = TalentNode.objects.create(
            skill=self.skill,
            code='cost_reduction_1',
            name='Cost Reduction 1',
            tier=1,
            xp_required=0,
            effect_type='gather_cost_reduction',
            effect_value=2
        )
        
        PlayerTalent.objects.create(player=self.player, talent_node=talent1)
        PlayerTalent.objects.create(player=self.player, talent_node=talent2)
        
        effects = get_active_effects(self.player, 'gathering')
        
        self.assertEqual(effects['gather_bonus'], 5)
        self.assertEqual(effects['gather_cost_reduction'], 2)
    
    def test_get_active_effects_returns_max_value_for_duplicate_types(self):
        """Test that get_active_effects returns max value when multiple talents have same effect type"""
        talent1 = TalentNode.objects.create(
            skill=self.skill,
            code='gather_bonus_1',
            name='Gather Bonus 1',
            tier=1,
            xp_required=0,
            effect_type='gather_bonus',
            effect_value=5
        )
        
        talent2 = TalentNode.objects.create(
            skill=self.skill,
            code='gather_bonus_2',
            name='Gather Bonus 2',
            tier=2,
            xp_required=0,
            effect_type='gather_bonus',
            effect_value=10
        )
        
        PlayerTalent.objects.create(player=self.player, talent_node=talent1)
        PlayerTalent.objects.create(player=self.player, talent_node=talent2)
        
        effects = get_active_effects(self.player, 'gathering')
        
        # Should return the maximum value (10, not 5)
        self.assertEqual(effects['gather_bonus'], 10)
