"""
Advanced nutrition service - SCUM-like nutrition and metabolism system
"""
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class AdvancedNutritionService:
    """
    Manages complex nutrition, digestion, and metabolism
    Similar to SCUM's detailed survival mechanics
    """

    # Daily nutrient requirements (based on moderate activity)
    DAILY_PROTEIN_GRAMS = 80
    DAILY_CARBS_GRAMS = 250
    DAILY_FATS_GRAMS = 70
    DAILY_CALORIES = 2200

    # Vitamin/mineral decay rates (% per hour)
    VITAMIN_DECAY_RATE = 2.5  # Vitamins decay at 2.5% per hour
    MINERAL_DECAY_RATE = 1.5  # Minerals decay slower

    # Metabolism constants
    PROTEIN_TO_MUSCLE_EFFICIENCY = 0.15  # 15% of protein goes to muscle
    FAT_STORAGE_THRESHOLD = 1.3  # Store fat when consuming > 130% daily needs
    ENERGY_FROM_FAT_EFFICIENCY = 0.9  # 90% efficient when burning fat

    @staticmethod
    def eat_food(player, material, quantity_grams=100):
        """
        Consume food and start digestion process
        Returns: dict with consumption results
        """
        from game.models.nutrition import NutritionalProfile, DigestingFood, PlayerNutrition

        # Get or create player nutrition status
        nutrition_status, _ = PlayerNutrition.objects.get_or_create(player=player)

        # Get nutritional profile
        try:
            nutrition = material.nutrition
        except NutritionalProfile.DoesNotExist:
            # Food has no nutrition data - use basic values
            logger.warning(f"Food {material.name} has no nutritional profile")
            return {
                'success': False,
                'message': f"{material.name} n'a pas de profil nutritionnel"
            }

        # Check if toxic
        if nutrition.is_toxic:
            nutrition_status.toxin_level += nutrition.toxicity_level * (quantity_grams / 100)
            if nutrition_status.toxin_level > 50:
                nutrition_status.food_poisoning = True
            nutrition_status.save()

        # Calculate total nutrients from consumed quantity
        multiplier = quantity_grams / 100.0  # Nutrition is per 100g

        proteins = nutrition.proteins * multiplier
        carbs = nutrition.carbohydrates * multiplier
        fats = nutrition.fats * multiplier
        calories = nutrition.calories * multiplier

        # Create vitamins and minerals data
        vitamins_data = {
            'a': nutrition.vitamin_a * multiplier,
            'b1': nutrition.vitamin_b1 * multiplier,
            'b2': nutrition.vitamin_b2 * multiplier,
            'b3': nutrition.vitamin_b3 * multiplier,
            'b6': nutrition.vitamin_b6 * multiplier,
            'b12': nutrition.vitamin_b12 * multiplier,
            'c': nutrition.vitamin_c * multiplier,
            'd': nutrition.vitamin_d * multiplier,
            'e': nutrition.vitamin_e * multiplier,
            'k': nutrition.vitamin_k * multiplier,
        }

        minerals_data = {
            'calcium': nutrition.calcium * multiplier,
            'iron': nutrition.iron * multiplier,
            'magnesium': nutrition.magnesium * multiplier,
            'phosphorus': nutrition.phosphorus * multiplier,
            'potassium': nutrition.potassium * multiplier,
            'sodium': nutrition.sodium * multiplier,
            'zinc': nutrition.zinc * multiplier,
        }

        # Add to digestion queue
        digesting = DigestingFood.objects.create(
            player=player,
            material=material,
            quantity_grams=quantity_grams,
            proteins_total=proteins,
            carbs_total=carbs,
            fats_total=fats,
            calories_total=calories,
            vitamins_data=vitamins_data,
            minerals_data=minerals_data,
            digestion_duration_minutes=nutrition.digestion_time
        )

        # Immediate hydration effect
        water_gain = nutrition.water * multiplier
        if water_gain > 0:
            player.thirst = min(player.max_thirst, player.thirst + water_gain / 10)

        # Immediate satiety effect (feeling full)
        player.satiety = min(100, player.satiety + quantity_grams / 5)

        player.save(update_fields=['thirst', 'satiety'])

        return {
            'success': True,
            'message': f"Consommé {quantity_grams}g de {material.name}",
            'nutrients': {
                'proteins': round(proteins, 1),
                'carbs': round(carbs, 1),
                'fats': round(fats, 1),
                'calories': round(calories, 1)
            },
            'digestion_time': nutrition.digestion_time
        }

    @staticmethod
    def process_digestion(player):
        """
        Process ongoing digestion and absorb nutrients
        Should be called periodically (e.g., every minute)
        """
        from game.models.nutrition import DigestingFood, PlayerNutrition
        from django.db.models import Q

        nutrition_status, _ = PlayerNutrition.objects.get_or_create(player=player)

        # Get all food being digested
        digesting_foods = DigestingFood.objects.filter(
            player=player,
            nutrients_absorbed__lt=100
        )

        total_absorbed = {
            'proteins': 0,
            'carbs': 0,
            'fats': 0,
            'calories': 0
        }

        for food in digesting_foods:
            # Calculate absorption progress based on time elapsed
            now = timezone.now()
            elapsed_minutes = (now - food.digestion_start).total_seconds() / 60
            expected_progress = min(100, (elapsed_minutes / food.digestion_duration_minutes) * 100)

            # Calculate how much to absorb this update
            absorption_delta = expected_progress - food.nutrients_absorbed

            if absorption_delta > 0:
                # Absorb nutrients proportionally
                factor = absorption_delta / 100.0

                proteins_absorbed = food.proteins_total * factor
                carbs_absorbed = food.carbs_total * factor
                fats_absorbed = food.fats_total * factor

                # Add to player's nutrient stores
                nutrition_status.stored_proteins += proteins_absorbed
                nutrition_status.stored_carbs += carbs_absorbed
                nutrition_status.stored_fats += fats_absorbed

                # Absorb vitamins
                for vit_key, vit_amount in food.vitamins_data.items():
                    absorbed = vit_amount * factor
                    AdvancedNutritionService._add_vitamin(nutrition_status, vit_key, absorbed)

                # Absorb minerals
                for min_key, min_amount in food.minerals_data.items():
                    absorbed = min_amount * factor
                    AdvancedNutritionService._add_mineral(nutrition_status, min_key, absorbed)

                # Update progress
                food.nutrients_absorbed = expected_progress
                food.save()

                total_absorbed['proteins'] += proteins_absorbed
                total_absorbed['carbs'] += carbs_absorbed
                total_absorbed['fats'] += fats_absorbed
                total_absorbed['calories'] += food.calories_total * factor

        # Delete fully digested food
        DigestingFood.objects.filter(player=player, nutrients_absorbed__gte=99.9).delete()

        # Save nutrition status
        nutrition_status.save()

        return total_absorbed

    @staticmethod
    def _add_vitamin(nutrition_status, vitamin_key, amount):
        """Add vitamin to player's vitamin levels"""
        # Convert mg to % of daily needs (simplified)
        daily_needs = {
            'a': 0.9,  # mg
            'b1': 1.2,
            'b2': 1.3,
            'b3': 16,
            'b6': 1.7,
            'b12': 0.0024,
            'c': 90,
            'd': 0.015,
            'e': 15,
            'k': 0.12
        }

        if vitamin_key in daily_needs:
            percentage_gain = (amount / daily_needs[vitamin_key]) * 100

            if vitamin_key == 'a':
                nutrition_status.vitamin_a_level = min(200, nutrition_status.vitamin_a_level + percentage_gain)
            elif vitamin_key in ['b1', 'b2', 'b3', 'b6', 'b12']:
                nutrition_status.vitamin_b_complex = min(200, nutrition_status.vitamin_b_complex + percentage_gain * 0.5)
            elif vitamin_key == 'c':
                nutrition_status.vitamin_c_level = min(200, nutrition_status.vitamin_c_level + percentage_gain)
            elif vitamin_key == 'd':
                nutrition_status.vitamin_d_level = min(200, nutrition_status.vitamin_d_level + percentage_gain)
            elif vitamin_key == 'e':
                nutrition_status.vitamin_e_level = min(200, nutrition_status.vitamin_e_level + percentage_gain)

    @staticmethod
    def _add_mineral(nutrition_status, mineral_key, amount):
        """Add mineral to player's mineral levels"""
        daily_needs = {
            'calcium': 1000,  # mg
            'iron': 18,
            'magnesium': 400,
            'phosphorus': 700,
            'potassium': 3500,
            'sodium': 2300,
            'zinc': 11
        }

        if mineral_key in daily_needs:
            percentage_gain = (amount / daily_needs[mineral_key]) * 100

            if mineral_key == 'calcium':
                nutrition_status.calcium_level = min(200, nutrition_status.calcium_level + percentage_gain)
            elif mineral_key == 'iron':
                nutrition_status.iron_level = min(200, nutrition_status.iron_level + percentage_gain)
            elif mineral_key in ['potassium', 'sodium', 'magnesium']:
                nutrition_status.electrolytes = min(200, nutrition_status.electrolytes + percentage_gain * 0.4)

    @staticmethod
    def update_metabolism(player):
        """
        Update player's metabolism - consume nutrients and affect health
        Should be called periodically (e.g., every 5-10 minutes)
        """
        from game.models.nutrition import PlayerNutrition

        nutrition_status, _ = PlayerNutrition.objects.get_or_create(player=player)

        now = timezone.now()
        last_update = nutrition_status.last_metabolism_update
        hours_elapsed = (now - last_update).total_seconds() / 3600

        if hours_elapsed < 0.05:  # Less than 3 minutes, skip
            return

        # Calculate hourly nutrient consumption based on activity
        activity_multiplier = AdvancedNutritionService._get_activity_multiplier(player)

        hourly_protein = (AdvancedNutritionService.DAILY_PROTEIN_GRAMS / 24) * activity_multiplier
        hourly_carbs = (AdvancedNutritionService.DAILY_CARBS_GRAMS / 24) * activity_multiplier
        hourly_fats = (AdvancedNutritionService.DAILY_FATS_GRAMS / 24) * activity_multiplier

        # Consume nutrients
        proteins_used = hourly_protein * hours_elapsed
        carbs_used = hourly_carbs * hours_elapsed
        fats_used = hourly_fats * hours_elapsed

        nutrition_status.stored_proteins = max(0, nutrition_status.stored_proteins - proteins_used)
        nutrition_status.stored_carbs = max(0, nutrition_status.stored_carbs - carbs_used)
        nutrition_status.stored_fats = max(0, nutrition_status.stored_fats - fats_used)

        # Decay vitamins and minerals
        vitamin_decay = AdvancedNutritionService.VITAMIN_DECAY_RATE * hours_elapsed
        mineral_decay = AdvancedNutritionService.MINERAL_DECAY_RATE * hours_elapsed

        nutrition_status.vitamin_a_level = max(0, nutrition_status.vitamin_a_level - vitamin_decay)
        nutrition_status.vitamin_b_complex = max(0, nutrition_status.vitamin_b_complex - vitamin_decay)
        nutrition_status.vitamin_c_level = max(0, nutrition_status.vitamin_c_level - vitamin_decay)
        nutrition_status.vitamin_d_level = max(0, nutrition_status.vitamin_d_level - vitamin_decay * 0.5)  # Slower
        nutrition_status.vitamin_e_level = max(0, nutrition_status.vitamin_e_level - vitamin_decay * 0.7)

        nutrition_status.calcium_level = max(0, nutrition_status.calcium_level - mineral_decay)
        nutrition_status.iron_level = max(0, nutrition_status.iron_level - mineral_decay)
        nutrition_status.electrolytes = max(0, nutrition_status.electrolytes - mineral_decay * 1.5)  # Faster

        # Update health effects
        AdvancedNutritionService._apply_nutrition_effects(player, nutrition_status)

        # Handle toxins
        if nutrition_status.toxin_level > 0:
            nutrition_status.toxin_level = max(0, nutrition_status.toxin_level - 5 * hours_elapsed)
            if nutrition_status.toxin_level < 10:
                nutrition_status.food_poisoning = False

        nutrition_status.last_metabolism_update = now
        nutrition_status.save()

    @staticmethod
    def _get_activity_multiplier(player):
        """Calculate metabolism multiplier based on recent activity"""
        # TODO: Track player activity (walking, fighting, etc.)
        # For now, return base multiplier
        return 1.0

    @staticmethod
    def apply_nutrition_health_effects(player, minutes_passed):
        """
        Apply real-time health effects based on vitamin/mineral levels
        Returns: dict with effects applied
        """
        from game.models.nutrition import PlayerNutrition

        nutrition_status, _ = PlayerNutrition.objects.get_or_create(player=player)
        
        effects = []
        health_drain = 0
        stat_modifiers = {}

        # Vitamin C deficiency (Scurvy)
        if nutrition_status.vitamin_c_level < 40:
            health_drain += 0.5 * minutes_passed  # -0.5 HP/min
            nutrition_status.immune_system = max(50, nutrition_status.immune_system - 10)
            effects.append("⚠️ Carence en vitamine C: Système immunitaire affaibli")
            if nutrition_status.vitamin_c_level < 20:
                effects.append("🩸 Scorbut: Saignements")

        # Vitamin D deficiency (Bone weakness)
        if nutrition_status.vitamin_d_level < 40:
            stat_modifiers['max_energy'] = -10  # -10% max energy
            effects.append("⚠️ Carence en vitamine D: Fatigue, os fragiles")

        # B Complex deficiency (Fatigue)
        if nutrition_status.vitamin_b_complex < 40:
            nutrition_status.stamina_regeneration = max(0.6, nutrition_status.stamina_regeneration - 0.2)
            effects.append("⚠️ Carence en vitamines B: Fatigue extrême")

        # Vitamin A deficiency (Vision problems)
        if nutrition_status.vitamin_a_level < 40:
            effects.append("⚠️ Carence en vitamine A: Vision réduite")

        # Vitamin E deficiency (Reduced healing)
        if nutrition_status.vitamin_e_level < 30:
            nutrition_status.healing_rate = max(0.5, nutrition_status.healing_rate - 0.3)
            effects.append("⚠️ Carence en vitamine E: Guérison ralentie")

        # Iron deficiency (Anemia)
        if nutrition_status.iron_level < 40:
            stat_modifiers['max_energy'] = stat_modifiers.get('max_energy', 0) - 15
            effects.append("🩸 Anémie: Énergie max réduite")
            if nutrition_status.iron_level < 20:
                health_drain += 0.3 * minutes_passed

        # Calcium deficiency (Bone weakness)
        if nutrition_status.calcium_level < 40:
            stat_modifiers['defense'] = -5  # -5% defense
            effects.append("⚠️ Carence en calcium: Os fragiles, défense réduite")

        # Electrolytes deficiency (Muscle problems)
        if nutrition_status.electrolytes < 30:
            stat_modifiers['strength'] = -10  # -10% strength
            effects.append("⚠️ Déséquilibre électrolytique: Crampes musculaires")
            if nutrition_status.electrolytes < 20:
                health_drain += 0.4 * minutes_passed
                effects.append("❌ Déshydratation sévère")

        # Apply health drain
        if health_drain > 0:
            player.health = max(0, player.health - health_drain)
            effects.append(f"💔 Perte de santé: -{round(health_drain, 1)} HP")

        # Apply stat modifiers
        if 'max_energy' in stat_modifiers:
            penalty = stat_modifiers['max_energy']
            player.max_energy = max(50, int(100 * (1 + penalty / 100)))

        # Save changes
        nutrition_status.save()
        player.save()

        return {
            'effects': effects,
            'health_drain': round(health_drain, 2),
            'stat_modifiers': stat_modifiers
        }

    @staticmethod
    def _apply_nutrition_effects(player, nutrition_status):
        """Apply health effects based on nutritional status"""
        score = nutrition_status.overall_nutrition_score

        # Immune system
        if score >= 80:
            nutrition_status.immune_system = 120
        elif score >= 60:
            nutrition_status.immune_system = 100
        elif score >= 40:
            nutrition_status.immune_system = 75
        else:
            nutrition_status.immune_system = 50

        # Stamina regeneration
        if score >= 75:
            nutrition_status.stamina_regeneration = 1.2
        elif score >= 50:
            nutrition_status.stamina_regeneration = 1.0
        else:
            nutrition_status.stamina_regeneration = 0.7

        # Healing rate
        if score >= 80 and nutrition_status.stored_proteins > 50:
            nutrition_status.healing_rate = 1.5
        elif score >= 60:
            nutrition_status.healing_rate = 1.0
        else:
            nutrition_status.healing_rate = 0.6

        # Apply effects to player
        # Malnourished players lose energy faster
        if nutrition_status.is_malnourished:
            player.max_energy = int(100 * 0.8)  # 20% penalty
        else:
            player.max_energy = 100

        # Food poisoning effects
        if nutrition_status.food_poisoning:
            player.health = max(0, player.health - 0.5)  # Gradual health loss

    @staticmethod
    def get_nutrition_summary(player):
        """Get comprehensive nutrition summary for UI"""
        from game.models.nutrition import PlayerNutrition, DigestingFood

        nutrition_status, _ = PlayerNutrition.objects.get_or_create(player=player)
        digesting = DigestingFood.objects.filter(player=player, nutrients_absorbed__lt=100)

        return {
            'overall_score': round(nutrition_status.overall_nutrition_score, 1),
            'status': nutrition_status.nutrition_status_description,
            'is_malnourished': nutrition_status.is_malnourished,
            'macronutrients': {
                'proteins': round(nutrition_status.stored_proteins, 1),
                'carbs': round(nutrition_status.stored_carbs, 1),
                'fats': round(nutrition_status.stored_fats, 1),
            },
            'vitamins': {
                'a': round(nutrition_status.vitamin_a_level, 1),
                'b': round(nutrition_status.vitamin_b_complex, 1),
                'c': round(nutrition_status.vitamin_c_level, 1),
                'd': round(nutrition_status.vitamin_d_level, 1),
                'e': round(nutrition_status.vitamin_e_level, 1),
            },
            'minerals': {
                'calcium': round(nutrition_status.calcium_level, 1),
                'iron': round(nutrition_status.iron_level, 1),
                'electrolytes': round(nutrition_status.electrolytes, 1),
            },
            'health_effects': {
                'immune_system': round(nutrition_status.immune_system, 1),
                'stamina_regen': round(nutrition_status.stamina_regeneration, 2),
                'healing_rate': round(nutrition_status.healing_rate, 2),
            },
            'body': {
                'fat_percentage': round(nutrition_status.body_fat_percentage, 1),
                'muscle_mass': round(nutrition_status.muscle_mass_kg, 1),
            },
            'digesting_count': digesting.count(),
            'food_poisoning': nutrition_status.food_poisoning,
            'toxin_level': round(nutrition_status.toxin_level, 1)
        }
