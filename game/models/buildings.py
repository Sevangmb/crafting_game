from django.db import models

class BuildingType(models.Model):
    """Types of buildings that can be constructed"""
    CATEGORY_CHOICES = [
        ('housing', 'Housing'),
        ('production', 'Production'),
        ('storage', 'Storage'),
        ('defense', 'Defense'),
        ('decoration', 'Decoration'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏠')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='housing')

    # Building benefits
    energy_regeneration_bonus = models.IntegerField(default=0, help_text="Energy regen per hour")
    storage_bonus = models.IntegerField(default=0, help_text="Additional storage slots")
    defense_bonus = models.IntegerField(default=0, help_text="Defense against attacks")
    production_bonus = models.FloatField(default=0.0, help_text="% boost to crafting/gathering")

    # Construction requirements
    construction_time = models.IntegerField(default=60, help_text="Time in seconds to build")
    required_level = models.IntegerField(default=1, help_text="Player level required")

    def __str__(self):
        return f"{self.icon} {self.name}"


class BuildingRecipe(models.Model):
    """Materials required to construct a building"""
    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE, related_name='recipe_materials')
    material = models.ForeignKey('game.Material', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('building_type', 'material')

    def __str__(self):
        return f"{self.building_type.name} requires {self.quantity}x {self.material.name}"


class Building(models.Model):
    """Buildings constructed by players on map cells"""
    STATUS_CHOICES = [
        ('under_construction', 'Under Construction'),
        ('completed', 'Completed'),
        ('damaged', 'Damaged'),
        ('destroyed', 'Destroyed'),
    ]

    player = models.ForeignKey('game.Player', on_delete=models.CASCADE, related_name='buildings')
    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE)
    cell = models.ForeignKey('game.MapCell', on_delete=models.CASCADE, related_name='buildings')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='under_construction')
    health = models.IntegerField(default=100)
    max_health = models.IntegerField(default=100)

    construction_started_at = models.DateTimeField(auto_now_add=True)
    construction_completed_at = models.DateTimeField(null=True, blank=True)

    # Track construction progress
    construction_progress = models.IntegerField(default=0, help_text="Percentage completed")

    class Meta:
        ordering = ['-construction_started_at']

    def __str__(self):
        return f"{self.player.user.username}'s {self.building_type.name} at ({self.cell.grid_x}, {self.cell.grid_y})"

class House(models.Model):
    player = models.ForeignKey('game.Player', on_delete=models.CASCADE, related_name='houses')
    grid_x = models.IntegerField()
    grid_y = models.IntegerField()
    level = models.IntegerField(default=1)
    material_requirements = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'grid_x', 'grid_y')

    def __str__(self):
        return f"{self.player.user.username}'s house at ({self.grid_x}, {self.grid_y})"
