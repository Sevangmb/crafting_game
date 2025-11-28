"""
Advanced vehicle service
Handles fuel, maintenance, repairs, and vehicle operations
"""
from django.utils import timezone
from django.db.models import F, Q
from decimal import Decimal
import random
import math

from ..models import (
    Player, VehicleType, VehiclePart, PlayerVehicle, PlayerVehiclePart,
    VehicleMaintenanceLog, FuelStation, Garage, Inventory, Material
)


def get_player_vehicles(player):
    """
    Get all vehicles owned by a player
    """
    return PlayerVehicle.objects.filter(player=player).select_related('vehicle_type')


def get_equipped_vehicle(player):
    """
    Get currently equipped vehicle
    """
    try:
        return PlayerVehicle.objects.get(player=player, is_equipped=True)
    except PlayerVehicle.DoesNotExist:
        return None


def equip_vehicle(player, vehicle_id):
    """
    Equip a vehicle for use
    """
    try:
        vehicle = PlayerVehicle.objects.get(id=vehicle_id, player=player)
    except PlayerVehicle.DoesNotExist:
        return {'success': False, 'error': 'Vehicle not found'}

    if vehicle.is_broken:
        return {'success': False, 'error': 'Vehicle is broken and needs repairs'}

    # Unequip current vehicle
    PlayerVehicle.objects.filter(player=player, is_equipped=True).update(is_equipped=False)

    # Equip new vehicle
    vehicle.is_equipped = True
    vehicle.save()

    player.current_vehicle = vehicle
    player.save()

    return {
        'success': True,
        'vehicle': vehicle.display_name,
        'can_drive': vehicle.can_drive,
    }


def unequip_vehicle(player):
    """
    Unequip current vehicle
    """
    current = get_equipped_vehicle(player)
    if not current:
        return {'success': False, 'error': 'No vehicle equipped'}

    current.is_equipped = False
    current.save()

    player.current_vehicle = None
    player.save()

    return {'success': True}


def refuel_vehicle(player, vehicle_id, fuel_amount, fuel_cost=0):
    """
    Add fuel to a vehicle

    Args:
        player: Player instance
        vehicle_id: int
        fuel_amount: float (liters to add)
        fuel_cost: int (cost in money, 0 for free refuel from inventory)
    """
    try:
        vehicle = PlayerVehicle.objects.get(id=vehicle_id, player=player)
    except PlayerVehicle.DoesNotExist:
        return {'success': False, 'error': 'Vehicle not found'}

    if vehicle.vehicle_type.fuel_type == 'none':
        return {'success': False, 'error': 'This vehicle does not use fuel'}

    # Check tank capacity
    max_fuel = vehicle.vehicle_type.fuel_tank_size
    current_fuel = vehicle.current_fuel
    space_available = max_fuel - current_fuel

    if space_available <= 0:
        return {'success': False, 'error': 'Fuel tank is full'}

    # Limit to available space
    actual_amount = min(fuel_amount, space_available)

    # Check payment
    if fuel_cost > 0:
        if player.money < fuel_cost:
            return {'success': False, 'error': 'Not enough money'}
        player.money -= fuel_cost
        player.save()

    # Add fuel
    vehicle.current_fuel += actual_amount
    vehicle.save()

    # Log maintenance
    VehicleMaintenanceLog.objects.create(
        player_vehicle=vehicle,
        maintenance_type='refuel',
        description=f'Refueled {actual_amount:.1f}L of {vehicle.vehicle_type.get_fuel_type_display()}',
        cost=fuel_cost,
        fuel_added=actual_amount,
        performed_by=player
    )

    return {
        'success': True,
        'fuel_added': actual_amount,
        'current_fuel': vehicle.current_fuel,
        'fuel_percentage': vehicle.fuel_percentage,
        'cost': fuel_cost,
    }


def calculate_fuel_needed(vehicle, distance_km):
    """
    Calculate fuel needed for a given distance

    Args:
        vehicle: PlayerVehicle instance
        distance_km: float

    Returns:
        float: liters of fuel needed
    """
    consumption_per_100km = vehicle.effective_fuel_consumption
    fuel_needed = (distance_km / 100.0) * consumption_per_100km
    return fuel_needed


def consume_fuel(vehicle, distance_km):
    """
    Consume fuel when vehicle travels

    Args:
        vehicle: PlayerVehicle instance
        distance_km: float
    """
    if vehicle.vehicle_type.fuel_type == 'none':
        return {'success': True, 'fuel_consumed': 0}

    fuel_needed = calculate_fuel_needed(vehicle, distance_km)

    if vehicle.current_fuel < fuel_needed:
        return {
            'success': False,
            'error': 'Not enough fuel',
            'fuel_needed': fuel_needed,
            'fuel_available': vehicle.current_fuel,
        }

    vehicle.current_fuel -= fuel_needed
    vehicle.total_distance_km += distance_km
    vehicle.distance_since_maintenance += distance_km

    # Check if maintenance is needed
    if vehicle.distance_since_maintenance >= vehicle.vehicle_type.maintenance_interval:
        vehicle.needs_maintenance = True

    vehicle.save()

    return {
        'success': True,
        'fuel_consumed': fuel_needed,
        'remaining_fuel': vehicle.current_fuel,
        'distance_traveled': distance_km,
    }


def apply_vehicle_damage(vehicle, damage_amount):
    """
    Apply damage to a vehicle

    Args:
        vehicle: PlayerVehicle instance
        damage_amount: int (durability points to remove)
    """
    vehicle.overall_durability = max(0, vehicle.overall_durability - damage_amount)

    # Check if vehicle is broken
    if vehicle.overall_durability <= 0:
        vehicle.is_broken = True
        vehicle.is_equipped = False

    vehicle.save()

    return {
        'success': True,
        'damage': damage_amount,
        'remaining_durability': vehicle.overall_durability,
        'is_broken': vehicle.is_broken,
    }


def repair_vehicle(player, vehicle_id, repair_points, repair_cost):
    """
    Repair a vehicle

    Args:
        player: Player instance
        vehicle_id: int
        repair_points: int (durability to restore)
        repair_cost: int (cost in money)
    """
    try:
        vehicle = PlayerVehicle.objects.get(id=vehicle_id, player=player)
    except PlayerVehicle.DoesNotExist:
        return {'success': False, 'error': 'Vehicle not found'}

    # Check payment
    if player.money < repair_cost:
        return {'success': False, 'error': 'Not enough money'}

    # Apply repair
    max_dur = vehicle.vehicle_type.max_durability
    vehicle.overall_durability = min(max_dur, vehicle.overall_durability + repair_points)

    # If repaired above 0, no longer broken
    if vehicle.overall_durability > 0:
        vehicle.is_broken = False

    vehicle.save()

    # Deduct cost
    player.money -= repair_cost
    player.save()

    # Log maintenance
    VehicleMaintenanceLog.objects.create(
        player_vehicle=vehicle,
        maintenance_type='repair',
        description=f'Repaired {repair_points} durability points',
        cost=repair_cost,
        durability_restored=repair_points,
        performed_by=player
    )

    return {
        'success': True,
        'durability_restored': repair_points,
        'current_durability': vehicle.overall_durability,
        'cost': repair_cost,
    }


def perform_maintenance(player, vehicle_id):
    """
    Perform routine maintenance on a vehicle
    Resets maintenance counter and improves condition
    """
    try:
        vehicle = PlayerVehicle.objects.get(id=vehicle_id, player=player)
    except PlayerVehicle.DoesNotExist:
        return {'success': False, 'error': 'Vehicle not found'}

    if not vehicle.needs_maintenance:
        return {'success': False, 'error': 'Vehicle does not need maintenance yet'}

    # Calculate maintenance cost
    base_cost = 100
    cost = int(base_cost * (vehicle.vehicle_type.max_durability / 1000))

    if player.money < cost:
        return {'success': False, 'error': 'Not enough money', 'cost_needed': cost}

    # Perform maintenance
    vehicle.distance_since_maintenance = 0
    vehicle.needs_maintenance = False
    vehicle.last_maintenance = timezone.now()

    # Small durability boost
    max_dur = vehicle.vehicle_type.max_durability
    vehicle.overall_durability = min(max_dur, vehicle.overall_durability + 50)

    vehicle.save()

    # Deduct cost
    player.money -= cost
    player.save()

    # Log maintenance
    VehicleMaintenanceLog.objects.create(
        player_vehicle=vehicle,
        maintenance_type='service',
        description='Routine maintenance performed',
        cost=cost,
        durability_restored=50,
        performed_by=player
    )

    return {
        'success': True,
        'cost': cost,
        'next_maintenance_km': vehicle.vehicle_type.maintenance_interval,
    }


def find_nearby_fuel_stations(player_x, player_y, max_distance_km=10):
    """
    Find fuel stations near player location

    Args:
        player_x: float (longitude)
        player_y: float (latitude)
        max_distance_km: float

    Returns:
        list of nearby fuel stations with distances
    """
    # Simple distance calculation (not perfect but good enough for game)
    # 1 degree latitude ≈ 111 km
    # 1 degree longitude ≈ 111 km * cos(latitude)

    lat_range = max_distance_km / 111.0
    lon_range = max_distance_km / (111.0 * math.cos(math.radians(player_y)))

    stations = FuelStation.objects.filter(
        is_operational=True,
        latitude__gte=player_y - lat_range,
        latitude__lte=player_y + lat_range,
        longitude__gte=player_x - lon_range,
        longitude__lte=player_x + lon_range,
    )

    result = []
    for station in stations:
        # Calculate approximate distance
        lat_diff = (station.latitude - player_y) * 111
        lon_diff = (station.longitude - player_x) * 111 * math.cos(math.radians(player_y))
        distance = math.sqrt(lat_diff**2 + lon_diff**2)

        if distance <= max_distance_km:
            result.append({
                'id': station.id,
                'name': station.name,
                'distance_km': round(distance, 2),
                'latitude': station.latitude,
                'longitude': station.longitude,
                'has_petrol': station.has_petrol,
                'has_diesel': station.has_diesel,
                'has_electric': station.has_electric,
                'petrol_price': station.petrol_price_per_liter,
                'diesel_price': station.diesel_price_per_liter,
                'electric_price': station.electric_price_per_kwh,
            })

    # Sort by distance
    result.sort(key=lambda x: x['distance_km'])
    return result


def find_nearby_garages(player_x, player_y, max_distance_km=10):
    """
    Find garages near player location
    """
    lat_range = max_distance_km / 111.0
    lon_range = max_distance_km / (111.0 * math.cos(math.radians(player_y)))

    garages = Garage.objects.filter(
        is_operational=True,
        latitude__gte=player_y - lat_range,
        latitude__lte=player_y + lat_range,
        longitude__gte=player_x - lon_range,
        longitude__lte=player_x + lon_range,
    )

    result = []
    for garage in garages:
        lat_diff = (garage.latitude - player_y) * 111
        lon_diff = (garage.longitude - player_x) * 111 * math.cos(math.radians(player_y))
        distance = math.sqrt(lat_diff**2 + lon_diff**2)

        if distance <= max_distance_km:
            result.append({
                'id': garage.id,
                'name': garage.name,
                'distance_km': round(distance, 2),
                'latitude': garage.latitude,
                'longitude': garage.longitude,
                'can_repair': garage.can_repair,
                'can_upgrade': garage.can_upgrade,
                'can_paint': garage.can_paint,
                'mechanic_skill': garage.mechanic_skill_level,
                'repair_cost_per_point': garage.repair_cost_per_point,
            })

    result.sort(key=lambda x: x['distance_km'])
    return result


def purchase_upgrade(player, vehicle_id, upgrade_type, upgrade_cost):
    """
    Purchase an upgrade for a vehicle

    Args:
        player: Player instance
        vehicle_id: int
        upgrade_type: str ('speed', 'fuel_efficiency', 'capacity')
        upgrade_cost: int
    """
    try:
        vehicle = PlayerVehicle.objects.get(id=vehicle_id, player=player)
    except PlayerVehicle.DoesNotExist:
        return {'success': False, 'error': 'Vehicle not found'}

    if player.money < upgrade_cost:
        return {'success': False, 'error': 'Not enough money'}

    # Apply upgrade
    upgrade_amount = 10.0  # 10% improvement

    if upgrade_type == 'speed':
        vehicle.speed_upgrade += upgrade_amount
    elif upgrade_type == 'fuel_efficiency':
        vehicle.fuel_efficiency_upgrade += upgrade_amount
    elif upgrade_type == 'capacity':
        vehicle.capacity_upgrade += 20.0  # +20kg
    else:
        return {'success': False, 'error': 'Invalid upgrade type'}

    vehicle.save()

    # Deduct cost
    player.money -= upgrade_cost
    player.save()

    # Log upgrade
    VehicleMaintenanceLog.objects.create(
        player_vehicle=vehicle,
        maintenance_type='upgrade',
        description=f'Upgraded {upgrade_type}',
        cost=upgrade_cost,
        performed_by=player
    )

    return {
        'success': True,
        'upgrade_type': upgrade_type,
        'cost': upgrade_cost,
        'current_upgrades': {
            'speed': vehicle.speed_upgrade,
            'fuel_efficiency': vehicle.fuel_efficiency_upgrade,
            'capacity': vehicle.capacity_upgrade,
        }
    }


def get_vehicle_status(vehicle):
    """
    Get comprehensive status of a vehicle

    Args:
        vehicle: PlayerVehicle instance

    Returns:
        dict with all vehicle info
    """
    return {
        'id': vehicle.id,
        'name': vehicle.display_name,
        'type': vehicle.vehicle_type.name,
        'category': vehicle.vehicle_type.get_category_display(),
        'icon': vehicle.vehicle_type.icon,

        # Condition
        'durability': vehicle.overall_durability,
        'max_durability': vehicle.vehicle_type.max_durability,
        'durability_percentage': vehicle.durability_percentage,
        'is_broken': vehicle.is_broken,

        # Fuel
        'fuel_type': vehicle.vehicle_type.get_fuel_type_display(),
        'current_fuel': vehicle.current_fuel,
        'max_fuel': vehicle.vehicle_type.fuel_tank_size,
        'fuel_percentage': vehicle.fuel_percentage,
        'fuel_consumption': vehicle.effective_fuel_consumption,

        # Performance
        'max_speed': vehicle.effective_speed,
        'carry_capacity': vehicle.effective_carry_capacity,
        'passenger_capacity': vehicle.vehicle_type.passenger_capacity,

        # Status
        'is_equipped': vehicle.is_equipped,
        'is_locked': vehicle.is_locked,
        'can_drive': vehicle.can_drive,

        # Mileage
        'total_distance_km': vehicle.total_distance_km,
        'distance_since_maintenance': vehicle.distance_since_maintenance,
        'needs_maintenance': vehicle.needs_maintenance,

        # Upgrades
        'upgrades': {
            'speed': vehicle.speed_upgrade,
            'fuel_efficiency': vehicle.fuel_efficiency_upgrade,
            'capacity': vehicle.capacity_upgrade,
            'has_turbo': vehicle.has_turbo,
            'has_armor': vehicle.has_armor,
        },

        # Capabilities
        'can_offroad': vehicle.vehicle_type.can_offroad,
        'requires_road': vehicle.vehicle_type.requires_road,
        'weather_protection': vehicle.vehicle_type.weather_protection,
        'noise_level': vehicle.vehicle_type.noise_level,
    }


def get_maintenance_history(vehicle, limit=10):
    """
    Get maintenance history for a vehicle
    """
    logs = VehicleMaintenanceLog.objects.filter(
        player_vehicle=vehicle
    ).order_by('-performed_at')[:limit]

    return [{
        'id': log.id,
        'type': log.get_maintenance_type_display(),
        'description': log.description,
        'cost': log.cost,
        'durability_restored': log.durability_restored,
        'fuel_added': log.fuel_added,
        'performed_at': log.performed_at.isoformat(),
    } for log in logs]
