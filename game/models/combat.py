from django.db import models

class Mob(models.Model):
    """Animals/Monsters that can be hunted"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🐾')
    
    level = models.IntegerField(default=1)
    health = models.IntegerField(default=20)
    attack = models.IntegerField(default=5)
    defense = models.IntegerField(default=0)
    xp_reward = models.IntegerField(default=10)
    
    # Combat behavior
    spawn_rate = models.FloatField(default=0.3, help_text="Probability of spawning (0.0-1.0)")
    aggression_level = models.CharField(max_length=20, choices=[
        ('passive', 'Passive'),
        ('neutral', 'Neutral'),
        ('aggressive', 'Aggressive'),
    ], default='neutral')
    
    # JSON Strings
    biomes_json = models.TextField(default='[]') # List of biomes e.g. ["plains", "forest"]
    loot_table_json = models.TextField(default='{}') # Dict e.g. {"Viande": {"min": 1, "max": 2, "chance": 1.0}}

    def get_biomes(self):
        import json
        try:
            return json.loads(self.biomes_json)
        except:
            return []

    def get_loot_table(self):
        import json
        try:
            return json.loads(self.loot_table_json)
        except:
            return {}

    def __str__(self):
        return self.name


class CombatLog(models.Model):
    """Log of combat encounters"""
    player = models.ForeignKey('game.Player', on_delete=models.CASCADE, related_name='combat_logs')
    mob = models.ForeignKey(Mob, on_delete=models.CASCADE)
    cell = models.ForeignKey('game.MapCell', on_delete=models.CASCADE)
    
    result = models.CharField(max_length=20, choices=[
        ('victory', 'Victory'),
        ('fled', 'Fled'),
        ('defeated', 'Defeated'),
    ])
    
    damage_dealt = models.IntegerField(default=0)
    damage_taken = models.IntegerField(default=0)
    rounds = models.IntegerField(default=0)
    xp_gained = models.IntegerField(default=0)
    loot_json = models.TextField(default='[]')  # List of items looted
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def get_loot(self):
        import json
        try:
            return json.loads(self.loot_json)
        except:
            return []
    
    def __str__(self):
        return f"{self.player.user.username} vs {self.mob.name} - {self.result}"
