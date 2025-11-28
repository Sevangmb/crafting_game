"""
Views for POI (Point of Interest) interactions
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import Player, MapCell
from ..services.poi_service import POIService
from ..serializers import PlayerSerializer


class POIViewSet(viewsets.ViewSet):
    """ViewSet for POI interactions"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='current-pois')
    def current_pois(self, request):
        """
        Get all interactive POIs in the player's current cell
        """
        try:
            player = get_object_or_404(Player, user=request.user)

            # Get current cell
            cell = MapCell.objects.filter(
                grid_x=player.grid_x,
                grid_y=player.grid_y
            ).first()

            if not cell:
                return Response({
                    'pois': [],
                    'message': 'Aucune cellule trouvée à cette position'
                })

            # Extract POIs from OSM features
            osm_features = cell.osm_features or []
            pois = POIService.get_poi_from_osm_features(osm_features)

            return Response({
                'pois': pois,
                'cell_position': {'x': cell.grid_x, 'y': cell.grid_y},
                'count': len(pois)
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='menu/(?P<poi_type>[^/.]+)')
    def get_menu(self, request, poi_type=None):
        """
        Get the menu/inventory for a specific POI type
        """
        try:
            menu_data = POIService.get_poi_menu(poi_type)

            if not menu_data or not menu_data.get('menu'):
                return Response(
                    {'error': f"Type de POI '{poi_type}' non reconnu ou menu vide"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(menu_data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='purchase')
    def purchase(self, request):
        """
        Purchase an item from a POI
        Expected data: {poi_type, material_id, quantity}
        """
        try:
            player = get_object_or_404(Player, user=request.user)

            poi_type = request.data.get('poi_type')
            material_id = request.data.get('material_id')
            quantity = request.data.get('quantity', 1)

            if not poi_type or not material_id:
                return Response(
                    {'error': 'poi_type et material_id sont requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate quantity
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Quantité invalide'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Attempt purchase
            success, message, player_data = POIService.purchase_item(
                player, poi_type, material_id, quantity
            )

            if success:
                return Response({
                    'success': True,
                    'message': message,
                    'player': player_data
                })
            else:
                return Response({
                    'success': False,
                    'error': message
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
