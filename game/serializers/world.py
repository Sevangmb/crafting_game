from rest_framework import serializers
from ..models import MapCell, CellMaterial, GatheringLog
from .items import MaterialSerializer, DroppedItemSerializer

class CellMaterialSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = CellMaterial
        fields = '__all__'

class MapCellSerializer(serializers.ModelSerializer):
    materials = CellMaterialSerializer(many=True, read_only=True)
    dropped_items = DroppedItemSerializer(many=True, read_only=True)
    buildings = serializers.SerializerMethodField()

    class Meta:
        model = MapCell
        fields = '__all__'

    def get_buildings(self, obj):
        """Get buildings on this cell"""
        from game.services import building_service
        return building_service.get_cell_buildings(obj)

class GatheringLogSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = GatheringLog
        fields = '__all__'
