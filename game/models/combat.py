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


class RandomEnemy(models.Model):
    """Random human enemies encountered on the map"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='👤')

    # Combat stats
    level = models.IntegerField(default=1)
    health = models.IntegerField(default=30)
    attack = models.IntegerField(default=8)
    defense = models.IntegerField(default=2)
    xp_reward = models.IntegerField(default=15)

    # Behavior
    encounter_rate = models.FloatField(default=0.2, help_text="Probability of encountering (0.0-1.0)")
    aggression_level = models.CharField(max_length=20, choices=[
        ('passive', 'Passif - N\'attaque jamais'),
        ('defensive', 'Défensif - Attaque si provoqué'),
        ('neutral', 'Neutre - Peut attaquer'),
        ('aggressive', 'Agressif - Attaque souvent'),
        ('very_aggressive', 'Très agressif - Attaque toujours'),
    ], default='neutral')

    # Loot
    money_min = models.IntegerField(default=5)
    money_max = models.IntegerField(default=20)

    # JSON fields
    biomes_json = models.TextField(default='[]', help_text='List of biomes where this enemy spawns')
    equipment_json = models.TextField(default='{}', help_text='Equipment carried by enemy')
    inventory_json = models.TextField(default='{}', help_text='Items in enemy inventory')

    # Spawn conditions
    min_level_required = models.IntegerField(default=1, help_text="Player level required to encounter")
    time_of_day = models.CharField(max_length=20, choices=[
        ('any', 'Anytime'),
        ('day', 'Day only'),
        ('night', 'Night only'),
    ], default='any')

    created_at = models.DateTimeField(auto_now_add=True)

    def get_biomes(self):
        import json
        try:
            return json.loads(self.biomes_json)
        except:
            return []

    def get_equipment(self):
        import json
        try:
            return json.loads(self.equipment_json)
        except:
            return {}

    def get_inventory(self):
        import json
        try:
            return json.loads(self.inventory_json)
        except:
            return {}

    def should_attack(self):
        """Determine if enemy attacks on sight based on aggression"""
        import random
        aggression_chances = {
            'passive': 0.0,
            'defensive': 0.1,
            'neutral': 0.4,
            'aggressive': 0.7,
            'very_aggressive': 1.0,
        }
        chance = aggression_chances.get(self.aggression_level, 0.4)
        return random.random() < chance

    def __str__(self):
        return self.name


class Encounter(models.Model):
    """Active encounter between player and enemy"""
    player = models.ForeignKey('game.Player', on_delete=models.CASCADE, related_name='encounters')
    enemy = models.ForeignKey(RandomEnemy, on_delete=models.CASCADE)
    cell = models.ForeignKey('game.MapCell', on_delete=models.CASCADE)

    # Encounter state
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('victory', 'Victory'),
        ('fled', 'Fled'),
        ('defeated', 'Defeated'),
    ], default='active')

    enemy_attacked_first = models.BooleanField(default=False)
    enemy_current_health = models.IntegerField()

    # Combat statistics
    damage_dealt = models.IntegerField(default=0)
    damage_taken = models.IntegerField(default=0)
    rounds = models.IntegerField(default=0)

    # Loot (set when encounter ends)
    loot_json = models.TextField(default='[]', help_text='Items looted from enemy')
    money_looted = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def get_loot(self):
        import json
        try:
            return json.loads(self.loot_json)
        except:
            return []

    def set_loot(self, loot_list):
        import json
        self.loot_json = json.dumps(loot_list)

    def __str__(self):
        return f"{self.player.user.username} vs {self.enemy.name} - {self.status}"
