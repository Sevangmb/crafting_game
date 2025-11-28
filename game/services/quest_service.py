"""
Quest Service - Manages quests, player progress, and rewards
"""
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from game.models import Quest, PlayerQuest, Player, Material, Inventory
import logging

logger = logging.getLogger(__name__)


class QuestService:
    """Service for managing quests"""

    @staticmethod
    def get_available_quests(player):
        """Get all quests available to the player"""
        # Get quests player meets level requirement for
        available_quests = Quest.objects.filter(
            is_active=True,
            required_level__lte=player.level
        )

        result = []
        for quest in available_quests:
            # Check if player has completed prerequisite
            if quest.prerequisite_quest:
                prereq_complete = PlayerQuest.objects.filter(
                    player=player,
                    quest=quest.prerequisite_quest,
                    status='completed'
                ).exists()
                if not prereq_complete:
                    continue

            # Check if quest is already active or completed
            player_quest = PlayerQuest.objects.filter(
                player=player,
                quest=quest
            ).first()

            if player_quest:
                if player_quest.status == 'active':
                    continue  # Already active
                elif player_quest.status == 'completed':
                    if not quest.is_repeatable:
                        continue  # Can't repeat
                    elif player_quest.can_repeat_at and timezone.now() < player_quest.can_repeat_at:
                        continue  # Still on cooldown

            result.append(quest)

        return result

    @staticmethod
    def get_active_quests(player):
        """Get all active quests for the player"""
        return PlayerQuest.objects.filter(
            player=player,
            status='active'
        ).select_related('quest')

    @staticmethod
    def accept_quest(player, quest_id):
        """Accept a quest"""
        try:
            quest = Quest.objects.get(id=quest_id, is_active=True)

            # Check level requirement
            if player.level < quest.required_level:
                return None, f"Niveau {quest.required_level} requis"

            # Check prerequisite
            if quest.prerequisite_quest:
                prereq_complete = PlayerQuest.objects.filter(
                    player=player,
                    quest=quest.prerequisite_quest,
                    status='completed'
                ).exists()
                if not prereq_complete:
                    return None, "Quête prérequise non complétée"

            # Check if already active
            existing = PlayerQuest.objects.filter(
                player=player,
                quest=quest
            ).first()

            if existing:
                if existing.status == 'active':
                    return None, "Quête déjà active"
                elif existing.status == 'completed':
                    if not quest.is_repeatable:
                        return None, "Quête déjà complétée"
                    elif existing.can_repeat_at and timezone.now() < existing.can_repeat_at:
                        hours_left = int((existing.can_repeat_at - timezone.now()).total_seconds() / 3600)
                        return None, f"Disponible dans {hours_left}h"

            # Create or update PlayerQuest
            if existing:
                existing.status = 'active'
                existing.accepted_at = timezone.now()
                existing.progress = {}
                existing.save()
                player_quest = existing
            else:
                player_quest = PlayerQuest.objects.create(
                    player=player,
                    quest=quest,
                    status='active',
                    accepted_at=timezone.now(),
                    progress={}
                )

            logger.info(f"Player {player.user.username} accepted quest {quest.name}")
            return player_quest, None

        except Quest.DoesNotExist:
            return None, "Quête introuvable"
        except Exception as e:
            logger.error(f"Error accepting quest: {e}")
            return None, str(e)

    @staticmethod
    def update_quest_progress(player, action_type, **kwargs):
        """Update quest progress based on player actions"""
        active_quests = PlayerQuest.objects.filter(
            player=player,
            status='active'
        ).select_related('quest')

        completed_quests = []

        for player_quest in active_quests:
            quest = player_quest.quest
            requirements = quest.requirements

            if not requirements:
                continue

            # Update progress based on action type
            if action_type == 'gather' and 'gather' in requirements:
                material_id = kwargs.get('material_id')
                quantity = kwargs.get('quantity', 1)

                for req in requirements['gather']:
                    if req.get('material_id') == material_id:
                        if 'gather' not in player_quest.progress:
                            player_quest.progress['gather'] = {}

                        key = str(material_id)
                        current = player_quest.progress['gather'].get(key, 0)
                        player_quest.progress['gather'][key] = current + quantity

            elif action_type == 'craft' and 'craft' in requirements:
                recipe_id = kwargs.get('recipe_id')
                quantity = kwargs.get('quantity', 1)

                for req in requirements['craft']:
                    if req.get('recipe_id') == recipe_id:
                        if 'craft' not in player_quest.progress:
                            player_quest.progress['craft'] = {}

                        key = str(recipe_id)
                        current = player_quest.progress['craft'].get(key, 0)
                        player_quest.progress['craft'][key] = current + quantity

            elif action_type == 'visit' and 'visit' in requirements:
                grid_x = kwargs.get('grid_x')
                grid_y = kwargs.get('grid_y')

                for req in requirements['visit']:
                    if req.get('grid_x') == grid_x and req.get('grid_y') == grid_y:
                        if 'visit' not in player_quest.progress:
                            player_quest.progress['visit'] = {}

                        key = f"{grid_x},{grid_y}"
                        player_quest.progress['visit'][key] = True

            elif action_type == 'defeat' and 'defeat' in requirements:
                mob_id = kwargs.get('mob_id')
                quantity = kwargs.get('quantity', 1)

                for req in requirements['defeat']:
                    if req.get('mob_id') == mob_id:
                        if 'defeat' not in player_quest.progress:
                            player_quest.progress['defeat'] = {}

                        key = str(mob_id)
                        current = player_quest.progress['defeat'].get(key, 0)
                        player_quest.progress['defeat'][key] = current + quantity

            # Check if quest is now complete
            if QuestService._is_quest_complete(player_quest):
                success, reward_info = QuestService.complete_quest(player, player_quest.id)
                if success:
                    completed_quests.append({
                        'quest': quest,
                        'rewards': reward_info
                    })
            else:
                player_quest.save()

        return completed_quests

    @staticmethod
    def _is_quest_complete(player_quest):
        """Check if all quest requirements are met"""
        quest = player_quest.quest
        requirements = quest.requirements
        progress = player_quest.progress

        if not requirements:
            return True

        for task_type, tasks in requirements.items():
            for task in tasks:
                required = task.get('quantity', 1)

                if task_type == 'gather':
                    material_id = str(task.get('material_id'))
                    current = progress.get('gather', {}).get(material_id, 0)
                    if current < required:
                        return False

                elif task_type == 'craft':
                    recipe_id = str(task.get('recipe_id'))
                    current = progress.get('craft', {}).get(recipe_id, 0)
                    if current < required:
                        return False

                elif task_type == 'visit':
                    grid_x = task.get('grid_x')
                    grid_y = task.get('grid_y')
                    key = f"{grid_x},{grid_y}"
                    if not progress.get('visit', {}).get(key, False):
                        return False

                elif task_type == 'defeat':
                    mob_id = str(task.get('mob_id'))
                    current = progress.get('defeat', {}).get(mob_id, 0)
                    if current < required:
                        return False

        return True

    @staticmethod
    @transaction.atomic
    def complete_quest(player, player_quest_id):
        """Complete a quest and grant rewards"""
        try:
            player_quest = PlayerQuest.objects.select_for_update().get(
                id=player_quest_id,
                player=player,
                status='active'
            )

            quest = player_quest.quest

            # Mark as completed
            player_quest.status = 'completed'
            player_quest.completed_at = timezone.now()
            player_quest.times_completed += 1

            # Set cooldown for repeatable quests
            if quest.is_repeatable:
                player_quest.can_repeat_at = timezone.now() + timedelta(hours=quest.cooldown_hours)

            player_quest.save()

            # Grant rewards
            reward_info = {}

            # XP
            if quest.reward_xp > 0:
                player.experience += quest.reward_xp
                reward_info['xp'] = quest.reward_xp

            # Money
            if quest.reward_money > 0:
                player.money += quest.reward_money
                reward_info['money'] = quest.reward_money

            # Items
            reward_items = []
            if quest.reward_items:
                for item_data in quest.reward_items:
                    material_id = item_data.get('material_id')
                    quantity = item_data.get('quantity', 1)

                    try:
                        material = Material.objects.get(id=material_id)

                        # Add to inventory
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
                        logger.warning(f"Reward material {material_id} not found")

            reward_info['items'] = reward_items

            # Check if player leveled up
            level_before = player.level
            xp_required = 100 * (player.level ** 2)
            while player.experience >= xp_required:
                player.level += 1
                player.experience -= xp_required
                xp_required = 100 * (player.level ** 2)

            player.save()

            if player.level > level_before:
                reward_info['level_up'] = True
                reward_info['new_level'] = player.level

            logger.info(f"Player {player.user.username} completed quest {quest.name}")
            return True, reward_info

        except PlayerQuest.DoesNotExist:
            return False, "Quête introuvable"
        except Exception as e:
            logger.error(f"Error completing quest: {e}")
            return False, str(e)

    @staticmethod
    def abandon_quest(player, player_quest_id):
        """Abandon an active quest"""
        try:
            player_quest = PlayerQuest.objects.get(
                id=player_quest_id,
                player=player,
                status='active'
            )

            player_quest.status = 'abandoned'
            player_quest.save()

            logger.info(f"Player {player.user.username} abandoned quest {player_quest.quest.name}")
            return True, None

        except PlayerQuest.DoesNotExist:
            return False, "Quête introuvable"
        except Exception as e:
            logger.error(f"Error abandoning quest: {e}")
            return False, str(e)

    @staticmethod
    def get_quest_chain(chain_id):
        """Get all quests in a chain, ordered by chain_order"""
        return Quest.objects.filter(
            chain_id=chain_id,
            is_active=True
        ).order_by('chain_order')

    @staticmethod
    def get_chain_progress(player, chain_id):
        """Get player's progress in a quest chain"""
        chain_quests = QuestService.get_quest_chain(chain_id)
        
        progress = {
            'chain_id': chain_id,
            'total_quests': chain_quests.count(),
            'completed_quests': 0,
            'current_quest': None,
            'quests': []
        }

        for quest in chain_quests:
            player_quest = PlayerQuest.objects.filter(
                player=player,
                quest=quest
            ).first()

            quest_data = {
                'quest_id': quest.id,
                'name': quest.name,
                'chain_order': quest.chain_order,
                'status': player_quest.status if player_quest else 'locked',
                'progress_percentage': player_quest.progress_percentage() if player_quest else 0
            }

            if player_quest and player_quest.status == 'completed':
                progress['completed_quests'] += 1
            elif player_quest and player_quest.status == 'active':
                progress['current_quest'] = quest_data
            
            progress['quests'].append(quest_data)

        return progress

    @staticmethod
    def get_all_chains():
        """Get all quest chains with basic info"""
        chains = {}
        chain_quests = Quest.objects.filter(
            chain_id__isnull=False,
            is_active=True
        ).values('chain_id').distinct()

        for item in chain_quests:
            chain_id = item['chain_id']
            quests = QuestService.get_quest_chain(chain_id)
            first_quest = quests.first()
            
            chains[chain_id] = {
                'chain_id': chain_id,
                'name': f"Chaîne: {first_quest.name if first_quest else chain_id}",
                'total_quests': quests.count(),
                'first_quest_id': first_quest.id if first_quest else None
            }

        return chains
