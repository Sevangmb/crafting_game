from rest_framework import serializers
from ..models import Achievement

class AchievementSerializer(serializers.ModelSerializer):
    """Serializer for achievements"""
    class Meta:
        model = Achievement
        fields = [
            'id', 'name', 'description', 'icon', 'category',
            'requirement_type', 'requirement_value', 'requirement_target',
            'reward_xp', 'hidden', 'created_at'
        ]
