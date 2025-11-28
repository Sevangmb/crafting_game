"""
Complete character sheet serializer
SCUM-style detailed character information
"""
from rest_framework import serializers
from ..models import Player
from .health import PlayerBodyPartSerializer, PlayerDiseaseSerializer, PlayerHealthStatusSerializer
from .player import PlayerSkillSerializer


class MetabolismSerializer(serializers.Serializer):
    """Metabolism and nutrition details"""
    # Body composition
    body_weight = serializers.FloatField()
    muscle_mass = serializers.FloatField()
    body_fat = serializers.FloatField()
    bmi = serializers.FloatField()
    body_fat_percentage = serializers.FloatField()
    muscle_percentage = serializers.FloatField()
    fitness_level = serializers.CharField()

    # Energy and nutrition
    calories_stored = serializers.FloatField()
    max_calories = serializers.FloatField()
    calorie_percentage = serializers.FloatField()
    nutrition_status = serializers.CharField()

    # Macronutrients
    protein_stored = serializers.FloatField()
    carbs_stored = serializers.FloatField()
    fat_stored = serializers.FloatField()

    # Hydration
    water_volume = serializers.FloatField()
    max_water_volume = serializers.FloatField()
    hydration_percentage = serializers.FloatField()
    hydration_status = serializers.CharField()

    # Digestion
    stomach_fullness = serializers.FloatField()
    intestine_contents = serializers.FloatField()
    bladder_fullness = serializers.FloatField()
    bowel_fullness = serializers.FloatField()
    needs_bathroom = serializers.BooleanField()

    # Condition flags
    is_hungry = serializers.BooleanField()
    is_starving = serializers.BooleanField()
    is_thirsty = serializers.BooleanField()
    is_dehydrated = serializers.BooleanField()
    is_overfed = serializers.BooleanField()
    is_bloated = serializers.BooleanField()

    # Performance modifiers
    energy_regen_modifier = serializers.FloatField()
    stamina_modifier = serializers.FloatField()
    strength_modifier = serializers.FloatField()

    # Actively digesting
    digesting_foods_count = serializers.IntegerField()


class DigestingFoodSerializer(serializers.Serializer):
    """Food currently being digested"""
    food = serializers.CharField()
    quantity_grams = serializers.FloatField()
    calories = serializers.FloatField()
    progress = serializers.FloatField()
    time_remaining_minutes = serializers.FloatField()


class CharacterStatsSerializer(serializers.Serializer):
    """Core character stats"""
    # Core attributes
    level = serializers.IntegerField()
    experience = serializers.IntegerField()
    strength = serializers.IntegerField()
    agility = serializers.IntegerField()
    intelligence = serializers.IntegerField()
    luck = serializers.IntegerField()

    # Vital stats
    health = serializers.IntegerField()
    max_health = serializers.IntegerField()
    energy = serializers.IntegerField()
    max_energy = serializers.IntegerField()

    # Combat stats
    total_attack = serializers.IntegerField()
    total_defense = serializers.IntegerField()
    total_speed_bonus = serializers.IntegerField()

    # Carry capacity
    current_carry_weight = serializers.FloatField()
    effective_carry_capacity = serializers.FloatField()
    is_overencumbered = serializers.BooleanField()

    # Currency
    money = serializers.IntegerField()
    credit_card_balance = serializers.IntegerField()


class CompleteCharacterSheetSerializer(serializers.Serializer):
    """
    Complete character sheet with all information
    SCUM-style comprehensive character data
    """
    # Basic info
    username = serializers.CharField(source='user.username')
    player_id = serializers.IntegerField(source='id')

    # Location
    current_x = serializers.FloatField()
    current_y = serializers.FloatField()

    # Core stats
    stats = CharacterStatsSerializer(source='*')

    # Metabolism and nutrition
    metabolism = MetabolismSerializer()

    # Health system
    health_status = PlayerHealthStatusSerializer()
    body_parts = PlayerBodyPartSerializer(many=True)
    active_diseases = PlayerDiseaseSerializer(source='diseases', many=True)

    # Skills
    skills = PlayerSkillSerializer(many=True)

    # Digesting foods
    digesting_foods = DigestingFoodSerializer(many=True)

    # Vehicle
    has_vehicle = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()

    def get_has_vehicle(self, obj):
        return obj.current_vehicle is not None

    def get_vehicle_info(self, obj):
        if not obj.current_vehicle:
            return None
        vehicle = obj.current_vehicle
        return {
            'name': vehicle.display_name,
            'type': vehicle.vehicle_type.name,
            'fuel_percentage': vehicle.fuel_percentage,
            'durability_percentage': vehicle.durability_percentage,
            'can_drive': vehicle.can_drive,
        }
