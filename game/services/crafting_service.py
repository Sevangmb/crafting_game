import math
import random
from ..models import Recipe, Player, Inventory, PlayerWorkstation, Workstation, CraftingLog, RecipeIngredient, Material, PlayerSkill, PlayerTalent
from ..serializers import PlayerSkillSerializer, PlayerTalentSerializer
from . import player_service
from ..utils.config_helper import GameSettings

def craft_recipe(player, recipe_id, quantity=1):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return {'error': 'Recette introuvable'}, 404

    # Define energy cost for crafting (configurable)
    from ..models import GameConfig
    base_craft_energy = GameConfig.get_config('craft_energy_cost', 2)
    energy_cost = base_craft_energy * quantity

    # Apply building bonuses to reduce energy cost
    from ..services.energy_service import apply_building_effects_to_action
    energy_cost = apply_building_effects_to_action(player, 'craft', energy_cost)

    if player.energy < energy_cost:
        return {'error': 'Pas assez d\'énergie'}, 400

    # Check if recipe requires a workstation
    if recipe.required_workstation:
        try:
            player_workstation = PlayerWorkstation.objects.get(
                player=player,
                workstation=recipe.required_workstation
            )
            if player_workstation.quantity < 1:
                return {
                    'error': f'Vous devez posséder une {recipe.required_workstation.name} pour fabriquer cet objet'
                }, 400
        except PlayerWorkstation.DoesNotExist:
            return {
                'error': f'Vous devez posséder une {recipe.required_workstation.name} pour fabriquer cet objet'
            }, 400

    # Check if player has all ingredients (apply material cost reduction if any)
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    # compute effects
    effects = player_service.get_active_effects(player, 'crafting')
    cost_reduction = effects.get('material_cost_reduction', 0)
    def reduced(q):
        if cost_reduction <= 0:
            return q
        # round up to ensure at least 1 when needed
        new_q = math.ceil(q * (1 - cost_reduction / 100.0))
        return max(1, new_q)

    for ingredient in ingredients:
        try:
            inventory = Inventory.objects.get(player=player, material=ingredient.material)
            need = reduced(ingredient.quantity) * quantity
            if inventory.quantity < need:
                return {
                    'error': f'Pas assez de {ingredient.material.name}. Besoin de {need}, vous avez {inventory.quantity}'
                }, 400
        except Inventory.DoesNotExist:
            return {
                'error': f'Matériau manquant: {ingredient.material.name}'
            }, 400

    # Check if materials should be consumed (talent: no material consumption)
    no_consumption_chance = effects.get('no_material_consumption_chance', 0)
    should_consume_materials = True
    if no_consumption_chance > 0 and random.randint(1, 100) <= no_consumption_chance:
        should_consume_materials = False

    # Deduct ingredients with reduction (unless no consumption triggered)
    if should_consume_materials:
        for ingredient in ingredients:
            inventory = Inventory.objects.get(player=player, material=ingredient.material)
            need = reduced(ingredient.quantity) * quantity
            inventory.quantity -= need
            inventory.save()

    # Add result to inventory
    result_inventory, created = Inventory.objects.get_or_create(
        player=player,
        material=recipe.result_material,
        defaults={'quantity': 0}
    )
    # Apply bonus output chance
    bonus_chance = effects.get('bonus_output_chance', 0)
    bonus = 0
    if bonus_chance > 0 and random.randint(1, 100) <= bonus_chance:
        bonus = recipe.result_quantity
    result_inventory.quantity += recipe.result_quantity * quantity + bonus
    # Initialize durability for tools
    tool_name = recipe.result_material.name.lower()
    def tool_durability_for(name: str):
        if name.startswith('pioche en bronze'):
            return 120
        if name.startswith('pioche'):
            return 90
        if name.startswith('hache en fer'):
            return 120
        if name.startswith('hache en pierre'):
            return 60
        if name.startswith('hache'):
            return 90
        if name.startswith('canne à pêche'):
            return 80
        if name.startswith('arc'):
            return 100
        return 0
    dur_max = tool_durability_for(tool_name)
    if dur_max > 0:
        result_inventory.durability_max = dur_max
        # If crafted multiple, reset current to max (single stack behavior)
        result_inventory.durability_current = dur_max
    result_inventory.save()

    # Log crafting
    CraftingLog.objects.create(
        player=player,
        recipe=recipe,
        quantity=quantity
    )

    # Award crafting XP and auto-unlock
    rarity_bonus = {
        'common': 0,
        'uncommon': 2,
        'rare': 4,
        'epic': 6,
        'legendary': 8,
    }.get(recipe.result_material.rarity, 0)
    base_xp_gain = GameSettings.crafting_base_xp_gain()
    xp_gain = base_xp_gain + rarity_bonus
    player_service.award_xp(player, 'crafting', xp_gain * quantity)

    # Award experience for crafting
    crafting_xp = GameSettings.crafting_xp_per_item() * quantity
    player.experience += crafting_xp

    # Handle level progression
    level_up_bonus = GameConfig.get_config('level_up_energy_bonus', 10)
    leveled_up = False
    while player.experience >= player.get_xp_for_level(player.level + 1):
        player.experience -= player.get_xp_for_level(player.level + 1)
        player.level += 1
        player.max_energy += level_up_bonus  # Increase max energy on level up
        player.energy = min(player.energy, player.max_energy)  # Cap current energy
        leveled_up = True

    player.save()

    # Check achievements
    from .achievement_service import check_achievements
    new_achievements = check_achievements(
        player,
        'craft',
        recipe_name=recipe.name
    )

    # Check level up achievements
    if leveled_up:
        level_achievements = check_achievements(player, 'level_up')
        new_achievements.extend(level_achievements)

    # Update quest progress
    from .quest_service import QuestService
    completed_quests = QuestService.update_quest_progress(
        player,
        'craft',
        recipe_id=recipe_id,
        quantity=quantity
    )

    # Check if this recipe builds a workstation
    workstation_mapping = {
        'Construire Établi': 'Établi',
        'Construire Forge': 'Forge',
        'Construire Enclume': 'Enclume',
        'Construire Table d\'Alchimie': 'Table d\'Alchimie',
    }

    if recipe.name in workstation_mapping:
        workstation_name = workstation_mapping[recipe.name]
        try:
            workstation = Workstation.objects.get(name=workstation_name)
            player_ws, created = PlayerWorkstation.objects.get_or_create(
                player=player,
                workstation=workstation,
                defaults={'quantity': 0}
            )
            player_ws.quantity += quantity
            player_ws.save()

            return {
                'message': f'Station de travail construite: {workstation.name} x{quantity}',
                'crafted': quantity,
                'workstation_built': True
            }, 200
        except Workstation.DoesNotExist:
            pass

    # Check if this recipe creates a Vehicle
    from ..models import Vehicle, PlayerVehicle
    try:
        vehicle = Vehicle.objects.get(name=recipe.result_material.name)
        # Create PlayerVehicle
        pv = PlayerVehicle.objects.create(
            player=player,
            vehicle=vehicle
        )
        return {
            'message': f'Véhicule construit: {vehicle.name}',
            'crafted': quantity,
            'vehicle_built': True,
            'vehicle': {'id': pv.id, 'name': vehicle.name}
        }, 200
    except Vehicle.DoesNotExist:
        pass

    # Return with updated skills/talents
    skills = PlayerSkill.objects.filter(player=player)
    talents = PlayerTalent.objects.filter(player=player)
    response_data = {
        'message': f'Fabriqué {recipe.result_quantity * quantity + bonus}x {recipe.result_material.name}',
        'crafted': recipe.result_quantity * quantity + bonus,
        'skills': PlayerSkillSerializer(skills, many=True).data,
        'talents': PlayerTalentSerializer(talents, many=True).data,
    }

    # Add achievements to response if any were completed
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

    # Add completed quests to response
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

    return response_data, 200

def install_workstation(player, material_id):
    if not material_id:
        return {'error': 'material_id requis'}, 400

    try:
        inv = Inventory.objects.select_related('material').get(player=player, material_id=material_id)
    except Inventory.DoesNotExist:
        return {'error': "Matériau non disponible dans l'inventaire"}, 404

    mat_name = inv.material.name
    try:
        ws = Workstation.objects.get(name=mat_name)
    except Workstation.DoesNotExist:
        return {'error': "Aucune station correspondante pour ce matériau"}, 400

    pw, _ = PlayerWorkstation.objects.get_or_create(player=player, workstation=ws, defaults={'quantity': 0})
    pw.quantity += 1
    pw.save()

    inv.quantity -= 1
    if inv.quantity <= 0:
        inv.delete()
    else:
        inv.save()

    return {
        'message': f"Installé: {ws.name}",
        'workstation': {'id': ws.id, 'name': ws.name},
        'quantity': pw.quantity
    }, 200

def repair_tool(player, material_id):
    try:
        inv = Inventory.objects.select_related('material').get(player=player, material_id=material_id)
    except Inventory.DoesNotExist:
        return {'error': "Outil introuvable dans l'inventaire"}, 404
    if inv.durability_max <= 0:
        return {'error': "Cet objet n'est pas un outil réparable"}, 400
    if inv.durability_current >= inv.durability_max:
        return {'message': 'Outil déjà en parfait état'}, 200

    name = inv.material.name.lower()
    # Determine repair cost item
    repair_item_name = None
    if name.startswith('hache en fer') or name.startswith('pioche'):
        repair_item_name = 'Barre de Fer'
    elif name.startswith('pioche en bronze'):
        repair_item_name = 'Barre de Bronze'
    elif name.startswith('arc') or name.startswith('canne à pêche') or name.startswith('hache en pierre') or name.startswith('hache'):
        repair_item_name = 'Corde'

    if repair_item_name:
        try:
            repair_mat = Material.objects.get(name=repair_item_name)
            cost_inv = Inventory.objects.get(player=player, material=repair_mat)
            if cost_inv.quantity < 1:
                return {'error': f'Pas assez de {repair_item_name} pour réparer'}, 400
            cost_inv.quantity -= 1
            cost_inv.save()
        except (Material.DoesNotExist, Inventory.DoesNotExist):
            return {'error': f'Matériau requis pour réparation manquant: {repair_item_name}'}, 400

    inv.durability_current = inv.durability_max
    inv.save()
    return {'message': 'Outil réparé', 'durability': {'current': inv.durability_current, 'max': inv.durability_max}}, 200
