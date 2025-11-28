"""
Shop views for buying and selling items
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Shop, ShopItem, Player, Material, Transaction
from ..serializers import ShopSerializer, ShopItemSerializer, TransactionSerializer
from ..services.economy_service import EconomyService
import logging

logger = logging.getLogger(__name__)


class ShopViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for shops"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter shops by biome if specified"""
        queryset = Shop.objects.all()
        biome = self.request.query_params.get('biome', None)
        
        if biome:
            # Show shops for this biome or shops available in all biomes
            queryset = queryset.filter(models.Q(biome=biome) | models.Q(biome__isnull=True) | models.Q(biome=''))
        
        return queryset

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get all items available in this shop"""
        shop = self.get_object()
        player = Player.objects.get(user=request.user)
        
        items = ShopItem.objects.filter(
            shop=shop,
            available=True
        ).select_related('material')
        
        serializer = ShopItemSerializer(items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        """Buy an item from this shop"""
        shop = self.get_object()
        player = Player.objects.get(user=request.user)

        # Get parameters
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity', 1)
        use_card = request.data.get('use_card', False)

        if not item_id:
            return Response(
                {'error': 'item_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get shop item
        try:
            shop_item = ShopItem.objects.get(id=item_id, shop=shop)
        except ShopItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in this shop'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Process purchase
        try:
            result = EconomyService.buy_item(player, shop_item, quantity, use_card=use_card)

            # Refresh player data
            player.refresh_from_db()

            return Response({
                'success': True,
                'message': f'Acheté {quantity}x {shop_item.material.name} ({result["payment_method"]})',
                'total_cost': result['total_cost'],
                'new_cash_balance': player.money,
                'new_card_balance': player.credit_card_balance,
                'payment_method': result['payment_method'],
                'transaction': TransactionSerializer(result['transaction']).data
            })

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error buying item: {e}", exc_info=True)
            return Response(
                {'error': 'An error occurred while processing your purchase'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def sell(self, request):
        """Sell an item to a shop"""
        player = Player.objects.get(user=request.user)
        
        # Get parameters
        material_id = request.data.get('material_id')
        quantity = request.data.get('quantity', 1)
        shop_id = request.data.get('shop_id')
        
        if not material_id or not shop_id:
            return Response(
                {'error': 'material_id and shop_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get material and shop
        material = get_object_or_404(Material, id=material_id)
        shop = get_object_or_404(Shop, id=shop_id)
        
        # Process sale
        try:
            result = EconomyService.sell_item(player, material, quantity, shop)
            
            return Response({
                'success': True,
                'message': f'Vendu {quantity}x {material.name}',
                'total_earnings': result['total_earnings'],
                'new_balance': player.money,
                'transaction': TransactionSerializer(result['transaction']).data
            })
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error selling item: {e}", exc_info=True)
            return Response(
                {'error': 'An error occurred while processing your sale'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing transaction history"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get transactions for the current player"""
        player = Player.objects.get(user=self.request.user)
        return Transaction.objects.filter(player=player)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent transactions"""
        player = Player.objects.get(user=request.user)
        limit = int(request.query_params.get('limit', 10))
        
        transactions = Transaction.objects.filter(player=player)[:limit]
        serializer = self.get_serializer(transactions, many=True)
        
        return Response(serializer.data)
