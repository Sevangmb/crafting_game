from rest_framework import serializers
from ..models import Workstation, Recipe, RecipeIngredient, CraftingLog, GameConfig
from .items import MaterialSerializer

class WorkstationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workstation
        fields = '__all__'

class RecipeIngredientSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    material_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'material', 'material_id', 'quantity']

class RecipeIngredientAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'recipe', 'material', 'quantity']

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    result_material = MaterialSerializer(read_only=True)
    required_workstation = WorkstationSerializer(read_only=True)
    energy_cost = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_energy_cost(self, obj):
        # Energy cost for crafting loaded from GameConfig
        try:
            cfg = GameConfig.get_config('crafting_config', {})
            return cfg.get('energy_cost_per_craft', 2)
        except Exception:
            return 2

class RecipeAdminSerializer(serializers.ModelSerializer):
    # writable foreign keys
    result_material_id = serializers.IntegerField(write_only=True, required=True)
    required_workstation_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'description', 'icon', 'result_material_id', 'result_quantity', 'required_workstation_id']

class CraftingLogSerializer(serializers.ModelSerializer):
    recipe = RecipeSerializer(read_only=True)

    class Meta:
        model = CraftingLog
        fields = '__all__'
