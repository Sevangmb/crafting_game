"""
Trading Views - API endpoints for player trading
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import models
from datetime import timedelta
from game.models import TradeOffer, Player
from game.serializers import TradeOfferSerializer
from game.services.trading_service import TradingService
import logging

logger = logging.getLogger(__name__)


class TradeViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for trading between players"""
    serializer_class = TradeOfferSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get trades relevant to current player"""
        player = self.request.user.player
        return TradeOffer.objects.filter(
            models.Q(from_player=player) | models.Q(to_player=player)
        ).select_related('from_player__user', 'to_player__user').order_by('-created_at')

    @action(detail=False, methods=['post'])
    def create_offer(self, request):
        """Create a new trade offer"""
        player = request.user.player

        to_player_id = request.data.get('to_player_id')
        offered_items = request.data.get('offered_items', [])
        offered_money = request.data.get('offered_money', 0)
        requested_items = request.data.get('requested_items', [])
        requested_money = request.data.get('requested_money', 0)
        message = request.data.get('message', '')
        duration_hours = request.data.get('duration_hours', 24)

        # Validate inputs
        if not to_player_id:
            return Response(
                {'error': 'to_player_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not offered_items and offered_money == 0:
            return Response(
                {'error': 'Vous devez offrir au moins quelque chose'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not requested_items and requested_money == 0:
            return Response(
                {'error': 'Vous devez demander au moins quelque chose'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create trade
        trade, error = TradingService.create_trade_offer(
            from_player=player,
            to_player_id=to_player_id,
            offered_items=offered_items,
            offered_money=offered_money,
            requested_items=requested_items,
            requested_money=requested_money,
            message=message,
            duration_hours=duration_hours
        )

        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(trade)
        return Response({
            'message': f'Offre envoyée à {trade.to_player.user.username}!',
            'trade': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def received(self, request):
        """Get trades received by current player"""
        player = request.user.player
        trades = TradingService.get_received_trades(player)
        serializer = self.get_serializer(trades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get trades sent by current player"""
        player = request.user.player
        trades = TradingService.get_sent_trades(player)
        serializer = self.get_serializer(trades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get trade history"""
        player = request.user.player
        limit = int(request.query_params.get('limit', 50))
        trades = TradingService.get_trade_history(player, limit=limit)
        serializer = self.get_serializer(trades, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a trade offer"""
        player = request.user.player

        success, error = TradingService.accept_trade(pk, player)

        if not success:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Refresh trade
        trade = TradeOffer.objects.get(id=pk)
        serializer = self.get_serializer(trade)

        return Response({
            'message': 'Échange réalisé avec succès!',
            'trade': serializer.data
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a trade offer"""
        player = request.user.player

        success, error = TradingService.reject_trade(pk, player)

        if not success:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        trade = TradeOffer.objects.get(id=pk)
        serializer = self.get_serializer(trade)

        return Response({
            'message': 'Offre refusée',
            'trade': serializer.data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel own trade offer"""
        player = request.user.player

        success, error = TradingService.cancel_trade(pk, player)

        if not success:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        trade = TradeOffer.objects.get(id=pk)
        serializer = self.get_serializer(trade)

        return Response({
            'message': 'Offre annulée',
            'trade': serializer.data
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get trading statistics for current player"""
        from django.db.models import Q
        player = request.user.player

        # Count trades
        total_sent = TradeOffer.objects.filter(from_player=player).count()
        total_received = TradeOffer.objects.filter(to_player=player).count()
        completed_as_sender = TradeOffer.objects.filter(
            from_player=player,
            status='completed'
        ).count()
        completed_as_receiver = TradeOffer.objects.filter(
            to_player=player,
            status='completed'
        ).count()
        pending_sent = TradeOffer.objects.filter(
            from_player=player,
            status='pending'
        ).count()
        pending_received = TradeOffer.objects.filter(
            to_player=player,
            status='pending'
        ).count()

        return Response({
            'total_sent': total_sent,
            'total_received': total_received,
            'completed_as_sender': completed_as_sender,
            'completed_as_receiver': completed_as_receiver,
            'total_completed': completed_as_sender + completed_as_receiver,
            'pending_sent': pending_sent,
            'pending_received': pending_received
        })
