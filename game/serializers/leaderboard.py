from rest_framework import serializers
from ..models import Leaderboard

class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer for leaderboard entries"""
    player_name = serializers.CharField(source='player.user.username', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Leaderboard
        fields = ['id', 'category', 'category_display', 'player', 'player_name',
                 'score', 'rank', 'metadata', 'last_updated']
        read_only_fields = ['rank', 'score', 'last_updated']
