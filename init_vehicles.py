"""
Initialize the vehicle system with vehicle types, fuel stations, and garages
Run this script once to populate the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from game.models import VehicleType, FuelStation, Garage, VehiclePart


def create_vehicle_types():
    """Create various vehicle types"""
    print("Creating vehicle types...")

    vehicles_data = [
        {
            'name': 'Velo de ville',
            'description': 'Un velo simple et fiable pour les deplacements urbains.',
            'category': 'bicycle',
            'icon': '🚲',
            'max_speed': 25,
            'acceleration': 3.0,
            'handling': 8.0,
            'passenger_capacity': 1,
            'carry_capacity': 15.0,
            'fuel_type': 'none',
            'fuel_tank_size': 0,
            'fuel_consumption': 0,
            'energy_cost_multiplier': 0.8,
            'max_durability': 500,
            'maintenance_interval': 1000,
            'can_offroad': False,
            'can_water': False,
            'requires_road': False,
            'noise_level': 5,
            'weather_protection': 0,
            'rarity': 'common',
            'base_value': 200,
        },
        {
            'name': 'VTT',
            'description': 'Velo tout-terrain robuste pour tous les terrains.',
            'category': 'bicycle',
            'icon': '🚵',
            'max_speed': 30,
            'acceleration': 4.0,
            'handling': 9.0,
            'passenger_capacity': 1,
            'carry_capacity': 20.0,
            'fuel_type': 'none',
            'fuel_tank_size': 0,
            'fuel_consumption': 0,
            'energy_cost_multiplier': 0.7,
            'max_durability': 700,
            'maintenance_interval': 1500,
            'can_offroad': True,
            'can_water': False,
            'requires_road': False,
            'noise_level': 5,
            'weather_protection': 0,
            'rarity': 'uncommon',
            'base_value': 500,
        },
        {
            'name': 'Moto 125cc',
            'description': 'Moto legere et economique, parfaite pour la ville.',
            'category': 'motorcycle',
            'icon': '🏍️',
            'max_speed': 90,
            'acceleration': 7.0,
            'handling': 8.0,
            'passenger_capacity': 2,
            'carry_capacity': 30.0,
            'fuel_type': 'petrol',
            'fuel_tank_size': 12.0,
            'fuel_consumption': 3.0,
            'energy_cost_multiplier': 0.3,
            'max_durability': 1000,
            'maintenance_interval': 3000,
            'can_offroad': False,
            'can_water': False,
            'requires_road': True,
            'noise_level': 70,
            'weather_protection': 10,
            'rarity': 'uncommon',
            'base_value': 3000,
        },
        {
            'name': 'Berline Citadine',
            'description': 'Voiture compacte ideale pour la ville.',
            'category': 'car',
            'icon': '🚗',
            'max_speed': 150,
            'acceleration': 6.0,
            'handling': 7.0,
            'passenger_capacity': 5,
            'carry_capacity': 400.0,
            'fuel_type': 'petrol',
            'fuel_tank_size': 45.0,
            'fuel_consumption': 6.5,
            'energy_cost_multiplier': 0.1,
            'max_durability': 1500,
            'maintenance_interval': 10000,
            'can_offroad': False,
            'can_water': False,
            'requires_road': True,
            'noise_level': 50,
            'weather_protection': 95,
            'rarity': 'common',
            'base_value': 10000,
        },
        {
            'name': 'SUV 4x4',
            'description': 'Vehicule tout-terrain avec grande capacite.',
            'category': 'car',
            'icon': '🚙',
            'max_speed': 170,
            'acceleration': 5.5,
            'handling': 6.0,
            'passenger_capacity': 7,
            'carry_capacity': 600.0,
            'fuel_type': 'diesel',
            'fuel_tank_size': 70.0,
            'fuel_consumption': 9.0,
            'energy_cost_multiplier': 0.1,
            'max_durability': 2000,
            'maintenance_interval': 12000,
            'can_offroad': True,
            'can_water': False,
            'requires_road': False,
            'noise_level': 55,
            'weather_protection': 98,
            'rarity': 'rare',
            'base_value': 30000,
        },
        {
            'name': 'Camionnette',
            'description': 'Vehicule utilitaire avec tres grande capacite de chargement.',
            'category': 'van',
            'icon': '🚐',
            'max_speed': 130,
            'acceleration': 4.0,
            'handling': 5.0,
            'passenger_capacity': 3,
            'carry_capacity': 1000.0,
            'fuel_type': 'diesel',
            'fuel_tank_size': 80.0,
            'fuel_consumption': 10.0,
            'energy_cost_multiplier': 0.1,
            'max_durability': 1800,
            'maintenance_interval': 15000,
            'can_offroad': False,
            'can_water': False,
            'requires_road': True,
            'noise_level': 60,
            'weather_protection': 90,
            'rarity': 'uncommon',
            'base_value': 20000,
        },
        {
            'name': 'Camion de Transport',
            'description': 'Grand camion pour transport de marchandises lourdes.',
            'category': 'truck',
            'icon': '🚚',
            'max_speed': 100,
            'acceleration': 3.0,
            'handling': 4.0,
            'passenger_capacity': 2,
            'carry_capacity': 3000.0,
            'fuel_type': 'diesel',
            'fuel_tank_size': 200.0,
            'fuel_consumption': 25.0,
            'energy_cost_multiplier': 0.05,
            'max_durability': 3000,
            'maintenance_interval': 20000,
            'can_offroad': False,
            'can_water': False,
            'requires_road': True,
            'noise_level': 75,
            'weather_protection': 85,
            'rarity': 'rare',
            'base_value': 50000,
        },
        {
            'name': 'Quad/ATV',
            'description': 'Vehicule tout-terrain leger et maniable.',
            'category': 'atv',
            'icon': '🏎️',
            'max_speed': 80,
            'acceleration': 8.0,
            'handling': 9.0,
            'passenger_capacity': 2,
            'carry_capacity': 100.0,
            'fuel_type': 'petrol',
            'fuel_tank_size': 20.0,
            'fuel_consumption': 8.0,
            'energy_cost_multiplier': 0.2,
            'max_durability': 1200,
            'maintenance_interval': 5000,
            'can_offroad': True,
            'can_water': False,
            'requires_road': False,
            'noise_level': 80,
            'weather_protection': 20,
            'rarity': 'uncommon',
            'base_value': 8000,
        },
        {
            'name': 'Bateau a moteur',
            'description': 'Petit bateau a moteur pour navigation cotiere.',
            'category': 'boat',
            'icon': '🚤',
            'max_speed': 60,
            'acceleration': 5.0,
            'handling': 6.0,
            'passenger_capacity': 6,
            'carry_capacity': 300.0,
            'fuel_type': 'petrol',
            'fuel_tank_size': 100.0,
            'fuel_consumption': 15.0,
            'energy_cost_multiplier': 0.1,
            'max_durability': 1500,
            'maintenance_interval': 8000,
            'can_offroad': False,
            'can_water': True,
            'requires_road': False,
            'noise_level': 65,
            'weather_protection': 30,
            'rarity': 'epic',
            'base_value': 40000,
        },
    ]

    for data in vehicles_data:
        vehicle, created = VehicleType.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"  [OK] Created: {vehicle.name}")
        else:
            print(f"  - Already exists: {vehicle.name}")

    print(f"\nTotal vehicle types: {VehicleType.objects.count()}\n")


def create_fuel_stations():
    """Create fuel stations in Valence area"""
    print("Creating fuel stations...")

    stations_data = [
        {
            'name': 'Station Total - Centre Valence',
            'latitude': 44.933,
            'longitude': 4.893,
            'has_petrol': True,
            'has_diesel': True,
            'has_electric': False,
            'petrol_price_per_liter': 1.75,
            'diesel_price_per_liter': 1.65,
            'petrol_stock': 10000,
            'diesel_stock': 10000,
            'is_operational': True,
        },
        {
            'name': 'Station BP - Nord Valence',
            'latitude': 44.950,
            'longitude': 4.900,
            'has_petrol': True,
            'has_diesel': True,
            'has_electric': True,
            'petrol_price_per_liter': 1.72,
            'diesel_price_per_liter': 1.62,
            'electric_price_per_kwh': 0.35,
            'petrol_stock': 15000,
            'diesel_stock': 15000,
            'is_operational': True,
        },
        {
            'name': 'Station Shell - Sud Valence',
            'latitude': 44.920,
            'longitude': 4.885,
            'has_petrol': True,
            'has_diesel': True,
            'has_electric': False,
            'petrol_price_per_liter': 1.78,
            'diesel_price_per_liter': 1.68,
            'petrol_stock': 8000,
            'diesel_stock': 8000,
            'is_operational': True,
        },
        {
            'name': 'Borne Electrique - Parking Gare',
            'latitude': 44.928,
            'longitude': 4.897,
            'has_petrol': False,
            'has_diesel': False,
            'has_electric': True,
            'electric_price_per_kwh': 0.30,
            'is_operational': True,
        },
    ]

    for data in stations_data:
        station, created = FuelStation.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"  [OK] Created: {station.name}")
        else:
            print(f"  - Already exists: {station.name}")

    print(f"\nTotal fuel stations: {FuelStation.objects.count()}\n")


def create_garages():
    """Create garages/repair shops"""
    print("Creating garages...")

    garages_data = [
        {
            'name': 'Garage Central - Valence',
            'latitude': 44.935,
            'longitude': 4.895,
            'can_repair': True,
            'can_upgrade': True,
            'can_paint': True,
            'can_install_parts': True,
            'repair_cost_per_point': 2.0,
            'upgrade_cost_multiplier': 1.0,
            'mechanic_skill_level': 80,
            'has_parts_inventory': True,
            'is_operational': True,
        },
        {
            'name': 'Atelier Mecanique du Rhone',
            'latitude': 44.945,
            'longitude': 4.905,
            'can_repair': True,
            'can_upgrade': True,
            'can_paint': False,
            'can_install_parts': True,
            'repair_cost_per_point': 1.5,
            'upgrade_cost_multiplier': 0.9,
            'mechanic_skill_level': 70,
            'has_parts_inventory': True,
            'is_operational': True,
        },
        {
            'name': 'Garage Express - Depannage Rapide',
            'latitude': 44.925,
            'longitude': 4.890,
            'can_repair': True,
            'can_upgrade': False,
            'can_paint': False,
            'can_install_parts': False,
            'repair_cost_per_point': 2.5,
            'upgrade_cost_multiplier': 1.0,
            'mechanic_skill_level': 50,
            'has_parts_inventory': False,
            'is_operational': True,
        },
    ]

    for data in garages_data:
        garage, created = Garage.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"  [OK] Created: {garage.name}")
        else:
            print(f"  - Already exists: {garage.name}")

    print(f"\nTotal garages: {Garage.objects.count()}\n")


def create_vehicle_parts():
    """Create some basic vehicle parts"""
    print("Creating vehicle parts...")

    parts_data = [
        {
            'name': 'Moteur Standard',
            'part_type': 'engine',
            'description': 'Moteur de remplacement standard',
            'max_durability': 100,
            'weight': 150.0,
            'speed_modifier': 0.0,
            'fuel_efficiency_modifier': 0.0,
            'handling_modifier': 0.0,
            'rarity': 'common',
            'value': 2000,
        },
        {
            'name': 'Moteur Performance',
            'part_type': 'engine',
            'description': 'Moteur ameliore offrant plus de puissance',
            'max_durability': 120,
            'weight': 170.0,
            'speed_modifier': 15.0,
            'fuel_efficiency_modifier': -5.0,
            'handling_modifier': 0.0,
            'rarity': 'rare',
            'value': 5000,
        },
        {
            'name': 'Pneus Standard',
            'part_type': 'wheels',
            'description': 'Pneus de remplacement basiques',
            'max_durability': 80,
            'weight': 40.0,
            'speed_modifier': 0.0,
            'fuel_efficiency_modifier': 0.0,
            'handling_modifier': 0.0,
            'rarity': 'common',
            'value': 300,
        },
        {
            'name': 'Pneus Sport',
            'part_type': 'wheels',
            'description': 'Pneus haute performance avec meilleure adherence',
            'max_durability': 100,
            'weight': 45.0,
            'speed_modifier': 5.0,
            'fuel_efficiency_modifier': 0.0,
            'handling_modifier': 10.0,
            'rarity': 'uncommon',
            'value': 800,
        },
        {
            'name': 'Batterie 12V Standard',
            'part_type': 'battery',
            'description': 'Batterie de remplacement 12V',
            'max_durability': 100,
            'weight': 15.0,
            'speed_modifier': 0.0,
            'fuel_efficiency_modifier': 0.0,
            'handling_modifier': 0.0,
            'rarity': 'common',
            'value': 150,
        },
        {
            'name': 'Reservoir de Carburant',
            'part_type': 'fuel_tank',
            'description': 'Reservoir de carburant de remplacement',
            'max_durability': 100,
            'weight': 20.0,
            'speed_modifier': 0.0,
            'fuel_efficiency_modifier': 0.0,
            'handling_modifier': 0.0,
            'rarity': 'common',
            'value': 400,
        },
    ]

    for data in parts_data:
        part, created = VehiclePart.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"  [OK] Created: {part.name}")
        else:
            print(f"  - Already exists: {part.name}")

    print(f"\nTotal vehicle parts: {VehiclePart.objects.count()}\n")


def main():
    print("=" * 60)
    print("INITIALISATION DU SYSTEME DE VEHICULES")
    print("=" * 60)
    print()

    create_vehicle_types()
    create_fuel_stations()
    create_garages()
    create_vehicle_parts()

    print("=" * 60)
    print("[SUCCESS] Initialisation terminee avec succes!")
    print("=" * 60)


if __name__ == '__main__':
    main()
