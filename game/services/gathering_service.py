import random
from ..models import MapCell, CellMaterial, Material, GatheringLog, Inventory, GameConfig
from . import player_service
from .survival_service import SurvivalService
from ..utils.config_helper import GameSettings
from ..services.energy_service import apply_building_effects_to_action
from .achievement_service import check_achievements
from .quest_service import QuestService

def gather_material(player, cell, material_id):
    # Update survival stats before action
    SurvivalService.update_survival_stats(player)

    # Check if player can act (not dead or too weak)
    can_act, reason = SurvivalService.check_can_act(player)
    if not can_act:
        return {'error': reason}, 400

    # Determine category and tool requirements
    try:
        cell_material = CellMaterial.objects.select_related('material').get(cell=cell, material_id=material_id)
    except CellMaterial.DoesNotExist:
        return {'error': 'Matériau introuvable dans cette cellule'}, 404

    # Check if player can carry more weight
    material_weight = cell_material.material.weight
    projected_weight = player.current_carry_weight + material_weight
    if projected_weight > player.effective_carry_capacity:
        return {
            'error': f'Trop lourd ! Ce matériau pèse {material_weight}kg. Capacité: {player.current_carry_weight:.1f}/{player.effective_carry_capacity:.1f}kg',
            'material_weight': material_weight,
            'current_weight': player.current_carry_weight,
            'max_weight': player.effective_carry_capacity
        }, 400

    material_name = cell_material.material.name.lower()

    def needs_pickaxe():
        return any(k in material_name for k in ['minerai', 'diamant', 'rubis', 'émeraude', 'saphir'])

    def needs_axe():
        return 'bois' in material_name or 'tronc' in material_name

    def needs_rod():
        return 'poisson' in material_name or 'poissons' in material_name

    def needs_bow():
        return any(k in material_name for k in ['viande', 'cuir'])

    required_tool = None
    if needs_pickaxe():
        required_tool = 'pickaxe'
    elif needs_axe():
        required_tool = 'axe'
    elif needs_rod():
        required_tool = 'rod'
    elif needs_bow():
        required_tool = 'bow'

    # Helper: check player tools and compute modifiers
    def find_tool_by_prefix(prefixes):
        qs = Inventory.objects.select_related('material').filter(player=player, quantity__gt=0)
        for inv in qs:
            name = inv.material.name.lower()
            if any(name.startswith(p.lower()) for p in prefixes):
                # If tool has durability fields set, ensure it is not broken
                if inv.durability_max > 0 and inv.durability_current <= 0:
                    continue
                return inv
        return None

    def get_tool_modifiers():
        # default modifiers (no tool): smaller yield, normal cost
        gather_min, gather_max = 1, 3
        energy_cost = 5
        quality_bonus = 0

        # Stat bonuses
        # Strength increases yield
        strength_bonus = max(0, (player.strength - 10) // 5) # +1 yield per 5 STR above 10
        gather_min += strength_bonus
        gather_max += strength_bonus
        
        # Luck increases quality bonus chance (implemented in XP/drops)
        # Luck also gives a small chance for extra yield
        if random.random() < (player.luck * 0.01):
            gather_max += 1

        used_tool = None
        if required_tool == 'pickaxe':
            tb = find_tool_by_prefix(['Pioche en Bronze'])
            if tb:
                gather_min += 1
                gather_max += 3
                energy_cost = 3
                quality_bonus = 1
                used_tool = tb
            else:
                ti = find_tool_by_prefix(['Pioche'])
                if ti:
                    gather_min += 0
                    gather_max += 2
                    energy_cost = 4
                    used_tool = ti
        elif required_tool == 'axe':
            ti = find_tool_by_prefix(['Hache en Fer'])
            if ti:
                gather_min += 1
                gather_max += 3
                energy_cost = 3
                quality_bonus = 1
                used_tool = ti
            else:
                tp = find_tool_by_prefix(['Hache en Pierre'])
                if tp:
                    gather_min += 0
                    gather_max += 1
                    energy_cost = 4
                    used_tool = tp
                else:
                    th = find_tool_by_prefix(['Hache'])
                    if th:
                        gather_min += 0
                        gather_max += 2
                        energy_cost = 4
                        used_tool = th
        elif required_tool == 'rod':
            tr = find_tool_by_prefix(['Canne à Pêche'])
            if tr:
                gather_min += 0
                gather_max += 2
                energy_cost = 4
                used_tool = tr
        elif required_tool == 'bow':
            tb = find_tool_by_prefix(['Arc'])
            if tb:
                gather_min += 0
                gather_max += 2
                energy_cost = 4
                used_tool = tb

        return gather_min, gather_max, energy_cost, quality_bonus, used_tool

    # Get gathering talents effects
    gathering_effects = player_service.get_active_effects(player, 'gathering')
    cost_reduction = gathering_effects.get('gather_cost_reduction', 0)

    # Enforce tool requirement if needed
    if required_tool == 'pickaxe' and not (find_tool_by_prefix(['Pioche en Bronze']) or find_tool_by_prefix(['Pioche'])):
        return {'error': 'Une pioche est nécessaire pour extraire ce matériau'}, 400
    if required_tool == 'axe' and not (find_tool_by_prefix(['Hache en Fer']) or find_tool_by_prefix(['Hache en Pierre']) or find_tool_by_prefix(['Hache'])):
        return {'error': 'Une hache est nécessaire pour récolter ce matériau'}, 400
    if required_tool == 'rod' and not find_tool_by_prefix(['Canne à Pêche']):
        return {'error': 'Une canne à pêche est nécessaire pour pêcher'}, 400
    if required_tool == 'bow' and not find_tool_by_prefix(['Arc']):
        return {'error': 'Un arc est nécessaire pour chasser'}, 400

    gather_min, gather_max, energy_cost, quality_bonus, used_tool = get_tool_modifiers()

    # Apply talent cost reduction
    energy_cost = max(1, energy_cost - cost_reduction)

    # Apply survival penalties (low hunger/thirst increases cost)
    energy_cost = SurvivalService.get_action_energy_cost(player, energy_cost)

    # Apply building bonuses to reduce energy cost
    energy_cost = apply_building_effects_to_action(player, 'gather', energy_cost)

    if player.energy < energy_cost:
        return {
            'error': f'Pas assez d\'énergie ! Requis: {energy_cost}, Disponible: {player.energy}',
            'required_energy': energy_cost,
            'current_energy': player.energy
        }, 400

    if cell_material.quantity <= 0:
        return {'error': 'Plus de ce matériau disponible'}, 400

    # Gather amount using tool modifiers (respecting global min/max)
    global_min = GameSettings.gathering_min_amount()
    global_max = GameSettings.gathering_max_amount()
    gather_min = max(global_min, gather_min)
    gather_max = max(global_max, gather_max)
    gather_amount = min(random.randint(gather_min, gather_max), cell_material.quantity)
    
    # Apply double yield chance from talents
    double_yield_chance = gathering_effects.get('double_yield_chance', 0)
    if random.randint(1, 100) <= double_yield_chance:
        gather_amount = min(gather_amount * 2, cell_material.quantity)
    
    # Apply triple yield chance from talents (only if not already doubled)
    triple_yield_chance = gathering_effects.get('triple_yield_chance', 0)
    if random.randint(1, 100) <= triple_yield_chance:
        gather_amount = min(gather_amount * 3, cell_material.quantity)
    
    cell_material.quantity -= gather_amount
    cell_material.save()

    # Add to player inventory
    inventory, created = Inventory.objects.get_or_create(
        player=player,
        material=cell_material.material,
        defaults={'quantity': 0}
    )
    inventory.quantity += gather_amount
    inventory.save()

    # Extra byproducts based on source type (multi-yield)
    extra_plan = {}
    if 'bois' in material_name or 'tronc' in material_name:
        # Tree: logs plus leaves and branches
        extra_plan['Feuilles'] = random.randint(1, max(1, min(3, gather_amount)))
        extra_plan['Branches'] = random.randint(1, max(1, min(2, gather_amount)))
    if material_name in ['baie', 'champignon', 'pomme']:
        # Bush/foraging: a bit of leaves and small branches
        extra_plan['Feuilles'] = max(extra_plan.get('Feuilles', 0), random.randint(1, 2))
        extra_plan['Branches'] = max(extra_plan.get('Branches', 0), random.randint(0, 1))
    if 'minerai' in material_name:
        # Mining: some stone debris
        extra_plan['Pierre'] = random.randint(1, 2)

    extras_awarded = []
    if extra_plan:
        # Only add extras for materials that actually exist
        existing = {m.name: m for m in Material.objects.filter(name__in=list(extra_plan.keys()))}
        for mname, qty in extra_plan.items():
            mat = existing.get(mname)
            if not mat or qty <= 0:
                continue
            inv, _ = Inventory.objects.get_or_create(player=player, material=mat, defaults={'quantity': 0})
            inv.quantity += qty
            inv.save()
            extras_awarded.append((mname, qty))

    # Tool durability loss
    tool_broke = False
    tool_name = ""
    if used_tool and used_tool.durability_max > 0:
        # Durability loss chance (default 100%, reduced by talents/stats?)
        # For now, 1 point per use
        used_tool.durability_current -= 1
        used_tool.save()
        tool_name = used_tool.material.name

        if used_tool.durability_current <= 0:
            tool_broke = True
            # Optional: remove broken tool or keep as broken?
            # Logic above checks durability > 0, so it becomes unusable.
            # Maybe auto-delete or mark broken?
            # For now, just mark broken in UI.

    player.energy -= energy_cost

    # Award gathering skill XP
    gathering_xp_multiplier = GameSettings.gathering_xp_multiplier()
    gathering_xp = (gather_amount + quality_bonus) * gathering_xp_multiplier
    player_service.award_xp(player, 'gathering', gathering_xp)

    # Award experience based on gathering
    base_xp = (gather_amount + quality_bonus) * 2

    # Get XP multipliers from database
    rarity_multipliers = GameConfig.get_config('rarity_xp_multipliers', {
        'common': 1,
        'uncommon': 1.2,
        'rare': 1.5,
        'epic': 2,
        'legendary': 2.5,
    })

    rarity_multiplier = rarity_multipliers.get(cell_material.material.rarity, 1)
    total_xp = int(base_xp * rarity_multiplier)
    player.experience += total_xp

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
    new_achievements = check_achievements(
        player,
        'gather',
        material_name=cell_material.material.name
    )

    # Check level up achievements
    if leveled_up:
        level_achievements = check_achievements(player, 'level_up')
        new_achievements.extend(level_achievements)

    # Update quest progress
    completed_quests = QuestService.update_quest_progress(
        player,
        'gather',
        material_id=material_id,
        quantity=gather_amount
    )

    extra_msg = ''
    if extras_awarded:
        parts = [f"{q}x {n}" for (n, q) in extras_awarded]
        extra_msg = " (+ bonus: " + ", ".join(parts) + ")"

    # Build message with tool durability info
    message = f"Récolté {gather_amount}x {cell_material.material.name}{extra_msg}"
    if tool_broke:
        message += f" | ⚠️ {tool_name} cassé !"

    response_data = {
        'message': message,
        'gathered': gather_amount,
        'extras': [{'name': n, 'quantity': q} for (n, q) in extras_awarded],
        'remaining': cell_material.quantity,
        'tool_broke': tool_broke
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
