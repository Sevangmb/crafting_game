"""
Health display service
Generate formatted data for SCUM-style health interface
"""
from django.utils import timezone
from datetime import timedelta


def get_color_for_percentage(percentage):
    """Get color code based on percentage"""
    if percentage >= 80:
        return "green"
    elif percentage >= 60:
        return "yellow"
    elif percentage >= 30:
        return "orange"
    else:
        return "red"


def get_status_icon(health_percentage, is_bleeding, is_fractured, is_infected):
    """Get status icon for body part"""
    if health_percentage <= 0:
        return "broken"
    elif is_bleeding or is_fractured or is_infected:
        return "critical"
    elif health_percentage < 50:
        return "warning"
    else:
        return "ok"


def format_body_parts_for_display(player):
    """Format body parts for visual display"""
    body_parts = player.body_parts.all()

    parts_data = []
    for part in body_parts:
        health_pct = part.health

        parts_data.append({
            'name': part.body_part.name,
            'part_type': part.body_part.body_part_type,
            'health_percentage': round(health_pct, 1),
            'color_code': get_color_for_percentage(health_pct),
            'status_icon': get_status_icon(health_pct, part.is_bleeding, part.is_fractured, part.is_infected),
            'is_bleeding': part.is_bleeding,
            'bleeding_severity': part.get_bleeding_severity_display() if part.is_bleeding else None,
            'is_fractured': part.is_fractured,
            'is_infected': part.is_infected,
            'pain_level': round(part.pain_level, 1),
            'is_bandaged': part.is_bandaged,
            'is_splinted': part.is_splinted,
            'status_text': part.status_description,
        })

    return parts_data


def create_nutrition_bar(name, current, max_val, unit, optimal_min=40, optimal_max=90):
    """Create nutrition bar data"""
    percentage = (current / max_val * 100) if max_val > 0 else 0

    # Determine warning level
    if percentage < 20:
        warning = "critical"
        color = "red"
    elif percentage < optimal_min:
        warning = "low"
        color = "orange"
    elif percentage > optimal_max:
        warning = "high"
        color = "yellow"
    else:
        warning = "none"
        color = "green"

    # Icons
    icons = {
        'Calories': '🔥',
        'Eau': '💧',
        'Protéines': '🥩',
        'Glucides': '🍞',
        'Lipides': '🥑',
        'Poids': '⚖️',
        'Muscle': '💪',
        'Graisse': '🫃',
    }

    return {
        'name': name,
        'current': round(current, 1),
        'max': round(max_val, 1),
        'percentage': round(percentage, 1),
        'unit': unit,
        'color': color,
        'warning_level': warning,
        'icon': icons.get(name, '📊'),
    }


def get_vitamin_mineral_status(level):
    """Get status for vitamin/mineral level"""
    if level < 30:
        return 'deficient', 'red'
    elif level < 60:
        return 'low', 'orange'
    elif level < 90:
        return 'normal', 'yellow'
    elif level <= 110:
        return 'optimal', 'green'
    else:
        return 'excess', 'yellow'


def format_metabolism_for_display(player):
    """Format metabolism data for display"""
    try:
        nutrition_status = player.nutrition_status
    except:
        nutrition_status = None

    # Body composition
    metabolism = {
        'body_weight': create_nutrition_bar('Poids', player.body_weight, 100, 'kg', 60, 80),
        'muscle_mass': create_nutrition_bar('Muscle', player.muscle_mass, 50, 'kg', 25, 40),
        'body_fat': create_nutrition_bar('Graisse', player.body_fat, 30, 'kg', 10, 20),

        'bmi': round(player.bmi, 1),
        'bmi_category': get_bmi_category(player.bmi),
        'fitness_level': player.fitness_level,

        # Energy
        'calories': create_nutrition_bar('Calories', player.calories_stored, player.max_calories, 'kcal'),
        'water': create_nutrition_bar('Eau', player.water_volume, player.max_water_volume, 'L'),

        # Macronutrients
        'proteins': create_nutrition_bar('Protéines', player.protein_stored, 500, 'g', 80, 300),
        'carbohydrates': create_nutrition_bar('Glucides', player.carbs_stored, 800, 'g', 100, 500),
        'fats': create_nutrition_bar('Lipides', player.fat_stored, 300, 'g', 50, 200),

        # Vitamins
        'vitamins': [],
        'minerals': [],

        # Digestion
        'stomach_fullness': round(player.stomach_fullness, 1),
        'intestine_fullness': round(player.intestine_contents, 1),
        'bladder_fullness': round(player.bladder_fullness, 1),
        'bowel_fullness': round(player.bowel_fullness, 1),

        # Flags
        'needs_food': player.is_hungry or player.is_starving,
        'needs_water': player.is_thirsty or player.is_dehydrated,
        'needs_bathroom': player.needs_bathroom,
    }

    # Add vitamins and minerals if nutrition status exists
    if nutrition_status:
        vitamins_data = [
            ('Vitamine A', nutrition_status.vitamin_a_level),
            ('Vitamine B', nutrition_status.vitamin_b_complex),
            ('Vitamine C', nutrition_status.vitamin_c_level),
            ('Vitamine D', nutrition_status.vitamin_d_level),
            ('Vitamine E', nutrition_status.vitamin_e_level),
        ]

        minerals_data = [
            ('Calcium', nutrition_status.calcium_level),
            ('Fer', nutrition_status.iron_level),
            ('Électrolytes', nutrition_status.electrolytes),
        ]

        metabolism['vitamins'] = [
            {
                'name': name,
                'level': round(level, 1),
                'status': get_vitamin_mineral_status(level)[0],
                'color': get_vitamin_mineral_status(level)[1],
            }
            for name, level in vitamins_data
        ]

        metabolism['minerals'] = [
            {
                'name': name,
                'level': round(level, 1),
                'status': get_vitamin_mineral_status(level)[0],
                'color': get_vitamin_mineral_status(level)[1],
            }
            for name, level in minerals_data
        ]

    return metabolism


def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi < 18.5:
        return "Sous-poids"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Surpoids"
    else:
        return "Obèse"


def format_vital_signs_for_display(player):
    """Format vital signs for display"""
    health_status = player.health_status

    # Temperature
    temp = health_status.body_temperature
    if temp < 35:
        temp_status = "Hypothermie"
        temp_color = "blue"
    elif temp < 36.5:
        temp_status = "Froid"
        temp_color = "cyan"
    elif temp > 38.5:
        temp_status = "Fièvre"
        temp_color = "orange"
    elif temp > 40:
        temp_status = "Hyperthermie"
        temp_color = "red"
    else:
        temp_status = "Normal"
        temp_color = "green"

    # Heart rate
    hr = health_status.heart_rate
    if hr < 50:
        hr_status = "Bradycardie"
        hr_color = "blue"
    elif hr > 100:
        hr_status = "Tachycardie"
        hr_color = "orange"
    elif hr > 120:
        hr_status = "Critique"
        hr_color = "red"
    else:
        hr_status = "Normal"
        hr_color = "green"

    # Blood
    blood = health_status.blood_volume
    if blood < 40:
        blood_status = "Hémorragie critique"
        blood_color = "red"
    elif blood < 70:
        blood_status = "Perte importante"
        blood_color = "orange"
    elif blood < 90:
        blood_status = "Légère perte"
        blood_color = "yellow"
    else:
        blood_status = "Normal"
        blood_color = "green"

    # Oxygen
    oxygen = health_status.oxygen_level
    if oxygen < 60:
        oxygen_status = "Hypoxie sévère"
        oxygen_color = "red"
    elif oxygen < 80:
        oxygen_status = "Hypoxie"
        oxygen_color = "orange"
    elif oxygen < 95:
        oxygen_status = "Légère hypoxie"
        oxygen_color = "yellow"
    else:
        oxygen_status = "Normal"
        oxygen_color = "green"

    return {
        'body_temperature': round(temp, 1),
        'temperature_status': temp_status,
        'temperature_color': temp_color,

        'heart_rate': hr,
        'heart_rate_status': hr_status,
        'heart_rate_color': hr_color,

        'blood_volume': round(blood, 1),
        'blood_status': blood_status,
        'blood_color': blood_color,

        'oxygen_level': round(oxygen, 1),
        'oxygen_status': oxygen_status,
        'oxygen_color': oxygen_color,

        'stamina': round(health_status.stamina, 1),
        'stamina_max': 100.0,
        'stamina_percentage': round(health_status.stamina, 1),
    }


def generate_health_alerts(player):
    """Generate health alerts and warnings"""
    alerts = []

    # Critical health
    if player.health < 20:
        alerts.append({
            'severity': 'emergency',
            'category': 'health',
            'message': 'SANTÉ CRITIQUE - Soins urgents requis!',
            'icon': '🚨',
            'action_required': 'Utiliser kit de soins ou trouver médecin',
        })

    # Bleeding
    bleeding_parts = player.body_parts.filter(is_bleeding=True).count()
    if bleeding_parts > 0:
        alerts.append({
            'severity': 'critical',
            'category': 'injury',
            'message': f'Saignement actif sur {bleeding_parts} partie(s)',
            'icon': '🩸',
            'action_required': 'Appliquer bandages immédiatement',
        })

    # Fractures
    fractured_parts = player.body_parts.filter(is_fractured=True).count()
    if fractured_parts > 0:
        alerts.append({
            'severity': 'warning',
            'category': 'injury',
            'message': f'{fractured_parts} fracture(s) détectée(s)',
            'icon': '🦴',
            'action_required': 'Poser attelles',
        })

    # Starvation
    if player.is_starving:
        alerts.append({
            'severity': 'critical',
            'category': 'nutrition',
            'message': 'FAMINE - Réserves d\'énergie critiques',
            'icon': '🍽️',
            'action_required': 'Manger immédiatement',
        })
    elif player.is_hungry:
        alerts.append({
            'severity': 'warning',
            'category': 'nutrition',
            'message': 'Faim - Énergie faible',
            'icon': '🍴',
            'action_required': 'Manger bientôt',
        })

    # Dehydration
    if player.is_dehydrated:
        alerts.append({
            'severity': 'critical',
            'category': 'hydration',
            'message': 'DÉSHYDRATATION - Danger!',
            'icon': '💧',
            'action_required': 'Boire immédiatement',
        })
    elif player.is_thirsty:
        alerts.append({
            'severity': 'warning',
            'category': 'hydration',
            'message': 'Soif',
            'icon': '🥤',
            'action_required': 'Boire de l\'eau',
        })

    # Diseases
    active_diseases = player.diseases.filter(current_severity__gt=0).count()
    if active_diseases > 0:
        alerts.append({
            'severity': 'warning',
            'category': 'disease',
            'message': f'{active_diseases} maladie(s) active(s)',
            'icon': '🦠',
            'action_required': 'Consulter onglet maladies',
        })

    # Bathroom
    if player.needs_bathroom:
        alerts.append({
            'severity': 'info',
            'category': 'comfort',
            'message': 'Besoin d\'utiliser les toilettes',
            'icon': '🚽',
            'action_required': 'Trouver des toilettes',
        })

    # Infections
    infected_parts = player.body_parts.filter(is_infected=True).count()
    if infected_parts > 0:
        alerts.append({
            'severity': 'warning',
            'category': 'injury',
            'message': f'{infected_parts} infection(s) active(s)',
            'icon': '🦠',
            'action_required': 'Utiliser antibiotiques',
        })

    # Blood volume
    if player.health_status.blood_volume < 70:
        alerts.append({
            'severity': 'critical',
            'category': 'health',
            'message': 'Volume sanguin faible',
            'icon': '🩸',
            'action_required': 'Transfusion ou solution saline requise',
        })

    return alerts


def generate_recommendations(player):
    """Generate health recommendations"""
    recommendations = []

    # Nutrition recommendations
    if player.calorie_percentage < 50:
        recommendations.append("Manger des aliments caloriques (viande, noix)")

    if player.protein_stored < 50:
        recommendations.append("Consommer plus de protéines (viande, poisson)")

    if player.carbs_stored < 100:
        recommendations.append("Manger des glucides (pain, fruits)")

    if player.hydration_percentage < 70:
        recommendations.append("Boire plus d'eau régulièrement")

    # Vitamins
    try:
        nutrition = player.nutrition_status
        if nutrition.vitamin_c_level < 60:
            recommendations.append("Manger des fruits (vitamine C)")
        if nutrition.vitamin_d_level < 60:
            recommendations.append("Exposition au soleil (vitamine D)")
        if nutrition.iron_level < 60:
            recommendations.append("Consommer viande rouge (fer)")
    except:
        pass

    # Body composition
    if player.body_fat_percentage > 25:
        recommendations.append("Augmenter activité physique, réduire lipides")
    elif player.body_fat_percentage < 10:
        recommendations.append("Augmenter apport calorique")

    if player.muscle_percentage < 30:
        recommendations.append("Augmenter apport protéines et exercice")

    # Health
    if player.health < 80:
        recommendations.append("Repos et bonne nutrition pour récupération")

    return recommendations


def get_time_since(dt):
    """Get formatted time since datetime"""
    if not dt:
        return "Jamais"

    now = timezone.now()
    delta = now - dt

    if delta.total_seconds() < 60:
        return "À l'instant"
    elif delta.total_seconds() < 3600:
        return f"Il y a {int(delta.total_seconds() / 60)} min"
    elif delta.total_seconds() < 86400:
        return f"Il y a {int(delta.total_seconds() / 3600)} h"
    else:
        return f"Il y a {int(delta.total_seconds() / 86400)} jours"


def get_complete_health_display(player):
    """
    Get complete health display data
    Optimized for SCUM-style interface
    """
    from ..services.metabolism_service import get_digesting_foods

    # Ensure health system is initialized
    if not hasattr(player, 'health_status'):
        from ..services.health_service import initialize_player_health
        initialize_player_health(player)

    health_status = player.health_status

    # Count conditions
    body_parts = player.body_parts.all()
    active_injuries = sum(1 for p in body_parts if p.health < 100)
    bleeding_count = sum(1 for p in body_parts if p.is_bleeding)
    fractured_count = sum(1 for p in body_parts if p.is_fractured)
    infected_count = sum(1 for p in body_parts if p.is_infected)
    diseases_count = player.diseases.filter(current_severity__gt=0).count()

    return {
        'overall_health_percentage': round(health_status.overall_health_percentage, 1),
        'health_status': health_status.status_summary,
        'is_critical': health_status.is_critical_condition,

        'body_parts': format_body_parts_for_display(player),
        'vital_signs': format_vital_signs_for_display(player),
        'metabolism': format_metabolism_for_display(player),

        'active_injuries_count': active_injuries,
        'active_diseases_count': diseases_count,
        'bleeding_parts_count': bleeding_count,
        'fractured_parts_count': fractured_count,
        'infected_parts_count': infected_count,

        'energy_regen_modifier': round(player.energy_regen_modifier, 2),
        'stamina_modifier': round(player.stamina_modifier, 2),
        'strength_modifier': round(player.strength_modifier, 2),

        'alerts': generate_health_alerts(player),
        'recommendations': generate_recommendations(player),

        'digesting_foods': get_digesting_foods(player),

        'time_since_last_meal': get_time_since(player.last_meal_time),
        'time_since_last_drink': get_time_since(player.last_drink_time),
        'time_until_next_meal_recommended': "2-4 heures" if player.last_meal_time else "Maintenant",
    }
