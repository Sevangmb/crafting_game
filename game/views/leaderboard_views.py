"""
Leaderboard Views - API endpoints for global rankings
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from game.models import Leaderboard
from game.serializers import LeaderboardSerializer
from game.services.leaderboard_service import LeaderboardService
import logging

logger = logging.getLogger(__name__)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for leaderboards"""
    serializer_class = LeaderboardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get leaderboard entries"""
        category = self.request.query_params.get('category')
        limit = int(self.request.query_params.get('limit', 100))

        if category:
            return Leaderboard.objects.filter(
                category=category
            ).select_related('player__user').order_by('rank')[:limit]

        return Leaderboard.objects.all().select_related('player__user').order_by('category', 'rank')[:limit]

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all available categories"""
        categories = []
        for choice in Leaderboard.CATEGORY_CHOICES:
            categories.append({
                'value': choice[0],
                'label': choice[1]
            })
        return Response(categories)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get leaderboards grouped by category"""
        limit = int(request.query_params.get('limit', 10))

        result = {}
        for category_code, category_name in Leaderboard.CATEGORY_CHOICES:
            entries = Leaderboard.objects.filter(
                category=category_code
            ).select_related('player__user').order_by('rank')[:limit]

            result[category_code] = {
                'name': category_name,
                'entries': self.get_serializer(entries, many=True).data
            }

        return Response(result)

    @action(detail=False, methods=['get'])
    def my_ranks(self, request):
        """Get current player's ranks in all categories"""
        player = request.user.player
        ranks = LeaderboardService.get_all_player_ranks(player)

        return Response(ranks)

    @action(detail=False, methods=['get'])
    def top_players(self, request):
        """Get top 10 players for each category"""
        result = {}

        for category_code, category_name in Leaderboard.CATEGORY_CHOICES:
            top = Leaderboard.objects.filter(
                category=category_code
            ).select_related('player__user').order_by('rank')[:10]

            result[category_code] = {
                'name': category_name,
                'top_players': self.get_serializer(top, many=True).data
            }

        return Response(result)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def update_all(self, request):
        """Update all leaderboards (admin only)"""
        try:
            updated_count = LeaderboardService.update_all_leaderboards()

            return Response({
                'message': f'{updated_count} entrées mises à jour',
                'updated_count': updated_count
            })
        except Exception as e:
            logger.error(f"Error updating leaderboards: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def update_category(self, request):
        """Update specific category (admin only)"""
        category = request.data.get('category')

        if not category:
            return Response(
                {'error': 'Catégorie requise'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            update_methods = {
                'level': LeaderboardService.update_level_leaderboard,
                'wealth': LeaderboardService.update_wealth_leaderboard,
                'gatherer': LeaderboardService.update_gatherer_leaderboard,
                'crafter': LeaderboardService.update_crafter_leaderboard,
                'explorer': LeaderboardService.update_explorer_leaderboard,
                'combatant': LeaderboardService.update_combatant_leaderboard,
                'quests': LeaderboardService.update_quests_leaderboard,
            }

            if category not in update_methods:
                return Response(
                    {'error': 'Catégorie invalide'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            count = update_methods[category]()

            return Response({
                'message': f'Catégorie {category} mise à jour',
                'updated_count': count
            })
        except Exception as e:
            logger.error(f"Error updating category {category}: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def player_rank(self, request):
        """Get rank for a specific player in a category"""
        player_id = request.query_params.get('player_id')
        category = request.query_params.get('category')

        if not player_id or not category:
            return Response(
                {'error': 'player_id et category requis'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from game.models import Player
            player = Player.objects.get(id=player_id)
            rank_info = LeaderboardService.get_player_rank(player, category)

            if not rank_info:
                return Response(
                    {'message': 'Joueur non classé dans cette catégorie'},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({
                'player_id': player_id,
                'player_name': player.user.username,
                'category': category,
                **rank_info
            })

        except Player.DoesNotExist:
            return Response(
                {'error': 'Joueur introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
