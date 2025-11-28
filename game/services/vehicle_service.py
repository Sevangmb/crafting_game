from ..models import Vehicle, PlayerVehicle, Player, Inventory, Recipe, RecipeIngredient, GameConfig
from . import player_service

def get_player_vehicles(player):
    """Get all vehicles owned by player"""
    return PlayerVehicle.objects.filter(player=player).select_related('vehicle')

def craft_vehicle(player, recipe_id):
    """Craft a vehicle from a recipe"""
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist:
        return {'error': 'Recette introuvable'}, 404

    # Check if result is actually a vehicle (by name convention or new field)
    # For now, we assume if the recipe result name matches a Vehicle, it's a vehicle recipe
    try:
        vehicle = Vehicle.objects.get(name=recipe.result_material.name)
    except Vehicle.DoesNotExist:
        return {'error': 'Cette recette ne produit pas de véhicule'}, 400

    # Check ingredients
    ingredients = RecipeIngredient.objects.filter(recipe=recipe)
    for ingredient in ingredients:
        try:
            inv = Inventory.objects.get(player=player, material=ingredient.material)
            if inv.quantity < ingredient.quantity:
                return {'error': f'Pas assez de {ingredient.material.name}'}, 400
        except Inventory.DoesNotExist:
            return {'error': f'Matériau manquant: {ingredient.material.name}'}, 400

    # Consume ingredients
    for ingredient in ingredients:
        inv = Inventory.objects.get(player=player, material=ingredient.material)
        inv.quantity -= ingredient.quantity
        inv.save()

    # Create PlayerVehicle
    pv = PlayerVehicle.objects.create(player=player, vehicle=vehicle)

    return {'message': f'Véhicule construit: {vehicle.name}', 'vehicle': {'id': pv.id, 'name': vehicle.name}}, 200

def equip_vehicle(player, vehicle_id):
    """Equip a vehicle"""
    try:
        pv = PlayerVehicle.objects.get(id=vehicle_id, player=player)
    except PlayerVehicle.DoesNotExist:
        return {'error': 'Véhicule introuvable'}, 404

    if player.current_vehicle == pv:
        return {'message': 'Véhicule déjà équipé'}, 200

    # Unequip current if any
    if player.current_vehicle:
        old_pv = player.current_vehicle
        old_pv.is_equipped = False
        old_pv.save()

    # Equip new
    pv.is_equipped = True
    pv.save()
    player.current_vehicle = pv
    player.save()

    return {
        'message': f'Véhicule équipé: {pv.vehicle.name}',
        'carry_capacity': player.effective_carry_capacity
    }, 200

def unequip_vehicle(player):
    """Unequip current vehicle"""
    if not player.current_vehicle:
        return {'error': 'Aucun véhicule équipé'}, 400

    pv = player.current_vehicle
    pv.is_equipped = False
    pv.save()
    
    player.current_vehicle = None
    player.save()

    return {
        'message': f'Véhicule déséquipé',
        'carry_capacity': player.effective_carry_capacity
    }, 200
