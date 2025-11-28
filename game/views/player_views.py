from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models import Player, PlayerSkill, PlayerTalent, TalentNode
from ..serializers import PlayerSerializer, PlayerSkillSerializer, PlayerTalentSerializer, TalentNodeSerializer
from ..services import player_service
from ..services.energy_service import regenerate_player_energy
from ..services.survival_service import SurvivalService

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Player.objects.filter(user=self.request.user).select_related(
            'user', 'current_vehicle'
        ).prefetch_related(
            'inventory__material',
            'equipped_items__material',
            'workstations__workstation'
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        player, created = Player.objects.get_or_create(user=request.user)

        # If player was just created, ensure all vital stats are at 100%
        if created:
            from django.utils import timezone
            player.energy = 100
            player.max_energy = 100
            player.health = 100
            player.max_health = 100
            player.hunger = 100
            player.max_hunger = 100
            player.thirst = 100
            player.max_thirst = 100
            player.radiation = 0
            player.last_energy_update = timezone.now()
            player.last_hunger_update = timezone.now()
            player.last_thirst_update = timezone.now()
            player.save()

        # Regenerate energy passively based on time and buildings
        energy_restored, minutes_passed = regenerate_player_energy(player)

        # Update survival stats (hunger, thirst, radiation)
        survival_status = SurvivalService.update_survival_stats(player)

        # Refresh player data after regeneration
        player.refresh_from_db()

        serializer = self.get_serializer(player)
        data = serializer.data
        data['is_staff'] = bool(request.user and request.user.is_staff)

        # Add regeneration info if any energy was restored
        if energy_restored > 0:
            data['energy_regenerated'] = energy_restored
            data['minutes_offline'] = minutes_passed

        # Add survival warnings
        data['survival_warnings'] = survival_status['warnings']
        
        # Add survival status (new!)
        data['survival_status'] = SurvivalService.get_survival_status(player)
        
        # Add survival multipliers (new!)
        data['survival_multipliers'] = SurvivalService.get_survival_multipliers(player)
        
        # Add health regen info if any
        if survival_status.get('health_regen', 0) > 0:
            data['health_regenerated'] = survival_status['health_regen']

        return Response(data)

    @action(detail=False, methods=['get'])
    def skills(self, request):
        player = Player.objects.select_related('user').get(user=request.user)
        player_service.ensure_default_skills()
        skills = PlayerSkill.objects.filter(player=player).select_related('skill', 'player')
        talents = PlayerTalent.objects.filter(player=player).select_related('talent_node__skill', 'player')
        return Response({
            'skills': PlayerSkillSerializer(skills, many=True).data,
            'talents': PlayerTalentSerializer(talents, many=True).data,
        })

    @action(detail=False, methods=['get'])
    def skills_tree(self, request):
        player_service.ensure_default_skills()
        nodes = TalentNode.objects.select_related('skill').all()
        return Response(TalentNodeSerializer(nodes, many=True).data)

    @action(detail=False, methods=['post'])
    def restart(self, request):
        """Restart the game - reset player position and inventory"""
        player = Player.objects.get(user=request.user)
        player = player_service.restart_player(player)
        serializer = self.get_serializer(player)
        return Response({
            'message': 'Partie recommencée avec succès!',
            'player': serializer.data
        })

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        player = self.get_object()
        direction = request.data.get('direction')

        result = player_service.move_player(player, direction)

        # Handle new format with achievements and quests
        if len(result) == 4:
            player_obj, status_code, new_achievements, completed_quests = result
        elif len(result) == 3:
            player_obj, status_code, new_achievements = result
            completed_quests = []
        else:
            player_obj, status_code = result
            new_achievements = []
            completed_quests = []

        if status_code != 200:
            return Response(player_obj, status=status_code)

        # result is player object
        serializer = self.get_serializer(player_obj)
        response_data = serializer.data

        # Add achievements if any
        if new_achievements:
            response_data['achievements_unlocked'] = [
                {
                    'name': ach.name,
                    'description': ach.description,
                    'icon': ach.icon,
                    'reward_xp': ach.reward_xp
                }
                for ach in new_achievements
            ]

        # Add completed quests if any
        if completed_quests:
            response_data['quests_completed'] = [
                {
                    'quest': {
                        'name': q['quest'].name,
                        'icon': q['quest'].icon,
                        'description': q['quest'].description
                    },
                    'rewards': q['rewards']
                }
                for q in completed_quests
            ]

        return Response(response_data)

    @action(detail=False, methods=['post'])
    def equip(self, request):
        player = Player.objects.get(user=request.user)
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response({'error': 'item_id est requis'}, status=400)
            
        result, status_code = player_service.equip_item(player, item_id)
        return Response(result, status=status_code)

    @action(detail=False, methods=['post'])
    def unequip(self, request):
        player = Player.objects.get(user=request.user)
        slot = request.data.get('slot')
        
        if not slot:
            return Response({'error': 'slot est requis'}, status=400)
            
        result, status_code = player_service.unequip_item(player, slot)
        return Response(result, status=status_code)

    @action(detail=False, methods=['post'])
    def hunt(self, request):
        player = Player.objects.get(user=request.user)
        from ..services import map_service
        result, status_code = map_service.hunt_at_location(player)
        return Response(result, status=status_code)
