"""
Service for handling random enemy encounters on the map
"""
import random
import json
from django.utils import timezone
from ..models import RandomEnemy, Encounter, Player, MapCell, Material, Inventory


class EncounterService:
    """Service for managing random enemy encounters"""

    @classmethod
    def check_for_encounter(cls, player, cell):
        """
        Check if player encounters an enemy when moving to a cell
        Returns (encountered: bool, enemy: RandomEnemy or None, attacked_first: bool)
        """
        # Don't spawn if player already has active encounter
        if Encounter.objects.filter(player=player, status='active').exists():
            return False, None, False

        # Get biome of current cell
        biome = cell.biome

        # Get all enemies that can spawn in this biome
        potential_enemies = RandomEnemy.objects.filter(
            min_level_required__lte=player.level
        )

        # Filter by biome
        eligible_enemies = []
        for enemy in potential_enemies:
            enemy_biomes = enemy.get_biomes()
            if not enemy_biomes or biome in enemy_biomes:
                eligible_enemies.append(enemy)

        if not eligible_enemies:
            return False, None, False

        # Calculate total encounter rate
        total_rate = sum(enemy.encounter_rate for enemy in eligible_enemies)

        # Roll for encounter
        if random.random() > total_rate:
            return False, None, False

        # Select enemy based on weighted probabilities
        weights = [enemy.encounter_rate for enemy in eligible_enemies]
        enemy = random.choices(eligible_enemies, weights=weights, k=1)[0]

        # Check if enemy attacks first
        attacked_first = enemy.should_attack()

        return True, enemy, attacked_first

    @classmethod
    def create_encounter(cls, player, enemy, cell, attacked_first=False):
        """
        Create a new encounter
        Returns the created Encounter object
        """
        encounter = Encounter.objects.create(
            player=player,
            enemy=enemy,
            cell=cell,
            enemy_current_health=enemy.health,
            enemy_attacked_first=attacked_first
        )

        return encounter

    @classmethod
    def resolve_encounter_victory(cls, encounter):
        """
        Resolve encounter when player wins
        Generates and awards loot
        Returns dict with loot information
        """
        from django.utils import timezone

        enemy = encounter.enemy

        # Generate money loot
        money_looted = random.randint(enemy.money_min, enemy.money_max)

        # Generate item loot from equipment
        loot_list = []
        equipment = enemy.get_equipment()

        for material_name, data in equipment.items():
            chance = data.get('chance', 0.5)
            quantity = data.get('quantity', 1)

            if random.random() < chance:
                try:
                    material = Material.objects.get(name=material_name)
                    loot_list.append({
                        'material_id': material.id,
                        'material_name': material.name,
                        'quantity': quantity,
                        'icon': material.icon
                    })

                    # Add to player inventory
                    inventory_item, created = Inventory.objects.get_or_create(
                        player=encounter.player,
                        material=material,
                        defaults={'quantity': 0, 'durability_current': 0, 'durability_max': 0}
                    )
                    inventory_item.quantity += quantity

                    # Set durability for equipment
                    if material.max_durability > 0:
                        inventory_item.durability_max = material.max_durability
                        inventory_item.durability_current = random.randint(
                            int(material.max_durability * 0.3),
                            int(material.max_durability * 0.8)
                        )

                    inventory_item.save()

                except Material.DoesNotExist:
                    print(f"DEBUG: Material '{material_name}' not found for enemy loot")
                    continue

        # Generate item loot from inventory
        inventory_items = enemy.get_inventory()

        for material_name, data in inventory_items.items():
            chance = data.get('chance', 0.3)
            min_qty = data.get('min', 1)
            max_qty = data.get('max', 3)

            if random.random() < chance:
                quantity = random.randint(min_qty, max_qty)
                try:
                    material = Material.objects.get(name=material_name)
                    loot_list.append({
                        'material_id': material.id,
                        'material_name': material.name,
                        'quantity': quantity,
                        'icon': material.icon
                    })

                    # Add to player inventory
                    inventory_item, created = Inventory.objects.get_or_create(
                        player=encounter.player,
                        material=material,
                        defaults={'quantity': 0, 'durability_current': 0, 'durability_max': 0}
                    )
                    inventory_item.quantity += quantity
                    inventory_item.save()

                except Material.DoesNotExist:
                    print(f"DEBUG: Material '{material_name}' not found for enemy loot")
                    continue

        # Award money
        encounter.player.money += money_looted
        encounter.player.save()

        # Update encounter
        encounter.status = 'victory'
        encounter.money_looted = money_looted
        encounter.set_loot(loot_list)
        encounter.ended_at = timezone.now()
        encounter.save()

        return {
            'money': money_looted,
            'items': loot_list,
            'xp': enemy.xp_reward
        }

    @classmethod
    def resolve_encounter_flee(cls, encounter):
        """
        Resolve encounter when player flees
        """
        from django.utils import timezone

        encounter.status = 'fled'
        encounter.ended_at = timezone.now()
        encounter.save()

        return {
            'success': True,
            'message': 'Vous avez fui le combat !'
        }

    @classmethod
    def get_active_encounter(cls, player):
        """
        Get player's current active encounter
        Returns Encounter object or None
        """
        try:
            return Encounter.objects.get(player=player, status='active')
        except Encounter.DoesNotExist:
            return None
