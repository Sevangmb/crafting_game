from ..models import Player, GameConfig, Inventory, GatheringLog, CraftingLog
from django.utils import timezone

# Import extracted services to expose them
from .movement_service import move_player
from .equipment_service import equip_item, unequip_item
from .skills_service import (
    ensure_default_skills, get_or_create_player_skill, award_xp,
    auto_unlock_talents, get_active_effects
)

def restart_player(player):
    """Restart the game - reset player position and inventory"""
    # Reset player stats - Start in Valence center
    player.current_x = 4.893  # Valence longitude
    player.current_y = 44.933  # Valence latitude
    player.grid_x = 0
    player.grid_y = 0

    starting_energy = GameConfig.get_config('starting_energy', 100)
    player.energy = starting_energy
    player.max_energy = starting_energy
    player.health = 100
    player.max_health = 100

    # Reset survival stats
    player.hunger = 100
    player.max_hunger = 100
    player.thirst = 100
    player.max_thirst = 100
    player.radiation = 0

    # Reset survival timestamps to prevent immediate decay
    player.last_energy_update = timezone.now()
    player.last_hunger_update = timezone.now()
    player.last_thirst_update = timezone.now()

    # Reset stats
    player.strength = 10
    player.agility = 10
    player.intelligence = 10
    player.luck = 10

    player.level = 1
    player.experience = 0
    player.save()

    # Clear inventory
    Inventory.objects.filter(player=player).delete()
    
    # Clear equipped items
    from ..models import EquippedItem
    EquippedItem.objects.filter(player=player).delete()

    # Clear gathering and crafting logs
    GatheringLog.objects.filter(player=player).delete()
    CraftingLog.objects.filter(player=player).delete()

    return player
