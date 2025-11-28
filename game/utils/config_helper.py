"""
Helper functions to retrieve game configurations from database
"""
from game.models import GameConfig
from functools import lru_cache


@lru_cache(maxsize=128)
def get_config_value(key, default=None, value_type=None):
    """
    Get a configuration value from database with caching

    Args:
        key: Configuration key
        default: Default value if key not found
        value_type: Type to convert value to (int, float, str, bool)

    Returns:
        Configuration value or default
    """
    try:
        config = GameConfig.objects.get(key=key)
        value = config.get_value()

        # Convert to desired type if specified
        if value_type is not None and value is not None:
            if value_type == bool:
                return str(value).lower() in ('true', '1', 'yes')
            return value_type(value)

        return value
    except GameConfig.DoesNotExist:
        return default


def get_int_config(key, default=0):
    """Get integer configuration value"""
    return get_config_value(key, default, int)


def get_float_config(key, default=0.0):
    """Get float configuration value"""
    return get_config_value(key, default, float)


def get_bool_config(key, default=False):
    """Get boolean configuration value"""
    return get_config_value(key, default, bool)


def get_str_config(key, default=''):
    """Get string configuration value"""
    return get_config_value(key, default, str)


def clear_config_cache():
    """Clear the configuration cache (call after updating configs)"""
    get_config_value.cache_clear()


# Pre-defined config getters for commonly used values
class GameSettings:
    """Static class to access game settings"""

    @staticmethod
    def energy_move_cost():
        return get_int_config('energy_move_cost', 1)

    @staticmethod
    def energy_gather_cost():
        return get_int_config('energy_gather_cost', 5)

    @staticmethod
    def energy_combat_base_cost():
        return get_int_config('energy_combat_base_cost', 5)

    @staticmethod
    def energy_base_regen_per_minute():
        return get_int_config('energy_base_regen_per_minute', 1)

    @staticmethod
    def movement_grid_offset():
        return get_float_config('movement_grid_offset', 0.0009)

    @staticmethod
    def movement_agility_reduction_factor():
        return get_float_config('movement_agility_reduction_factor', 0.01)

    @staticmethod
    def movement_speed_bonus_factor():
        return get_float_config('movement_speed_bonus_factor', 0.005)

    @staticmethod
    def combat_flee_base_chance():
        return get_float_config('combat_flee_base_chance', 0.5)

    @staticmethod
    def combat_flee_agility_bonus():
        return get_float_config('combat_flee_agility_bonus', 0.01)

    @staticmethod
    def combat_perfect_victory_xp_bonus():
        return get_int_config('combat_perfect_victory_xp_bonus', 50)

    @staticmethod
    def combat_quick_victory_xp_bonus():
        return get_int_config('combat_quick_victory_xp_bonus', 25)

    @staticmethod
    def combat_level_up_health_bonus():
        return get_int_config('combat_level_up_health_bonus', 10)

    @staticmethod
    def combat_level_5_stat_bonus():
        return get_int_config('combat_level_5_stat_bonus', 2)

    @staticmethod
    def combat_level_5_luck_bonus():
        return get_int_config('combat_level_5_luck_bonus', 1)

    @staticmethod
    def combat_death_health_restore():
        return get_int_config('combat_death_health_restore', 1)

    @staticmethod
    def crafting_base_xp_gain():
        return get_int_config('crafting_base_xp_gain', 8)

    @staticmethod
    def crafting_xp_per_item():
        return get_int_config('crafting_xp_per_item', 10)

    @staticmethod
    def gathering_xp_multiplier():
        return get_int_config('gathering_xp_multiplier', 2)

    @staticmethod
    def gathering_min_amount():
        return get_int_config('gathering_min_amount', 1)

    @staticmethod
    def gathering_max_amount():
        return get_int_config('gathering_max_amount', 5)

    @staticmethod
    def player_start_energy():
        return get_int_config('player_start_energy', 100)

    @staticmethod
    def player_start_health():
        return get_int_config('player_start_health', 100)

    @staticmethod
    def player_start_lat():
        return get_float_config('player_start_lat', 44.933)

    @staticmethod
    def player_start_lon():
        return get_float_config('player_start_lon', 4.893)

    @staticmethod
    def player_start_strength():
        return get_int_config('player_start_strength', 10)

    @staticmethod
    def player_start_agility():
        return get_int_config('player_start_agility', 10)

    @staticmethod
    def player_start_intelligence():
        return get_int_config('player_start_intelligence', 10)

    @staticmethod
    def player_start_luck():
        return get_int_config('player_start_luck', 5)

    @staticmethod
    def biome_bonus(biome_type, material_type):
        """Get biome-specific gathering bonus"""
        key = f'biome_bonus_{biome_type}_{material_type}'
        return get_float_config(key, 1.0)

    @staticmethod
    def material_quantity_range(rarity):
        """Get min/max quantity for material rarity"""
        min_qty = get_int_config(f'material_qty_{rarity}_min', 1)
        max_qty = get_int_config(f'material_qty_{rarity}_max', 5)
        return min_qty, max_qty

    @staticmethod
    def survival_hunger_decrease_rate():
        return get_float_config('survival_hunger_decrease_rate', 1)

    @staticmethod
    def survival_thirst_decrease_rate():
        return get_float_config('survival_thirst_decrease_rate', 1.5)

    @staticmethod
    def survival_radiation_decay_rate():
        return get_float_config('survival_radiation_decay_rate', 0.5)
