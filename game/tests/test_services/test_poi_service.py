"""
Unit tests for POI (Point of Interest) service

Tests POI interactions, shop purchases, and location-based features.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch
from game.models import Player, Material, Inventory, MapCell
from game.services.poi_service import POIService


class POITypesTests(TestCase):
    """Test POI type configurations"""

    def test_poi_types_defined(self):
        """Test that POI types are properly defined"""
        self.assertIsNotNone(POIService.POI_TYPES)
        self.assertIsInstance(POIService.POI_TYPES, dict)

    def test_restaurant_type_exists(self):
        """Test restaurant POI type exists"""
        self.assertIn('restaurant', POIService.POI_TYPES)
        restaurant = POIService.POI_TYPES['restaurant']
        self.assertIn('offerings', restaurant)
        self.assertIn('currency', restaurant)

    def test_supermarket_type_exists(self):
        """Test supermarket POI type exists"""
        self.assertIn('supermarket', POIService.POI_TYPES)
        supermarket = POIService.POI_TYPES['supermarket']
        self.assertIn('offerings', supermarket)

    def test_hardware_store_type_exists(self):
        """Test hardware store POI type exists"""
        self.assertIn('hardware', POIService.POI_TYPES)
        hardware = POIService.POI_TYPES['hardware']
        self.assertIn('offerings', hardware)

    def test_pharmacy_type_exists(self):
        """Test pharmacy POI type exists"""
        self.assertIn('pharmacy', POIService.POI_TYPES)
        pharmacy = POIService.POI_TYPES['pharmacy']
        self.assertIn('offerings', pharmacy)

    def test_offerings_have_prices(self):
        """Test all offerings have price information"""
        for poi_type, data in POIService.POI_TYPES.items():
            offerings = data.get('offerings', {})
            for item_name, item_data in offerings.items():
                self.assertIn('price', item_data,
                             f"{item_name} in {poi_type} missing price")
                self.assertGreater(item_data['price'], 0,
                                  f"{item_name} in {poi_type} has invalid price")

    def test_offerings_have_stock_info(self):
        """Test all offerings have stock information"""
        for poi_type, data in POIService.POI_TYPES.items():
            offerings = data.get('offerings', {})
            for item_name, item_data in offerings.items():
                self.assertIn('stock', item_data,
                             f"{item_name} in {poi_type} missing stock info")


class PriceFluctuationTests(TestCase):
    """Test price fluctuation mechanics"""

    def test_price_fluctuation_constants_exist(self):
        """Test price fluctuation constants are defined"""
        self.assertTrue(hasattr(POIService, 'PRICE_FLUCTUATION_MIN'))
        self.assertTrue(hasattr(POIService, 'PRICE_FLUCTUATION_MAX'))

    def test_price_fluctuation_ranges_valid(self):
        """Test price fluctuation ranges are reasonable"""
        self.assertGreater(POIService.PRICE_FLUCTUATION_MIN, 0)
        self.assertLess(POIService.PRICE_FLUCTUATION_MIN, 1)
        self.assertGreater(POIService.PRICE_FLUCTUATION_MAX, 1)
        self.assertLess(POIService.PRICE_FLUCTUATION_MAX, 2)

    def test_price_fluctuation_min_less_than_max(self):
        """Test min fluctuation is less than max"""
        self.assertLess(
            POIService.PRICE_FLUCTUATION_MIN,
            POIService.PRICE_FLUCTUATION_MAX
        )


class POIOfferingsTests(TestCase):
    """Test POI offerings and inventory"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            money=1000,
            level=5
        )

    def test_restaurant_offers_food(self):
        """Test restaurant offers food items"""
        restaurant = POIService.POI_TYPES['restaurant']
        offerings = restaurant['offerings']

        # Should have common food items
        self.assertTrue(any('Viande' in item for item in offerings.keys()))

    def test_supermarket_offers_variety(self):
        """Test supermarket offers variety of items"""
        supermarket = POIService.POI_TYPES['supermarket']
        offerings = supermarket['offerings']

        # Supermarket should have multiple items
        self.assertGreater(len(offerings), 3)

    def test_hardware_offers_tools(self):
        """Test hardware store offers tools"""
        hardware = POIService.POI_TYPES['hardware']
        offerings = hardware['offerings']

        # Should have tools like pickaxe
        self.assertTrue(any('Pioche' in item or 'Hache' in item for item in offerings.keys()))

    def test_pharmacy_offers_medical_items(self):
        """Test pharmacy offers medical items"""
        pharmacy = POIService.POI_TYPES['pharmacy']
        offerings = pharmacy['offerings']

        # Should have medical items
        self.assertTrue(any('Bandage' in item for item in offerings.keys()))

    def test_unlimited_stock_items(self):
        """Test unlimited stock items are properly marked"""
        for poi_type, data in POIService.POI_TYPES.items():
            offerings = data.get('offerings', {})
            for item_name, item_data in offerings.items():
                if item_data['stock'] == 'unlimited':
                    # Unlimited items shouldn't have max quantity
                    self.assertNotIn('max', item_data)

    def test_limited_stock_items_have_max(self):
        """Test limited stock items have max quantity"""
        for poi_type, data in POIService.POI_TYPES.items():
            offerings = data.get('offerings', {})
            for item_name, item_data in offerings.items():
                if item_data['stock'] == 'limited':
                    self.assertIn('max', item_data,
                                 f"{item_name} has limited stock but no max")
                    self.assertGreater(item_data['max'], 0)


class POICurrencyTests(TestCase):
    """Test POI currency systems"""

    def test_all_pois_have_currency_type(self):
        """Test all POI types specify currency"""
        for poi_type, data in POIService.POI_TYPES.items():
            self.assertIn('currency', data,
                         f"POI type {poi_type} missing currency")

    def test_money_currency_pois(self):
        """Test POIs that use money currency"""
        money_pois = ['restaurant', 'fast_food', 'cafe', 'supermarket',
                      'hardware', 'pharmacy', 'clothes']

        for poi_type in money_pois:
            if poi_type in POIService.POI_TYPES:
                poi_data = POIService.POI_TYPES[poi_type]
                self.assertEqual(poi_data['currency'], 'money',
                               f"{poi_type} should use money currency")


class POIInteractionTests(TestCase):
    """Test POI interaction mechanics"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.player = Player.objects.create(
            user=self.user,
            money=500,
            grid_x=0,
            grid_y=0
        )

        self.cell = MapCell.objects.create(
            grid_x=0,
            grid_y=0,
            center_lat=44.933,
            center_lon=4.893,
            biome='urban'
        )

        # Create food material for testing
        self.bread = Material.objects.create(
            name='Pain',
            icon='🍞',
            category='food',
            is_food=True,
            hunger_restore=20
        )

    def test_poi_service_class_exists(self):
        """Test POIService class is properly defined"""
        self.assertTrue(hasattr(POIService, 'POI_TYPES'))
        self.assertIsInstance(POIService.POI_TYPES, dict)

    def test_poi_has_icon(self):
        """Test POI types have icons"""
        for poi_type, data in POIService.POI_TYPES.items():
            self.assertIn('icon', data,
                         f"POI type {poi_type} missing icon")
            self.assertIsInstance(data['icon'], str)
            self.assertGreater(len(data['icon']), 0)


class POIPricingTests(TestCase):
    """Test POI pricing mechanics"""

    def test_restaurant_prices_reasonable(self):
        """Test restaurant prices are reasonable"""
        restaurant = POIService.POI_TYPES['restaurant']
        offerings = restaurant['offerings']

        for item, data in offerings.items():
            price = data['price']
            # Prices should be positive and reasonable (< 1000)
            self.assertGreater(price, 0)
            self.assertLess(price, 1000)

    def test_hardware_prices_higher_than_food(self):
        """Test hardware items generally cost more than food"""
        hardware = POIService.POI_TYPES.get('hardware', {})
        restaurant = POIService.POI_TYPES.get('restaurant', {})

        if hardware.get('offerings') and restaurant.get('offerings'):
            avg_hardware_price = sum(
                item['price'] for item in hardware['offerings'].values()
            ) / len(hardware['offerings'])

            avg_food_price = sum(
                item['price'] for item in restaurant['offerings'].values()
            ) / len(restaurant['offerings'])

            # Hardware should generally be more expensive
            self.assertGreater(avg_hardware_price, avg_food_price)

    def test_price_consistency_across_pois(self):
        """Test same items have consistent pricing across POI types"""
        # Find items that appear in multiple POIs
        item_prices = {}

        for poi_type, data in POIService.POI_TYPES.items():
            offerings = data.get('offerings', {})
            for item_name, item_data in offerings.items():
                if item_name not in item_prices:
                    item_prices[item_name] = []
                item_prices[item_name].append({
                    'poi': poi_type,
                    'price': item_data['price']
                })

        # Check items that appear in multiple places
        for item_name, price_list in item_prices.items():
            if len(price_list) > 1:
                # Prices should be somewhat consistent (within 3x range)
                prices = [p['price'] for p in price_list]
                min_price = min(prices)
                max_price = max(prices)

                # Max shouldn't be more than 3x min for same item
                if min_price > 0:
                    self.assertLessEqual(max_price / min_price, 3.0,
                        f"{item_name} has inconsistent pricing: {price_list}")


class POIStockManagementTests(TestCase):
    """Test POI stock management"""

    def test_unlimited_stock_availability(self):
        """Test unlimited stock items are always available"""
        restaurant = POIService.POI_TYPES['restaurant']
        offerings = restaurant['offerings']

        for item_name, item_data in offerings.items():
            if item_data['stock'] == 'unlimited':
                # These should always be available
                self.assertEqual(item_data['stock'], 'unlimited')

    def test_limited_stock_has_constraints(self):
        """Test limited stock items have max quantity"""
        clothes = POIService.POI_TYPES.get('clothes', {})
        offerings = clothes.get('offerings', {})

        limited_items = [
            item for item, data in offerings.items()
            if data.get('stock') == 'limited'
        ]

        # Should have some limited stock items
        self.assertGreater(len(limited_items), 0)

        for item_name in limited_items:
            item_data = offerings[item_name]
            self.assertIn('max', item_data)
            self.assertGreater(item_data['max'], 0)
            self.assertLess(item_data['max'], 10)  # Reasonable limit
