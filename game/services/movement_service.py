from ..models import Player, MapCell, GameConfig
from ..resource_generator import get_biome_from_coordinates
from . import map_service
from .survival_service import SurvivalService
from ..utils.config_helper import GameSettings
from django.utils import timezone
import random

def move_player(player, direction):
    # Update survival stats before action
    SurvivalService.update_survival_stats(player)

    # Check if player can act (not dead or too weak)
    can_act, reason = SurvivalService.check_can_act(player)
    if not can_act:
        return {'error': reason}, 400

    # Check if overencumbered (slowed or blocked)
    if player.is_overencumbered:
        overweight = player.current_carry_weight - player.effective_carry_capacity
        return {
            'error': f'Vous êtes surchargé de {overweight:.1f}kg ! Déposez des objets avant de bouger.',
            'current_weight': player.current_carry_weight,
            'max_weight': player.effective_carry_capacity
        }, 400
    # Calculate new position
    new_grid_x = player.grid_x
    new_grid_y = player.grid_y

    if direction == 'north':
        new_grid_y += 1
    elif direction == 'south':
        new_grid_y -= 1
    elif direction == 'east':
        new_grid_x += 1
    elif direction == 'west':
        new_grid_x -= 1
    else:
        return {'error': 'Direction invalide'}, 400

    # Check if destination cell exists and is not water
    try:
        destination_cell = MapCell.objects.get(grid_x=new_grid_x, grid_y=new_grid_y)
        if destination_cell.biome == 'water':
            # Check if player has a boat or swimming skill (future)
            return {'error': 'Vous ne pouvez pas aller sur l\'eau! Trouvez une case de terre.'}, 400
    except MapCell.DoesNotExist:
        # Create new cell - make sure it's not water
        pass

    # Update player position
    player.grid_x = new_grid_x
    player.grid_y = new_grid_y

    # Calculate new coordinates (approximately 100m per cell)
    grid_offset = GameSettings.movement_grid_offset()
    lat_offset = grid_offset if direction == 'north' else (-grid_offset if direction == 'south' else 0)
    lon_offset = grid_offset if direction == 'east' else (-grid_offset if direction == 'west' else 0)
    player.current_y += lat_offset
    player.current_x += lon_offset

    # Calculate movement cost based on Agility and Speed Bonus
    base_cost = GameSettings.energy_move_cost()

    # Agility reduces cost by configured factor, Speed Bonus also reduces cost
    agility_factor = GameSettings.movement_agility_reduction_factor()
    speed_factor = GameSettings.movement_speed_bonus_factor()
    reduction_factor = 1.0 - (player.agility * agility_factor + player.total_speed_bonus * speed_factor)
    reduction_factor = max(0.1, reduction_factor)  # Min 10% cost

    movement_energy_cost = max(0, int(base_cost * reduction_factor))

    # --- Environment multiplier (time of day, season, biome, weather) ---
    try:
        now = timezone.now()
        hour = now.hour
        month = now.month

        # Time of day buckets
        if 5 <= hour < 8:
            time_of_day = 'dawn'
        elif 8 <= hour < 18:
            time_of_day = 'day'
        elif 18 <= hour < 21:
            time_of_day = 'evening'
        else:
            time_of_day = 'night'

        # Season by month (northern hemisphere)
        if month in (12, 1, 2):
            season = 'winter'
        elif month in (3, 4, 5):
            season = 'spring'
        elif month in (6, 7, 8):
            season = 'summer'
        else:
            season = 'autumn'

        # Determine biome for weather bias
        try:
            biome = get_biome_from_coordinates(player.current_y, player.current_x, player.grid_x, player.grid_y)
        except Exception:
            biome = 'plains'

        # Deterministic RNG per day/biome so weather is stable
        seed_str = f"{now.date()}:{biome}:{player.grid_x}:{player.grid_y}"
        rng = random.Random(seed_str)

        # Weather distribution depending on biome & season
        if biome in ('forest', 'swamp'):
            weather_options = ['clear', 'cloudy', 'rain', 'rain', 'storm']
        elif biome in ('mountain', 'glacier'):
            weather_options = ['clear', 'cloudy', 'snow', 'snow', 'storm']
        elif biome in ('desert', 'volcano'):
            weather_options = ['clear', 'clear', 'clear', 'storm']
        else:
            weather_options = ['clear', 'cloudy', 'rain']

        if season == 'winter' and biome in ('plains', 'forest', 'mountain', 'glacier'):
            weather_options.append('snow')

        weather = rng.choice(weather_options)

        # Build environment multiplier
        env_mult = 1.0

        # Night and evening are harder to travel
        if time_of_day == 'evening':
            env_mult *= 1.10
        elif time_of_day == 'night':
            env_mult *= 1.25

        # Weather impact
        if weather == 'cloudy':
            env_mult *= 1.05
        elif weather == 'rain':
            env_mult *= 1.15
        elif weather == 'snow':
            env_mult *= 1.20
        elif weather == 'storm':
            env_mult *= 1.30

        # Season/biome combination impact
        if season == 'winter' and biome in ('mountain', 'glacier', 'plains', 'forest'):
            env_mult *= 1.10
        if season == 'summer' and biome in ('desert', 'volcano'):
            env_mult *= 1.10

        # Apply biome-specific movement modifier
        from ..resource_generator import get_biome_info
        biome_info = get_biome_info(biome)
        biome_movement_modifier = biome_info.get('movement_modifier', 1.0)
        env_mult *= (2.0 - biome_movement_modifier)  # Convert modifier to multiplier (0.7 modifier = 1.3x cost)

        # Apply multiplier (and round conservatively up)
        movement_energy_cost = int(max(0, round(movement_energy_cost * env_mult)))
    except Exception:
        # In case of any error, keep original cost
        pass

    # Ensure minimum 1 energy if base is > 0, unless super high stats
    if base_cost > 0 and movement_energy_cost == 0 and reduction_factor > 0.1:
         movement_energy_cost = 1

    # Apply survival penalties (low hunger/thirst increases cost)
    movement_energy_cost = SurvivalService.get_action_energy_cost(player, movement_energy_cost)

    # Apply building bonuses to reduce energy cost
    from ..services.energy_service import apply_building_effects_to_action
    movement_energy_cost = apply_building_effects_to_action(player, 'move', movement_energy_cost)

    # Check if player has enough energy
    if player.energy < movement_energy_cost:
        return {
            'error': f'Pas assez d\'énergie ! Requis: {movement_energy_cost}, Disponible: {player.energy}',
            'required_energy': movement_energy_cost,
            'current_energy': player.energy
        }, 400

    player.energy = max(0, player.energy - movement_energy_cost)
    player.total_moves += 1  # Track movement for achievements

    # Apply additional survival pressure from environment on each move
    try:
        SurvivalService.adjust_survival_for_environment(player, season, biome, weather, time_of_day)
    except Exception:
        # Non-critical, ignore errors here
        player.save()
    else:
        # adjust_survival_for_environment already saved fields, but ensure all movement-related fields are saved
        player.save(update_fields=['grid_x', 'grid_y', 'current_x', 'current_y', 'energy', 'total_moves'])

    # Get or create the new cell with OSM-aware biome detection
    # Ensure starting cell (0,0) is always plains in Valence
    if player.grid_x == 0 and player.grid_y == 0:
        biome = 'plains'
        default_lat = 44.933
        default_lon = 4.893
    else:
        default_lat = player.current_y
        default_lon = player.current_x
        
        # Try to fetch OSM features for better biome detection
        try:
            from ..osm_utils import fetch_osm_features
            from .osm_biome_service import detect_biome_from_osm
            
            osm_features = fetch_osm_features(default_lat, default_lon, radius=100)
            osm_biome = detect_biome_from_osm(osm_features) if osm_features else None
            
            if osm_biome:
                biome = osm_biome
                print(f"[MAP] Using OSM biome '{biome}' for new cell at ({player.grid_x}, {player.grid_y})")
            else:
                # Fallback to procedural generation
                biome = get_biome_from_coordinates(default_lat, default_lon, player.grid_x, player.grid_y)
                print(f"[MAP] Using procedural biome '{biome}' for new cell at ({player.grid_x}, {player.grid_y})")
        except Exception as e:
            # If OSM fails, use procedural generation
            print(f"[WARNING] OSM fetch failed, using procedural biome: {str(e)}")
            biome = get_biome_from_coordinates(default_lat, default_lon, player.grid_x, player.grid_y)

    cell, created = MapCell.objects.get_or_create(
        grid_x=player.grid_x,
        grid_y=player.grid_y,
        defaults={
            'center_lat': default_lat,
            'center_lon': default_lon,
            'biome': biome
        }
    )

    if created or not cell.materials.exists():
        # Populate cell with biome-specific materials
        map_service.populate_cell_materials(cell)

    # Check achievements for movement
    from .achievement_service import check_achievements
    new_achievements = check_achievements(
        player,
        'move',
        biome=cell.biome
    )

    # Update quest progress
    from .quest_service import QuestService
    completed_quests = QuestService.update_quest_progress(
        player,
        'visit',
        grid_x=player.grid_x,
        grid_y=player.grid_y
    )

    # Check for random enemy encounter
    from .encounter_service import EncounterService
    encountered, enemy, attacked_first = EncounterService.check_for_encounter(player, cell)

    encounter_data = None
    if encountered:
        # Create the encounter
        encounter = EncounterService.create_encounter(player, enemy, cell, attacked_first)
        encounter_data = {
            'encountered': True,
            'enemy': {
                'id': enemy.id,
                'name': enemy.name,
                'description': enemy.description,
                'icon': enemy.icon,
                'level': enemy.level,
                'health': enemy.health,
                'attack': enemy.attack,
                'defense': enemy.defense,
                'aggression_level': enemy.aggression_level,
            },
            'attacked_first': attacked_first,
            'encounter_id': encounter.id
        }

    # Return player, achievements, and encounter data
    return player, 200, new_achievements if new_achievements else [], completed_quests, encounter_data
