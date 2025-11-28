import random
from ..models import MapCell, Inventory, Material
from ..services.energy_service import apply_building_effects_to_action

def scavenge_location(player):
    """
    Scavenge the current location (Urban only).
    """
    # 1. Check location
    try:
        cell = MapCell.objects.get(grid_x=player.grid_x, grid_y=player.grid_y)
    except MapCell.DoesNotExist:
        return {'error': 'Position invalide'}, 400

    if cell.biome != 'urban':
        return {'error': 'Vous ne pouvez fouiller que dans les zones urbaines (villes, villages)'}, 400

    # 2. Check Energy
    energy_cost = 10
    # Apply building bonuses
    energy_cost = apply_building_effects_to_action(player, 'scavenge', energy_cost)

    if player.energy < energy_cost:
        return {'error': 'Pas assez d\'énergie pour fouiller'}, 400

    # 3. Scavenge Logic
    # Loot table for urban scavenging
    loot_table = [
        {'name': 'Conserve', 'chance': 0.4, 'min': 1, 'max': 2},
        {'name': 'Bouteille d\'Eau', 'chance': 0.4, 'min': 1, 'max': 2},
        {'name': 'Tissu', 'chance': 0.3, 'min': 1, 'max': 3},
        {'name': 'Ferraille', 'chance': 0.3, 'min': 1, 'max': 3},
        {'name': 'Médicaments', 'chance': 0.1, 'min': 1, 'max': 1},
        {'name': 'Composants Électroniques', 'chance': 0.05, 'min': 1, 'max': 1},
    ]

    loot_results = []
    found_something = False

    for item in loot_table:
        # Luck bonus
        chance = item['chance'] + (player.luck * 0.01)
        if random.random() < chance:
            found_something = True
            qty = random.randint(item['min'], item['max'])
            
            try:
                mat = Material.objects.get(name=item['name'])
                inv, _ = Inventory.objects.get_or_create(player=player, material=mat)
                inv.quantity += qty
                inv.save()
                loot_results.append({'name': item['name'], 'quantity': qty})
            except Material.DoesNotExist:
                pass

    player.energy -= energy_cost
    
    # Award XP
    xp_gain = 15
    if found_something:
        xp_gain += 10
    player.experience += xp_gain
    player.save()

    if not found_something:
        return {
            'message': 'Vous avez fouillé les décombres mais n\'avez rien trouvé d\'utile.',
            'result': 'nothing',
            'energy_cost': energy_cost
        }, 200

    return {
        'message': 'Fouille terminée !',
        'result': 'success',
        'loot': loot_results,
        'xp_gained': xp_gain
    }, 200
