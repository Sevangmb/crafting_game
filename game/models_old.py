from django.db import models
from django.contrib.auth.models import User
import json
from django.core.validators import MinValueValidator

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
    result_material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='crafting_result')
    result_quantity = models.IntegerField(default=1)
    icon = models.CharField(max_length=50, default='⚙️')
    required_workstation = models.ForeignKey(Workstation, on_delete=models.SET_NULL, null=True, blank=True, related_name='recipes')

    def __str__(self):
        return f"{self.name} -> {self.result_material.name}"

class RecipeIngredient(models.Model):
    """Ingredients required for a recipe"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('recipe', 'material')

    def __str__(self):
        return f"{self.material.name} x{self.quantity}"

class Player(models.Model):
    """Player profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_x = models.FloatField(default=4.893)  # Longitude - Valence centre
    current_y = models.FloatField(default=44.933)  # Latitude - Valence centre
    grid_x = models.IntegerField(default=0)  # Grid cell X
    grid_y = models.IntegerField(default=0)  # Grid cell Y
    energy = models.IntegerField(default=100)
    max_energy = models.IntegerField(default=100)
    health = models.IntegerField(default=100)
    max_health = models.IntegerField(default=100)
    
    # Core Stats
    strength = models.IntegerField(default=10)  # Mining, Carry Capacity, Melee Damage
    agility = models.IntegerField(default=10)   # Movement Speed, Dodge, Ranged Damage
    intelligence = models.IntegerField(default=10) # Crafting Speed, Magic, Mana (future)
    luck = models.IntegerField(default=10)      # Drop Rates, Critical Hit Chance

    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)

    # Statistics for achievements
    total_moves = models.IntegerField(default=0)  # Track total movements

    # Energy regeneration tracking
    last_energy_update = models.DateTimeField(null=True, blank=True)

    # Survival Stats (Day R inspired)
    hunger = models.IntegerField(default=100)  # 0-100, decreases over time
    max_hunger = models.IntegerField(default=100)
    thirst = models.IntegerField(default=100)  # 0-100, decreases faster than hunger
    max_thirst = models.IntegerField(default=100)
    radiation = models.IntegerField(default=0)  # 0-100, accumulated in certain biomes

    # Currency system
    money = models.IntegerField(default=0, help_text="Player's cash money (liquide)")
    credit_card_balance = models.IntegerField(default=0, help_text="Player's credit card balance (argent en banque)")

    # Inventory capacity
    max_carry_weight = models.FloatField(default=50.0)  # Base carry capacity, increased by strength

    # Tracking for survival decay
    last_hunger_update = models.DateTimeField(null=True, blank=True)
    last_thirst_update = models.DateTimeField(null=True, blank=True)

    # Vehicle
    current_vehicle = models.ForeignKey('PlayerVehicle', on_delete=models.SET_NULL, null=True, blank=True, related_name='driven_by')

    def get_xp_for_level(self, level):
        """Calculate XP required for a given level using configurable formula"""
        if level <= 1:
            return 0

        # Get XP formula from database or use default
        default_formula = {
            'base': 100,
            'exponent': 1.2,
            'multiplier': 1.0
        }
        formula_config = GameConfig.get_config('xp_formula', default_formula)
        if not isinstance(formula_config, dict):
            formula_config = default_formula

        base = formula_config.get('base', 100)
        exponent = formula_config.get('exponent', 1.2)
        multiplier = formula_config.get('multiplier', 1.0)

        return int(base * ((level - 1) ** exponent) * multiplier)

    @property
    def total_defense(self):
        """Calculate total defense from equipment"""
        defense = 0
        for item in self.equipped_items.all():
            defense += item.material.defense
        return defense

    @property
    def total_attack(self):
        """Calculate total attack from equipment"""
        attack = 0
        for item in self.equipped_items.all():
            attack += item.material.attack
        return attack

    @property
    def total_speed_bonus(self):
        """Calculate total speed bonus from equipment"""
        speed = 0
        for item in self.equipped_items.all():
            speed += item.material.speed_bonus
        return speed

    @property
    def current_carry_weight(self):
        """Calculate current inventory weight"""
        total_weight = 0.0
        for inv_item in self.inventory.all():
            total_weight += inv_item.material.weight * inv_item.quantity
        return round(total_weight, 2)

    @property
    def effective_carry_capacity(self):
        """Calculate effective carry capacity (base + strength bonus + equipment)"""
        base = self.max_carry_weight
        strength_bonus = (self.strength - 10) * 2.0  # +2kg per strength point above 10
        equipment_bonus = sum(item.material.weight_capacity_bonus for item in self.equipped_items.all())
        
        vehicle_bonus = 0.0
        if self.current_vehicle:
            vehicle_bonus = self.current_vehicle.vehicle.carry_bonus
            
        return base + strength_bonus + equipment_bonus + vehicle_bonus

    @property
    def is_overencumbered(self):
        """Check if player is carrying too much"""
        return self.current_carry_weight > self.effective_carry_capacity

    def __str__(self):
        return self.user.username

class PlayerWorkstation(models.Model):
    """Workstations owned by a player"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='workstations')
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('player', 'workstation')

    def __str__(self):
        return f"{self.player.user.username} - {self.workstation.name}: {self.quantity}"

class PlayerVehicle(models.Model):
    """Vehicles owned by a player"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='vehicles')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    durability_current = models.IntegerField(default=100)
    is_equipped = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username}'s {self.vehicle.name}"


class Inventory(models.Model):
    """Player inventory"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='inventory')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    durability_current = models.IntegerField(default=0)
    durability_max = models.IntegerField(default=0)

    class Meta:
        unique_together = ('player', 'material')
        verbose_name_plural = 'Inventories'

    def __str__(self):
        return f"{self.player.user.username} - {self.material.name}: {self.quantity}"

class EquippedItem(models.Model):
    """Items equipped by the player"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='equipped_items')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    slot = models.CharField(max_length=20, choices=[
        ('head', 'Tête'),
        ('chest', 'Torse'),
        ('hands', 'Mains'),
        ('legs', 'Jambes'),
        ('feet', 'Pieds'),
        ('backpack', 'Sac à dos'),
        ('main_hand', 'Main principale'),
        ('off_hand', 'Main secondaire'),
        ('accessory', 'Accessoire')
    ])
    
    class Meta:
        unique_together = ('player', 'slot')

    def __str__(self):
        return f"{self.player.user.username} - {self.slot}: {self.material.name}"

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
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=10)
    max_quantity = models.IntegerField(default=100)

    class Meta:
        unique_together = ('cell', 'material')

    def __str__(self):
        return f"{self.cell} - {self.material.name}: {self.quantity}"

class GatheringLog(models.Model):
    """Log of player gathering activities"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    cell = models.ForeignKey(MapCell, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username} gathered {self.quantity}x {self.material.name}"

class CraftingLog(models.Model):
    """Log of player crafting activities"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.username} crafted {self.recipe.name}"

# --- Skills & Talents ---

class Skill(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name

class PlayerSkill(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    xp = models.IntegerField(default=0)  # current xp towards next level
    xp_to_next = models.IntegerField(default=50)
    total_xp = models.IntegerField(default=0)

    class Meta:
        unique_together = ('player', 'skill')

    def __str__(self):
        return f"{self.player.user.username} - {self.skill.code} L{self.level}"

class TalentNode(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='talents')
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    tier = models.IntegerField(default=1)
    xp_required = models.IntegerField(default=0)  # total_xp required to auto-unlock
    prereq_codes = models.JSONField(default=list, blank=True)
    effect_type = models.CharField(max_length=100)  # e.g., material_cost_reduction, bonus_output_chance
    effect_value = models.IntegerField(default=0)  # percent or flat depending on effect
    params = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('skill', 'code')

    def __str__(self):
        return f"{self.skill.code}:{self.code}"

class PlayerTalent(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='talents')
    talent_node = models.ForeignKey(TalentNode, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'talent_node')

    def __str__(self):
        return f"{self.player.user.username} unlocked {self.talent_node.code}"

# --- Game Configuration ---

class GameConfig(models.Model):
    """Global game configuration settings"""
    key = models.CharField(max_length=100, unique=True, help_text="Configuration key (unique identifier)")
    value = models.TextField(help_text="Configuration value (can be JSON for complex values)")
    description = models.TextField(blank=True, default='', help_text="Description of what this configuration does")
    last_modified = models.DateTimeField(auto_now=True, help_text="Last time this configuration was modified")

    class Meta:
        verbose_name = "Game Configuration"
        verbose_name_plural = "Game Configurations"
        ordering = ['key']

    def get_value(self):
        """Parse JSON value or return string"""
        import json
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value

    def set_value(self, value):
        """Store value as JSON string"""
        import json
        self.value = json.dumps(value)

    @classmethod
    def get_config(cls, key, default=None):
        """Get configuration value with default fallback"""
        try:
            config = cls.objects.get(key=key)
            return config.get_value()
        except cls.DoesNotExist:
            return default

    def save(self, *args, **kwargs):
        """Override save to clear configuration cache"""
        super().save(*args, **kwargs)
        # Clear the configuration cache when a config is updated
        from game.utils.config_helper import clear_config_cache
        clear_config_cache()

    def __str__(self):
        value_preview = str(self.value)[:30]
        if len(str(self.value)) > 30:
            value_preview += "..."
        return f"{self.key} = {value_preview}"

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
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='combat_logs')
    mob = models.ForeignKey(Mob, on_delete=models.CASCADE)
    cell = models.ForeignKey(MapCell, on_delete=models.CASCADE)
    
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


# --- Achievements System ---

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
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    progress = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('player', 'achievement')

    def __str__(self):
        status = "✓" if self.completed else f"{self.progress}/{self.achievement.requirement_value}"
        return f"{self.player.user.username} - {self.achievement.name} ({status})"


# --- Building System ---

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
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
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

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='buildings')
    building_type = models.ForeignKey(BuildingType, on_delete=models.CASCADE)
    cell = models.ForeignKey(MapCell, on_delete=models.CASCADE, related_name='buildings')

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
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='houses')
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



# --- Dropped Items System ---

class DroppedItem(models.Model):
    """Items dropped on the ground by players"""
    cell = models.ForeignKey(MapCell, on_delete=models.CASCADE, related_name='dropped_items')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    # Durability info (for tools)
    durability_current = models.IntegerField(default=0)
    durability_max = models.IntegerField(default=0)

    # Track who dropped it and when
    dropped_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='items_dropped')
    dropped_at = models.DateTimeField(auto_now_add=True)

    # Optional: Auto-cleanup after certain time
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Item disappears after this time")

    class Meta:
        ordering = ['-dropped_at']

    def __str__(self):
        return f"{self.quantity}x {self.material.name} at ({self.cell.grid_x}, {self.cell.grid_y})"


# --- Economy System ---

class Shop(models.Model):
    """Shops where players can buy and sell items"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏪')
    biome = models.CharField(max_length=50, blank=True, null=True, help_text="Shop appears only in this biome (empty = all biomes)")
    
    # Shop settings
    buy_price_multiplier = models.FloatField(default=1.0, help_text="Multiplier for buy prices")
    sell_price_multiplier = models.FloatField(default=0.5, help_text="Multiplier for sell prices (player sells to shop)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class ShopItem(models.Model):
    """Items available in a shop"""
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='items')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    
    # Pricing
    base_buy_price = models.IntegerField(default=10, help_text="Base price for player to buy")
    base_sell_price = models.IntegerField(default=5, help_text="Base price for player to sell to shop")
    
    # Stock management
    stock = models.IntegerField(default=-1, help_text="-1 = unlimited stock")
    max_stock = models.IntegerField(default=-1, help_text="Maximum stock (-1 = no limit)")
    restock_rate = models.IntegerField(default=0, help_text="Items restocked per hour (0 = no restock)")
    last_restock = models.DateTimeField(auto_now_add=True)
    
    # Availability
    available = models.BooleanField(default=True)
    required_level = models.IntegerField(default=1, help_text="Player level required to purchase")
    
    class Meta:
        unique_together = ('shop', 'material')
        ordering = ['material__name']
    
    def __str__(self):
        return f"{self.shop.name} - {self.material.name}"
    
    @property
    def effective_buy_price(self):
        """Calculate effective buy price with shop multiplier"""
        return int(self.base_buy_price * self.shop.buy_price_multiplier)
    
    @property
    def effective_sell_price(self):
        """Calculate effective sell price with shop multiplier"""
        return int(self.base_sell_price * self.shop.sell_price_multiplier)


class Bank(models.Model):
    """Banks where players can deposit and withdraw money"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='🏦')

    # Bank location (appears on cells)
    cell = models.ForeignKey('MapCell', on_delete=models.CASCADE, related_name='banks', null=True, blank=True)

    # Bank fees
    deposit_fee_percent = models.FloatField(default=0.0, help_text="Fee percentage for deposits (0-100)")
    withdrawal_fee_percent = models.FloatField(default=0.0, help_text="Fee percentage for withdrawals (0-100)")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.icon} {self.name}"



class Transaction(models.Model):
    """Record of all money transactions"""
    TRANSACTION_TYPES = [
        ('buy', 'Achat au magasin'),
        ('sell', 'Vente au magasin'),
        ('deposit', 'Dépôt à la banque'),
        ('withdrawal', 'Retrait à la banque'),
        ('reward', 'Récompense'),
        ('quest', 'Quête'),
        ('achievement', 'Succès'),
        ('admin', 'Administrateur'),
        ('other', 'Autre'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField(help_text="Positive = gain, negative = loss")
    balance_after = models.IntegerField(help_text="Player balance after transaction")
    description = models.TextField()
    
    # Optional references
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        sign = "+" if self.amount >= 0 else ""
        return f"{self.player.user.username}: {sign}{self.amount} coins ({self.transaction_type})"


# --- Quest System ---

class Quest(models.Model):
    """Quests/missions that players can complete"""
    QUEST_TYPES = [
        ('gather', 'Récolter'),
        ('craft', 'Fabriquer'),
        ('explore', 'Explorer'),
        ('combat', 'Combat'),
        ('delivery', 'Livraison'),
        ('talk', 'Parler'),
    ]

    QUEST_DIFFICULTIES = [
        ('easy', 'Facile'),
        ('medium', 'Moyen'),
        ('hard', 'Difficile'),
        ('epic', 'Épique'),
    ]

    # Basic info
    name = models.CharField(max_length=200)
    description = models.TextField()
    story_text = models.TextField(blank=True, help_text="Narration / contexte de la quête")
    icon = models.CharField(max_length=50, default='📜')

    # Quest properties
    quest_type = models.CharField(max_length=20, choices=QUEST_TYPES)
    difficulty = models.CharField(max_length=20, choices=QUEST_DIFFICULTIES, default='easy')
    required_level = models.IntegerField(default=1, help_text="Niveau minimum requis")

    # Requirements (stored as JSON for flexibility)
    requirements = models.JSONField(default=dict, help_text="""
    Format: {
        'gather': [{'material_id': 1, 'quantity': 10}],
        'craft': [{'recipe_id': 5, 'quantity': 3}],
        'visit': [{'grid_x': 5, 'grid_y': 10}],
        'defeat': [{'mob_id': 2, 'quantity': 5}]
    }
    """)

    # Rewards
    reward_xp = models.IntegerField(default=0)
    reward_money = models.IntegerField(default=0)
    reward_items = models.JSONField(default=list, help_text="[{'material_id': 1, 'quantity': 5}]")

    # Quest chain
    chain_id = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant de la chaîne de quêtes")
    chain_order = models.IntegerField(default=0, help_text="Position dans la chaîne (0 = quête indépendante)")
    prerequisite_quest = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='next_quests')
    is_repeatable = models.BooleanField(default=False)
    is_daily = models.BooleanField(default=False, help_text="Quête quotidienne qui se reset automatiquement")
    cooldown_hours = models.IntegerField(default=24, help_text="Hours before quest can be repeated")

    # Availability
    is_active = models.BooleanField(default=True)
    start_npc = models.CharField(max_length=100, blank=True, help_text="PNJ qui donne la quête")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['required_level', 'name']

    def __str__(self):
        return f"{self.icon} {self.name} ({self.get_difficulty_display()})"


class PlayerQuest(models.Model):
    """Tracks player progress on quests"""
    QUEST_STATUS = [
        ('available', 'Disponible'),
        ('active', 'En cours'),
        ('completed', 'Terminée'),
        ('failed', 'Échouée'),
        ('abandoned', 'Abandonnée'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='quests')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='player_quests')
    status = models.CharField(max_length=20, choices=QUEST_STATUS, default='available')

    # Progress tracking (stored as JSON)
    progress = models.JSONField(default=dict, help_text="""
    Format: {
        'gather': {'material_1': 5, 'material_2': 10},
        'craft': {'recipe_5': 2},
        'visit': {'5,10': True},
        'defeat': {'mob_2': 3}
    }
    """)

    # Timestamps
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    can_repeat_at = models.DateTimeField(null=True, blank=True, help_text="When quest can be repeated")

    # Stats
    times_completed = models.IntegerField(default=0)

    class Meta:
        unique_together = ('player', 'quest')
        ordering = ['-accepted_at']

    def __str__(self):
        return f"{self.player.user.username} - {self.quest.name} ({self.get_status_display()})"

    def progress_percentage(self):
        """Calculate completion percentage"""
        if not self.quest.requirements:
            return 0

        total_tasks = 0
        completed_tasks = 0

        for task_type, tasks in self.quest.requirements.items():
            for task in tasks:
                total_tasks += 1
                # Check if this task is completed in progress
                if task_type in self.progress:
                    task_key = str(task.get('material_id') or task.get('recipe_id') or task.get('mob_id') or f"{task.get('grid_x')},{task.get('grid_y')}")
                    if task_key in self.progress[task_type]:
                        required = task.get('quantity', 1)
                        current = self.progress[task_type][task_key]
                        if current >= required:
                            completed_tasks += 1

        return int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0


class DynamicEvent(models.Model):
    """Random events that occur on the map"""
    EVENT_TYPES = [
        ('treasure', 'Trésor'),
        ('merchant', 'Marchand ambulant'),
        ('danger', 'Danger'),
        ('resource', 'Ressources abondantes'),
        ('weather', 'Météo'),
    ]

    # Event info
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='✨')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    # Location
    cell = models.ForeignKey(MapCell, on_delete=models.CASCADE, related_name='events')

    # Rewards/Effects (JSON)
    rewards = models.JSONField(default=dict, help_text="""
    {
        'xp': 50,
        'money': 100,
        'items': [{'material_id': 1, 'quantity': 5}],
        'gather_multiplier': 2.0
    }
    """)

    # Duration
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    # Availability
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=-1, help_text="-1 = unlimited")
    participants = models.ManyToManyField(Player, related_name='participated_events', blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.icon} {self.name} at ({self.cell.grid_x}, {self.cell.grid_y})"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def can_participate(self, player):
        if not self.is_active or self.is_expired():
            return False
        if self.max_participants > 0 and self.participants.count() >= self.max_participants:
            return False
        return player not in self.participants.all()


# --- Trading System ---

class TradeOffer(models.Model):
    """Trade offers between players"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
        ('cancelled', 'Annulée'),
        ('completed', 'Complétée'),
        ('expired', 'Expirée'),
    ]

    # Players involved
    from_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='trades_sent')
    to_player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='trades_received')

    # Offer details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    message = models.TextField(blank=True, help_text="Message optionnel")

    # What the initiator offers (JSON)
    offered_items = models.JSONField(default=list, help_text="[{'material_id': 1, 'quantity': 5}]")
    offered_money = models.IntegerField(default=0)

    # What the initiator wants
    requested_items = models.JSONField(default=list, help_text="[{'material_id': 2, 'quantity': 3}]")
    requested_money = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text="Offre expire après ce temps")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Trade: {self.from_player.user.username} → {self.to_player.user.username} ({self.status})"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at and self.status == 'pending'

    def can_accept(self):
        """Check if trade can be accepted"""
        if self.status != 'pending':
            return False, "L'offre n'est plus en attente"
        if self.is_expired():
            return False, "L'offre a expiré"
        return True, None


class Leaderboard(models.Model):
    """Leaderboard entries for various categories"""
    CATEGORY_CHOICES = [
        ('level', 'Niveau'),
        ('wealth', 'Richesse'),
        ('gatherer', 'Récolteur'),
        ('crafter', 'Artisan'),
        ('explorer', 'Explorateur'),
        ('combatant', 'Combattant'),
        ('quests', 'Quêtes'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='leaderboard_entries')
    score = models.BigIntegerField(default=0)
    rank = models.IntegerField(default=0)

    # Additional context (JSON)
    metadata = models.JSONField(default=dict, help_text="""
    {
        'level': 15,
        'total_gathered': 1000,
        'total_crafted': 500,
        etc.
    }
    """)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('category', 'player')
        ordering = ['category', 'rank']
        indexes = [
            models.Index(fields=['category', 'rank']),
        ]

    def __str__(self):
        return f"#{self.rank} {self.player.user.username} - {self.get_category_display()}: {self.score}"

