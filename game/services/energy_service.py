"""
Energy regeneration service
Handles passive energy regeneration based on buildings
"""
from django.utils import timezone
from datetime import timedelta
from game.models import Player
from game.services.building_service import calculate_player_bonuses
from game.utils.config_helper import GameSettings
import logging

logger = logging.getLogger(__name__)


def regenerate_player_energy(player):
    """
    Regenerate player energy based on time passed and buildings owned

    Args:
        player: Player instance

    Returns:
        tuple: (energy_restored, time_passed_minutes)
    """
    # Get player's building bonuses
    bonuses = calculate_player_bonuses(player)
    base_regen = GameSettings.energy_base_regen_per_minute()
    bonus_regen = bonuses.get('energy_regeneration', 0)
    total_regen_per_minute = base_regen + bonus_regen

    # Calculate time since last update
    now = timezone.now()
    last_update = getattr(player, 'last_energy_update', None)

    if not last_update:
        # First time, set it to now
        player.last_energy_update = now
        player.save()
        return 0, 0

    time_passed = now - last_update
    minutes_passed = time_passed.total_seconds() / 60  # Changed from hours

    # Calculate energy to restore
    energy_to_restore = int(total_regen_per_minute * minutes_passed)

    if energy_to_restore > 0:
        old_energy = player.energy
        player.energy = min(player.max_energy, player.energy + energy_to_restore)
        player.last_energy_update = now
        player.save()

        actual_restored = player.energy - old_energy
        logger.info(f"Regenerated {actual_restored} energy for {player.user.username}")
        return actual_restored, int(minutes_passed)

    return 0, 0


def apply_building_effects_to_action(player, action_type, base_cost):
    """
    Apply building bonuses to action costs

    Args:
        player: Player instance
        action_type: 'gather', 'craft', 'move'
        base_cost: Base energy/resource cost

    Returns:
        int: Modified cost after bonuses
    """
    bonuses = calculate_player_bonuses(player)
    production_bonus = bonuses.get('production', 0.0)

    # Production bonus reduces costs
    if production_bonus > 0:
        reduction = base_cost * production_bonus
        modified_cost = max(1, int(base_cost - reduction))
        return modified_cost

    return base_cost
