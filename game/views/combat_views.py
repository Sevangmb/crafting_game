"""
Combat-related API views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..services import combat_service
from ..models import Player
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_combat(request):
    """
    Initiate combat with a mob at current location or specific mob_id.
    """
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        return Response({'error': 'Joueur introuvable'}, status=status.HTTP_404_NOT_FOUND)
    
    mob_id = request.data.get('mob_id', None)
    
    combat_state, status_code = combat_service.initiate_combat(player, mob_id)
    
    if status_code != 200:
        return Response(combat_state, status=status_code)
    
    return Response(combat_state, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def combat_action(request):
    """
    Execute a combat action (attack, defend, flee).
    Expects: combat_state (dict) and action (string)
    """
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        return Response({'error': 'Joueur introuvable'}, status=status.HTTP_404_NOT_FOUND)
    
    combat_state = request.data.get('combat_state')
    action = request.data.get('action', 'attack')
    
    if not combat_state:
        return Response({'error': 'État de combat manquant'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate combat state structure
    required_fields = ['mob_id', 'mob_health', 'player_health', 'status', 'rounds']
    for field in required_fields:
        if field not in combat_state:
            return Response(
                {'error': f'État de combat invalide: {field} manquant'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Validate action
    if action not in ['attack', 'defend', 'flee']:
        return Response({'error': 'Action invalide'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate combat is ongoing
    if combat_state.get('status') != 'ongoing':
        return Response({'error': 'Le combat est déjà terminé'}, status=status.HTTP_400_BAD_REQUEST)
    
    updated_state, status_code = combat_service.process_combat_action(player, combat_state, action)
    
    if status_code != 200:
        return Response(updated_state, status=status_code)
    
    # Refresh player data to send back
    player.refresh_from_db()
    updated_state['player_current_health'] = player.health
    updated_state['player_current_energy'] = player.energy
    updated_state['player_level'] = player.level
    updated_state['player_experience'] = player.experience
    
    return Response(updated_state, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def combat_history(request):
    """
    Get player's combat history.
    """
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        return Response({'error': 'Joueur introuvable'}, status=status.HTTP_404_NOT_FOUND)
    
    limit = int(request.query_params.get('limit', 10))
    history = combat_service.get_combat_history(player, limit)
    
    return Response({'history': history}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_for_mob(request):
    """
    Search for a mob at current location without starting combat.
    """
    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        return Response({'error': 'Joueur introuvable'}, status=status.HTTP_404_NOT_FOUND)
    
    # Check energy
    if player.energy < 2:
        return Response({'error': 'Pas assez d\'énergie pour chercher'}, status=status.HTTP_400_BAD_REQUEST)
    
    mob, found = combat_service.find_mob_at_location(player)
    
    # Deduct small energy for searching
    player.energy = max(0, player.energy - 2)
    player.save()
    
    if not found or not mob:
        return Response({
            'found': False,
            'message': 'Vous ne trouvez aucune trace d\'animal ici.'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'found': True,
        'mob': {
            'id': mob.id,
            'name': mob.name,
            'icon': mob.icon,
            'level': mob.level,
            'health': mob.health,
            'attack': mob.attack,
            'defense': mob.defense,
            'aggression': mob.aggression_level,
            'description': mob.description
        },
        'message': f'Vous avez trouvé un {mob.name}!'
    }, status=status.HTTP_200_OK)
