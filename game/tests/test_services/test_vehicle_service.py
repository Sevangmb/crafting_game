from django.test import TestCase
from django.contrib.auth.models import User
from game.models import Player, VehicleType, PlayerVehicle, VehicleMaintenanceLog, FuelStation, Garage
from game.services import advanced_vehicle_service as vehicle_service

class VehicleServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.player = Player.objects.create(user=self.user, money=1000)
        
        self.vehicle_type = VehicleType.objects.create(
            name='Test Car',
            category='car',
            max_durability=100,
            fuel_tank_size=50,
            fuel_type='petrol',
            fuel_consumption=10.0,
            maintenance_interval=1000
        )
        
        self.vehicle = PlayerVehicle.objects.create(
            player=self.player,
            vehicle_type=self.vehicle_type,
            current_fuel=10,
            overall_durability=100
        )

    def tearDown(self):
        """Clean up after each test"""
        # Clean up database objects
        VehicleMaintenanceLog.objects.all().delete()
        PlayerVehicle.objects.all().delete()
        VehicleType.objects.all().delete()
        FuelStation.objects.all().delete()
        Garage.objects.all().delete()
        Player.objects.all().delete()
        User.objects.all().delete()


    def test_equip_vehicle(self):
        # Test equipping a vehicle
        result = vehicle_service.equip_vehicle(self.player, self.vehicle.id)
        self.assertTrue(result['success'])
        self.vehicle.refresh_from_db()
        self.assertTrue(self.vehicle.is_equipped)
        self.assertEqual(self.player.current_vehicle, self.vehicle)

        # Test equipping broken vehicle
        self.vehicle.is_broken = True
        self.vehicle.save()
        result = vehicle_service.equip_vehicle(self.player, self.vehicle.id)
        self.assertFalse(result['success'])
        self.assertIn('broken', result['error'])

    def test_unequip_vehicle(self):
        # Setup equipped vehicle
        vehicle_service.equip_vehicle(self.player, self.vehicle.id)
        
        result = vehicle_service.unequip_vehicle(self.player)
        self.assertTrue(result['success'])
        self.vehicle.refresh_from_db()
        self.assertFalse(self.vehicle.is_equipped)
        self.assertIsNone(self.player.current_vehicle)

    def test_refuel_vehicle(self):
        # Test successful refuel
        result = vehicle_service.refuel_vehicle(self.player, self.vehicle.id, 20, fuel_cost=100)
        self.assertTrue(result['success'], f"Refuel failed: {result.get('error')}")
        self.assertEqual(result['fuel_added'], 20)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_fuel, 30)
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, 900)

        # Test overfill
        print(f"Before overfill: Fuel={self.vehicle.current_fuel}, Max={self.vehicle.vehicle_type.fuel_tank_size}")
        result = vehicle_service.refuel_vehicle(self.player, self.vehicle.id, 100, fuel_cost=0)
        self.assertTrue(result['success'], f"Overfill refuel failed: {result.get('error')}")
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.current_fuel, 50) # Max capacity

        # Test insufficient funds
        self.vehicle.current_fuel = 0
        self.vehicle.save()
        self.player.money = 0
        self.player.save()
        result = vehicle_service.refuel_vehicle(self.player, self.vehicle.id, 10, fuel_cost=100)
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'Not enough money')

    def test_consume_fuel(self):
        # Test fuel consumption
        initial_fuel = self.vehicle.current_fuel
        distance = 100 # Should consume 10L (10L/100km)
        
        result = vehicle_service.consume_fuel(self.vehicle, distance)
        self.assertTrue(result['success'])
        self.vehicle.refresh_from_db()
        self.assertAlmostEqual(self.vehicle.current_fuel, initial_fuel - 10)
        self.assertEqual(self.vehicle.total_distance_km, 100)

        # Test not enough fuel
        self.vehicle.current_fuel = 1
        self.vehicle.save()
        result = vehicle_service.consume_fuel(self.vehicle, 100)
        self.assertFalse(result['success'])
        self.assertIn('fuel', result['error'])

    def test_apply_damage(self):
        # Test applying damage
        result = vehicle_service.apply_vehicle_damage(self.vehicle, 50)
        self.assertTrue(result['success'])
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.overall_durability, 50)
        self.assertFalse(self.vehicle.is_broken)

        # Test breaking vehicle
        result = vehicle_service.apply_vehicle_damage(self.vehicle, 60)
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.overall_durability, 0)
        self.assertTrue(self.vehicle.is_broken)

    def test_repair_vehicle(self):
        # Setup damaged vehicle
        self.vehicle.overall_durability = 50
        self.vehicle.save()

        result = vehicle_service.repair_vehicle(self.player, self.vehicle.id, 50, repair_cost=100)
        self.assertTrue(result['success'])
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.overall_durability, 100)
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, 900)

    def test_maintenance(self):
        # Setup vehicle needing maintenance
        self.vehicle.needs_maintenance = True
        self.vehicle.save()

        result = vehicle_service.perform_maintenance(self.player, self.vehicle.id)
        self.assertTrue(result['success'])
        self.vehicle.refresh_from_db()
        self.assertFalse(self.vehicle.needs_maintenance)
        self.assertEqual(self.vehicle.distance_since_maintenance, 0)

    def test_upgrades(self):
        # Test purchasing upgrade
        result = vehicle_service.purchase_upgrade(self.player, self.vehicle.id, 'speed', 500)
        self.assertTrue(result['success'])
        self.vehicle.refresh_from_db()
        self.assertEqual(self.vehicle.speed_upgrade, 10.0)
        self.player.refresh_from_db()
        self.assertEqual(self.player.money, 500)

    def test_find_nearby_stations(self):
        # Create a fuel station
        FuelStation.objects.create(
            name="Test Station",
            latitude=0,
            longitude=0,
            is_operational=True
        )
        
        # Search near 0,0
        stations = vehicle_service.find_nearby_fuel_stations(0, 0, max_distance_km=10)
        self.assertEqual(len(stations), 1)
        self.assertEqual(stations[0]['name'], "Test Station")

        # Search far away
        stations = vehicle_service.find_nearby_fuel_stations(10, 10, max_distance_km=10)
        self.assertEqual(len(stations), 0)
