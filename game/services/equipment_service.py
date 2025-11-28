"""Equipment Management Service

Handles equipping and unequipping items for players.
"""
from typing import Tuple, Dict, Any
from ..models import Inventory, Player


def equip_item(player: Player, item_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Equip an item from player's inventory.
    
    Args:
        player: The player instance
        item_id: The inventory item ID to equip
    
    Returns:
        Tuple of (response dict, status code)
    """
    from ..models import EquippedItem
    
    try:
        inventory_item = Inventory.objects.get(player=player, id=item_id)
    except Inventory.DoesNotExist:
        return {'error': 'Item non trouvé dans l\'inventaire'}, 404
        
    material = inventory_item.material
    if not material.is_equipment or not material.equipment_slot:
        return {'error': 'Cet objet ne peut pas être équipé'}, 400
        
    slot = material.equipment_slot
    
    # Check if slot is occupied
    existing_item = EquippedItem.objects.filter(player=player, slot=slot).first()
    if existing_item:
        # Unequip existing
        unequip_item(player, slot)
        
    # Create equipped item
    EquippedItem.objects.create(
        player=player,
        material=material,
        slot=slot
    )
    
    # Remove from inventory (reduce quantity or delete)
    if inventory_item.quantity > 1:
        inventory_item.quantity -= 1
        inventory_item.save()
    else:
        inventory_item.delete()
        
    return {'message': f'{material.name} équipé avec succès'}, 200

def unequip_item(player: Player, slot: str) -> Tuple[Dict[str, Any], int]:
    """
    Unequip an item from a specific equipment slot.
    
    Args:
        player: The player instance
        slot: The equipment slot name (e.g., 'head', 'chest', 'main_hand')
    
    Returns:
        Tuple of (response dict, status code)
    """
    from ..models import EquippedItem
    
    try:
        equipped = EquippedItem.objects.get(player=player, slot=slot)
    except EquippedItem.DoesNotExist:
        return {'error': 'Aucun objet équipé dans cet emplacement'}, 404
        
    # Add back to inventory
    inventory, created = Inventory.objects.get_or_create(
        player=player,
        material=equipped.material,
        defaults={'quantity': 0}
    )
    inventory.quantity += 1
    inventory.save()
    
    equipped.delete()
    return {'message': 'Objet déséquipé'}, 200
