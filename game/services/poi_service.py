"""
Service for Point of Interest (POI) interactions
Handles restaurants, shops, and other interactive locations
"""
import random
from datetime import timedelta
from django.utils import timezone
from ..models import Material, Inventory, Player

class POIService:
    """Service for handling POI interactions"""

    # Price fluctuation settings
    PRICE_FLUCTUATION_MIN = 0.85  # Prices can go down to 85% of base
    PRICE_FLUCTUATION_MAX = 1.20  # Prices can go up to 120% of base

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
                # Vetements quotidiens
                'T-shirt Coton': {'price': 15, 'stock': 'unlimited'},
                'Jean': {'price': 50, 'stock': 'unlimited'},
                'Hoodie': {'price': 45, 'stock': 'unlimited'},
                'Baskets': {'price': 70, 'stock': 'unlimited'},
                'Blouson Denim': {'price': 80, 'stock': 'limited', 'max': 3},
                'Parka': {'price': 180, 'stock': 'limited', 'max': 2},
                'Casquette': {'price': 20, 'stock': 'unlimited'},
                'Gants Laine': {'price': 20, 'stock': 'unlimited'},
                # Vetements sport
                'T-shirt Dry-Fit': {'price': 35, 'stock': 'unlimited'},
                'Short Running': {'price': 30, 'stock': 'unlimited'},
                'Veste Softshell': {'price': 100, 'stock': 'limited', 'max': 3},
                'Chaussures Randonnee': {'price': 120, 'stock': 'limited', 'max': 2},
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
                # Equipement travail
                'Casque de Chantier': {'price': 25, 'stock': 'unlimited'},
                'Lunettes de Protection': {'price': 15, 'stock': 'unlimited'},
                'Gants Anti-coupure': {'price': 20, 'stock': 'unlimited'},
                'Chaussures Securite S3': {'price': 80, 'stock': 'limited', 'max': 3},
                'Gilet Fluorescent': {'price': 12, 'stock': 'unlimited'},
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
    def _get_dynamic_price(cls, base_price, material_id, poi_type):
        """
        Calculate dynamic price with daily fluctuation
        Uses material_id and poi_type as seed for consistent daily prices
        """
        # Get current day as seed (changes daily)
        current_day = timezone.now().date().toordinal()

        # Create seed from material_id, poi_type hash, and current day
        seed = hash((material_id, poi_type, current_day)) % 10000
        random.seed(seed)

        # Generate fluctuation multiplier
        fluctuation = random.uniform(cls.PRICE_FLUCTUATION_MIN, cls.PRICE_FLUCTUATION_MAX)

        # Reset random seed to avoid affecting other random operations
        random.seed()

        return int(base_price * fluctuation)

    @classmethod
    def get_poi_menu(cls, poi_type):
        """Get the menu/inventory for a POI type with dynamic pricing"""
        poi_data = cls.POI_TYPES.get(poi_type, {})
        offerings = poi_data.get('offerings', {})

        menu = []
        for material_name, details in offerings.items():
            # Check if material exists in database
            try:
                material = Material.objects.get(name=material_name)

                # Calculate dynamic price
                base_price = details['price']
                current_price = cls._get_dynamic_price(base_price, material.id, poi_type)

                # Calculate price change percentage for UI
                price_change = ((current_price - base_price) / base_price) * 100

                menu.append({
                    'material_id': material.id,
                    'material_name': material.name,
                    'material_icon': material.icon,
                    'material_description': material.description,
                    'price': current_price,
                    'base_price': base_price,  # Original price for comparison
                    'price_change': round(price_change, 1),  # Percentage change
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

    @classmethod
    def sell_item(cls, player, poi_type, material_id, quantity=1):
        """
        Sell an item to a POI
        Returns (success, message, updated_player_data)
        """
        # Check if material exists
        try:
            material = Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            return False, "Matériau non trouvé.", None

        # Check if player has the item in inventory
        try:
            inventory_item = Inventory.objects.get(player=player, material=material)
        except Inventory.DoesNotExist:
            return False, f"Vous n'avez pas de {material.name} dans votre inventaire.", None

        # Check if player has enough quantity
        if inventory_item.quantity < quantity:
            return False, f"Quantité insuffisante. Vous avez {inventory_item.quantity}x {material.name}.", None

        # Determine if POI accepts this item type and get sell price
        sell_price = cls.get_sell_price(material, poi_type)

        if sell_price == 0:
            return False, f"Ce magasin n'achète pas de {material.category}.", None

        # Calculate total earned
        total_earned = sell_price * quantity

        # Remove item from inventory
        inventory_item.quantity -= quantity
        if inventory_item.quantity == 0:
            inventory_item.delete()
        else:
            inventory_item.save()

        # Add money to player
        player.money += total_earned
        player.save()

        # Success message
        message = f"✅ Vendu {quantity}x {material.name} pour {total_earned}₡!"

        # Return updated player data
        from ..serializers import PlayerSerializer
        player_data = PlayerSerializer(player).data

        return True, message, player_data

    @classmethod
    def _can_poi_buy_item(cls, poi_type, material):
        """
        Determine if a POI type will buy this material
        Returns (accepted: bool, sell_price_percentage: float)
        """
        # Define what each POI type accepts
        poi_accepts = {
            'restaurant': {
                'categories': ['nourriture'],
                'sell_percentage': 0.6  # 60% of base price
            },
            'fast_food': {
                'categories': ['nourriture'],
                'sell_percentage': 0.5  # 50% of base price
            },
            'cafe': {
                'categories': ['nourriture'],
                'sell_percentage': 0.5
            },
            'supermarket': {
                'categories': ['nourriture', 'divers'],
                'sell_percentage': 0.6
            },
            'clothes': {
                'categories': ['equipement'],  # If you add clothing category
                'sell_percentage': 0.5
            },
            'hardware': {
                'categories': ['bois', 'minerais', 'divers'],
                'sell_percentage': 0.7  # Tools/materials sell better
            },
            'pharmacy': {
                'categories': ['divers'],  # Medical items
                'sell_percentage': 0.6
            },
            'fuel': {
                'categories': ['divers'],
                'sell_percentage': 0.5
            },
        }

        poi_config = poi_accepts.get(poi_type)
        if not poi_config:
            return False, 0.0

        # Check if material category is accepted
        if material.category in poi_config['categories']:
            return True, poi_config['sell_percentage']

        return False, 0.0

    @classmethod
    def get_sell_price(cls, material, poi_type):
        """
        Get the exact sell price for a material at a POI
        Returns the actual price the player will receive
        """
        # Get base price
        base_price = cls._get_base_sell_price(material, poi_type)

        # Apply dynamic pricing to base
        dynamic_base = cls._get_dynamic_price(base_price, material.id, poi_type)

        # Get sell percentage
        accepted, sell_percentage = cls._can_poi_buy_item(poi_type, material)

        if not accepted:
            return 0

        # Calculate final sell price
        sell_price = int(dynamic_base * sell_percentage)

        return max(1, sell_price)  # Minimum 1 coin

    @classmethod
    def _get_base_sell_price(cls, material, poi_type):
        """
        Get base sell price for a material
        Checks if material is in POI's offerings, otherwise uses default
        """
        poi_data = cls.POI_TYPES.get(poi_type, {})
        offerings = poi_data.get('offerings', {})

        # If POI sells this item, use that price
        if material.name in offerings:
            return offerings[material.name]['price']

        # Otherwise, estimate price based on material properties
        # This is a fallback for items not explicitly in the menu
        base_price = 5  # Default minimum

        # Food items
        if material.is_food:
            base_price = max(
                5,
                (material.hunger_restore or 0) * 0.5 +
                (material.thirst_restore or 0) * 0.4 +
                (material.energy_restore or 0) * 0.3
            )

        # Equipment/tools (estimated by rarity)
        elif material.is_equipment or material.max_durability > 0:
            rarity_multipliers = {
                'common': 1.0,
                'uncommon': 2.0,
                'rare': 4.0,
                'epic': 8.0,
                'legendary': 15.0
            }
            base_price = 20 * rarity_multipliers.get(material.rarity, 1.0)

        # Raw materials
        else:
            base_price = 3

        return int(base_price)
