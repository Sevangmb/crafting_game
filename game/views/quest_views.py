"""
Quest Views - API endpoints for quest management
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models
from game.models import Quest, PlayerQuest, DynamicEvent
from game.serializers import QuestSerializer, PlayerQuestSerializer, DynamicEventSerializer
from game.services.quest_service import QuestService
import logging

logger = logging.getLogger(__name__)


class QuestViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for quests"""
    serializer_class = QuestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Quest.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get quests available to the current player"""
        player = request.user.player
        available_quests = QuestService.get_available_quests(player)
        serializer = self.get_serializer(available_quests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get player's active quests"""
        player = request.user.player
        active_quests = QuestService.get_active_quests(player)
        serializer = PlayerQuestSerializer(active_quests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a quest"""
        player = request.user.player
        player_quest, error = QuestService.accept_quest(player, pk)

        if error:
            return Response(
                {'error': error},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PlayerQuestSerializer(player_quest)
        return Response({
            'message': f"✅ Quête '{player_quest.quest.name}' acceptée!",
            'quest': serializer.data
        })

    @action(detail=True, methods=['post'])
    def abandon(self, request, pk=None):
        """Abandon a quest"""
        player = request.user.player

        try:
            player_quest = PlayerQuest.objects.get(
                quest_id=pk,
                player=player,
                status='active'
            )

            success, error = QuestService.abandon_quest(player, player_quest.id)

            if error:
                return Response(
                    {'error': error},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'message': f"Quête '{player_quest.quest.name}' abandonnée"
            })

        except PlayerQuest.DoesNotExist:
            return Response(
                {'error': 'Quête non trouvée ou non active'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get player's completed quests"""
        player = request.user.player
        completed_quests = PlayerQuest.objects.filter(
            player=player,
            status='completed'
        ).select_related('quest').order_by('-completed_at')

        serializer = PlayerQuestSerializer(completed_quests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get player's quest statistics"""
        player = request.user.player

        active_count = PlayerQuest.objects.filter(
            player=player,
            status='active'
        ).count()

        completed_count = PlayerQuest.objects.filter(
            player=player,
            status='completed'
        ).count()

        total_completions = PlayerQuest.objects.filter(
            player=player,
            status='completed'
        ).aggregate(total=models.Sum('times_completed'))['total'] or 0

        available_count = len(QuestService.get_available_quests(player))

        return Response({
            'active': active_count,
            'completed': completed_count,
            'available': available_count,
            'total_completions': total_completions
        })


class DynamicEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for dynamic events"""
    serializer_class = DynamicEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get active events"""
        return DynamicEvent.objects.filter(is_active=True)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Get events near the player"""
        player = request.user.player
        radius = int(request.query_params.get('radius', 5))

        events = DynamicEvent.objects.filter(
            is_active=True,
            cell__grid_x__gte=player.grid_x - radius,
            cell__grid_x__lte=player.grid_x + radius,
            cell__grid_y__gte=player.grid_y - radius,
            cell__grid_y__lte=player.grid_y + radius
        ).select_related('cell')

        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def participate(self, request, pk=None):
        """Participate in an event"""
        player = request.user.player

        try:
            event = DynamicEvent.objects.get(id=pk)

            if not event.can_participate(player):
                return Response(
                    {'error': 'Vous ne pouvez pas participer à cet événement'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if player is on the event cell
            if player.grid_x != event.cell.grid_x or player.grid_y != event.cell.grid_y:
                return Response(
                    {'error': 'Vous devez être sur la cellule de l\'événement'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Add player to participants
            event.participants.add(player)

            # Grant rewards
            rewards_granted = {}
            rewards = event.rewards

            if 'xp' in rewards:
                player.experience += rewards['xp']
                rewards_granted['xp'] = rewards['xp']

            if 'money' in rewards:
                player.money += rewards['money']
                rewards_granted['money'] = rewards['money']

            if 'items' in rewards:
                from game.models import Material, Inventory
                reward_items = []

                for item_data in rewards['items']:
                    material_id = item_data.get('material_id')
                    quantity = item_data.get('quantity', 1)

                    try:
                        material = Material.objects.get(id=material_id)
                        inventory_item, created = Inventory.objects.get_or_create(
                            player=player,
                            material=material,
                            defaults={'quantity': 0}
                        )
                        inventory_item.quantity += quantity
                        inventory_item.save()

                        reward_items.append({
                            'material': material.name,
                            'quantity': quantity,
                            'icon': material.icon
                        })

                    except Material.DoesNotExist:
                        logger.warning(f"Event reward material {material_id} not found")

                rewards_granted['items'] = reward_items

            player.save()

            return Response({
                'message': f"✨ Vous avez participé à l'événement '{event.name}'!",
                'rewards': rewards_granted,
                'event': self.get_serializer(event).data
            })

        except DynamicEvent.DoesNotExist:
            return Response(
                {'error': 'Événement introuvable'},
                status=status.HTTP_404_NOT_FOUND
            )
