"""
Health display serializer
SCUM-style detailed health UI data
"""
from rest_framework import serializers


class BodyPartDisplaySerializer(serializers.Serializer):
    """Body part for visual display"""
    name = serializers.CharField()
    part_type = serializers.CharField()
    health_percentage = serializers.FloatField()

    # Visual indicators
    color_code = serializers.CharField()  # green, yellow, orange, red
    status_icon = serializers.CharField()  # ok, warning, critical, broken

    # Detailed status
    is_bleeding = serializers.BooleanField()
    bleeding_severity = serializers.CharField()
    is_fractured = serializers.BooleanField()
    is_infected = serializers.BooleanField()
    pain_level = serializers.FloatField()

    # Treatment status
    is_bandaged = serializers.BooleanField()
    is_splinted = serializers.BooleanField()

    # Descriptive status
    status_text = serializers.CharField()


class NutritionBarSerializer(serializers.Serializer):
    """Nutrition bar display"""
    name = serializers.CharField()
    current = serializers.FloatField()
    max = serializers.FloatField()
    percentage = serializers.FloatField()
    unit = serializers.CharField()

    # Visual
    color = serializers.CharField()
    warning_level = serializers.CharField()  # none, low, critical
    icon = serializers.CharField()


class VitaminMineralSerializer(serializers.Serializer):
    """Vitamin/mineral level display"""
    name = serializers.CharField()
    level = serializers.FloatField()  # 0-200% of daily needs
    status = serializers.CharField()  # deficient, low, normal, optimal, excess
    color = serializers.CharField()


class MetabolismDisplaySerializer(serializers.Serializer):
    """Metabolism display data"""
    # Body composition bars
    body_weight = NutritionBarSerializer()
    muscle_mass = NutritionBarSerializer()
    body_fat = NutritionBarSerializer()

    # Calculated stats
    bmi = serializers.FloatField()
    bmi_category = serializers.CharField()
    fitness_level = serializers.CharField()

    # Energy bars
    calories = NutritionBarSerializer()
    water = NutritionBarSerializer()

    # Macronutrients
    proteins = NutritionBarSerializer()
    carbohydrates = NutritionBarSerializer()
    fats = NutritionBarSerializer()

    # Vitamins
    vitamins = VitaminMineralSerializer(many=True)

    # Minerals
    minerals = VitaminMineralSerializer(many=True)

    # Digestion indicators
    stomach_fullness = serializers.FloatField()
    intestine_fullness = serializers.FloatField()
    bladder_fullness = serializers.FloatField()
    bowel_fullness = serializers.FloatField()

    # Status flags
    needs_food = serializers.BooleanField()
    needs_water = serializers.BooleanField()
    needs_bathroom = serializers.BooleanField()


class VitalSignsDisplaySerializer(serializers.Serializer):
    """Vital signs display"""
    # Temperature
    body_temperature = serializers.FloatField()
    temperature_status = serializers.CharField()
    temperature_color = serializers.CharField()

    # Heart
    heart_rate = serializers.IntegerField()
    heart_rate_status = serializers.CharField()
    heart_rate_color = serializers.CharField()

    # Blood
    blood_volume = serializers.FloatField()
    blood_status = serializers.CharField()
    blood_color = serializers.CharField()

    # Oxygen
    oxygen_level = serializers.FloatField()
    oxygen_status = serializers.CharField()
    oxygen_color = serializers.CharField()

    # Stamina
    stamina = serializers.FloatField()
    stamina_max = serializers.FloatField()
    stamina_percentage = serializers.FloatField()


class HealthAlertSerializer(serializers.Serializer):
    """Health alerts and warnings"""
    severity = serializers.CharField()  # info, warning, critical, emergency
    category = serializers.CharField()  # injury, disease, nutrition, hydration, etc.
    message = serializers.CharField()
    icon = serializers.CharField()
    action_required = serializers.CharField()  # recommended action


class HealthDisplaySerializer(serializers.Serializer):
    """
    Complete health display data
    Optimized for SCUM-style health interface
    """
    # Overall health
    overall_health_percentage = serializers.FloatField()
    health_status = serializers.CharField()
    is_critical = serializers.BooleanField()

    # Body map (for visual body display)
    body_parts = BodyPartDisplaySerializer(many=True)

    # Vital signs
    vital_signs = VitalSignsDisplaySerializer()

    # Metabolism and nutrition
    metabolism = MetabolismDisplaySerializer()

    # Active conditions
    active_injuries_count = serializers.IntegerField()
    active_diseases_count = serializers.IntegerField()
    bleeding_parts_count = serializers.IntegerField()
    fractured_parts_count = serializers.IntegerField()
    infected_parts_count = serializers.IntegerField()

    # Performance modifiers
    energy_regen_modifier = serializers.FloatField()
    stamina_modifier = serializers.FloatField()
    strength_modifier = serializers.FloatField()

    # Alerts and warnings
    alerts = HealthAlertSerializer(many=True)

    # Recommendations
    recommendations = serializers.ListField(child=serializers.CharField())

    # Digesting foods
    digesting_foods = serializers.ListField(child=serializers.DictField())

    # Time-based info
    time_since_last_meal = serializers.CharField()
    time_since_last_drink = serializers.CharField()
    time_until_next_meal_recommended = serializers.CharField()
