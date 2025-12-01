from ..models import Inventory
from .survival_service import SurvivalService
from .advanced_nutrition_service import AdvancedNutritionService
import logging

logger = logging.getLogger(__name__)

def consume_item(player, inventory_id):
    try:
        inventory = Inventory.objects.get(id=inventory_id, player=player)
    except Inventory.DoesNotExist:
        return {'error': 'Objet non trouvé dans l\'inventaire'}, 404

    if not inventory.material.is_food:
        return {'error': 'Cet objet n\'est pas consommable'}, 400

    material = inventory.material

    # Try to use advanced nutrition service first (with detailed nutrients)
    try:
        # Check if food has nutritional profile
        if hasattr(material, 'nutrition'):
            # Use advanced nutrition system (proteins, vitamins, minerals, etc.)
            nutrition_result = AdvancedNutritionService.eat_food(player, material, quantity_grams=100)

            # Also update basic survival stats (hunger/thirst)
            survival_result = SurvivalService.consume_food(player, material, quantity=1)

            # Remove consumed item
            inventory.quantity -= 1
            if inventory.quantity <= 0:
                inventory.delete()
            else:
                inventory.save()

            # Build comprehensive message
            message_parts = []
            if survival_result.get('hunger_restored', 0) > 0:
                message_parts.append(f"🍖 +{int(survival_result['hunger_restored'])} faim")
            if survival_result.get('thirst_restored', 0) > 0:
                message_parts.append(f"💧 +{int(survival_result['thirst_restored'])} soif")
            if survival_result.get('energy_restored', 0) > 0:
                message_parts.append(f"⚡ +{int(survival_result['energy_restored'])} énergie")

            # Add nutrition info if available
            if nutrition_result.get('success'):
                message_parts.append(f"✨ Nutriments absorbés")

            message = ' | '.join(message_parts) if message_parts else 'Consommé'

            return {
                'message': message,
                'energy': survival_result.get('new_energy', player.energy),
                'max_energy': player.max_energy,
                'hunger': survival_result.get('new_hunger', player.hunger),
                'thirst': survival_result.get('new_thirst', player.thirst),
                'radiation': survival_result.get('new_radiation', player.radiation),
                'nutrition_updated': True,
                'inventory_updated': inventory.quantity if hasattr(inventory, 'quantity') else 0
            }, 200
    except Exception as e:
        # Fallback to basic survival system if advanced nutrition fails
        logger.warning(f"Advanced nutrition failed for {material.name}, using basic system: {e}")

    # Fallback: Use basic survival service
    result = SurvivalService.consume_food(player, material, quantity=1)

    # Remove consumed item
    inventory.quantity -= 1
    if inventory.quantity <= 0:
        inventory.delete()
    else:
        inventory.save()

    # Build response message
    message_parts = []
    if result['energy_restored'] > 0:
        message_parts.append(f"⚡ +{result['energy_restored']} énergie")
    if result['hunger_restored'] > 0:
        message_parts.append(f"🍖 +{result['hunger_restored']} faim")
    if result['thirst_restored'] > 0:
        message_parts.append(f"💧 +{result['thirst_restored']} soif")
    if result['radiation_change'] < 0:
        message_parts.append(f"☢️ {result['radiation_change']} radiation")

    message = ' | '.join(message_parts) if message_parts else 'Consommé'

    return {
        'message': message,
        'energy': result['new_energy'],
        'max_energy': player.max_energy,
        'hunger': result['new_hunger'],
        'thirst': result['new_thirst'],
        'radiation': result['new_radiation'],
        'inventory_updated': inventory.quantity if hasattr(inventory, 'quantity') else 0
    }, 200

def get_inventory_summary(player):
    # Get all inventory items with preloaded materials
    queryset = Inventory.objects.filter(player=player).select_related('material')
    
    # Prepare response with empty categories
    response_data = {
        'nourriture': [],
        'bois': [],
        'minerais': [],
        'gemmes': [],
        'magie': [],
        'divers': []
    }
    
    # We need to serialize this data. 
    # Since we are in a service, we should return objects or dicts. 
    # The view will handle serialization usually, but here the logic was grouping them.
    # Let's return the queryset and let the view handle serialization and grouping?
    # Or we can return the grouped data if we use values() or manual dict construction.
    # The original view used InventorySerializer.
    # To keep service pure, maybe just return the queryset?
    # But the view logic was specific about grouping.
    # Let's keep the grouping logic here but we need the serializer.
    # Importing serializer in service might be circular if serializer imports models/views.
    # Serializers usually import models.
    # Let's try to import InventorySerializer inside the function to avoid top-level circularity if any.
    
    from ..serializers import InventorySerializer
    serializer = InventorySerializer(queryset, many=True)
    
    for item in serializer.data:
        category = item.pop('category', 'divers')
        if category in response_data:
            response_data[category].append(item)
        else:
            response_data['divers'].append(item)
    
    return response_data
