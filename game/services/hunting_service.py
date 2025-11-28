import random
import math
from ..models import MapCell, Mob, Inventory, Material
from . import player_service
from ..services.energy_service import apply_building_effects_to_action

def hunt_at_location(player):
    """
    Attempt to hunt a mob at the player's current location.
    """
    # 1. Get current cell and biome
    try:
        cell = MapCell.objects.get(grid_x=player.grid_x, grid_y=player.grid_y)
        biome = cell.biome
    except MapCell.DoesNotExist:
        return {'error': 'Position invalide'}, 400

    # 2. Check Energy
    # Get hunting talents effects
    hunting_effects = player_service.get_active_effects(player, 'hunting')
    cost_reduction = hunting_effects.get('hunt_cost_reduction', 0)

    energy_cost = max(1, 5 - cost_reduction) # Base cost 5, reduced by talents

    # Apply building bonuses to reduce energy cost
    energy_cost = apply_building_effects_to_action(player, 'gather', energy_cost)

    if player.energy < energy_cost:
        return {'error': 'Pas assez d\'énergie pour chasser'}, 400

    # 3. Find Mobs for this biome
    # Since we store biomes as JSON string list, we have to filter in python or use regex if simple
    # For small number of mobs, python filtering is fine.
    all_mobs = Mob.objects.all()
    possible_mobs = []
    for m in all_mobs:
        if biome in m.get_biomes():
            possible_mobs.append(m)
    
    if not possible_mobs:
        # Deduct small energy for failed search?
        player.energy = max(0, player.energy - 1)
        player.save()
        return {'message': 'Vous ne trouvez aucune trace d\'animal ici.', 'result': 'nothing'}, 200

    # 4. Select Mob (random for now, could be weighted by rarity/level)
    mob = random.choice(possible_mobs)

    # 5. Combat Calculation (Simplified)
    # Player Power
    damage_bonus = hunting_effects.get('damage_bonus', 0)
    player_attack = player.total_attack + (player.strength // 2) + damage_bonus
    player_defense = player.total_defense + (player.agility // 2) # Agility helps dodge/defense

    # Mob Power
    mob_attack = mob.attack
    mob_defense = mob.defense
    mob_hp = mob.health

    # Damage dealt to mob
    dmg_to_mob = max(1, player_attack - mob_defense)
    
    # Damage dealt to player
    dmg_to_player = max(0, mob_attack - player_defense)

    # Rounds to kill mob
    rounds = math.ceil(mob_hp / dmg_to_mob)
    
    # Total damage taken by player
    total_player_dmg = dmg_to_player * rounds
    
    # Check if player survives (or has enough health to risk it)
    if player.health <= total_player_dmg:
        # Flee or Faint
        player.energy = max(0, player.energy - energy_cost)
        player.health = 1 # Leave with 1 HP
        player.save()
        return {
            'message': f'Vous avez rencontré un {mob.name} mais il était trop fort ! Vous avez fui de justesse.',
            'result': 'fled',
            'mob': mob.name,
            'damage_taken': total_player_dmg
        }, 200

    # Victory!
    player.health = max(1, player.health - total_player_dmg)
    player.energy = max(0, player.energy - energy_cost)
    player.experience += mob.xp_reward
    player.save()

    # Loot
    loot_table = mob.get_loot_table()
    loot_results = []
    
    # Loot bonus from talents
    loot_bonus_chance = hunting_effects.get('loot_bonus_chance', 0)
    
    for mat_name, rules in loot_table.items():
        chance = rules.get('chance', 1.0)
        # Luck bonus to chance
        chance += (player.luck * 0.01)
        
        if random.random() < chance:
            min_q = rules.get('min', 1)
            max_q = rules.get('max', 1)
            # Luck bonus to quantity (small chance)
            if random.random() < (player.luck * 0.02):
                max_q += 1
            # Talent bonus to quantity
            if random.randint(1, 100) <= loot_bonus_chance:
                max_q += 1
                
            quantity = random.randint(min_q, max_q)
            
            try:
                material = Material.objects.get(name=mat_name)
                inv_item, _ = Inventory.objects.get_or_create(player=player, material=material)
                inv_item.quantity += quantity
                inv_item.save()
                loot_results.append({'name': mat_name, 'quantity': quantity})
            except Material.DoesNotExist:
                pass

    # Rare loot chance from talents
    rare_loot_chance = hunting_effects.get('rare_loot_chance', 0)
    if random.randint(1, 100) <= rare_loot_chance:
        # Add a bonus rare item (e.g., extra leather or bones)
        rare_items = ['Cuir', 'Os']
        for rare_item_name in rare_items:
            try:
                rare_material = Material.objects.get(name=rare_item_name)
                inv_item, _ = Inventory.objects.get_or_create(player=player, material=rare_material)
                bonus_qty = random.randint(1, 2)
                inv_item.quantity += bonus_qty
                inv_item.save()
                loot_results.append({'name': rare_item_name, 'quantity': bonus_qty, 'rare': True})
            except Material.DoesNotExist:
                pass

    # Award hunting skill XP
    hunting_xp = mob.xp_reward
    player_service.award_xp(player, 'hunting', hunting_xp)

    return {
        'message': f'Vous avez chassé un {mob.name} !',
        'result': 'success',
        'mob': mob.name,
        'damage_taken': total_player_dmg,
        'xp_gained': mob.xp_reward,
        'loot': loot_results
    }, 200
