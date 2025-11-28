from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..services import vehicle_service
from ..models import Player

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_vehicles(request):
    player = request.user.player
    from ..services.advanced_vehicle_service import get_player_vehicles, get_vehicle_status

    vehicles = get_player_vehicles(player)
    data = [get_vehicle_status(v) for v in vehicles]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def equip_vehicle(request, vehicle_id):
    player = request.user.player
    result, status = vehicle_service.equip_vehicle(player, vehicle_id)
    return Response(result, status=status)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unequip_vehicle(request):
    player = request.user.player
    result, status = vehicle_service.unequip_vehicle(player)
    return Response(result, status=status)
