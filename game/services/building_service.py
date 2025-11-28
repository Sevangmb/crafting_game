"""
Building construction service
Handles construction, completion, and building management
"""
from django.utils import timezone
from django.db.models import Q
from game.models import Building, BuildingType, BuildingRecipe, Inventory, MapCell, Player
from game.services import house_service
from game.exceptions import (
    InsufficientMaterialsError,
    InvalidActionError,
    NotFoundError
)
from game.services.achievement_service import check_achievements
import logging

logger = logging.getLogger(__name__)


def get_available_building_types(player):
    """Get all building types available to the player based on level"""
    building_types = BuildingType.objects.filter(
        required_level__lte=player.level
    ).prefetch_related('recipe_materials__material')

    result = []
    for bt in building_types:
        # Get recipe materials
        recipes = BuildingRecipe.objects.filter(building_type=bt).select_related('material')
        materials_needed = [
            {
                'material_id': recipe.material.id,
                'material_name': recipe.material.name,
                'material_icon': recipe.material.icon,
                'quantity': recipe.quantity
            }
            for recipe in recipes
        ]

        result.append({
            'id': bt.id,
            'name': bt.name,
            'description': bt.description,
            'icon': bt.icon,
            'category': bt.category,
            'energy_regeneration_bonus': bt.energy_regeneration_bonus,
            'storage_bonus': bt.storage_bonus,
            'defense_bonus': bt.defense_bonus,
            'production_bonus': bt.production_bonus,
            'construction_time': bt.construction_time,
            'required_level': bt.required_level,
            'materials': materials_needed
        })

    return result


def check_can_build(player, building_type_id, cell):
    """Check if player can build on this cell"""
    try:
        building_type = BuildingType.objects.get(id=building_type_id)
    except BuildingType.DoesNotExist:
        raise NotFoundError("Type de bâtiment introuvable")

    # Check level requirement
    if player.level < building_type.required_level:
        raise InvalidActionError(
            f"Niveau {building_type.required_level} requis pour construire {building_type.name}"
        )

    # Check if cell already has a building from this player
    existing = Building.objects.filter(
        player=player,
        cell=cell,
        status__in=['under_construction', 'completed']
    ).exists()

    if existing:
        raise InvalidActionError("Vous avez déjà un bâtiment sur cette case")

    # Check materials
    recipes = BuildingRecipe.objects.filter(building_type=building_type).select_related('material')
    inventory_items = Inventory.objects.filter(player=player).select_related('material')
    inventory_dict = {inv.material.id: inv.quantity for inv in inventory_items}

    missing_materials = []
    for recipe in recipes:
        available = inventory_dict.get(recipe.material.id, 0)
        if available < recipe.quantity:
            missing_materials.append(
                f"{recipe.material.name} ({available}/{recipe.quantity})"
            )

    if missing_materials:
        raise InsufficientMaterialsError(
            f"Matériaux insuffisants: {', '.join(missing_materials)}"
        )

    return True, building_type, recipes


def start_construction(player, building_type_id, cell_id):
    """Start construction of a building"""
    try:
        cell = MapCell.objects.get(id=cell_id)
    except MapCell.DoesNotExist:
        raise NotFoundError("Cellule introuvable")

    # Check if cell is player's current cell
    if cell.grid_x != player.grid_x or cell.grid_y != player.grid_y:
        raise InvalidActionError("Vous ne pouvez construire que sur votre case actuelle")

    # Check can build
    can_build, building_type, recipes = check_can_build(player, building_type_id, cell)

    # Deduct materials from inventory
    for recipe in recipes:
        inventory = Inventory.objects.get(player=player, material=recipe.material)
        inventory.quantity -= recipe.quantity
        if inventory.quantity <= 0:
            inventory.delete()
        else:
            inventory.save()

    # Create building
    building = Building.objects.create(
        player=player,
        building_type=building_type,
        cell=cell,
        status='under_construction',
        construction_progress=0
    )

    logger.info(f"Player {player.user.username} started construction of {building_type.name} at ({cell.grid_x}, {cell.grid_y})")

    # Check achievements
    new_achievements = check_achievements(player, 'building_count')
    new_achievements.extend(check_achievements(player, 'building_constructed', building_name=building_type.name))

    return building, new_achievements


def complete_construction(building_id, player):
    """Complete construction of a building instantly (for testing) or after time.

    Returns:
        tuple[Building, bool]: (building, house_created)
    """
    try:
        building = Building.objects.get(id=building_id, player=player)
    except Building.DoesNotExist:
        raise NotFoundError("Bâtiment introuvable")

    if building.status != 'under_construction':
        raise InvalidActionError("Ce bâtiment n'est pas en construction")

    # Complete the building
    building.status = 'completed'
    building.construction_progress = 100
    building.construction_completed_at = timezone.now()
    building.save()

    # If this is a housing-type building, create or ensure a House exists on this cell
    house_created = False
    try:
        if building.building_type.category == 'housing':
            _, created = house_service.create_house(player, building.cell)
            house_created = bool(created)
    except Exception as e:
        # Do not fail the completion if house creation has an issue; log and continue
        logger.error(f"Failed to create House for player {player.user.username} at ({building.cell.grid_x}, {building.cell.grid_y}): {e}")

    logger.info(f"Player {player.user.username} completed construction of {building.building_type.name}")

    return building, house_created


def get_player_buildings(player):
    """Get all buildings owned by player"""
    buildings = Building.objects.filter(
        player=player
    ).select_related('building_type', 'cell').order_by('-construction_started_at')

    result = []
    for b in buildings:
        result.append({
            'id': b.id,
            'building_type': {
                'id': b.building_type.id,
                'name': b.building_type.name,
                'icon': b.building_type.icon,
                'category': b.building_type.category,
            },
            'cell': {
                'id': b.cell.id,
                'grid_x': b.cell.grid_x,
                'grid_y': b.cell.grid_y,
            },
            'status': b.status,
            'health': b.health,
            'max_health': b.max_health,
            'construction_progress': b.construction_progress,
            'construction_started_at': b.construction_started_at,
            'construction_completed_at': b.construction_completed_at,
        })

    return result


def get_cell_buildings(cell):
    """Get all buildings on a cell"""
    buildings = Building.objects.filter(
        cell=cell,
        status__in=['under_construction', 'completed']
    ).select_related('building_type', 'player__user')

    result = []
    for b in buildings:
        result.append({
            'id': b.id,
            'building_type': {
                'id': b.building_type.id,
                'name': b.building_type.name,
                'icon': b.building_type.icon,
            },
            'owner': b.player.user.username,
            'status': b.status,
            'construction_progress': b.construction_progress,
        })

    return result


def calculate_player_bonuses(player):
    """Calculate total bonuses from all completed buildings"""
    buildings = Building.objects.filter(
        player=player,
        status='completed'
    ).select_related('building_type')

    bonuses = {
        'energy_regeneration': 0,
        'storage': 0,
        'defense': 0,
        'production': 0.0,
    }

    for building in buildings:
        bonuses['energy_regeneration'] += building.building_type.energy_regeneration_bonus
        bonuses['storage'] += building.building_type.storage_bonus
        bonuses['defense'] += building.building_type.defense_bonus
        bonuses['production'] += building.building_type.production_bonus

    return bonuses
