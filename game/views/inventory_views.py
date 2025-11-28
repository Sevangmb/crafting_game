from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Inventory, DroppedItem, MapCell, Player
from ..serializers import InventorySerializer, PlayerSerializer
from ..services import inventory_service

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(
            player__user=self.request.user
        ).select_related(
            'material', 'player__user'
        ).only(
            'id', 'quantity', 'durability_current', 'durability_max',
            'material__id', 'material__name', 'material__icon', 'material__rarity',
            'material__weight', 'material__is_food', 'material__category'
        )

    def list(self, request, *args, **kwargs):
        player = request.user.player
        data = inventory_service.get_inventory_summary(player)
        return Response(data)

    @action(detail=False, methods=['post'])
    def consume(self, request, pk=None):
        inventory_id = request.data.get('inventory_id')
        player = request.user.player

        result, status_code = inventory_service.consume_item(player, inventory_id)
        return Response(result, status=status_code)

    @action(detail=False, methods=['post'], url_path='drop')
    def drop_item(self, request):
        """Drop an item from inventory onto the ground"""
        try:
            player = request.user.player
            inventory_id = request.data.get('inventory_id')
            quantity = request.data.get('quantity', 1)

            if not inventory_id:
                return Response(
                    {'error': 'inventory_id est requis'},
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

            # Get inventory item
            try:
                inv_item = Inventory.objects.select_related('material').get(id=inventory_id, player=player)
            except Inventory.DoesNotExist:
                return Response(
                    {'error': 'Item non trouvé dans l\'inventaire'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check quantity available
            if inv_item.quantity < quantity:
                return Response(
                    {'error': f'Quantité insuffisante. Disponible: {inv_item.quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get or create current cell
            cell, created = MapCell.objects.get_or_create(
                grid_x=player.grid_x,
                grid_y=player.grid_y,
                defaults={
                    'center_lat': player.current_y,
                    'center_lon': player.current_x,
                    'biome': 'plains'
                }
            )

            # Create dropped item
            dropped = DroppedItem.objects.create(
                cell=cell,
                material=inv_item.material,
                quantity=quantity,
                durability_current=inv_item.durability_current if inv_item.durability_max > 0 else 0,
                durability_max=inv_item.durability_max,
                dropped_by=player
            )

            # Deduct from inventory
            inv_item.quantity -= quantity
            if inv_item.quantity == 0:
                inv_item.delete()
            else:
                inv_item.save()

            # Refresh player
            player.refresh_from_db()

            return Response({
                'success': True,
                'message': f'✅ Déposé {quantity}x {inv_item.material.name} sur le sol',
                'dropped_item_id': dropped.id,
                'player': PlayerSerializer(player).data
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='pickup')
    def pickup_item(self, request):
        """Pick up a dropped item from the ground"""
        try:
            player = request.user.player
            dropped_item_id = request.data.get('dropped_item_id')

            if not dropped_item_id:
                return Response(
                    {'error': 'dropped_item_id est requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get dropped item
            try:
                dropped = DroppedItem.objects.select_related('material', 'cell').get(id=dropped_item_id)
            except DroppedItem.DoesNotExist:
                return Response(
                    {'error': 'Objet non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if player is on the same cell
            if dropped.cell.grid_x != player.grid_x or dropped.cell.grid_y != player.grid_y:
                return Response(
                    {'error': 'Vous devez être sur la même cellule pour ramasser cet objet'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check weight capacity
            additional_weight = dropped.material.weight * dropped.quantity
            if player.current_carry_weight + additional_weight > player.effective_carry_capacity:
                return Response({
                    'error': f'Trop lourd ! Cet objet pèse {additional_weight:.1f}kg. Capacité: {player.current_carry_weight:.1f}/{player.effective_carry_capacity:.1f}kg'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Add to inventory
            inv_item, created = Inventory.objects.get_or_create(
                player=player,
                material=dropped.material,
                defaults={
                    'quantity': 0,
                    'durability_current': 0,
                    'durability_max': 0
                }
            )

            inv_item.quantity += dropped.quantity

            # For tools with durability, preserve durability
            if dropped.durability_max > 0:
                inv_item.durability_max = dropped.durability_max
                inv_item.durability_current = dropped.durability_current

            inv_item.save()

            # Delete dropped item
            material_name = dropped.material.name
            quantity = dropped.quantity
            dropped.delete()

            # Refresh player
            player.refresh_from_db()

            return Response({
                'success': True,
                'message': f'✅ Ramassé {quantity}x {material_name}',
                'player': PlayerSerializer(player).data
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
