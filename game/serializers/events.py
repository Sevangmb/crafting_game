from rest_framework import serializers
from ..models import DynamicEvent

class DynamicEventSerializer(serializers.ModelSerializer):
    """Serializer for dynamic events"""
    type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    cell_info = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = DynamicEvent
        fields = ['id', 'name', 'description', 'icon', 'event_type', 'type_display',
                 'cell_info', 'rewards', 'started_at', 'expires_at', 'is_active',
                 'is_expired', 'max_participants', 'participant_count']

    def get_cell_info(self, obj):
        return {
            'grid_x': obj.cell.grid_x,
            'grid_y': obj.cell.grid_y,
            'biome': obj.cell.biome
        }

    def get_is_expired(self, obj):
        return obj.is_expired()

    def get_participant_count(self, obj):
        return obj.participants.count()
