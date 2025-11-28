"""
Service for Point of Interest (POI) interactions
Handles restaurants, shops, and other interactive locations
"""
import random
from ..models import Material, Inventory, Player

class POIService:
    """Service for handling POI interactions"""

    # Define POI types and their offerings
    POI_TYPES = {
        'restaurant': {
            'icon': '🍽️',
            'currency': 'money',  # Costs money to buy food
            'offerings': {
                'Viande Cuite': {'price': 15, 'stock': 'unlimited'},
                'Poisson Cuit': {'price': 12, 'stock': 'unlimited'},
                'Pain': {'price': 8, 'stock': 'unlimited'},
                'Soupe': {'price': 10, 'stock': 'unlimited'},
                'Eau Purifiée': {'price': 5, 'stock': 'unlimited'},
            }
        },
        'fast_food': {
            'icon': '🍔',
            'currency': 'money',
            'offerings': {
                'Viande Cuite': {'price': 10, 'stock': 'unlimited'},
                'Pain': {'price': 5, 'stock': 'unlimited'},
                'Eau Purifiée': {'price': 3, 'stock': 'unlimited'},
            }
        },
        'cafe': {
            'icon': '☕',
            'currency': 'money',
            'offerings': {
                'Pain': {'price': 6, 'stock': 'unlimited'},
                'Baie': {'price': 4, 'stock': 'unlimited'},
                'Eau Purifiée': {'price': 3, 'stock': 'unlimited'},
            }
        },
        'supermarket': {
            'icon': '🛒',
            'currency': 'money',
            'offerings': {
                'Viande Crue': {'price': 8, 'stock': 'unlimited'},
                'Poisson Cru': {'price': 6, 'stock': 'unlimited'},
                'Baie': {'price': 3, 'stock': 'unlimited'},
                'Pomme': {'price': 4, 'stock': 'unlimited'},
                'Eau Purifiée': {'price': 2, 'stock': 'unlimited'},
                'Pain': {'price': 5, 'stock': 'unlimited'},
            }
        },
        'clothes': {
            'icon': '👕',
            'currency': 'money',
            'offerings': {
                # Equipment items
                'Veste en Cuir': {'price': 50, 'stock': 'limited', 'max': 3},
                'Bottes': {'price': 40, 'stock': 'limited', 'max': 2},
                'Gants': {'price': 30, 'stock': 'limited', 'max': 2},
                'Sac à Dos': {'price': 80, 'stock': 'limited', 'max': 1},
            }
        },
        'hardware': {
            'icon': '🔧',
            'currency': 'money',
            'offerings': {
                'Pioche': {'price': 60, 'stock': 'limited', 'max': 2},
                'Hache': {'price': 50, 'stock': 'limited', 'max': 2},
                'Pelle': {'price': 45, 'stock': 'limited', 'max': 2},
                'Corde': {'price': 20, 'stock': 'unlimited'},
            }
        },
        'pharmacy': {
            'icon': '⚕️',
            'currency': 'money',
            'offerings': {
                'Bandage': {'price': 25, 'stock': 'unlimited'},
                'Anti-Radiation': {'price': 50, 'stock': 'limited', 'max': 5},
                'Stimulant': {'price': 40, 'stock': 'limited', 'max': 3},
            }
        },
        'fuel': {
            'icon': '⛽',
            'currency': 'money',
            'offerings': {
                'Essence': {'price': 30, 'stock': 'unlimited'},
                'Jerrycan': {'price': 50, 'stock': 'limited', 'max': 2},
            }
        },
    }

    @classmethod
    def get_poi_from_osm_features(cls, features):
        """
        Extract interactive POIs from OSM features
        Returns list of POI dicts with name, type, icon
        """
        pois = []

        # Mapping from OSM tags to POI types
        osm_to_poi = {
            ('amenity', 'restaurant'): 'restaurant',
            ('amenity', 'fast_food'): 'fast_food',
            ('amenity', 'cafe'): 'cafe',
            ('shop', 'supermarket'): 'supermarket',
            ('shop', 'convenience'): 'supermarket',
            ('shop', 'clothes'): 'clothes',
            ('shop', 'fashion'): 'clothes',
            ('shop', 'boutique'): 'clothes',
            ('shop', 'hardware'): 'hardware',
            ('shop', 'doityourself'): 'hardware',
            ('amenity', 'pharmacy'): 'pharmacy',
            ('shop', 'chemist'): 'pharmacy',
            ('amenity', 'fuel'): 'fuel',
        }

        for feature in features:
            category = feature.get('category')
            subcategory = feature.get('subcategory')
            key = (category, subcategory)

            if key in osm_to_poi:
                poi_type = osm_to_poi[key]
                poi_data = cls.POI_TYPES.get(poi_type, {})

                pois.append({
                    'name': feature.get('name', f"{subcategory.title()} sans nom"),
                    'type': poi_type,
                    'icon': poi_data.get('icon', '📍'),
                    'osm_id': feature.get('id'),
                })

        return pois

    @classmethod
    def get_poi_menu(cls, poi_type):
        """Get the menu/inventory for a POI type"""
        poi_data = cls.POI_TYPES.get(poi_type, {})
        offerings = poi_data.get('offerings', {})

        menu = []
        for material_name, details in offerings.items():
            # Check if material exists in database
            try:
                material = Material.objects.get(name=material_name)
                menu.append({
                    'material_id': material.id,
                    'material_name': material.name,
                    'material_icon': material.icon,
                    'material_description': material.description,
                    'price': details['price'],
                    'stock_type': details['stock'],
                    'available': True,
                    'hunger_restore': material.hunger_restore,
                    'thirst_restore': material.thirst_restore,
                    'energy_restore': material.energy_restore,
                })
            except Material.DoesNotExist:
                # Material doesn't exist in DB, skip it
                print(f"DEBUG: Material '{material_name}' not found in database for POI '{poi_type}'")
                continue

        return {
            'poi_type': poi_type,
            'icon': poi_data.get('icon', '📍'),
            'currency': poi_data.get('currency', 'money'),
            'menu': menu
        }

    @classmethod
    def purchase_item(cls, player, poi_type, material_id, quantity=1):
        """
        Purchase an item from a POI
        Returns (success, message, updated_player_data)
        """
        # Get POI menu
        poi_menu = cls.get_poi_menu(poi_type)

        # Find the item in menu
        item = next((m for m in poi_menu['menu'] if m['material_id'] == material_id), None)
        if not item:
            return False, "Cet article n'est pas disponible ici.", None

        # Calculate total cost
        total_cost = item['price'] * quantity

        # Check if player has enough currency (money)
        if player.money < total_cost:
            return False, f"Pas assez d'argent ! Requis: {total_cost}₡, Disponible: {player.money}₡", None

        # Check weight capacity
        material = Material.objects.get(id=material_id)
        additional_weight = material.weight * quantity

        if player.current_carry_weight + additional_weight > player.effective_carry_capacity:
            return False, f"Trop lourd ! Cet achat pèse {additional_weight:.1f}kg. Capacité: {player.current_carry_weight:.1f}/{player.effective_carry_capacity:.1f}kg", None

        # Deduct money (payment)
        player.money -= total_cost
        player.save()

        # Add item to inventory
        inventory_item, created = Inventory.objects.get_or_create(
            player=player,
            material=material,
            defaults={'quantity': 0, 'durability_current': 0, 'durability_max': 0}
        )

        inventory_item.quantity += quantity

        # If item has durability, set it to max
        if material.max_durability > 0:
            # For multiple items, we'd need to handle stacking properly
            # For now, set the durability on the stack
            inventory_item.durability_max = material.max_durability
            inventory_item.durability_current = material.max_durability

        inventory_item.save()

        # Success message
        message = f"✅ Acheté {quantity}x {material.name} pour {total_cost}₡!"

        # Return updated player data
        from ..serializers import PlayerSerializer
        player_data = PlayerSerializer(player).data

        return True, message, player_data
