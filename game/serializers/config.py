from rest_framework import serializers
from ..models import GameConfig

class GameConfigSerializer(serializers.ModelSerializer):
    """Serializer for game configuration with automatic JSON parsing"""
    parsed_value = serializers.SerializerMethodField()

    class Meta:
        model = GameConfig
        fields = ['id', 'key', 'value', 'parsed_value', 'description']

    def get_parsed_value(self, obj):
        """Return the parsed JSON value"""
        return obj.get_value()
