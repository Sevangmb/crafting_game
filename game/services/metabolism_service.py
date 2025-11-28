"""
Advanced metabolism and digestion service
Ultra-realistic SCUM-style metabolism simulation
"""
from django.utils import timezone
from django.db.models import F
from decimal import Decimal
import math

from ..models import Player, PlayerNutrition, DigestingFood, NutritionalProfile


def update_player_metabolism(player):
    """
    Main metabolism update - should be called periodically (every 5-10 minutes)
    Simulates realistic body processes
    """
    now = timezone.now()

    if not player.last_metabolism_update:
        player.last_metabolism_update = now
        player.save()
        return

    # Calculate time elapsed in minutes
    elapsed_seconds = (now - player.last_metabolism_update).total_seconds()
    elapsed_minutes = elapsed_seconds / 60.0

    if elapsed_minutes < 1:
        return  # Too soon

    # Update all metabolic processes
    _process_digestion(player, elapsed_minutes)
    _burn_calories(player, elapsed_minutes)
    _process_hydration(player, elapsed_minutes)
    _update_body_composition(player)
    _update_condition_flags(player)
    _apply_stat_modifiers(player)

    player.last_metabolism_update = now
    player.save()

    return {
        'success': True,
        'elapsed_minutes': elapsed_minutes,
        'calories': player.calories_stored,
        'water': player.water_volume,
        'status': player.nutrition_status,
    }


def _process_digestion(player, elapsed_minutes):
    """
    Process food digestion from stomach to intestines to absorption
    """
    # Stomach to intestines (takes ~30-60 minutes in real life)
    if player.stomach_fullness > 0:
        # Transfer from stomach to intestines
        digestion_rate = 2.0  # % per minute
        amount_digested = min(player.stomach_fullness, digestion_rate * elapsed_minutes)

        player.stomach_fullness -= amount_digested
        player.intestine_contents = min(100, player.intestine_contents + amount_digested)

    # Intestines to absorption (takes 2-4 hours in real life)
    if player.intestine_contents > 0:
        # Absorb nutrients from intestines
        absorption_rate = 0.8  # % per minute
        amount_absorbed = min(player.intestine_contents, absorption_rate * elapsed_minutes)

        player.intestine_contents -= amount_absorbed

        # Increase bowel fullness (what's left becomes waste)
        waste_rate = 0.3
        player.bowel_fullness = min(100, player.bowel_fullness + (amount_absorbed * waste_rate * elapsed_minutes))

    # Process actively digesting food
    digesting_foods = DigestingFood.objects.filter(player=player)

    for food in digesting_foods:
        # Calculate digestion progress
        time_digesting = (now - food.digestion_start).total_seconds() / 60.0
        progress_pct = (time_digesting / food.digestion_duration_minutes) * 100

        if progress_pct >= 100:
            # Fully digested - add nutrients to body stores
            player.calories_stored = min(player.max_calories,
                                        player.calories_stored + food.calories_total)
            player.protein_stored = min(500, player.protein_stored + food.proteins_total)
            player.carbs_stored = min(800, player.carbs_stored + food.carbs_total)
            player.fat_stored = min(300, player.fat_stored + food.fats_total)

            # Update PlayerNutrition vitamins/minerals
            try:
                nutrition = player.nutrition_status
                # Add vitamins/minerals from food
                if food.vitamins_data:
                    for vitamin, amount in food.vitamins_data.items():
                        # Simplified vitamin addition
                        pass
            except:
                pass

            # Delete fully digested food
            food.delete()
        else:
            # Update absorption progress
            food.nutrients_absorbed = progress_pct
            food.save()

    # Bladder filling (liquid waste)
    water_processed = elapsed_minutes * 0.5  # ml per minute
    player.bladder_fullness = min(100, player.bladder_fullness + (water_processed / 5.0))

    # Auto bathroom if needed
    if player.bladder_fullness >= 100 or player.bowel_fullness >= 100:
        player.needs_bathroom = True


def _burn_calories(player, elapsed_minutes):
    """
    Burn calories based on activity level and basal metabolic rate
    """
    # Basal Metabolic Rate (BMR) calculation
    # Mifflin-St Jeor equation for men: BMR = 10*weight + 6.25*height - 5*age + 5
    # Simplified: ~1800 kcal/day for 70kg person = 1.25 kcal/minute

    base_burn_rate = 1.25  # kcal per minute at rest

    # Adjust for metabolism rate (activity level)
    burn_rate = base_burn_rate * player.metabolism_rate

    # Adjust for body weight
    weight_factor = player.body_weight / 70.0
    burn_rate *= weight_factor

    # Total calories burned
    calories_burned = burn_rate * elapsed_minutes

    # Burn calories from stores
    if player.calories_stored > calories_burned:
        player.calories_stored -= calories_burned
    else:
        # Not enough calories - start consuming body stores
        deficit = calories_burned - player.calories_stored
        player.calories_stored = 0

        # Burn carbs first
        carbs_to_burn = min(deficit / 4.0, player.carbs_stored)  # 4 kcal per gram
        player.carbs_stored -= carbs_to_burn
        deficit -= carbs_to_burn * 4.0

        # Then fats
        if deficit > 0:
            fats_to_burn = min(deficit / 9.0, player.fat_stored)  # 9 kcal per gram
            player.fat_stored -= fats_to_burn
            deficit -= fats_to_burn * 9.0

        # Finally protein (muscle catabolism - bad!)
        if deficit > 0:
            protein_to_burn = min(deficit / 4.0, player.protein_stored)
            player.protein_stored -= protein_to_burn

            # Losing protein means losing muscle
            muscle_lost = protein_to_burn * 0.25  # Rough estimate
            player.muscle_mass = max(20, player.muscle_mass - muscle_lost)


def _process_hydration(player, elapsed_minutes):
    """
    Process water loss through breathing, sweating, urination
    """
    # Base water loss: ~2.5L per day = ~0.00174L per minute
    base_water_loss = 0.00174  # liters per minute

    # Adjust for activity
    water_loss = base_water_loss * player.metabolism_rate

    # Adjust for temperature (if we had weather system)
    # water_loss *= temperature_factor

    total_water_lost = water_loss * elapsed_minutes

    player.water_volume = max(30, player.water_volume - total_water_lost)

    # Update thirst and hydration
    hydration_pct = (player.water_volume / player.max_water_volume) * 100

    if hydration_pct < 70:
        player.is_thirsty = True
    else:
        player.is_thirsty = False

    if hydration_pct < 50:
        player.is_dehydrated = True
    else:
        player.is_dehydrated = False

    # Sync with old system
    player.thirst = int(hydration_pct)
    player.hydration = hydration_pct


def _update_body_composition(player):
    """
    Update body weight based on fat, muscle, and other factors
    """
    # Bones, organs, etc. = ~20% of body weight (constant)
    base_weight = 20.0

    # Total weight = base + muscle + fat + water
    lean_mass = player.muscle_mass
    fat_mass = player.fat_stored / 1000.0  # Convert grams to kg approximation
    water_mass = player.water_volume

    player.body_weight = base_weight + lean_mass + fat_mass + water_mass
    player.body_fat = fat_mass


def _update_condition_flags(player):
    """
    Update hunger, starving, overfed flags based on calorie levels
    """
    calorie_pct = player.calorie_percentage

    # Hunger states
    if calorie_pct < 20:
        player.is_starving = True
        player.is_hungry = True
    elif calorie_pct < 40:
        player.is_starving = False
        player.is_hungry = True
    else:
        player.is_starving = False
        player.is_hungry = False

    # Overfed states
    if calorie_pct > 95:
        player.is_overfed = True
    else:
        player.is_overfed = False

    # Bloated (too much in stomach)
    if player.stomach_fullness > 80:
        player.is_bloated = True
    else:
        player.is_bloated = False

    # Sync with old system
    player.hunger = int(calorie_pct)
    player.satiety = calorie_pct


def _apply_stat_modifiers(player):
    """
    Apply performance modifiers based on nutrition state
    """
    # Energy regeneration
    if player.is_starving:
        player.energy_regen_modifier = 0.3
    elif player.is_hungry:
        player.energy_regen_modifier = 0.7
    elif player.calorie_percentage > 80:
        player.energy_regen_modifier = 1.2
    else:
        player.energy_regen_modifier = 1.0

    # Stamina
    if player.is_dehydrated:
        player.stamina_modifier = 0.5
    elif player.is_thirsty:
        player.stamina_modifier = 0.8
    else:
        player.stamina_modifier = 1.0

    # Strength (affected by muscle mass)
    muscle_pct = player.muscle_percentage
    if muscle_pct > 45:
        player.strength_modifier = 1.3
    elif muscle_pct > 40:
        player.strength_modifier = 1.2
    elif muscle_pct > 35:
        player.strength_modifier = 1.0
    elif muscle_pct < 25:
        player.strength_modifier = 0.7
    else:
        player.strength_modifier = 0.9


def eat_food(player, food_material, quantity_grams=100):
    """
    Consume food - add to stomach and create digesting food entry

    Args:
        player: Player instance
        food_material: Material instance (food item)
        quantity_grams: Amount in grams
    """
    try:
        nutrition_profile = food_material.nutrition
    except:
        return {'success': False, 'error': 'This item has no nutritional value'}

    # Check stomach capacity
    if player.stomach_fullness >= 100:
        return {'success': False, 'error': 'Stomach is too full'}

    # Calculate nutrients from this food
    multiplier = quantity_grams / 100.0  # Nutrition is per 100g

    proteins = nutrition_profile.proteins * multiplier
    carbs = nutrition_profile.carbohydrates * multiplier
    fats = nutrition_profile.fats * multiplier
    calories = nutrition_profile.calories * multiplier

    # Add water content directly
    water_ml = nutrition_profile.water * multiplier
    player.water_volume = min(player.max_water_volume, player.water_volume + (water_ml / 1000.0))

    # Create digesting food entry
    digesting = DigestingFood.objects.create(
        player=player,
        material=food_material,
        quantity_grams=quantity_grams,
        proteins_total=proteins,
        carbs_total=carbs,
        fats_total=fats,
        calories_total=calories,
        digestion_duration_minutes=nutrition_profile.digestion_time,
        nutrients_absorbed=0,
        vitamins_data={},  # TODO: Extract from nutrition profile
        minerals_data={},
    )

    # Increase stomach fullness
    # Rough estimate: 100g food = ~10% stomach fullness
    fullness_increase = (quantity_grams / 1000.0) * 10
    player.stomach_fullness = min(100, player.stomach_fullness + fullness_increase)

    player.last_meal_time = timezone.now()
    player.save()

    return {
        'success': True,
        'food': food_material.name,
        'quantity_grams': quantity_grams,
        'calories': calories,
        'stomach_fullness': player.stomach_fullness,
        'digestion_time_minutes': nutrition_profile.digestion_time,
    }


def drink_water(player, amount_ml=250):
    """
    Drink water or other beverages

    Args:
        player: Player instance
        amount_ml: Amount in milliliters
    """
    # Convert ml to liters
    amount_liters = amount_ml / 1000.0

    # Add to water volume
    player.water_volume = min(player.max_water_volume, player.water_volume + amount_liters)

    # Reduce thirst immediately
    player.is_thirsty = False

    # Fill bladder a bit
    player.bladder_fullness = min(100, player.bladder_fullness + (amount_ml / 50.0))

    player.last_drink_time = timezone.now()
    player.save()

    return {
        'success': True,
        'amount_ml': amount_ml,
        'water_volume': player.water_volume,
        'hydration_percentage': player.hydration_percentage,
    }


def use_bathroom(player):
    """
    Player uses the bathroom - empties bladder and bowels
    """
    if not player.needs_bathroom:
        return {'success': False, 'error': 'No need to use bathroom'}

    player.bladder_fullness = 0
    player.bowel_fullness = 0
    player.needs_bathroom = False
    player.save()

    return {
        'success': True,
        'message': 'Relieved'
    }


def get_metabolism_status(player):
    """
    Get comprehensive metabolism status for character sheet
    """
    return {
        # Body composition
        'body_weight': round(player.body_weight, 1),
        'muscle_mass': round(player.muscle_mass, 1),
        'body_fat': round(player.body_fat, 1),
        'bmi': player.bmi,
        'body_fat_percentage': player.body_fat_percentage,
        'muscle_percentage': player.muscle_percentage,
        'fitness_level': player.fitness_level,

        # Energy and nutrition
        'calories_stored': round(player.calories_stored, 0),
        'max_calories': player.max_calories,
        'calorie_percentage': player.calorie_percentage,
        'nutrition_status': player.nutrition_status,

        # Macronutrients
        'protein_stored': round(player.protein_stored, 1),
        'carbs_stored': round(player.carbs_stored, 1),
        'fat_stored': round(player.fat_stored, 1),

        # Hydration
        'water_volume': round(player.water_volume, 2),
        'max_water_volume': player.max_water_volume,
        'hydration_percentage': player.hydration_percentage,
        'hydration_status': player.hydration_status,

        # Digestion
        'stomach_fullness': round(player.stomach_fullness, 1),
        'intestine_contents': round(player.intestine_contents, 1),
        'bladder_fullness': round(player.bladder_fullness, 1),
        'bowel_fullness': round(player.bowel_fullness, 1),
        'needs_bathroom': player.needs_bathroom,

        # Condition flags
        'is_hungry': player.is_hungry,
        'is_starving': player.is_starving,
        'is_thirsty': player.is_thirsty,
        'is_dehydrated': player.is_dehydrated,
        'is_overfed': player.is_overfed,
        'is_bloated': player.is_bloated,

        # Performance modifiers
        'energy_regen_modifier': player.energy_regen_modifier,
        'stamina_modifier': player.stamina_modifier,
        'strength_modifier': player.strength_modifier,

        # Actively digesting
        'digesting_foods_count': DigestingFood.objects.filter(player=player).count(),
    }


def get_digesting_foods(player):
    """
    Get list of foods currently being digested
    """
    foods = DigestingFood.objects.filter(player=player).order_by('digestion_start')

    return [{
        'food': food.material.name,
        'quantity_grams': food.quantity_grams,
        'calories': food.calories_total,
        'progress': round(food.digestion_progress, 1),
        'time_remaining_minutes': max(0, food.digestion_duration_minutes -
                                      ((timezone.now() - food.digestion_start).total_seconds() / 60.0)),
    } for food in foods]
