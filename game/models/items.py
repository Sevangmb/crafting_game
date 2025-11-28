from django.db import models

class Vehicle(models.Model):
    """Vehicles that can be crafted and used for travel"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🚲')
    
    # Stats
    carry_bonus = models.FloatField(default=0.0, help_text="Additional carry capacity in kg")
    speed_bonus = models.IntegerField(default=0, help_text="Speed bonus (reduces travel time/energy)")
    energy_efficiency = models.IntegerField(default=0, help_text="Percentage reduction in move energy cost")
    
    # Durability
    max_durability = models.IntegerField(default=100)
    
    def __str__(self):
        return self.name

class Material(models.Model):
    """Materials that can be found on the map"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary')
    ], default='common')
    category = models.CharField(max_length=50, choices=[
        ('minerais', 'Minerais'),
        ('bois', 'Bois'),
        ('gemmes', 'Gemmes'),
        ('magie', 'Magie'),
        ('nourriture', 'Nourriture'),
        ('divers', 'Divers')
    ], default='divers')
    icon = models.TextField(default='🔹')  # Changed to TextField to support base64 images
    is_food = models.BooleanField(default=False)
    energy_restore = models.IntegerField(default=0)
    
    # Equipment stats
    is_equipment = models.BooleanField(default=False)
    equipment_slot = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('head', 'Head'),
        ('chest', 'Chest'),
        ('legs', 'Legs'),
        ('feet', 'Feet'),
        ('main_hand', 'Main Hand'),
        ('off_hand', 'Off Hand'),
        ('accessory', 'Accessory')
    ])
    defense = models.IntegerField(default=0)
    attack = models.IntegerField(default=0)
    speed_bonus = models.IntegerField(default=0)

    # Survival mechanics (Day R inspired)
    weight = models.FloatField(default=1.0, help_text="Weight in kg")
    max_durability = models.IntegerField(default=0, help_text="0 = infinite durability")
    weight_capacity_bonus = models.FloatField(default=0.0, help_text="Backpack/bag capacity bonus")

    # Food effects
    hunger_restore = models.IntegerField(default=0, help_text="Hunger restored when consumed")
    thirst_restore = models.IntegerField(default=0, help_text="Thirst restored when consumed")
    health_restore = models.IntegerField(default=0, help_text="Health restored when consumed")
    radiation_change = models.IntegerField(default=0, help_text="Radiation change (negative = reduces)")

    def __str__(self):
        return self.name

class Weapon(models.Model):
    """Weapon items, can be used in combat and crafted"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🗡️')
    attack = models.IntegerField(default=0, help_text='Attack power')
    defense = models.IntegerField(default=0, help_text='Defense value')
    weight = models.FloatField(default=0.0, help_text='Weight for encumbrance')
    slot = models.CharField(max_length=20, choices=[
        ('main_hand', 'Main Hand'),
        ('off_hand', 'Off Hand'),
        ('both_hands', 'Both Hands'),
    ], default='main_hand')
    def __str__(self):
        return f"{self.name} ({self.icon})"

class Clothing(models.Model):
    """Clothing items providing defense and capacity bonuses"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='👕')
    defense = models.IntegerField(default=0, help_text='Defense provided')
    weight = models.FloatField(default=0.0, help_text='Weight of the clothing')
    slot = models.CharField(max_length=20, choices=[
        ('head', 'Head'),
        ('chest', 'Chest'),
        ('legs', 'Legs'),
        ('feet', 'Feet'),
        ('accessory', 'Accessory'),
    ])
    def __str__(self):
        return f"{self.name} ({self.icon})"

class DroppedItem(models.Model):
    """Items dropped on the ground by players"""
    cell = models.ForeignKey('game.MapCell', on_delete=models.CASCADE, related_name='dropped_items')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    # Durability info (for tools)
    durability_current = models.IntegerField(default=0)
    durability_max = models.IntegerField(default=0)

    # Track who dropped it and when
    dropped_by = models.ForeignKey('game.Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='items_dropped')
    dropped_at = models.DateTimeField(auto_now_add=True)

    # Optional: Auto-cleanup after certain time
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Item disappears after this time")

    class Meta:
        ordering = ['-dropped_at']

    def __str__(self):
        return f"{self.quantity}x {self.material.name} at ({self.cell.grid_x}, {self.cell.grid_y})"
