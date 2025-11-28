from django.db import models

class Achievement(models.Model):
    """Achievements/Trophies that players can unlock"""
    CATEGORY_CHOICES = [
        ('exploration', 'Exploration'),
        ('crafting', 'Crafting'),
        ('gathering', 'Gathering'),
        ('combat', 'Combat'),
        ('progression', 'Progression'),
        ('collection', 'Collection'),
    ]

    REQUIREMENT_TYPE_CHOICES = [
        ('gather_count', 'Gather Count'),
        ('craft_count', 'Craft Count'),
        ('move_count', 'Move Count'),
        ('level_reached', 'Level Reached'),
        ('material_collected', 'Material Collected'),
        ('recipe_crafted', 'Recipe Crafted'),
        ('biome_visited', 'Biome Visited'),
        ('mob_defeated', 'Mob Defeated'),
        ('building_count', 'Building Count'),
        ('building_constructed', 'Building Constructed'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏆')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='progression')
    requirement_type = models.CharField(max_length=30, choices=REQUIREMENT_TYPE_CHOICES)
    requirement_value = models.IntegerField(help_text="Quantity or ID required")
    requirement_target = models.CharField(max_length=100, blank=True, null=True, help_text="Material name, recipe name, etc.")
    reward_xp = models.IntegerField(default=0)
    hidden = models.BooleanField(default=False, help_text="Hidden until unlocked")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.icon} {self.name}"


class PlayerAchievement(models.Model):
    """Tracks player progress towards achievements"""
    player = models.ForeignKey('game.Player', on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('player', 'achievement')

    def __str__(self):
        status = "✓" if self.completed else f"{self.progress}/{self.achievement.requirement_value}"
        return f"{self.player.user.username} - {self.achievement.name} ({status})"
