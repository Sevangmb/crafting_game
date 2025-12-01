"""
Views for random enemy encounters
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import Player, Encounter, RandomEnemy
from ..services.encounter_service import EncounterService
from ..services import combat_service as CombatService


class EncounterViewSet(viewsets.ViewSet):
    """ViewSet for managing random encounters"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='current')
    def current_encounter(self, request):
        """Get current active encounter"""
        try:
            player = get_object_or_404(Player, user=request.user)
            encounter = EncounterService.get_active_encounter(player)

            if not encounter:
                return Response({'encounter': None})

            return Response({
                'encounter': {
                    'id': encounter.id,
                    'enemy': {
                        'id': encounter.enemy.id,
                        'name': encounter.enemy.name,
                        'description': encounter.enemy.description,
                        'icon': encounter.enemy.icon,
                        'level': encounter.enemy.level,
                        'health': encounter.enemy.health,
                        'current_health': encounter.enemy_current_health,
                        'attack': encounter.enemy.attack,
                        'defense': encounter.enemy.defense,
                        'aggression_level': encounter.enemy.aggression_level,
                    },
                    'status': encounter.status,
                    'attacked_first': encounter.enemy_attacked_first,
                    'rounds': encounter.rounds,
                    'damage_dealt': encounter.damage_dealt,
                    'damage_taken': encounter.damage_taken,
                }
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='attack')
    def attack(self, request):
        """Attack the enemy in current encounter"""
        try:
            player = get_object_or_404(Player, user=request.user)
            encounter = EncounterService.get_active_encounter(player)

            if not encounter:
                return Response(
                    {'error': 'Aucune rencontre active'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Use combat service to calculate damage
            enemy = encounter.enemy

            # Player attacks enemy
            player_damage = CombatService.calculate_damage(
                attacker=player,
                defender_defense=enemy.defense,
                is_player=True
            )

            encounter.enemy_current_health -= player_damage
            encounter.damage_dealt += player_damage
            encounter.rounds += 1

            combat_log = [f"Vous infligez {player_damage} dégâts à {enemy.name}!"]

            # Check if enemy defeated
            if encounter.enemy_current_health <= 0:
                encounter.enemy_current_health = 0
                loot = EncounterService.resolve_encounter_victory(encounter)

                # Award XP
                player.xp += enemy.xp_reward
                player.save()

                return Response({
                    'victory': True,
                    'combat_log': combat_log + [f"💀 {enemy.name} est vaincu!"],
                    'loot': loot,
                    'enemy_health': 0
                })

            # Enemy counter-attacks
            enemy_damage = CombatService.calculate_damage(
                attacker_attack=enemy.attack,
                defender_defense=player.total_defense,
                is_player=False
            )

            player.health = max(0, player.health - enemy_damage)
            player.save()

            encounter.damage_taken += enemy_damage
            encounter.save()

            combat_log.append(f"{enemy.name} vous inflige {enemy_damage} dégâts!")

            # Check if player defeated
            if player.health <= 0:
                encounter.status = 'defeated'
                encounter.save()

                return Response({
                    'defeated': True,
                    'combat_log': combat_log + ["💀 Vous avez été vaincu..."],
                    'enemy_health': encounter.enemy_current_health
                })

            return Response({
                'success': True,
                'combat_log': combat_log,
                'enemy_health': encounter.enemy_current_health,
                'player_health': player.health
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='flee')
    def flee(self, request):
        """Attempt to flee from encounter"""
        try:
            player = get_object_or_404(Player, user=request.user)
            encounter = EncounterService.get_active_encounter(player)

            if not encounter:
                return Response(
                    {'error': 'Aucune rencontre active'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            import random
            # Base 70% chance to flee, modified by agility
            flee_chance = 0.7 + (player.agility * 0.02)  # +2% per agility point
            flee_chance = min(0.95, flee_chance)  # Max 95%

            if random.random() < flee_chance:
                # Successful flee
                EncounterService.resolve_encounter_flee(encounter)

                return Response({
                    'success': True,
                    'message': f'Vous avez réussi à fuir {encounter.enemy.name}!'
                })
            else:
                # Failed flee - enemy gets free attack
                enemy = encounter.enemy
                enemy_damage = CombatService.calculate_damage(
                    attacker_attack=enemy.attack,
                    defender_defense=player.total_defense,
                    is_player=False
                )

                player.health = max(0, player.health - enemy_damage)
                player.save()

                encounter.damage_taken += enemy_damage
                encounter.save()

                if player.health <= 0:
                    encounter.status = 'defeated'
                    encounter.save()

                    return Response({
                        'success': False,
                        'defeated': True,
                        'message': f'Fuite échouée! {enemy.name} vous rattrape et vous inflige {enemy_damage} dégâts fatals!'
                    })

                return Response({
                    'success': False,
                    'message': f'Fuite échouée! {enemy.name} vous rattrape et vous inflige {enemy_damage} dégâts!',
                    'damage_taken': enemy_damage,
                    'player_health': player.health
                })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
