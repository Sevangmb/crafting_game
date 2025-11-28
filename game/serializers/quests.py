from rest_framework import serializers
from ..models import Quest

class QuestSerializer(serializers.ModelSerializer):
    """Serializer for quests"""
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    type_display = serializers.CharField(source='get_quest_type_display', read_only=True)

    class Meta:
        model = Quest
        fields = ['id', 'name', 'description', 'story_text', 'icon', 'quest_type', 'type_display',
                 'difficulty', 'difficulty_display', 'required_level', 'requirements',
                 'reward_xp', 'reward_money', 'reward_items', 'is_repeatable',
                 'cooldown_hours', 'start_npc', 'prerequisite_quest']
