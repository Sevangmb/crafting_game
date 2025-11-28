"""
Time-related API views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from game.services.time_service import TimeService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_game_time(request):
    """Get current game time information"""
    player = request.user.player
    time_info = TimeService.get_time_info(player)
    
    return Response(time_info)
