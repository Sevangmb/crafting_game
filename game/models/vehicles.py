"""
Advanced vehicle system
Includes fuel, parts, damage, maintenance, and upgrades
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class VehicleType(models.Model):
    """
    Types of vehicles (car, motorcycle, bicycle, truck, etc.)
    """
    VEHICLE_CATEGORIES = [
        ('bicycle', 'Vélo'),
        ('motorcycle', 'Moto'),
        ('car', 'Voiture'),
        ('truck', 'Camion'),
        ('van', 'Camionnette'),
        ('bus', 'Bus'),
        ('boat', 'Bateau'),
        ('helicopter', 'Hélicoptère'),
        ('atv', 'Quad/VTT'),
    ]

    FUEL_TYPES = [
        ('none', 'Aucun'),
        ('petrol', 'Essence'),
        ('diesel', 'Diesel'),
        ('electric', 'Électrique'),
        ('hybrid', 'Hybride'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=VEHICLE_CATEGORIES)
    icon = models.TextField(default='🚗')

    # Performance Stats
    max_speed = models.IntegerField(default=60, help_text="Max speed in km/h")
    acceleration = models.FloatField(default=5.0, help_text="Acceleration factor")
    handling = models.FloatField(default=5.0, help_text="Handling quality (0-10)")

    # Capacity
    passenger_capacity = models.IntegerField(default=1, help_text="Number of passengers")
    carry_capacity = models.FloatField(default=50.0, help_text="Cargo capacity in kg")

    # Fuel system
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES, default='petrol')
    fuel_tank_size = models.FloatField(default=50.0, help_text="Fuel tank size in liters")
    fuel_consumption = models.FloatField(
        default=8.0,
        help_text="Liters per 100km"
    )

    # Energy efficiency for movement
    energy_cost_multiplier = models.FloatField(
        default=0.5,
        help_text="Multiplier for player energy cost when using vehicle"
    )

    # Durability
    max_durability = models.IntegerField(default=1000)
    maintenance_interval = models.IntegerField(
        default=5000,
        help_text="Distance in km before maintenance needed"
    )

    # Terrain capabilities
    can_offroad = models.BooleanField(default=False)
    can_water = models.BooleanField(default=False)
    requires_road = models.BooleanField(default=True)

    # Noise and visibility
    noise_level = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="How loud the vehicle is (affects stealth)"
    )

    # Weather resistance
    weather_protection = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Protection from rain/cold"
    )

    # Rarity and value
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Commun'),
        ('uncommon', 'Peu commun'),
        ('rare', 'Rare'),
        ('epic', 'Épique'),
        ('legendary', 'Légendaire'),
    ], default='common')

    base_value = models.IntegerField(default=1000, help_text="Base monetary value")

    class Meta:
        app_label = 'game'
        verbose_name = 'Type de véhicule'
        verbose_name_plural = 'Types de véhicules'

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class VehiclePart(models.Model):
    """
    Vehicle parts that can be damaged and replaced
    """
    PART_TYPES = [
        ('engine', 'Moteur'),
        ('transmission', 'Transmission'),
        ('wheels', 'Roues'),
        ('battery', 'Batterie'),
        ('fuel_tank', 'Réservoir'),
        ('radiator', 'Radiateur'),
        ('brakes', 'Freins'),
        ('suspension', 'Suspension'),
        ('body', 'Carrosserie'),
        ('windshield', 'Pare-brise'),
        ('lights', 'Feux'),
        ('seats', 'Sièges'),
        ('electrical', 'Système électrique'),
        ('exhaust', 'Échappement'),
    ]

    name = models.CharField(max_length=100, unique=True)
    part_type = models.CharField(max_length=20, choices=PART_TYPES)
    description = models.TextField()

    # Which vehicles can use this part
    compatible_vehicles = models.ManyToManyField(VehicleType, related_name='parts')

    # Stats
    max_durability = models.IntegerField(default=100)
    weight = models.FloatField(default=10.0, help_text="Weight in kg")

    # Effects on vehicle performance
    speed_modifier = models.FloatField(default=0.0, help_text="Speed bonus/penalty")
    fuel_efficiency_modifier = models.FloatField(default=0.0, help_text="Fuel consumption modifier")
    handling_modifier = models.FloatField(default=0.0)

    # Rarity and crafting
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Commun'),
        ('uncommon', 'Peu commun'),
        ('rare', 'Rare'),
        ('epic', 'Épique'),
        ('legendary', 'Légendaire'),
    ], default='common')

    value = models.IntegerField(default=100, help_text="Monetary value")

    class Meta:
        app_label = 'game'
        verbose_name = 'Pièce de véhicule'
        verbose_name_plural = 'Pièces de véhicules'

    def __str__(self):
        return f"{self.name} ({self.get_part_type_display()})"


class PlayerVehicle(models.Model):
    """
    Vehicles owned by players with detailed state tracking
    """
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='owned_vehicles')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, null=True, blank=True)

    # Custom name
    custom_name = models.CharField(max_length=100, blank=True, null=True)

    # Overall condition
    overall_durability = models.IntegerField(default=1000)

    # Fuel
    current_fuel = models.FloatField(default=0.0, help_text="Current fuel in liters")

    # Mileage
    total_distance_km = models.FloatField(default=0.0, help_text="Total distance traveled")
    distance_since_maintenance = models.FloatField(default=0.0)

    # Status
    is_equipped = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=True)
    is_broken = models.BooleanField(default=False)

    # Location (if parked)
    parked_x = models.FloatField(null=True, blank=True)
    parked_y = models.FloatField(null=True, blank=True)

    # Maintenance
    needs_maintenance = models.BooleanField(default=False)
    last_maintenance = models.DateTimeField(null=True, blank=True)

    # Modifications
    has_turbo = models.BooleanField(default=False)
    has_armor = models.BooleanField(default=False)
    armor_value = models.IntegerField(default=0)

    # Upgrades
    fuel_efficiency_upgrade = models.FloatField(default=0.0, help_text="% reduction in fuel consumption")
    speed_upgrade = models.FloatField(default=0.0, help_text="% increase in max speed")
    capacity_upgrade = models.FloatField(default=0.0, help_text="Additional cargo capacity")

    # Ownership
    acquired_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        app_label = 'game'
        verbose_name = 'Véhicule du joueur'
        verbose_name_plural = 'Véhicules des joueurs'

    def __str__(self):
        name = self.custom_name or self.vehicle_type.name
        return f"{self.player.user.username}'s {name}"

    @property
    def display_name(self):
        """Get display name (custom or default)"""
        return self.custom_name or self.vehicle_type.name

    @property
    def fuel_percentage(self):
        """Get fuel level as percentage"""
        if self.vehicle_type.fuel_tank_size == 0:
            return 100.0
        return (self.current_fuel / self.vehicle_type.fuel_tank_size) * 100

    @property
    def durability_percentage(self):
        """Get overall durability as percentage"""
        return (self.overall_durability / self.vehicle_type.max_durability) * 100

    @property
    def effective_speed(self):
        """Calculate effective max speed with upgrades and damage"""
        base_speed = self.vehicle_type.max_speed

        # Apply upgrades
        speed = base_speed * (1 + self.speed_upgrade / 100)

        # Apply damage penalty
        if self.durability_percentage < 50:
            speed *= (self.durability_percentage / 50)

        return int(speed)

    @property
    def effective_fuel_consumption(self):
        """Calculate effective fuel consumption"""
        base_consumption = self.vehicle_type.fuel_consumption

        # Apply upgrades
        consumption = base_consumption * (1 - self.fuel_efficiency_upgrade / 100)

        # Damaged vehicles consume more fuel
        if self.durability_percentage < 70:
            consumption *= 1.3

        return consumption

    @property
    def effective_carry_capacity(self):
        """Calculate effective cargo capacity"""
        base_capacity = self.vehicle_type.carry_capacity
        return base_capacity + self.capacity_upgrade

    @property
    def can_drive(self):
        """Check if vehicle can be driven"""
        if self.is_broken:
            return False

        # Electric vehicles need battery
        if self.vehicle_type.fuel_type == 'electric':
            return self.current_fuel > 0

        # Fuel vehicles need fuel
        if self.vehicle_type.fuel_type in ['petrol', 'diesel', 'hybrid']:
            return self.current_fuel > 0

        # No fuel needed (bicycle)
        return True


class PlayerVehiclePart(models.Model):
    """
    Individual parts installed on a player's vehicle
    """
    player_vehicle = models.ForeignKey(PlayerVehicle, on_delete=models.CASCADE, related_name='installed_parts')
    part = models.ForeignKey(VehiclePart, on_delete=models.CASCADE)

    # Condition
    current_durability = models.IntegerField(default=100)

    # Installation
    installed_at = models.DateTimeField(auto_now_add=True)

    # Quality/condition affects performance
    is_damaged = models.BooleanField(default=False)
    is_broken = models.BooleanField(default=False)

    class Meta:
        app_label = 'game'
        verbose_name = 'Pièce de véhicule installée'
        verbose_name_plural = 'Pièces de véhicules installées'
        unique_together = ('player_vehicle', 'part')

    def __str__(self):
        return f"{self.part.name} on {self.player_vehicle}"

    @property
    def durability_percentage(self):
        """Get durability as percentage"""
        return (self.current_durability / self.part.max_durability) * 100

    @property
    def condition_description(self):
        """Get human-readable condition"""
        if self.is_broken:
            return "Cassé"
        elif self.is_damaged:
            return "Endommagé"
        elif self.durability_percentage > 80:
            return "Excellent"
        elif self.durability_percentage > 60:
            return "Bon"
        elif self.durability_percentage > 40:
            return "Usé"
        elif self.durability_percentage > 20:
            return "Mauvais"
        else:
            return "Critique"


class VehicleMaintenanceLog(models.Model):
    """
    Track maintenance history for vehicles
    """
    MAINTENANCE_TYPES = [
        ('repair', 'Réparation'),
        ('service', 'Entretien'),
        ('part_replacement', 'Remplacement de pièce'),
        ('upgrade', 'Amélioration'),
        ('refuel', 'Ravitaillement'),
    ]

    player_vehicle = models.ForeignKey(PlayerVehicle, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)

    # Details
    description = models.TextField()
    cost = models.IntegerField(default=0, help_text="Cost in money")

    # What was done
    durability_restored = models.IntegerField(default=0)
    fuel_added = models.FloatField(default=0.0)
    parts_replaced = models.ManyToManyField(VehiclePart, blank=True)

    # When
    performed_at = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True)

    class Meta:
        app_label = 'game'
        verbose_name = 'Journal d\'entretien'
        verbose_name_plural = 'Journaux d\'entretien'
        ordering = ['-performed_at']

    def __str__(self):
        return f"{self.get_maintenance_type_display()} - {self.player_vehicle} at {self.performed_at}"


class FuelStation(models.Model):
    """
    Fuel stations on the map
    """
    name = models.CharField(max_length=100)

    # Location
    latitude = models.FloatField()
    longitude = models.FloatField()

    # Fuel availability
    has_petrol = models.BooleanField(default=True)
    has_diesel = models.BooleanField(default=True)
    has_electric = models.BooleanField(default=False)

    # Pricing
    petrol_price_per_liter = models.FloatField(default=1.5)
    diesel_price_per_liter = models.FloatField(default=1.3)
    electric_price_per_kwh = models.FloatField(default=0.3)

    # Stock (optional, for scarcity mechanic)
    petrol_stock = models.FloatField(default=10000.0, help_text="Liters available")
    diesel_stock = models.FloatField(default=10000.0, help_text="Liters available")

    # Status
    is_operational = models.BooleanField(default=True)

    class Meta:
        app_label = 'game'
        verbose_name = 'Station-service'
        verbose_name_plural = 'Stations-service'

    def __str__(self):
        return f"{self.name} at ({self.latitude}, {self.longitude})"


class Garage(models.Model):
    """
    Garages where vehicles can be repaired and upgraded
    """
    name = models.CharField(max_length=100)

    # Location
    latitude = models.FloatField()
    longitude = models.FloatField()

    # Services offered
    can_repair = models.BooleanField(default=True)
    can_upgrade = models.BooleanField(default=True)
    can_paint = models.BooleanField(default=False)
    can_install_parts = models.BooleanField(default=True)

    # Pricing
    repair_cost_per_point = models.FloatField(default=1.0, help_text="Cost per durability point")
    upgrade_cost_multiplier = models.FloatField(default=1.0)

    # Quality
    mechanic_skill_level = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Affects repair quality and available services"
    )

    # Inventory
    has_parts_inventory = models.BooleanField(default=True)

    # Status
    is_operational = models.BooleanField(default=True)

    class Meta:
        app_label = 'game'
        verbose_name = 'Garage'
        verbose_name_plural = 'Garages'

    def __str__(self):
        return f"{self.name} at ({self.latitude}, {self.longitude})"
