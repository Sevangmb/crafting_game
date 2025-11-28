from rest_framework import serializers
from ..models import BuildingType, BuildingRecipe, Building
from .items import MaterialSerializer

class BuildingRecipeSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = BuildingRecipe
        fields = ['id', 'material', 'quantity']

class BuildingTypeSerializer(serializers.ModelSerializer):
    recipe_materials = BuildingRecipeSerializer(many=True, read_only=True)

    class Meta:
        model = BuildingType
        fields = '__all__'

class BuildingSerializer(serializers.ModelSerializer):
    building_type = BuildingTypeSerializer(read_only=True)
    cell_info = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = '__all__'

    def get_cell_info(self, obj):
        return {
            'id': obj.cell.id,
            'grid_x': obj.cell.grid_x,
            'grid_y': obj.cell.grid_y,
            'biome': obj.cell.biome,
        }

    def get_owner(self, obj):
        return obj.player.user.username
