"""
Health management service
Handles injuries, bleeding, diseases, and body part health
Inspired by SCUM's detailed health system
"""
from django.utils import timezone
from django.db.models import F
from decimal import Decimal
import random

from ..models import (
    Player, BodyPart, PlayerBodyPart, PlayerHealthStatus,
    Disease, PlayerDisease, MedicalItem
)


def initialize_player_health(player):
    """
    Initialize health status and body parts for a new player
    Call this when a player is created
    """
    # Create health status if it doesn't exist
    health_status, created = PlayerHealthStatus.objects.get_or_create(
        player=player,
        defaults={
            'body_temperature': 37.0,
            'heart_rate': 70,
            'blood_volume': 100.0,
            'oxygen_level': 100.0,
            'stamina': 100.0,
            'wetness_level': 0.0,
            'exhaustion_level': 0.0,
            'immune_strength': 100.0,
            'health_regen_rate': 1.0,
        }
    )

    # Create all body parts
    all_body_parts = BodyPart.objects.all()
    for body_part in all_body_parts:
        PlayerBodyPart.objects.get_or_create(
            player=player,
            body_part=body_part,
            defaults={
                'health': 100.0,
                'is_bleeding': False,
                'bleeding_severity': 'none',
                'bleeding_rate': 0.0,
                'is_fractured': False,
                'fracture_severity': 'none',
                'is_infected': False,
                'infection_level': 0.0,
                'pain_level': 0.0,
            }
        )

    return health_status


def apply_damage_to_body_part(player, body_part_type, damage_amount, cause_bleeding=False,
                              bleeding_severity='minor', can_fracture=False):
    """
    Apply damage to a specific body part

    Args:
        player: Player instance
        body_part_type: str (e.g., 'head', 'left_arm')
        damage_amount: float (amount of health to reduce)
        cause_bleeding: bool (whether this causes bleeding)
        bleeding_severity: str ('minor', 'moderate', 'severe', 'critical')
        can_fracture: bool (whether this can cause a fracture)

    Returns:
        dict with damage details
    """
    try:
        body_part = BodyPart.objects.get(body_part_type=body_part_type)
        player_body_part = PlayerBodyPart.objects.get(player=player, body_part=body_part)
    except (BodyPart.DoesNotExist, PlayerBodyPart.DoesNotExist):
        return {'success': False, 'error': 'Body part not found'}

    # Apply damage
    player_body_part.health = max(0, player_body_part.health - damage_amount)

    # Pain increases with damage
    pain_increase = damage_amount * 0.5
    player_body_part.pain_level = min(100, player_body_part.pain_level + pain_increase)

    # Bleeding
    if cause_bleeding and not player_body_part.is_bleeding:
        player_body_part.is_bleeding = True
        player_body_part.bleeding_severity = bleeding_severity

        # Calculate bleeding rate based on severity and body part
        severity_multipliers = {
            'minor': 0.5,
            'moderate': 1.0,
            'severe': 2.0,
            'critical': 4.0,
        }
        multiplier = severity_multipliers.get(bleeding_severity, 1.0)
        player_body_part.bleeding_rate = body_part.base_bleeding_rate * multiplier

    # Fracture chance
    if can_fracture and body_part.can_fracture and not player_body_part.is_fractured:
        fracture_chance = min(damage_amount / 100.0, 0.8)  # Max 80% chance
        if random.random() < fracture_chance:
            player_body_part.is_fractured = True
            # Severity based on damage
            if damage_amount < 20:
                player_body_part.fracture_severity = 'minor'
            elif damage_amount < 40:
                player_body_part.fracture_severity = 'moderate'
            elif damage_amount < 70:
                player_body_part.fracture_severity = 'severe'
            else:
                player_body_part.fracture_severity = 'critical'

    player_body_part.save()

    # Update overall player health based on body part damage
    update_overall_health(player)

    return {
        'success': True,
        'body_part': body_part.name,
        'damage': damage_amount,
        'remaining_health': player_body_part.health,
        'is_bleeding': player_body_part.is_bleeding,
        'is_fractured': player_body_part.is_fractured,
        'pain_level': player_body_part.pain_level,
    }


def update_overall_health(player):
    """
    Update player's overall health based on all body parts
    Critical parts (head, torso) have more weight
    """
    health_status = PlayerHealthStatus.objects.get(player=player)
    overall_health = health_status.overall_health_percentage

    # Update player's main health
    player.health = int(overall_health)
    player.save()

    return overall_health


def process_bleeding(player):
    """
    Process bleeding for all injured body parts
    Called periodically (e.g., every minute)

    Returns:
        dict with total blood loss
    """
    health_status = PlayerHealthStatus.objects.get(player=player)
    bleeding_parts = PlayerBodyPart.objects.filter(player=player, is_bleeding=True)

    total_blood_loss = 0.0

    for part in bleeding_parts:
        if not part.is_bandaged:
            # Lose blood based on bleeding rate
            blood_loss = part.bleeding_rate * 0.1  # Per minute
            total_blood_loss += blood_loss

            # Increase pain
            part.pain_level = min(100, part.pain_level + 1)

            # Chance of infection if bleeding for too long
            if random.random() < 0.01:  # 1% chance per minute
                part.is_infected = True
                part.infection_level = 5.0

            part.save()
        else:
            # Bandaged wounds have reduced bleeding
            if part.bandage_quality > 50:
                # Good bandage stops bleeding
                part.is_bleeding = False
                part.bleeding_rate = 0.0
                part.bleeding_severity = 'none'
                part.save()

    # Update blood volume
    health_status.blood_volume = max(0, health_status.blood_volume - total_blood_loss)
    health_status.save()

    # Critical blood loss affects overall health
    if health_status.blood_volume < 50:
        player.health = int(player.health * 0.98)  # Gradual health loss
        player.save()

    return {
        'total_blood_loss': total_blood_loss,
        'current_blood_volume': health_status.blood_volume,
        'bleeding_parts_count': bleeding_parts.count(),
    }


def apply_bandage(player, body_part_type, bandage_quality=70):
    """
    Apply a bandage to a bleeding body part

    Args:
        player: Player instance
        body_part_type: str
        bandage_quality: int (0-100, quality of the bandage)
    """
    try:
        body_part = BodyPart.objects.get(body_part_type=body_part_type)
        player_body_part = PlayerBodyPart.objects.get(player=player, body_part=body_part)
    except (BodyPart.DoesNotExist, PlayerBodyPart.DoesNotExist):
        return {'success': False, 'error': 'Body part not found'}

    if not player_body_part.is_bleeding:
        return {'success': False, 'error': 'Body part is not bleeding'}

    player_body_part.is_bandaged = True
    player_body_part.bandage_quality = bandage_quality
    player_body_part.bandage_applied_at = timezone.now()

    # High quality bandages stop bleeding immediately
    if bandage_quality >= 80:
        player_body_part.is_bleeding = False
        player_body_part.bleeding_rate = 0.0
        player_body_part.bleeding_severity = 'none'
    else:
        # Reduce bleeding rate
        player_body_part.bleeding_rate *= (1 - bandage_quality / 100.0)

    player_body_part.save()

    return {
        'success': True,
        'body_part': body_part.name,
        'still_bleeding': player_body_part.is_bleeding,
    }


def apply_splint(player, body_part_type):
    """
    Apply a splint to a fractured body part
    """
    try:
        body_part = BodyPart.objects.get(body_part_type=body_part_type)
        player_body_part = PlayerBodyPart.objects.get(player=player, body_part=body_part)
    except (BodyPart.DoesNotExist, PlayerBodyPart.DoesNotExist):
        return {'success': False, 'error': 'Body part not found'}

    if not player_body_part.is_fractured:
        return {'success': False, 'error': 'Body part is not fractured'}

    player_body_part.is_splinted = True
    player_body_part.splint_applied_at = timezone.now()

    # Reduce pain
    player_body_part.pain_level = max(0, player_body_part.pain_level - 20)

    player_body_part.save()

    return {
        'success': True,
        'body_part': body_part.name,
        'pain_level': player_body_part.pain_level,
    }


def heal_body_part(player, body_part_type, heal_amount):
    """
    Heal a specific body part
    """
    try:
        body_part = BodyPart.objects.get(body_part_type=body_part_type)
        player_body_part = PlayerBodyPart.objects.get(player=player, body_part=body_part)
    except (BodyPart.DoesNotExist, PlayerBodyPart.DoesNotExist):
        return {'success': False, 'error': 'Body part not found'}

    player_body_part.health = min(100, player_body_part.health + heal_amount)

    # Reduce pain as health increases
    player_body_part.pain_level = max(0, player_body_part.pain_level - heal_amount * 0.3)

    player_body_part.save()
    update_overall_health(player)

    return {
        'success': True,
        'body_part': body_part.name,
        'current_health': player_body_part.health,
    }


def process_infections(player):
    """
    Process infections in body parts
    Called periodically
    """
    infected_parts = PlayerBodyPart.objects.filter(player=player, is_infected=True)

    for part in infected_parts:
        # Infection worsens over time if not treated
        part.infection_level = min(100, part.infection_level + 1.0)

        # High infection causes health damage
        if part.infection_level > 50:
            damage = (part.infection_level - 50) * 0.1
            part.health = max(0, part.health - damage)

        # Pain increases with infection
        part.pain_level = min(100, part.pain_level + 0.5)

        # Very high infection can spread to disease
        if part.infection_level > 80 and random.random() < 0.05:
            contract_disease(player, 'Infection bactérienne')

        part.save()

    update_overall_health(player)

    return {
        'infected_parts_count': infected_parts.count(),
    }


def contract_disease(player, disease_name, initial_severity=10.0):
    """
    Player contracts a disease

    Args:
        player: Player instance
        disease_name: str (name of the disease)
        initial_severity: float (starting severity)
    """
    try:
        disease = Disease.objects.get(name=disease_name)
    except Disease.DoesNotExist:
        return {'success': False, 'error': 'Disease not found'}

    player_disease, created = PlayerDisease.objects.get_or_create(
        player=player,
        disease=disease,
        defaults={
            'current_severity': initial_severity,
            'is_being_treated': False,
            'treatment_effectiveness': 0.0,
        }
    )

    if not created:
        # Increase severity if already has disease
        player_disease.current_severity = min(100, player_disease.current_severity + 5)
        player_disease.save()

    # Update health status
    health_status = PlayerHealthStatus.objects.get(player=player)
    health_status.is_sick = True
    health_status.save()

    return {
        'success': True,
        'disease': disease.name,
        'severity': player_disease.current_severity,
        'created': created,
    }


def process_diseases(player):
    """
    Process all active diseases affecting the player
    Called periodically (e.g., every hour)
    """
    active_diseases = PlayerDisease.objects.filter(player=player, current_severity__gt=0)
    health_status = PlayerHealthStatus.objects.get(player=player)

    total_health_drain = 0.0
    total_stat_penalty = 0.0

    for player_disease in active_diseases:
        disease = player_disease.disease

        # Disease progression
        if player_disease.is_being_treated:
            # Treatment reduces severity
            recovery = player_disease.treatment_effectiveness
            player_disease.current_severity = max(0, player_disease.current_severity - recovery)
        else:
            # Disease worsens
            progression = disease.progression_rate
            # Immune system can slow progression
            immune_factor = health_status.immune_strength / 100.0
            progression *= (1 - immune_factor * 0.5)

            player_disease.current_severity = min(100, player_disease.current_severity + progression)

        # Apply disease effects
        if player_disease.current_severity > 0:
            total_health_drain += disease.health_drain_rate * (player_disease.current_severity / 100.0)
            total_stat_penalty += disease.stat_penalty * (player_disease.current_severity / 100.0)

            # Symptoms
            if disease.causes_fever:
                health_status.body_temperature = min(40, 37 + player_disease.current_severity / 20.0)

            if disease.causes_fatigue:
                health_status.exhaustion_level = min(100, health_status.exhaustion_level + 1)

        player_disease.save()

    # Apply total health drain
    if total_health_drain > 0:
        player.health = max(0, int(player.health - total_health_drain))
        player.save()

    # Check if still sick
    if not active_diseases.exists():
        health_status.is_sick = False
        health_status.body_temperature = 37.0

    health_status.sickness_severity = max(pd.current_severity for pd in active_diseases) if active_diseases.exists() else 0
    health_status.save()

    return {
        'active_diseases_count': active_diseases.count(),
        'total_health_drain': total_health_drain,
        'total_stat_penalty': total_stat_penalty,
    }


def natural_healing(player):
    """
    Process natural health regeneration
    Called periodically (e.g., every hour)
    Healing is affected by nutrition, rest, and overall condition
    """
    health_status = PlayerHealthStatus.objects.get(player=player)

    # Base healing rate
    healing = health_status.health_regen_rate

    # Nutrition affects healing
    try:
        nutrition_status = player.nutrition_status
        nutrition_score = nutrition_status.overall_nutrition_score / 100.0
        healing *= nutrition_status.healing_rate * nutrition_score
    except:
        pass

    # Exhaustion reduces healing
    if health_status.exhaustion_level > 50:
        healing *= 0.5

    # Disease reduces healing
    if health_status.is_sick:
        healing *= 0.3

    # Heal body parts gradually
    damaged_parts = PlayerBodyPart.objects.filter(
        player=player,
        health__lt=100
    ).exclude(is_fractured=True)  # Fractured parts need splints

    for part in damaged_parts:
        # Faster healing if splinted
        part_healing = healing
        if part.is_splinted:
            part_healing *= 1.5

        part.health = min(100, part.health + part_healing)

        # Reduce pain as healing occurs
        part.pain_level = max(0, part.pain_level - 0.5)

        # Reduce infection if immune system is strong
        if part.is_infected and health_status.immune_strength > 70:
            part.infection_level = max(0, part.infection_level - 0.5)
            if part.infection_level == 0:
                part.is_infected = False

        part.save()

    update_overall_health(player)

    return {
        'healing_amount': healing,
        'parts_healed': damaged_parts.count(),
    }


def get_player_health_summary(player):
    """
    Get comprehensive health summary for the player
    """
    try:
        health_status = PlayerHealthStatus.objects.get(player=player)
    except PlayerHealthStatus.DoesNotExist:
        health_status = initialize_player_health(player)

    body_parts = PlayerBodyPart.objects.filter(player=player)
    diseases = PlayerDisease.objects.filter(player=player, current_severity__gt=0)

    # Calculate overall pain
    total_pain = sum(part.pain_level for part in body_parts) / max(body_parts.count(), 1)

    # Count injuries
    bleeding_count = body_parts.filter(is_bleeding=True).count()
    fractured_count = body_parts.filter(is_fractured=True).count()
    infected_count = body_parts.filter(is_infected=True).count()

    return {
        'overall_health': player.health,
        'blood_volume': health_status.blood_volume,
        'body_temperature': health_status.body_temperature,
        'stamina': health_status.stamina,
        'overall_pain': total_pain,
        'is_critical': health_status.is_critical_condition,
        'status_summary': health_status.status_summary,
        'injuries': {
            'bleeding_parts': bleeding_count,
            'fractured_parts': fractured_count,
            'infected_parts': infected_count,
        },
        'diseases_count': diseases.count(),
        'body_parts': [
            {
                'name': part.body_part.name,
                'type': part.body_part.body_part_type,
                'health': part.health,
                'status': part.status_description,
                'is_healthy': part.is_healthy,
            }
            for part in body_parts
        ],
        'active_diseases': [
            {
                'name': disease.disease.name,
                'severity': disease.current_severity,
                'stage': disease.stage_description,
            }
            for disease in diseases
        ],
    }
