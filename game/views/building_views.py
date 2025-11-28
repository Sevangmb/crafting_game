"""
Building API Views
Handles building construction, management, and queries
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from game.models import Building, BuildingType, MapCell, Player
from game.serializers import BuildingSerializer, BuildingTypeSerializer
from game.services import building_service
from game.cache_utils import cache_view_response, CacheManager
import logging

logger = logging.getLogger(__name__)


class BuildingTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for building types (read-only)"""
    queryset = BuildingType.objects.all()
    serializer_class = BuildingTypeSerializer
    permission_classes = [IsAuthenticated]

    @cache_view_response('cache_long', 'building_types')
    def list(self, request, *args, **kwargs):
        """List all building types"""
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get building types available to current player based on level"""
        try:
            player = Player.objects.get(user=request.user)
            available_types = building_service.get_available_building_types(player)
            return Response(available_types, status=status.HTTP_200_OK)
        except Player.DoesNotExist:
            return Response(
                {'error': 'Joueur introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting available building types: {e}")
            return Response(
                {'error': 'Erreur lors de la récupération des types de bâtiments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BuildingViewSet(viewsets.ModelViewSet):
    """ViewSet for player buildings"""
    serializer_class = BuildingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get buildings for current player"""
        return Building.objects.filter(
            player__user=self.request.user
        ).select_related('building_type', 'cell', 'player__user')

    @action(detail=False, methods=['get'])
    def my_buildings(self, request):
        """Get all buildings owned by current player"""
        try:
            player = Player.objects.get(user=request.user)
            buildings = building_service.get_player_buildings(player)
            return Response(buildings, status=status.HTTP_200_OK)
        except Player.DoesNotExist:
            return Response(
                {'error': 'Joueur introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting player buildings: {e}")
            return Response(
                {'error': 'Erreur lors de la récupération des bâtiments'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def construct(self, request):
        """
        Start construction of a new building
        Required data: building_type_id, cell_id
        """
        try:
            player = Player.objects.get(user=request.user)
            building_type_id = request.data.get('building_type_id')
            cell_id = request.data.get('cell_id')

            if not building_type_id or not cell_id:
                return Response(
                    {'error': 'building_type_id et cell_id sont requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            building, new_achievements = building_service.start_construction(player, building_type_id, cell_id)

            # Clear cache
            CacheManager.clear_player_cache(player.id)

            response_data = {
                'message': f'Construction de {building.building_type.name} commencée!',
                'building': BuildingSerializer(building).data
            }

            # Add achievements if any
            if new_achievements:
                response_data['achievements_unlocked'] = [
                    {
                        'id': ach.id,
                        'name': ach.name,
                        'description': ach.description,
                        'icon': ach.icon,
                        'reward_xp': ach.reward_xp
                    }
                    for ach in new_achievements
                ]

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Player.DoesNotExist:
            return Response(
                {'error': 'Joueur introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error starting construction: {e}")
            error_message = str(e) if str(e) else 'Erreur lors du démarrage de la construction'
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Complete construction of a building
        """
        try:
            player = Player.objects.get(user=request.user)
            building, house_created = building_service.complete_construction(pk, player)

            # Clear cache
            CacheManager.clear_player_cache(player.id)

            return Response({
                'message': f'{building.building_type.name} construction terminée!',
                'building': BuildingSerializer(building).data,
                'house_created': house_created
            }, status=status.HTTP_200_OK)

        except Player.DoesNotExist:
            return Response(
                {'error': 'Joueur introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error completing construction: {e}")
            error_message = str(e) if str(e) else 'Erreur lors de la finalisation de la construction'
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def bonuses(self, request):
        """Get total bonuses from all player's completed buildings"""
        try:
            player = Player.objects.get(user=request.user)
            bonuses = building_service.calculate_player_bonuses(player)
            return Response(bonuses, status=status.HTTP_200_OK)
        except Player.DoesNotExist:
            return Response(
                {'error': 'Joueur introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error calculating bonuses: {e}")
            return Response(
                {'error': 'Erreur lors du calcul des bonus'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
