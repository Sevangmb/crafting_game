"""
Durability service (Day R inspired)
Handles item durability consumption and breakage
"""
from game.models import Inventory, EquippedItem, Material
from game.exceptions import GameException
import random


class DurabilityService:
    """Service for managing item durability"""

    @staticmethod
    def initialize_durability(inventory_item, material):
        """
        Initialize durability for a newly acquired item
        """
        if material.max_durability > 0:
            inventory_item.durability_max = material.max_durability
            inventory_item.durability_current = material.max_durability
        else:
            # Non-durable items
            inventory_item.durability_max = 0
            inventory_item.durability_current = 0
        inventory_item.save()

    @staticmethod
    def consume_durability(inventory_item, amount=1):
        """
        Consume durability from an item
        Returns: (item_broke, new_durability)
        """
        if inventory_item.durability_max == 0:
            # Item has infinite durability
            return False, 0

        if inventory_item.durability_current <= 0:
            raise GameException(f"{inventory_item.material.name} est cassé et ne peut plus être utilisé")

        inventory_item.durability_current = max(0, inventory_item.durability_current - amount)

        item_broke = inventory_item.durability_current == 0

        if item_broke:
            # Item broke, remove from inventory
            material_name = inventory_item.material.name
            inventory_item.quantity = max(0, inventory_item.quantity - 1)

            if inventory_item.quantity > 0:
                # Player has more of this item, reset durability for next one
                inventory_item.durability_current = inventory_item.durability_max
            else:
                # No more items
                inventory_item.delete()
                return True, 0

        inventory_item.save()
        return item_broke, inventory_item.durability_current

    @staticmethod
    def get_equipped_tool(player, tool_type='main_hand'):
        """
        Get the equipped tool in specified slot
        """
        try:
            equipped = EquippedItem.objects.get(player=player, slot=tool_type)
            return Inventory.objects.get(player=player, material=equipped.material)
        except (EquippedItem.DoesNotExist, Inventory.DoesNotExist):
            return None

    @staticmethod
    def consume_tool_durability(player, action_type='gather', tool_slot='main_hand'):
        """
        Consume durability from equipped tool during action
        Returns: (tool_name, broke, remaining_durability)
        """
        tool = DurabilityService.get_equipped_tool(player, tool_slot)

        if not tool:
            return None, False, 0

        # Different actions consume different amounts
        durability_cost = {
            'gather': 1,
            'mine': 2,
            'chop': 1,
            'attack': 1,
            'craft': 0  # Crafting doesn't consume tool durability
        }.get(action_type, 1)

        # Add randomness (20% chance to not consume durability)
        if random.random() < 0.2:
            durability_cost = 0

        if durability_cost > 0:
            broke, remaining = DurabilityService.consume_durability(tool, durability_cost)
            return tool.material.name, broke, remaining

        return tool.material.name, False, tool.durability_current

    @staticmethod
    def get_durability_percentage(inventory_item):
        """Get durability as percentage"""
        if inventory_item.durability_max == 0:
            return 100  # Infinite durability

        if inventory_item.durability_max == 0:
            return 0

        return int((inventory_item.durability_current / inventory_item.durability_max) * 100)

    @staticmethod
    def repair_item(inventory_item, material_cost=None):
        """
        Repair an item (future feature)
        Can require materials to repair
        """
        if inventory_item.durability_max == 0:
            raise GameException("Cet objet n'a pas besoin de réparation")

        # For now, full repair
        inventory_item.durability_current = inventory_item.durability_max
        inventory_item.save()

        return inventory_item.durability_current

    @staticmethod
    def get_tool_efficiency(inventory_item):
        """
        Get tool efficiency based on durability
        Lower durability = lower efficiency
        """
        if inventory_item.durability_max == 0:
            return 1.0  # Full efficiency for infinite durability

        percentage = DurabilityService.get_durability_percentage(inventory_item)

        if percentage > 50:
            return 1.0  # Full efficiency
        elif percentage > 25:
            return 0.8  # 80% efficiency
        elif percentage > 10:
            return 0.6  # 60% efficiency
        else:
            return 0.4  # 40% efficiency

    @staticmethod
    def check_tool_for_gathering(player, biome):
        """
        Check if player has appropriate tool for biome
        Returns: (has_tool, efficiency_bonus, tool_name)
        """
        tool = DurabilityService.get_equipped_tool(player, 'main_hand')

        if not tool:
            return False, 1.0, None

        # Different materials/biomes benefit from different tools
        tool_bonuses = {
            'Pioche': {'mountain': 1.5, 'plains': 1.2},
            'Hache': {'forest': 1.5, 'jungle': 1.5},
            'Pelle': {'plains': 1.3, 'beach': 1.4},
            'Épée': {},  # Combat only
        }

        tool_name = tool.material.name
        bonuses = tool_bonuses.get(tool_name, {})
        efficiency = bonuses.get(biome, 1.0)

        # Apply durability penalty
        durability_efficiency = DurabilityService.get_tool_efficiency(tool)
        final_efficiency = efficiency * durability_efficiency

        return True, final_efficiency, tool_name
