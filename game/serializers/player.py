from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Player, Inventory, PlayerWorkstation, PlayerSkill, PlayerTalent, PlayerAchievement, PlayerQuest
from .items import MaterialSerializer, EquippedItemSerializer
from .crafting import WorkstationSerializer
from .skills import SkillSerializer, TalentNodeSerializer
from .achievements import AchievementSerializer
from .quests import QuestSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class InventorySerializer(serializers.ModelSerializer):
    material = MaterialSerializer()
    category = serializers.CharField(source='material.category', read_only=True)
    durability_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = ['id', 'material', 'quantity', 'category', 'durability_current', 'durability_max', 'durability_percentage']
        read_only_fields = ['player']

    def get_durability_percentage(self, obj):
        if obj.durability_max == 0:
            return 100
        return int((obj.durability_current / obj.durability_max) * 100) if obj.durability_max > 0 else 100

class PlayerWorkstationSerializer(serializers.ModelSerializer):
    workstation = WorkstationSerializer(read_only=True)

    class Meta:
        model = PlayerWorkstation
        fields = '__all__'

class PlayerSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = PlayerSkill
        fields = ['id', 'skill', 'level', 'xp', 'xp_to_next', 'total_xp']

class PlayerTalentSerializer(serializers.ModelSerializer):
    talent_node = TalentNodeSerializer(read_only=True)

    class Meta:
        model = PlayerTalent
        fields = ['id', 'talent_node', 'unlocked_at']

class PlayerAchievementSerializer(serializers.ModelSerializer):
    """Serializer for player achievement progress"""
    achievement = AchievementSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = PlayerAchievement
        fields = ['id', 'achievement', 'progress', 'completed', 'completed_at', 'progress_percentage']

    def get_progress_percentage(self, obj):
        """Calculate progress percentage"""
        if obj.achievement.requirement_value == 0:
            return 100 if obj.completed else 0
        return min(100, int((obj.progress / obj.achievement.requirement_value) * 100))

class PlayerQuestSerializer(serializers.ModelSerializer):
    """Serializer for player quests with progress"""
    quest = QuestSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PlayerQuest
        fields = ['id', 'quest', 'status', 'status_display', 'progress', 'progress_percentage',
                  'accepted_at', 'completed_at', 'can_repeat_at', 'times_completed']

    def get_progress_percentage(self, obj):
        return obj.progress_percentage()

class PlayerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    inventory = InventorySerializer(many=True, read_only=True)
    workstations = PlayerWorkstationSerializer(many=True, read_only=True)
    equipped_items = EquippedItemSerializer(many=True, read_only=True)
    current_carry_weight = serializers.FloatField(read_only=True)
    effective_carry_capacity = serializers.FloatField(read_only=True)
    is_overencumbered = serializers.BooleanField(read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'user', 'current_x', 'current_y', 'grid_x', 'grid_y',
                 'energy', 'max_energy', 'health', 'max_health',
                 'hunger', 'max_hunger', 'thirst', 'max_thirst', 'radiation',
                 'satiety', 'hydration', 'metabolism_rate',
                 'strength', 'agility', 'intelligence', 'luck',
                 'level', 'experience', 'money', 'credit_card_balance', 'inventory',
                 'workstations', 'equipped_items',
                 'total_defense', 'total_attack', 'total_speed_bonus',
                 'current_carry_weight', 'effective_carry_capacity', 'is_overencumbered']
