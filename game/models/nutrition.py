"""
Advanced nutrition system inspired by SCUM
Tracks macronutrients, micronutrients, digestion, and metabolism
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class NutritionalProfile(models.Model):
    """
    Nutritional profile for food items
    Similar to SCUM's detailed nutrition tracking
    """
    # Link to material (food item)
    material = models.OneToOneField('Material', on_delete=models.CASCADE, related_name='nutrition')

    # Macronutrients (in grams per 100g)
    proteins = models.FloatField(default=0, validators=[MinValueValidator(0)],
                                 help_text="Protein content (g per 100g)")
    carbohydrates = models.FloatField(default=0, validators=[MinValueValidator(0)],
                                      help_text="Carbohydrate content (g per 100g)")
    fats = models.FloatField(default=0, validators=[MinValueValidator(0)],
                            help_text="Fat content (g per 100g)")
    fiber = models.FloatField(default=0, validators=[MinValueValidator(0)],
                             help_text="Fiber content (g per 100g)")
    water = models.FloatField(default=0, validators=[MinValueValidator(0)],
                             help_text="Water content (g per 100g)")

    # Calories (kcal per 100g)
    calories = models.FloatField(default=0, validators=[MinValueValidator(0)],
                                help_text="Energy content (kcal per 100g)")

    # Micronutrients - Vitamins (mg per 100g)
    vitamin_a = models.FloatField(default=0, validators=[MinValueValidator(0)])
    vitamin_b1 = models.FloatField(default=0, validators=[MinValueValidator(0)])  # Thiamine
    vitamin_b2 = models.FloatField(default=0, validators=[MinValueValidator(0)])  # Riboflavin
    vitamin_b3 = models.FloatField(default=0, validators=[MinValueValidator(0)])  # Niacin
    vitamin_b6 = models.FloatField(default=0, validators=[MinValueValidator(0)])
    vitamin_b12 = models.FloatField(default=0, validators=[MinValueValidator(0)])
    vitamin_c = models.FloatField(default=0, validators=[MinValueValidator(0)])
    vitamin_d = models.FloatField(default=0, validators=[MinValueValidator(0)])
    vitamin_e = models.FloatField(default=0, validators=[MinValueValidator(0)])
    vitamin_k = models.FloatField(default=0, validators=[MinValueValidator(0)])

    # Micronutrients - Minerals (mg per 100g)
    calcium = models.FloatField(default=0, validators=[MinValueValidator(0)])
    iron = models.FloatField(default=0, validators=[MinValueValidator(0)])
    magnesium = models.FloatField(default=0, validators=[MinValueValidator(0)])
    phosphorus = models.FloatField(default=0, validators=[MinValueValidator(0)])
    potassium = models.FloatField(default=0, validators=[MinValueValidator(0)])
    sodium = models.FloatField(default=0, validators=[MinValueValidator(0)])
    zinc = models.FloatField(default=0, validators=[MinValueValidator(0)])

    # Digestion properties
    digestion_time = models.IntegerField(default=60,
                                        help_text="Time to fully digest (minutes)")
    absorption_rate = models.FloatField(default=1.0,
                                       validators=[MinValueValidator(0), MaxValueValidator(1)],
                                       help_text="Nutrient absorption efficiency (0-1)")

    # Food quality
    freshness_decay_rate = models.FloatField(default=1.0,
                                            help_text="How fast food spoils (higher = faster)")
    is_perishable = models.BooleanField(default=True)

    # Special properties
    is_toxic = models.BooleanField(default=False)
    toxicity_level = models.FloatField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        app_label = 'game'

    def __str__(self):
        return f"Nutrition: {self.material.name}"


class PlayerNutrition(models.Model):
    """
    Tracks player's nutritional status
    Similar to SCUM's metabolism tracking
    """
    player = models.OneToOneField('Player', on_delete=models.CASCADE, related_name='nutrition_status')

    # Current nutrient stores (in grams)
    stored_proteins = models.FloatField(default=0, validators=[MinValueValidator(0)])
    stored_carbs = models.FloatField(default=0, validators=[MinValueValidator(0)])
    stored_fats = models.FloatField(default=0, validators=[MinValueValidator(0)])

    # Vitamin levels (percentage of daily needs, 0-200%)
    vitamin_a_level = models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(200)])
    vitamin_b_complex = models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(200)])
    vitamin_c_level = models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(200)])
    vitamin_d_level = models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(200)])
    vitamin_e_level = models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(200)])

    # Mineral levels (percentage of daily needs, 0-200%)
    calcium_level = models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(200)])
    iron_level = models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(200)])
    electrolytes = models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(200)])

    # Metabolism stats
    metabolic_rate = models.FloatField(default=1.0, help_text="Overall metabolism speed multiplier")
    body_fat_percentage = models.FloatField(default=15.0,
                                           validators=[MinValueValidator(3), MaxValueValidator(50)])
    muscle_mass_kg = models.FloatField(default=30.0, validators=[MinValueValidator(10)])

    # Health effects from nutrition
    immune_system = models.FloatField(default=100, validators=[MinValueValidator(0), MaxValueValidator(150)],
                                     help_text="Immune strength %, affects disease resistance")
    stamina_regeneration = models.FloatField(default=1.0, validators=[MinValueValidator(0.1), MaxValueValidator(2)],
                                            help_text="Energy/stamina regen multiplier")
    healing_rate = models.FloatField(default=1.0, validators=[MinValueValidator(0.1), MaxValueValidator(2)],
                                    help_text="Health regeneration multiplier")

    # Toxicity and illness
    toxin_level = models.FloatField(default=0, validators=[MinValueValidator(0)])
    food_poisoning = models.BooleanField(default=False)

    # Timestamps
    last_metabolism_update = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'game'

    def __str__(self):
        return f"Nutrition: {self.player.user.username}"

    @property
    def overall_nutrition_score(self):
        """Calculate overall nutrition health (0-100)"""
        scores = [
            min(self.vitamin_a_level, 100),
            min(self.vitamin_b_complex, 100),
            min(self.vitamin_c_level, 100),
            min(self.vitamin_d_level, 100),
            min(self.vitamin_e_level, 100),
            min(self.calcium_level, 100),
            min(self.iron_level, 100),
            min(self.electrolytes, 100),
        ]
        return sum(scores) / len(scores)

    @property
    def is_malnourished(self):
        """Check if player is malnourished"""
        return self.overall_nutrition_score < 50

    @property
    def nutrition_status_description(self):
        """Get human-readable nutrition status"""
        score = self.overall_nutrition_score
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        elif score >= 40:
            return "Poor"
        else:
            return "Critically Malnourished"


class DigestingFood(models.Model):
    """
    Tracks food currently being digested
    Implements gradual nutrient absorption over time
    """
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='digesting_food')
    material = models.ForeignKey('Material', on_delete=models.CASCADE)

    # Amount and nutrients
    quantity_grams = models.FloatField(validators=[MinValueValidator(0)])

    # Nutrient content (calculated when food is eaten)
    proteins_total = models.FloatField(default=0)
    carbs_total = models.FloatField(default=0)
    fats_total = models.FloatField(default=0)
    calories_total = models.FloatField(default=0)

    # Vitamins and minerals
    vitamins_data = models.JSONField(default=dict, help_text="Vitamin content")
    minerals_data = models.JSONField(default=dict, help_text="Mineral content")

    # Digestion tracking
    digestion_start = models.DateTimeField(auto_now_add=True)
    digestion_duration_minutes = models.IntegerField(default=60)
    nutrients_absorbed = models.FloatField(default=0,
                                          validators=[MinValueValidator(0), MaxValueValidator(100)],
                                          help_text="Percentage of nutrients absorbed so far")

    class Meta:
        app_label = 'game'
        ordering = ['digestion_start']

    def __str__(self):
        return f"{self.player.user.username} digesting {self.material.name}"

    @property
    def is_fully_digested(self):
        """Check if digestion is complete"""
        return self.nutrients_absorbed >= 99.9

    @property
    def digestion_progress(self):
        """Get digestion progress percentage"""
        from django.utils import timezone
        elapsed = (timezone.now() - self.digestion_start).total_seconds() / 60
        progress = min(100, (elapsed / self.digestion_duration_minutes) * 100)
        return progress
