"""
Achievement service for tracking and unlocking achievements
"""
from django.utils import timezone
from django.db import models
from ..models import Achievement, PlayerAchievement, Player, GatheringLog, CraftingLog
import logging

logger = logging.getLogger(__name__)


class AchievementService:
    """Service for managing player achievements"""

    @staticmethod
    def check_and_update_achievements(player, event_type, **kwargs):
        """
        Check and update achievements based on player actions

        Args:
            player: Player instance
            event_type: Type of event ('gather', 'craft', 'move', 'level_up', 'mob_defeat')
            **kwargs: Additional event data (material, recipe, quantity, etc.)

        Returns:
            List of newly completed achievements
        """
        newly_completed = []

        # Get all relevant achievements for this event type
        achievements = Achievement.objects.filter(
            requirement_type__in=AchievementService._get_relevant_types(event_type)
        )

        for achievement in achievements:
            # Get or create player achievement
            player_achievement, created = PlayerAchievement.objects.get_or_create(
                player=player,
                achievement=achievement,
                defaults={'progress': 0}
            )

            # Skip if already completed
            if player_achievement.completed:
                continue

            # Update progress based on achievement type
            updated = AchievementService._update_progress(
                player, player_achievement, achievement, event_type, **kwargs
            )

            if updated and player_achievement.progress >= achievement.requirement_value:
                # Achievement completed!
                player_achievement.completed = True
                player_achievement.completed_at = timezone.now()
                player_achievement.save()

                # Award XP
                if achievement.reward_xp > 0:
                    player.experience += achievement.reward_xp
                    player.save()

                newly_completed.append(achievement)
                logger.info(f"Player {player.user.username} unlocked achievement: {achievement.name}")

        return newly_completed

    @staticmethod
    def _get_relevant_types(event_type):
        """Map event types to achievement requirement types"""
        mapping = {
            'gather': ['gather_count', 'material_collected'],
            'craft': ['craft_count', 'recipe_crafted'],
            'move': ['move_count', 'biome_visited'],
            'level_up': ['level_reached'],
            'mob_defeat': ['mob_defeated'],
            'building_count': ['building_count'],
            'building_constructed': ['building_constructed'],
        }
        return mapping.get(event_type, [])

    @staticmethod
    def _update_progress(player, player_achievement, achievement, event_type, **kwargs):
        """Update achievement progress based on event"""
        req_type = achievement.requirement_type
        updated = False

        if req_type == 'gather_count':
            # Count total gatherings
            count = GatheringLog.objects.filter(player=player).count()
            player_achievement.progress = count
            updated = True

        elif req_type == 'craft_count':
            # Count total crafts
            count = CraftingLog.objects.filter(player=player).count()
            player_achievement.progress = count
            updated = True

        elif req_type == 'move_count':
            # Use player's total_moves counter
            player_achievement.progress = player.total_moves
            updated = True

        elif req_type == 'level_reached':
            # Check current level
            player_achievement.progress = player.level
            updated = True

        elif req_type == 'material_collected':
            # Check if specific material was gathered
            material_name = kwargs.get('material_name')
            if material_name == achievement.requirement_target:
                # Count total quantity of this material gathered
                count = GatheringLog.objects.filter(
                    player=player,
                    material__name=material_name
                ).count()
                player_achievement.progress = count
                updated = True

        elif req_type == 'recipe_crafted':
            # Check if specific recipe was crafted
            recipe_name = kwargs.get('recipe_name')
            if recipe_name == achievement.requirement_target:
                count = CraftingLog.objects.filter(
                    player=player,
                    recipe__name=recipe_name
                ).count()
                player_achievement.progress = count
                updated = True

        elif req_type == 'biome_visited':
            # Track unique biomes visited (requires separate tracking)
            # For now, increment on each new biome
            if event_type == 'move':
                biome = kwargs.get('biome')
                if biome and biome == achievement.requirement_target:
                    player_achievement.progress = 1  # Simple flag for visited
                    updated = True

        elif req_type == 'mob_defeated':
            # Track mob defeats
            mob_name = kwargs.get('mob_name')
            if mob_name == achievement.requirement_target:
                player_achievement.progress += kwargs.get('quantity', 1)
                updated = True

        elif req_type == 'building_count':
            # Count total buildings owned by player
            from ..models import Building
            count = Building.objects.filter(
                player=player,
                status__in=['under_construction', 'completed']
            ).count()
            player_achievement.progress = count
            updated = True

        elif req_type == 'building_constructed':
            # Check if specific building type was constructed
            building_name = kwargs.get('building_name')
            if building_name == achievement.requirement_target:
                from ..models import Building
                count = Building.objects.filter(
                    player=player,
                    building_type__name=building_name
                ).count()
                player_achievement.progress = count
                updated = True

        if updated:
            player_achievement.save()

        return updated

    @staticmethod
    def get_player_achievements(player, include_hidden=False):
        """
        Get all achievements for a player with progress

        Returns:
            dict with 'completed' and 'in_progress' lists
        """
        all_achievements = Achievement.objects.all()

        if not include_hidden:
            # Filter out hidden achievements that are not yet started
            player_achievement_ids = PlayerAchievement.objects.filter(
                player=player
            ).values_list('achievement_id', flat=True)

            all_achievements = all_achievements.filter(
                models.Q(hidden=False) | models.Q(id__in=player_achievement_ids)
            )

        # Get player's progress
        player_achievements = {
            pa.achievement_id: pa
            for pa in PlayerAchievement.objects.filter(player=player).select_related('achievement')
        }

        completed = []
        in_progress = []

        for achievement in all_achievements:
            pa = player_achievements.get(achievement.id)

            if pa and pa.completed:
                completed.append({
                    'achievement': achievement,
                    'progress': pa.progress,
                    'completed_at': pa.completed_at,
                })
            else:
                in_progress.append({
                    'achievement': achievement,
                    'progress': pa.progress if pa else 0,
                    'max_progress': achievement.requirement_value,
                })

        return {
            'completed': completed,
            'in_progress': in_progress,
        }


# Convenience function
def check_achievements(player, event_type, **kwargs):
    """Shorthand for checking achievements"""
    return AchievementService.check_and_update_achievements(player, event_type, **kwargs)
