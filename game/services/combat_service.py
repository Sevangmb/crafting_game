"""
Combat service for handling player vs mob combat
"""
import random
import json
from ..models import Player, Mob, CombatLog, MapCell, Inventory, Material
from . import player_service
from .survival_service import SurvivalService
from .durability_service import DurabilityService
from ..utils.config_helper import GameSettings


def find_mob_at_location(player):
    """
    Search for a mob at the player's current location.
    Returns (mob, spawn_success) tuple.
    """
    try:
        cell = MapCell.objects.get(grid_x=player.grid_x, grid_y=player.grid_y)
        biome = cell.biome
    except MapCell.DoesNotExist:
        return None, False
    
    # Find mobs that can spawn in this biome
    all_mobs = Mob.objects.all()
    possible_mobs = []
    for mob in all_mobs:
        if biome in mob.get_biomes():
            # Check spawn rate
            if random.random() < mob.spawn_rate:
                possible_mobs.append(mob)
    
    if not possible_mobs:
        return None, False
    
    # Select random mob (could be weighted by level/rarity later)
    mob = random.choice(possible_mobs)
    return mob, True


def calculate_hit_chance(attacker_agility, is_heavy_attack=False):
    """
    Calculate chance to hit based on agility
    Heavy attacks have lower accuracy
    """
    base_accuracy = 0.85  # 85% base hit chance
    agility_bonus = (attacker_agility - 10) * 0.01  # +1% per agility above 10
    
    accuracy = base_accuracy + agility_bonus
    
    if is_heavy_attack:
        accuracy *= 0.7  # Heavy attacks are 30% less accurate
    
    return min(0.95, max(0.50, accuracy))  # Clamp between 50% and 95%


def calculate_damage(attacker_attack, defender_defense, attacker_strength=0, luck=0, is_heavy_attack=False):
    """
    Calculate damage dealt in combat.
    Heavy attacks deal 1.5x damage but have lower accuracy
    """
    base_damage = max(1, attacker_attack - defender_defense)
    
    # Strength bonus
    strength_bonus = attacker_strength // 5
    
    # Heavy attack bonus
    if is_heavy_attack:
        base_damage = int(base_damage * 1.5)
    
    # Critical hit chance based on luck
    is_critical = random.random() < (luck * 0.01)
    if is_critical:
        base_damage = int(base_damage * 1.5)
    
    total_damage = base_damage + strength_bonus
    return total_damage, is_critical


def execute_combat_round(player, mob, player_action='attack'):
    """
    Execute one round of combat.
    Returns: (player_damage, mob_damage, is_critical, combat_log, fled)
    """
    combat_log = []
    is_crit = False
    
    # Player's turn
    if player_action in ['attack', 'heavy_attack']:
        is_heavy = player_action == 'heavy_attack'
        
        # Check if attack hits
        hit_chance = calculate_hit_chance(player.agility, is_heavy)
        if random.random() < hit_chance:
            player_dmg, is_crit = calculate_damage(
                player.total_attack,
                mob.defense,
                player.strength,
                player.luck,
                is_heavy
            )
            
            attack_type = "Coup puissant" if is_heavy else "Vous attaquez"
            crit_text = " (Critique!)" if is_crit else ""
            combat_log.append(f"{attack_type} {mob.name} pour {player_dmg} dégâts{crit_text}")
        else:
            player_dmg = 0
            combat_log.append(f"❌ Attaque manquée !")
    elif player_action == 'defend':
        player_dmg = 0
        combat_log.append(f"🛡️ Vous vous défendez")
    else:  # flee attempt
        flee_chance = GameSettings.combat_flee_base_chance() + (player.agility * GameSettings.combat_flee_agility_bonus())
        if random.random() < flee_chance:
            combat_log.append("💨 Vous avez réussi à fuir!")
            return 0, 0, False, combat_log, True  # fled successfully
        else:
            player_dmg = 0
            combat_log.append("❌ Échec de la fuite!")
    
    # Mob's turn (only if player didn't flee)
    # Use full defense value, reduction happens after damage calculation
    defense_value = player.total_defense if player_action == 'defend' else player.total_defense
    mob_dmg, mob_crit = calculate_damage(
        mob.attack,
        defense_value,
        0,
        0
    )
    
    # Defending reduces damage AFTER calculation
    if player_action == 'defend':
        mob_dmg = mob_dmg // 2
        combat_log.append(f"{mob.name} vous attaque pour {mob_dmg} dégâts (réduits)")
    else:
        combat_log.append(f"{mob.name} vous attaque pour {mob_dmg} dégâts")
    
    return player_dmg, mob_dmg, is_crit if player_action == 'attack' else False, combat_log, False


def initiate_combat(player, mob_id=None):
    """
    Start a combat encounter.
    Returns combat state dict or error.
    """
    # Update survival stats before action
    SurvivalService.update_survival_stats(player)

    # Check if player can act (not dead or too weak)
    can_act, reason = SurvivalService.check_can_act(player)
    if not can_act:
        return {'error': reason}, 400

    # Get or find mob
    if mob_id:
        try:
            mob = Mob.objects.get(id=mob_id)
        except Mob.DoesNotExist:
            return {'error': 'Mob introuvable'}, 404
    else:
        mob, found = find_mob_at_location(player)
        if not found or not mob:
            return {'error': 'Aucun animal trouvé dans cette zone'}, 404

    # Check energy with survival penalties
    base_energy_cost = GameSettings.energy_combat_base_cost()
    energy_cost = SurvivalService.get_action_energy_cost(player, base_energy_cost)

    if player.energy < energy_cost:
        return {
            'error': f'Pas assez d\'énergie ! Requis: {energy_cost}, Disponible: {player.energy}',
            'required_energy': energy_cost,
            'current_energy': player.energy
        }, 400
    
    # Initialize combat state
    combat_state = {
        'mob_id': mob.id,
        'mob_name': mob.name,
        'mob_icon': mob.icon,
        'mob_level': mob.level,
        'mob_health': mob.health,
        'mob_max_health': mob.health,
        'mob_attack': mob.attack,
        'mob_defense': mob.defense,
        'player_health': player.health,
        'player_max_health': player.max_health,
        'rounds': 0,
        'total_damage_dealt': 0,
        'total_damage_taken': 0,
        'combat_log': [f"Un {mob.name} apparaît! (Niveau {mob.level})"],
        'status': 'ongoing'
    }
    
    return combat_state, 200


def process_combat_action(player, combat_state, action='attack'):
    """
    Process a combat action and update state.
    Returns updated combat_state or error.
    """
    if combat_state['status'] != 'ongoing':
        return {'error': 'Le combat est terminé'}, 400
    
    # Get mob
    try:
        mob = Mob.objects.get(id=combat_state['mob_id'])
    except Mob.DoesNotExist:
        return {'error': 'Mob introuvable'}, 404
    
    # Execute combat round
    player_dmg, mob_dmg, is_crit, round_log, fled = execute_combat_round(
        player,
        mob,
        action
    )

    # Handle flee
    if fled:
        combat_state['status'] = 'fled'
        combat_state['combat_log'].extend(round_log)
        player.energy = max(0, player.energy - 2)
        player.save()
        return combat_state, 200

    # Consume weapon durability on attack
    if action == 'attack':
        weapon_name, broke, remaining = DurabilityService.consume_tool_durability(
            player, action_type='attack', tool_slot='main_hand'
        )
        if broke:
            round_log.append(f"⚠️ {weapon_name} s'est cassé !")
            combat_state['weapon_broke'] = True

    # Update health
    combat_state['mob_health'] = max(0, combat_state['mob_health'] - player_dmg)
    combat_state['player_health'] = max(0, combat_state['player_health'] - mob_dmg)
    combat_state['rounds'] += 1
    combat_state['total_damage_dealt'] += player_dmg
    combat_state['total_damage_taken'] += mob_dmg
    combat_state['combat_log'].extend(round_log)
    
    # Synchronize player health immediately to prevent desync
    player.health = combat_state['player_health']
    player.save()
    
    # Check victory/defeat
    if combat_state['mob_health'] <= 0:
        combat_state['status'] = 'victory'
        combat_state['combat_log'].append(f"Vous avez vaincu {mob.name}!")
        
        # Resolve victory
        resolve_combat_victory(player, mob, combat_state)
        
    elif combat_state['player_health'] <= 0:
        combat_state['status'] = 'defeated'
        combat_state['combat_log'].append("Vous avez été vaincu...")
        
        # Resolve defeat
        resolve_combat_defeat(player, mob, combat_state)
    
    return combat_state, 200


def resolve_combat_victory(player, mob, combat_state):
    """
    Handle victory rewards and logging.
    """
    # Calculate XP with bonuses
    base_xp = int(mob.xp_reward * 1.5)  # 50% increase to base XP
    bonus_xp = 0
    bonus_messages = []
    
    # Perfect victory bonus (no damage taken)
    if combat_state['total_damage_taken'] == 0:
        perfect_bonus = GameSettings.combat_perfect_victory_xp_bonus()
        bonus_xp += perfect_bonus
        bonus_messages.append(f"🏆 Victoire parfaite! +{perfect_bonus} XP bonus")

    # Quick victory bonus (3 rounds or less)
    if combat_state['rounds'] <= 3:
        quick_bonus = GameSettings.combat_quick_victory_xp_bonus()
        bonus_xp += quick_bonus
        bonus_messages.append(f"⚡ Victoire rapide! +{quick_bonus} XP bonus")
    
    total_xp = base_xp + bonus_xp
    player.experience += total_xp
    combat_state['xp_gained'] = total_xp
    combat_state['base_xp'] = base_xp
    combat_state['bonus_xp'] = bonus_xp
    
    # Add bonus messages to combat log
    for msg in bonus_messages:
        combat_state['combat_log'].append(msg)
    
    # Award hunting skill XP
    hunting_xp = total_xp
    player_service.award_xp(player, 'hunting', hunting_xp)
    
    # Generate loot
    loot_table = mob.get_loot_table()
    loot_results = []
    
    # Get hunting talents effects
    hunting_effects = player_service.get_active_effects(player, 'hunting')
    loot_bonus_chance = hunting_effects.get('loot_bonus_chance', 0)
    
    for mat_name, rules in loot_table.items():
        chance = rules.get('chance', 1.0)
        # Luck bonus to chance
        chance += (player.luck * 0.01)
        
        if random.random() < chance:
            min_q = rules.get('min', 1)
            max_q = rules.get('max', 1)
            
            # Luck bonus to quantity
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
                loot_results.append({'name': mat_name, 'quantity': quantity, 'icon': material.icon})
            except Material.DoesNotExist:
                pass
    
    combat_state['loot'] = loot_results
    
    # Deduct energy
    player.energy = max(0, player.energy - 5)
    
    # Update health
    player.health = combat_state['player_health']
    
    # Handle level up with improved rewards
    from ..models import GameConfig
    level_up_bonus = GameConfig.get_config('level_up_energy_bonus', 10)
    leveled_up = False
    while player.experience >= player.get_xp_for_level(player.level + 1):
        player.experience -= player.get_xp_for_level(player.level + 1)
        old_level = player.level
        player.level += 1

        # Increase max stats
        player.max_energy += level_up_bonus
        player.max_health += GameSettings.combat_level_up_health_bonus()

        # Full heal on level up
        player.energy = player.max_energy
        player.health = player.max_health

        # Bonus stats every 5 levels
        if player.level % 5 == 0:
            stat_bonus = GameSettings.combat_level_5_stat_bonus()
            luck_bonus = GameSettings.combat_level_5_luck_bonus()
            player.strength += stat_bonus
            player.agility += stat_bonus
            player.intelligence += stat_bonus
            player.luck += luck_bonus
            combat_state['combat_log'].append(f"⭐ Bonus de stats! STR+{stat_bonus}, AGI+{stat_bonus}, INT+{stat_bonus}, LUCK+{luck_bonus}")
        
        leveled_up = True
        combat_state['combat_log'].append(f"🎉 Niveau {old_level} → {player.level}! Santé et énergie restaurées!")
    
    player.save()
    
    # Log combat
    try:
        cell = MapCell.objects.get(grid_x=player.grid_x, grid_y=player.grid_y)
        CombatLog.objects.create(
            player=player,
            mob=mob,
            cell=cell,
            result='victory',
            damage_dealt=combat_state['total_damage_dealt'],
            damage_taken=combat_state['total_damage_taken'],
            rounds=combat_state['rounds'],
            xp_gained=total_xp,
            loot_json=json.dumps(loot_results)
        )
    except MapCell.DoesNotExist:
        pass


def resolve_combat_defeat(player, mob, combat_state):
    """
    Handle defeat consequences and logging.
    """
    # Set health to minimum value (don't kill player)
    player.health = GameSettings.combat_death_health_restore()
    combat_state['player_health'] = GameSettings.combat_death_health_restore()
    
    # Deduct energy
    player.energy = max(0, player.energy - 3)
    
    player.save()
    
    # Log combat
    try:
        cell = MapCell.objects.get(grid_x=player.grid_x, grid_y=player.grid_y)
        CombatLog.objects.create(
            player=player,
            mob=mob,
            cell=cell,
            result='defeated',
            damage_dealt=combat_state['total_damage_dealt'],
            damage_taken=combat_state['total_damage_taken'],
            rounds=combat_state['rounds'],
            xp_gained=0,
            loot_json='[]'
        )
    except MapCell.DoesNotExist:
        pass


def get_combat_history(player, limit=10):
    """
    Get player's recent combat history.
    """
    logs = CombatLog.objects.filter(player=player).order_by('-timestamp')[:limit]
    
    history = []
    for log in logs:
        history.append({
            'id': log.id,
            'mob_name': log.mob.name,
            'mob_icon': log.mob.icon,
            'result': log.result,
            'damage_dealt': log.damage_dealt,
            'damage_taken': log.damage_taken,
            'rounds': log.rounds,
            'xp_gained': log.xp_gained,
            'loot': log.get_loot(),
            'timestamp': log.timestamp.isoformat()
        })
    
    return history
