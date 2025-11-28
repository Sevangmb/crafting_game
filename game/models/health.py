"""
Advanced health system inspired by SCUM
Tracks body parts, injuries, diseases, and detailed health states
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class BodyPart(models.Model):
    """
    Represents a body part that can be injured
    Similar to SCUM's body part system
    """
    BODY_PART_TYPES = [
        ('head', 'Tête'),
        ('torso', 'Torse'),
        ('left_arm', 'Bras gauche'),
        ('right_arm', 'Bras droit'),
        ('left_leg', 'Jambe gauche'),
        ('right_leg', 'Jambe droite'),
        ('left_hand', 'Main gauche'),
        ('right_hand', 'Main droite'),
        ('left_foot', 'Pied gauche'),
        ('right_foot', 'Pied droit'),
    ]

    name = models.CharField(max_length=50, unique=True)
    body_part_type = models.CharField(max_length=20, choices=BODY_PART_TYPES, unique=True)

    # Importance factor (head/torso are critical)
    critical_multiplier = models.FloatField(
        default=1.0,
        help_text="Damage to this part affects overall health by this multiplier"
    )

    # Bleeding rates
    base_bleeding_rate = models.FloatField(
        default=1.0,
        help_text="How fast this part bleeds when injured"
    )

    # Can this part be broken/fractured?
    can_fracture = models.BooleanField(default=True)

    class Meta:
        app_label = 'game'

    def __str__(self):
        return f"{self.name} ({self.get_body_part_type_display()})"


class PlayerBodyPart(models.Model):
    """
    Tracks the health status of individual body parts for each player
    """
    INJURY_SEVERITY = [
        ('none', 'Aucune'),
        ('minor', 'Mineure'),
        ('moderate', 'Modérée'),
        ('severe', 'Sévère'),
        ('critical', 'Critique'),
    ]

    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='body_parts')
    body_part = models.ForeignKey(BodyPart, on_delete=models.CASCADE)

    # Health of this specific part (0-100)
    health = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Injury states
    is_bleeding = models.BooleanField(default=False)
    bleeding_severity = models.CharField(max_length=20, choices=INJURY_SEVERITY, default='none')
    bleeding_rate = models.FloatField(default=0.0, help_text="HP lost per minute from bleeding")

    is_fractured = models.BooleanField(default=False)
    fracture_severity = models.CharField(max_length=20, choices=INJURY_SEVERITY, default='none')

    is_infected = models.BooleanField(default=False)
    infection_level = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Pain level affects player stats
    pain_level = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pain level (0-100), reduces player effectiveness"
    )

    # Bandaged/treated status
    is_bandaged = models.BooleanField(default=False)
    bandage_quality = models.FloatField(default=0.0, help_text="Quality of bandage (0-100)")
    bandage_applied_at = models.DateTimeField(null=True, blank=True)

    is_splinted = models.BooleanField(default=False)
    splint_applied_at = models.DateTimeField(null=True, blank=True)

    # Bullet/shrapnel embedded
    has_bullet = models.BooleanField(default=False)

    # Last update for decay/healing calculations
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'game'
        unique_together = ('player', 'body_part')

    def __str__(self):
        return f"{self.player.user.username} - {self.body_part.name}: {self.health:.1f}%"

    @property
    def is_healthy(self):
        """Check if body part is in good condition"""
        return (self.health >= 80 and
                not self.is_bleeding and
                not self.is_fractured and
                not self.is_infected and
                self.pain_level < 20)

    @property
    def status_description(self):
        """Get human-readable status"""
        statuses = []

        if self.health < 20:
            statuses.append("Gravement blessé")
        elif self.health < 50:
            statuses.append("Blessé")
        elif self.health < 80:
            statuses.append("Légèrement blessé")

        if self.is_bleeding:
            statuses.append(f"Saignement {self.get_bleeding_severity_display()}")
        if self.is_fractured:
            statuses.append(f"Fracture {self.get_fracture_severity_display()}")
        if self.is_infected:
            statuses.append(f"Infection ({self.infection_level:.0f}%)")
        if self.pain_level > 50:
            statuses.append(f"Douleur intense ({self.pain_level:.0f}%)")
        elif self.pain_level > 20:
            statuses.append(f"Douleur modérée ({self.pain_level:.0f}%)")

        if self.is_bandaged:
            statuses.append("Bandé")
        if self.is_splinted:
            statuses.append("Attelle posée")

        return ", ".join(statuses) if statuses else "Sain"


class PlayerHealthStatus(models.Model):
    """
    Overall health status and vital signs for the player
    Extends the basic Player model with detailed health tracking
    """
    player = models.OneToOneField('Player', on_delete=models.CASCADE, related_name='health_status')

    # Vital signs
    body_temperature = models.FloatField(
        default=37.0,  # Normal body temp in Celsius
        validators=[MinValueValidator(30), MaxValueValidator(43)],
        help_text="Body temperature in °C"
    )

    heart_rate = models.IntegerField(
        default=70,
        validators=[MinValueValidator(30), MaxValueValidator(200)],
        help_text="Beats per minute"
    )

    # Blood system
    blood_volume = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Blood volume percentage (100 = full)"
    )

    # Oxygen and stamina
    oxygen_level = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Blood oxygen saturation %"
    )

    stamina = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Current stamina level"
    )

    # Environmental effects
    is_wet = models.BooleanField(default=False)
    wetness_level = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Temperature conditions
    is_hypothermic = models.BooleanField(default=False)
    is_hyperthermic = models.BooleanField(default=False)

    # Overall condition modifiers
    exhaustion_level = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Exhaustion reduces all stats"
    )

    # Disease and illness
    is_sick = models.BooleanField(default=False)
    sickness_severity = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Immunity and recovery
    immune_strength = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0), MaxValueValidator(150)],
        help_text="Immune system strength affects disease resistance and recovery"
    )

    # Natural regeneration
    health_regen_rate = models.FloatField(
        default=1.0,
        help_text="HP regenerated per hour"
    )

    # Last update timestamp
    last_vital_update = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'game'

    def __str__(self):
        return f"Health Status: {self.player.user.username}"

    @property
    def is_critical_condition(self):
        """Check if player is in critical condition"""
        return (self.blood_volume < 40 or
                self.body_temperature < 34 or
                self.body_temperature > 40 or
                self.oxygen_level < 60)

    @property
    def overall_health_percentage(self):
        """Calculate overall health based on all body parts"""
        body_parts = self.player.body_parts.all()
        if not body_parts:
            return 100.0

        total_weighted_health = 0
        total_weight = 0

        for part in body_parts:
            weight = part.body_part.critical_multiplier
            total_weighted_health += part.health * weight
            total_weight += weight

        if total_weight == 0:
            return 100.0

        return total_weighted_health / total_weight

    @property
    def status_summary(self):
        """Get summary of health status"""
        status = []

        # Temperature
        if self.is_hypothermic:
            status.append("Hypothermie")
        elif self.is_hyperthermic:
            status.append("Hyperthermie")
        elif self.body_temperature < 36:
            status.append("Froid")
        elif self.body_temperature > 38:
            status.append("Fièvre")

        # Blood
        if self.blood_volume < 40:
            status.append("Hémorragie critique")
        elif self.blood_volume < 70:
            status.append("Perte de sang importante")

        # Oxygen
        if self.oxygen_level < 70:
            status.append("Hypoxie")

        # Conditions
        if self.is_sick:
            status.append(f"Malade ({self.sickness_severity:.0f}%)")
        if self.exhaustion_level > 70:
            status.append("Épuisé")
        elif self.exhaustion_level > 40:
            status.append("Fatigué")

        if self.is_wet:
            status.append(f"Mouillé ({self.wetness_level:.0f}%)")

        return ", ".join(status) if status else "Normal"


class Disease(models.Model):
    """
    Diseases that can affect the player
    """
    DISEASE_TYPES = [
        ('infection', 'Infection'),
        ('virus', 'Virus'),
        ('bacterial', 'Bactérienne'),
        ('parasitic', 'Parasitaire'),
        ('food_poisoning', 'Intoxication alimentaire'),
        ('radiation_sickness', 'Mal des rayons'),
        ('common_cold', 'Rhume'),
        ('flu', 'Grippe'),
        ('dysentery', 'Dysenterie'),
        ('cholera', 'Choléra'),
        ('malaria', 'Paludisme'),
    ]

    name = models.CharField(max_length=100, unique=True)
    disease_type = models.CharField(max_length=50, choices=DISEASE_TYPES)
    description = models.TextField()

    # Severity and progression
    base_severity = models.FloatField(
        default=10.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    progression_rate = models.FloatField(
        default=1.0,
        help_text="How fast the disease worsens (per hour)"
    )

    # Effects on player
    health_drain_rate = models.FloatField(default=0.0, help_text="HP lost per hour")
    stamina_penalty = models.FloatField(default=0.0, help_text="% stamina reduction")
    stat_penalty = models.FloatField(default=0.0, help_text="% reduction to all stats")

    # Symptoms
    causes_fever = models.BooleanField(default=False)
    causes_vomiting = models.BooleanField(default=False)
    causes_fatigue = models.BooleanField(default=True)
    causes_pain = models.BooleanField(default=False)

    # Recovery
    natural_recovery_rate = models.FloatField(
        default=1.0,
        help_text="% recovery per hour without treatment"
    )
    requires_medicine = models.BooleanField(default=False)

    # Contagion
    is_contagious = models.BooleanField(default=False)

    class Meta:
        app_label = 'game'

    def __str__(self):
        return f"{self.name} ({self.get_disease_type_display()})"


class PlayerDisease(models.Model):
    """
    Tracks active diseases affecting a player
    """
    player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='diseases')
    disease = models.ForeignKey(Disease, on_delete=models.CASCADE)

    # Progression
    current_severity = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Current disease severity"
    )

    # Treatment
    is_being_treated = models.BooleanField(default=False)
    treatment_effectiveness = models.FloatField(
        default=0.0,
        help_text="How effective current treatment is (0-100%)"
    )

    # Timestamps
    contracted_at = models.DateTimeField(auto_now_add=True)
    last_progression_update = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'game'
        unique_together = ('player', 'disease')

    def __str__(self):
        return f"{self.player.user.username} - {self.disease.name} ({self.current_severity:.0f}%)"

    @property
    def is_active(self):
        """Check if disease is still affecting player"""
        return self.current_severity > 0

    @property
    def stage_description(self):
        """Get disease stage description"""
        if self.current_severity < 20:
            return "Stade précoce"
        elif self.current_severity < 40:
            return "Stade léger"
        elif self.current_severity < 60:
            return "Stade modéré"
        elif self.current_severity < 80:
            return "Stade avancé"
        else:
            return "Stade critique"


class MedicalItem(models.Model):
    """
    Medical items for treating injuries and diseases
    """
    MEDICAL_TYPES = [
        ('bandage', 'Bandage'),
        ('advanced_bandage', 'Bandage avancé'),
        ('splint', 'Attelle'),
        ('painkiller', 'Antidouleur'),
        ('antibiotic', 'Antibiotique'),
        ('antiviral', 'Antiviral'),
        ('antirad', 'Anti-radiation'),
        ('blood_bag', 'Poche de sang'),
        ('saline', 'Solution saline'),
        ('antidote', 'Antidote'),
        ('stimulant', 'Stimulant'),
        ('surgery_kit', 'Kit de chirurgie'),
    ]

    material = models.OneToOneField('Material', on_delete=models.CASCADE, related_name='medical_properties')
    medical_type = models.CharField(max_length=50, choices=MEDICAL_TYPES)

    # Healing properties
    heals_bleeding = models.BooleanField(default=False)
    bleeding_stop_chance = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="% chance to stop bleeding"
    )

    heals_fractures = models.BooleanField(default=False)

    restores_health = models.FloatField(default=0.0, help_text="HP restored instantly")
    restores_blood = models.FloatField(default=0.0, help_text="Blood volume restored")

    # Infection and disease
    cures_infection = models.BooleanField(default=False)
    infection_cure_rate = models.FloatField(default=0.0, help_text="% reduction in infection per use")

    treats_disease = models.BooleanField(default=False)
    disease_cure_rate = models.FloatField(default=0.0, help_text="% reduction in disease severity")

    # Pain management
    reduces_pain = models.BooleanField(default=False)
    pain_reduction = models.FloatField(default=0.0, help_text="Pain level reduced")
    pain_duration = models.IntegerField(default=0, help_text="Duration in minutes")

    # Special effects
    restores_stamina = models.FloatField(default=0.0)
    boosts_immune_system = models.FloatField(default=0.0, help_text="Temporary immune boost %")

    # Usage
    requires_skill = models.BooleanField(default=False)
    required_skill_level = models.IntegerField(default=0)
    use_time_seconds = models.IntegerField(default=5, help_text="Time to apply/use")

    # Can fail
    success_rate = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Base success rate %"
    )

    class Meta:
        app_label = 'game'

    def __str__(self):
        return f"Medical: {self.material.name} ({self.get_medical_type_display()})"
