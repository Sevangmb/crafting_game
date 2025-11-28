"""
API views for the health system
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import Player, BodyPart, PlayerBodyPart, PlayerHealthStatus, Disease
from ..serializers import (
    BodyPartSerializer, PlayerBodyPartSerializer, PlayerHealthStatusSerializer,
    DiseaseSerializer, PlayerDiseaseSerializer, HealthSummarySerializer
)
from ..services.health_service import (
    initialize_player_health,
    apply_damage_to_body_part,
    apply_bandage,
    apply_splint,
    heal_body_part,
    get_player_health_summary,
    contract_disease,
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_health_status(request):
    """
    Get comprehensive health status for the current player

    GET /api/health/status/

    Returns:
        - overall_health: Overall health percentage
        - blood_volume: Current blood volume
        - body_temperature: Current body temperature
        - stamina: Current stamina
        - overall_pain: Average pain level across all body parts
        - is_critical: Whether player is in critical condition
        - status_summary: Human-readable status
        - injuries: Count of bleeding, fractured, and infected parts
        - diseases_count: Number of active diseases
        - body_parts: Detailed status of all body parts
        - active_diseases: List of active diseases
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
        initialize_player_health(player)

    summary = get_player_health_summary(player)
    serializer = HealthSummarySerializer(summary)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_body_parts(request):
    """
    Get status of all body parts

    GET /api/health/body-parts/
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    body_parts = PlayerBodyPart.objects.filter(player=player).select_related('body_part')
    serializer = PlayerBodyPartSerializer(body_parts, many=True)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_diseases(request):
    """
    Get all active diseases affecting the player

    GET /api/health/diseases/
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    diseases = player.diseases.filter(current_severity__gt=0).select_related('disease')
    serializer = PlayerDiseaseSerializer(diseases, many=True)

    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_bandage(request):
    """
    Apply a bandage to a bleeding body part

    POST /api/health/bandage/

    Request body:
        {
            "body_part_type": "head",  // or "left_arm", "torso", etc.
            "bandage_quality": 70  // Optional, defaults to 70
        }

    Returns:
        {
            "success": true,
            "body_part": "Tête",
            "still_bleeding": false
        }
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    body_part_type = request.data.get('body_part_type')
    bandage_quality = request.data.get('bandage_quality', 70)

    if not body_part_type:
        return Response(
            {'error': 'body_part_type is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    result = apply_bandage(player, body_part_type, bandage_quality)

    if not result['success']:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_splint(request):
    """
    Apply a splint to a fractured body part

    POST /api/health/splint/

    Request body:
        {
            "body_part_type": "left_leg"
        }

    Returns:
        {
            "success": true,
            "body_part": "Jambe gauche",
            "pain_level": 30.0
        }
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    body_part_type = request.data.get('body_part_type')

    if not body_part_type:
        return Response(
            {'error': 'body_part_type is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    result = apply_splint(player, body_part_type)

    if not result['success']:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def heal_part(request):
    """
    Heal a specific body part (using medical items)

    POST /api/health/heal/

    Request body:
        {
            "body_part_type": "head",
            "heal_amount": 20
        }
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    body_part_type = request.data.get('body_part_type')
    heal_amount = request.data.get('heal_amount', 10)

    if not body_part_type:
        return Response(
            {'error': 'body_part_type is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    result = heal_body_part(player, body_part_type, heal_amount)

    if not result['success']:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(result)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def damage_part(request):
    """
    Apply damage to a body part (for testing or combat)

    POST /api/health/damage/

    Request body:
        {
            "body_part_type": "torso",
            "damage_amount": 25,
            "cause_bleeding": true,
            "bleeding_severity": "moderate",
            "can_fracture": true
        }
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    body_part_type = request.data.get('body_part_type')
    damage_amount = request.data.get('damage_amount', 10)
    cause_bleeding = request.data.get('cause_bleeding', False)
    bleeding_severity = request.data.get('bleeding_severity', 'minor')
    can_fracture = request.data.get('can_fracture', False)

    if not body_part_type:
        return Response(
            {'error': 'body_part_type is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    result = apply_damage_to_body_part(
        player, body_part_type, damage_amount,
        cause_bleeding, bleeding_severity, can_fracture
    )

    if not result['success']:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_diseases(request):
    """
    List all available diseases in the game

    GET /api/health/diseases/all/
    """
    diseases = Disease.objects.all()
    serializer = DiseaseSerializer(diseases, many=True)

    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def infect_disease(request):
    """
    Contract a disease (for testing or game events)

    POST /api/health/diseases/contract/

    Request body:
        {
            "disease_name": "Grippe",
            "initial_severity": 20.0
        }
    """
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    disease_name = request.data.get('disease_name')
    initial_severity = request.data.get('initial_severity', 10.0)

    if not disease_name:
        return Response(
            {'error': 'disease_name is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    result = contract_disease(player, disease_name, initial_severity)

    if not result['success']:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    return Response(result)
