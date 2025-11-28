from django.db import models
from django.contrib.auth.models import User
from .config import GameConfig

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

    # Realistic metabolism system (SCUM-inspired)
    satiety = models.FloatField(default=100.0, help_text="Satiety level (0-100), decays slower than hunger")
    hydration = models.FloatField(default=100.0, help_text="Hydration level (0-100), decays slower than thirst")
    last_meal_time = models.DateTimeField(null=True, blank=True, help_text="When player last ate")
    last_drink_time = models.DateTimeField(null=True, blank=True, help_text="When player last drank")
    metabolism_rate = models.FloatField(default=1.0, help_text="Multiplier for hunger/thirst decay (affected by activity)")

    # Advanced metabolism (SCUM-style)
    # Energy storage
    calories_stored = models.FloatField(default=2000.0, help_text="Current caloric energy (kcal)")
    max_calories = models.FloatField(default=3000.0, help_text="Maximum caloric storage")

    # Macronutrients in body
    protein_stored = models.FloatField(default=100.0, help_text="Protein reserves in grams")
    carbs_stored = models.FloatField(default=300.0, help_text="Carbohydrate reserves in grams")
    fat_stored = models.FloatField(default=150.0, help_text="Fat reserves in grams")

    # Water balance
    water_volume = models.FloatField(default=42.0, help_text="Body water in liters (70kg person ~60% water)")
    max_water_volume = models.FloatField(default=45.0, help_text="Maximum healthy water volume")

    # Body composition
    body_weight = models.FloatField(default=70.0, help_text="Body weight in kg")
    muscle_mass = models.FloatField(default=30.0, help_text="Muscle mass in kg")
    body_fat = models.FloatField(default=15.0, help_text="Body fat in kg")

    # Digestion tracking
    stomach_fullness = models.FloatField(default=0.0, help_text="How full stomach is (0-100%)")
    intestine_contents = models.FloatField(default=0.0, help_text="Food in intestines (0-100%)")

    # Metabolism timestamps
    last_metabolism_update = models.DateTimeField(null=True, blank=True)
    last_calorie_burn = models.DateTimeField(null=True, blank=True)

    # Physical condition effects
    is_hungry = models.BooleanField(default=False)
    is_starving = models.BooleanField(default=False)
    is_thirsty = models.BooleanField(default=False)
    is_dehydrated = models.BooleanField(default=False)
    is_overfed = models.BooleanField(default=False)
    is_bloated = models.BooleanField(default=False)

    # Performance modifiers from nutrition state
    energy_regen_modifier = models.FloatField(default=1.0, help_text="Multiplier for energy regeneration")
    stamina_modifier = models.FloatField(default=1.0, help_text="Multiplier for stamina")
    strength_modifier = models.FloatField(default=1.0, help_text="Multiplier for strength")

    # Bowel movements (realistic detail)
    needs_bathroom = models.BooleanField(default=False)
    bladder_fullness = models.FloatField(default=0.0, help_text="0-100%")
    bowel_fullness = models.FloatField(default=0.0, help_text="0-100%")

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

    @property
    def bmi(self):
        """Calculate Body Mass Index"""
        if self.body_weight <= 0:
            return 0
        # Assuming average height of 1.75m
        height_m = 1.75
        return round(self.body_weight / (height_m ** 2), 1)

    @property
    def body_fat_percentage(self):
        """Calculate body fat percentage"""
        if self.body_weight <= 0:
            return 0
        return round((self.body_fat / self.body_weight) * 100, 1)

    @property
    def muscle_percentage(self):
        """Calculate muscle mass percentage"""
        if self.body_weight <= 0:
            return 0
        return round((self.muscle_mass / self.body_weight) * 100, 1)

    @property
    def calorie_percentage(self):
        """Current calories as percentage of max"""
        if self.max_calories <= 0:
            return 0
        return round((self.calories_stored / self.max_calories) * 100, 1)

    @property
    def hydration_percentage(self):
        """Current hydration as percentage"""
        if self.max_water_volume <= 0:
            return 0
        return round((self.water_volume / self.max_water_volume) * 100, 1)

    @property
    def nutrition_status(self):
        """Get overall nutrition status description"""
        if self.is_starving:
            return "Affamé"
        elif self.is_hungry:
            return "Faim"
        elif self.is_overfed:
            return "Trop mangé"
        elif self.calorie_percentage < 30:
            return "Sous-alimenté"
        elif self.calorie_percentage > 90:
            return "Bien nourri"
        else:
            return "Normal"

    @property
    def hydration_status(self):
        """Get hydration status description"""
        if self.is_dehydrated:
            return "Déshydraté"
        elif self.is_thirsty:
            return "Soif"
        elif self.hydration_percentage < 30:
            return "Déshydratation légère"
        elif self.hydration_percentage > 90:
            return "Bien hydraté"
        else:
            return "Normal"

    @property
    def fitness_level(self):
        """Calculate fitness level based on muscle and fat"""
        muscle_pct = self.muscle_percentage
        fat_pct = self.body_fat_percentage

        if muscle_pct > 45 and fat_pct < 12:
            return "Athlétique"
        elif muscle_pct > 40 and fat_pct < 15:
            return "En forme"
        elif muscle_pct > 35 and fat_pct < 20:
            return "Moyen"
        elif fat_pct > 25:
            return "En surpoids"
        else:
            return "Faible"

    def __str__(self):
        return self.user.username

class PlayerWorkstation(models.Model):
    """Workstations owned by a player"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='workstations')
    workstation = models.ForeignKey('game.Workstation', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    class Meta:
        unique_together = ('player', 'workstation')

    def __str__(self):
        return f"{self.player.user.username} - {self.workstation.name}: {self.quantity}"

# PlayerVehicle is now in vehicles.py - this is kept for backwards compatibility
# and will be removed in a future migration


class Inventory(models.Model):
    """Player inventory"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='inventory')
    material = models.ForeignKey('game.Material', on_delete=models.CASCADE)
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
    material = models.ForeignKey('game.Material', on_delete=models.CASCADE)
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

class PlayerSkill(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey('game.Skill', on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    xp = models.IntegerField(default=0)  # current xp towards next level
    xp_to_next = models.IntegerField(default=50)
    total_xp = models.IntegerField(default=0)

    class Meta:
        unique_together = ('player', 'skill')

    def __str__(self):
        return f"{self.player.user.username} - {self.skill.code} L{self.level}"

class PlayerTalent(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='talents')
    talent_node = models.ForeignKey('game.TalentNode', on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player', 'talent_node')

    def __str__(self):
        return f"{self.player.user.username} unlocked {self.talent_node.code}"
