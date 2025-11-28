"""
Character sheet API views
Complete SCUM-style character information
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import Player
from ..serializers.character_sheet import (
    CompleteCharacterSheetSerializer,
    DigestingFoodSerializer,
    MetabolismSerializer
)
from ..services.metabolism_service import (
    update_player_metabolism,
    get_metabolism_status,
    get_digesting_foods,
    eat_food,
    drink_water,
    use_bathroom
)
from ..services.health_service import (
    get_player_health_summary,
    initialize_player_health
)
from ..services.health_display_service import get_complete_health_display


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_character_sheet(request):
    """
    Get complete character sheet with all detailed information

    GET /api/character/sheet/

    Returns comprehensive SCUM-style character data including:
    - Core stats (level, attributes, health, energy)
    - Metabolism (calories, nutrients, hydration, body composition)
    - Health (body parts, diseases, vital signs)
    - Skills
    - Digesting foods
    - Vehicle info
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Initialize health system if needed
    if not hasattr(player, 'health_status'):
        from ..services.health_service import initialize_player_health
        initialize_player_health(player)

    # Update metabolism before returning data
    update_player_metabolism(player)

    # Prepare data
    player.refresh_from_db()

    # Get metabolism status
    metabolism = get_metabolism_status(player)

    # Get digesting foods
    digesting_foods = get_digesting_foods(player)

    # Get health status
    health_status = player.health_status
    body_parts = player.body_parts.all()
    diseases = player.diseases.filter(current_severity__gt=0)

    # Get skills
    skills = player.skills.all()

    # Build complete character data
    character_data = {
        'username': player.user.username,
        'player_id': player.id,
        'current_x': player.current_x,
        'current_y': player.current_y,

        'stats': {
            'level': player.level,
            'experience': player.experience,
            'strength': player.strength,
            'agility': player.agility,
            'intelligence': player.intelligence,
            'luck': player.luck,
            'health': player.health,
            'max_health': player.max_health,
            'energy': player.energy,
            'max_energy': player.max_energy,
            'total_attack': player.total_attack,
            'total_defense': player.total_defense,
            'total_speed_bonus': player.total_speed_bonus,
            'current_carry_weight': player.current_carry_weight,
            'effective_carry_capacity': player.effective_carry_capacity,
            'is_overencumbered': player.is_overencumbered,
            'money': player.money,
            'credit_card_balance': player.credit_card_balance,
        },

        'metabolism': metabolism,
        'digesting_foods': digesting_foods,

        'health_status': {
            'body_temperature': health_status.body_temperature,
            'heart_rate': health_status.heart_rate,
            'blood_volume': health_status.blood_volume,
            'oxygen_level': health_status.oxygen_level,
            'stamina': health_status.stamina,
            'is_wet': health_status.is_wet,
            'wetness_level': health_status.wetness_level,
            'is_hypothermic': health_status.is_hypothermic,
            'is_hyperthermic': health_status.is_hyperthermic,
            'exhaustion_level': health_status.exhaustion_level,
            'is_sick': health_status.is_sick,
            'sickness_severity': health_status.sickness_severity,
            'immune_strength': health_status.immune_strength,
            'is_critical': health_status.is_critical_condition,
            'overall_health': health_status.overall_health_percentage,
            'status': health_status.status_summary,
        },

        'body_parts': [{
            'name': part.body_part.name,
            'type': part.body_part.body_part_type,
            'health': part.health,
            'is_bleeding': part.is_bleeding,
            'is_fractured': part.is_fractured,
            'is_infected': part.is_infected,
            'pain_level': part.pain_level,
            'status': part.status_description,
        } for part in body_parts],

        'active_diseases': [{
            'name': disease.disease.name,
            'severity': disease.current_severity,
            'stage': disease.stage_description,
        } for disease in diseases],

        'skills': [{
            'name': skill.skill.name,
            'code': skill.skill.code,
            'level': skill.level,
            'xp': skill.xp,
            'xp_to_next': skill.xp_to_next,
        } for skill in skills],

        'has_vehicle': player.current_vehicle is not None,
        'vehicle_info': None,
    }

    # Add vehicle info if equipped
    if player.current_vehicle:
        vehicle = player.current_vehicle
        character_data['vehicle_info'] = {
            'name': vehicle.display_name,
            'type': vehicle.vehicle_type.name,
            'fuel_percentage': vehicle.fuel_percentage,
            'durability_percentage': vehicle.durability_percentage,
            'can_drive': vehicle.can_drive,
        }

    return Response(character_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_metabolism_details(request):
    """
    Get detailed metabolism information only

    GET /api/character/metabolism/
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Update metabolism
    update_player_metabolism(player)
    player.refresh_from_db()

    metabolism = get_metabolism_status(player)
    digesting = get_digesting_foods(player)

    return Response({
        'metabolism': metabolism,
        'digesting_foods': digesting,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def consume_food(request):
    """
    Consume food item

    POST /api/character/eat/
    {
        "food_material_id": 123,
        "quantity_grams": 150
    }
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    food_material_id = request.data.get('food_material_id')
    quantity_grams = request.data.get('quantity_grams', 100)

    if not food_material_id:
        return Response(
            {'error': 'food_material_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    from ..models import Material
    try:
        food_material = Material.objects.get(id=food_material_id, is_food=True)
    except Material.DoesNotExist:
        return Response(
            {'error': 'Food item not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    result = eat_food(player, food_material, quantity_grams)

    if not result['success']:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def drink(request):
    """
    Drink water or beverage

    POST /api/character/drink/
    {
        "amount_ml": 250
    }
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    amount_ml = request.data.get('amount_ml', 250)

    result = drink_water(player, amount_ml)
    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bathroom(request):
    """
    Use bathroom

    POST /api/character/bathroom/
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    result = use_bathroom(player)

    if not result['success']:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_metabolism(request):
    """
    Manually trigger metabolism update

    POST /api/character/metabolism/update/
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    result = update_player_metabolism(player)
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_health_display(request):
    """
    Get complete health display data for SCUM-style interface

    GET /api/character/health-display/

    Returns comprehensive health UI data including:
    - Body parts with color codes and status
    - Vital signs with colored indicators
    - Metabolism bars (calories, water, nutrients)
    - Vitamins and minerals levels
    - Body composition (weight, muscle, fat)
    - Digestion status
    - Health alerts and warnings
    - Recommendations
    - Performance modifiers

    Optimized for visual health interface like SCUM
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Update metabolism before getting display data
    update_player_metabolism(player)
    player.refresh_from_db()

    # Get formatted display data
    display_data = get_complete_health_display(player)

    return Response(display_data)
