from django.db import models

class MapCell(models.Model):
    """Grid cell on the map with available materials"""
    grid_x = models.IntegerField()
    grid_y = models.IntegerField()
    center_lat = models.FloatField()
    center_lon = models.FloatField()
    biome = models.CharField(max_length=50, default='plains')  # forest, water, mountain, etc.
    osm_features = models.JSONField(default=list, blank=True)  # Store OSM features data
    location_description = models.TextField(default='Zone inconnue', blank=True)  # Human-readable description
    last_regenerated = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('grid_x', 'grid_y')

    def __str__(self):
        return f"Cell ({self.grid_x}, {self.grid_y})"

class CellMaterial(models.Model):
    """Materials available in a map cell"""
    cell = models.ForeignKey(MapCell, on_delete=models.CASCADE, related_name='materials')
    material = models.ForeignKey('game.Material', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=10)
    max_quantity = models.IntegerField(default=100)

    class Meta:
        unique_together = ('cell', 'material')

    def __str__(self):
        return f"{self.cell} - {self.material.name}: {self.quantity}"

class GatheringLog(models.Model):
    """Log of player gathering activities"""
    player = models.ForeignKey('game.Player', on_delete=models.CASCADE)
    cell = models.ForeignKey(MapCell, on_delete=models.CASCADE)
    material = models.ForeignKey('game.Material', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username} gathered {self.quantity}x {self.material.name}"
