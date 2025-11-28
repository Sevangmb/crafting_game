from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Achievement, PlayerAchievement, Player
from ..serializers import AchievementSerializer, PlayerAchievementSerializer
from ..services.achievement_service import AchievementService
from django.db import models


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing achievements"""
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter hidden achievements for non-staff users"""
        user = self.request.user
        queryset = Achievement.objects.all()

        # Non-staff users don't see hidden achievements they haven't started
        if not user.is_staff:
            player = Player.objects.filter(user=user).first()
            if player:
                # Get IDs of achievements the player has started
                player_achievement_ids = PlayerAchievement.objects.filter(
                    player=player
                ).values_list('achievement_id', flat=True)

                # Show non-hidden OR started achievements
                queryset = queryset.filter(
                    models.Q(hidden=False) | models.Q(id__in=player_achievement_ids)
                )
            else:
                # No player yet, only show non-hidden
                queryset = queryset.filter(hidden=False)

        return queryset.order_by('category', 'requirement_value')

    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """Get current player's achievement progress"""
        try:
            player = Player.objects.get(user=request.user)
        except Player.DoesNotExist:
            return Response({'error': 'Joueur introuvable'}, status=404)

        # Get all achievements with player progress
        result = AchievementService.get_player_achievements(player, include_hidden=False)

        return Response({
            'completed': result['completed'],
            'in_progress': result['in_progress'],
            'stats': {
                'total_completed': len(result['completed']),
                'total_available': len(result['completed']) + len(result['in_progress']),
            }
        })

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get achievements grouped by category"""
        try:
            player = Player.objects.get(user=request.user)
        except Player.DoesNotExist:
            return Response({'error': 'Joueur introuvable'}, status=404)

        # Get player's progress
        player_achievements = {
            pa.achievement_id: pa
            for pa in PlayerAchievement.objects.filter(player=player).select_related('achievement')
        }

        # Get all visible achievements
        achievements = self.get_queryset()

        # Group by category
        categories = {}
        for achievement in achievements:
            cat = achievement.category
            if cat not in categories:
                categories[cat] = {
                    'category': cat,
                    'achievements': [],
                    'completed_count': 0,
                    'total_count': 0
                }

            pa = player_achievements.get(achievement.id)
            achievement_data = AchievementSerializer(achievement).data

            if pa:
                achievement_data['progress'] = pa.progress
                achievement_data['completed'] = pa.completed
                achievement_data['completed_at'] = pa.completed_at
                achievement_data['progress_percentage'] = min(
                    100,
                    int((pa.progress / achievement.requirement_value) * 100) if achievement.requirement_value > 0 else 0
                )
                if pa.completed:
                    categories[cat]['completed_count'] += 1
            else:
                achievement_data['progress'] = 0
                achievement_data['completed'] = False
                achievement_data['completed_at'] = None
                achievement_data['progress_percentage'] = 0

            categories[cat]['achievements'].append(achievement_data)
            categories[cat]['total_count'] += 1

        return Response(list(categories.values()))

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently completed achievements"""
        try:
            player = Player.objects.get(user=request.user)
        except Player.DoesNotExist:
            return Response({'error': 'Joueur introuvable'}, status=404)

        recent_achievements = PlayerAchievement.objects.filter(
            player=player,
            completed=True
        ).select_related('achievement').order_by('-completed_at')[:10]

        serializer = PlayerAchievementSerializer(recent_achievements, many=True)
        return Response(serializer.data)
