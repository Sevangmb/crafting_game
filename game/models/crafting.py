from django.db import models

class Workstation(models.Model):
    """Crafting workstations"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🔨')

    def __str__(self):
        return self.name

class Recipe(models.Model):
    """Crafting recipes"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    result_material = models.ForeignKey('game.Material', on_delete=models.CASCADE, related_name='crafting_result')
    result_quantity = models.IntegerField(default=1)
    icon = models.CharField(max_length=50, default='⚙️')
    required_workstation = models.ForeignKey(Workstation, on_delete=models.SET_NULL, null=True, blank=True, related_name='recipes')

    def __str__(self):
        return f"{self.name} -> {self.result_material.name}"

class RecipeIngredient(models.Model):
    """Ingredients required for a recipe"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    material = models.ForeignKey('game.Material', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('recipe', 'material')

    def __str__(self):
        return f"{self.material.name} x{self.quantity}"

class CraftingLog(models.Model):
    """Log of player crafting activities"""
    player = models.ForeignKey('game.Player', on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username} crafted {self.recipe.name}"
