"""
Survival mechanics service (Realistic life simulation)
Handles hunger, thirst, radiation, and survival effects with realistic metabolism
"""
from django.utils import timezone
from datetime import timedelta
from game.models import Player
from game.exceptions import GameException
from game.utils.config_helper import GameSettings
import math


class SurvivalService:
    """Service for managing player survival stats with realistic mechanics"""

    # Survival level thresholds (more granular)
    HUNGER_LEVELS = {
        'full': (80, 100),        # Rassasié
        'satisfied': (60, 80),    # Satisfait
        'normal': (40, 60),       # Normal
        'hungry': (20, 40),       # Faim
        'very_hungry': (10, 20),  # Très faim
        'starving': (0, 10)       # Famine
    }

    THIRST_LEVELS = {
        'hydrated': (80, 100),    # Bien hydraté
        'satisfied': (60, 80),    # Satisfait
        'normal': (40, 60),       # Normal
        'thirsty': (25, 40),      # Soif
        'very_thirsty': (10, 25), # Très soif
        'dehydrated': (0, 10)     # Déshydraté
    }

    # Activity multipliers for metabolism
    ACTIVITY_MULTIPLIERS = {
        'resting': 0.5,      # Repos
        'walking': 1.0,      # Marche normale
        'running': 1.5,      # Course
        'gathering': 1.3,    # Récolte
        'crafting': 0.8,     # Artisanat
        'combat': 2.0        # Combat
    }

    @staticmethod
    def get_hunger_level(hunger_value):
        """Get descriptive hunger level"""
        for level, (min_val, max_val) in SurvivalService.HUNGER_LEVELS.items():
            if min_val <= hunger_value <= max_val:
                return level
        return 'normal'

    @staticmethod
    def get_thirst_level(thirst_value):
        """Get descriptive thirst level"""
        for level, (min_val, max_val) in SurvivalService.THIRST_LEVELS.items():
            if min_val <= thirst_value <= max_val:
                return level
        return 'normal'

    @staticmethod
    def calculate_decay_rate(current_value, base_rate, activity_multiplier=1.0):
        """
        Calculate realistic decay rate
        Decay accelerates as values get lower (simulating body stress)
        """
        # Base decay
        decay = base_rate * activity_multiplier

        # Accelerate decay when low (body panics)
        if current_value < 30:
            acceleration = 1 + (30 - current_value) / 30  # Up to 2x faster at 0
            decay *= acceleration

        return decay

    @staticmethod
    def update_survival_stats(player, activity='walking'):
        """
        Update player survival stats based on time passed and activity
        More realistic simulation with progressive effects
        """
        now = timezone.now()

        # Calculate time passed
        hunger_minutes = 0
        thirst_minutes = 0

        # Get activity multiplier
        activity_mult = SurvivalService.ACTIVITY_MULTIPLIERS.get(activity, 1.0)

        # Update hunger with realistic decay
        if player.last_hunger_update:
            hunger_minutes = (now - player.last_hunger_update).total_seconds() / 60

            # Realistic hunger decay (slower with satiety)
            base_hunger_rate = GameSettings.survival_hunger_decrease_rate()

            # Satiety slows down hunger
            satiety_factor = max(0.5, player.satiety / 100)

            hunger_decay = SurvivalService.calculate_decay_rate(
                player.hunger,
                base_hunger_rate * satiety_factor,
                activity_mult
            )

            hunger_loss = hunger_decay * hunger_minutes
            player.hunger = max(0, player.hunger - hunger_loss)

            # Satiety decays slower
            satiety_loss = (base_hunger_rate * 0.3) * hunger_minutes
            player.satiety = max(0, player.satiety - satiety_loss)

        player.last_hunger_update = now

        # Update thirst with realistic decay (faster than hunger)
        if player.last_thirst_update:
            thirst_minutes = (now - player.last_thirst_update).total_seconds() / 60

            # Realistic thirst decay
            base_thirst_rate = GameSettings.survival_thirst_decrease_rate()

            # Hydration slows down thirst
            hydration_factor = max(0.5, player.hydration / 100)

            thirst_decay = SurvivalService.calculate_decay_rate(
                player.thirst,
                base_thirst_rate * hydration_factor,
                activity_mult * 1.2  # Thirst affected more by activity
            )

            thirst_loss = thirst_decay * thirst_minutes
            player.thirst = max(0, player.thirst - thirst_loss)

            # Hydration decays slower
            hydration_loss = (base_thirst_rate * 0.4) * thirst_minutes
            player.hydration = max(0, player.hydration - hydration_loss)

        player.last_thirst_update = now

        # Natural radiation decay
        if player.radiation > 0:
            if player.last_energy_update:
                minutes_passed = (now - player.last_energy_update).total_seconds() / 60
                rad_decay = int(GameSettings.survival_radiation_decay_rate() * minutes_passed)
                player.radiation = max(0, player.radiation - rad_decay)

        # Health regeneration (realistic)
        health_regen = SurvivalService.regenerate_health(player, max(hunger_minutes, thirst_minutes))

        # Apply nutrition effects (vitamins/minerals)
        nutrition_effects = {'effects': [], 'health_drain': 0, 'stat_modifiers': {}}
        try:
            from game.services.advanced_nutrition_service import AdvancedNutritionService
            nutrition_effects = AdvancedNutritionService.apply_nutrition_health_effects(
                player, max(hunger_minutes, thirst_minutes)
            )
        except Exception as e:
            import logging
            logging.error(f"Error applying nutrition effects: {e}")

        player.save()

        # Apply survival effects (damage, penalties)
        effects = SurvivalService.apply_survival_effects(player, max(hunger_minutes, thirst_minutes))

        # Combine effects
        all_effects = effects + nutrition_effects['effects']

        return {
            'hunger': player.hunger,
            'thirst': player.thirst,
            'satiety': player.satiety,
            'hydration': player.hydration,
            'radiation': player.radiation,
            'health': player.health,
            'health_regen': health_regen,
            'nutrition_health_drain': nutrition_effects['health_drain'],
            'effects': all_effects,
            'warnings': SurvivalService.get_survival_warnings(player),
            'hunger_level': SurvivalService.get_hunger_level(player.hunger),
            'thirst_level': SurvivalService.get_thirst_level(player.thirst)
        }

    @staticmethod
    def regenerate_health(player, minutes_passed):
        """
        Realistic passive health regeneration
        Only when well-fed AND well-hydrated
        Boosted by good nutrition (vitamins/minerals)
        """
        if player.health >= player.max_health:
            return 0

        hunger_level = SurvivalService.get_hunger_level(player.hunger)
        thirst_level = SurvivalService.get_thirst_level(player.thirst)

        # No regen if hungry or thirsty
        if hunger_level in ['very_hungry', 'starving'] or thirst_level in ['very_thirsty', 'dehydrated']:
            return 0

        # Calculate regen rate based on both stats
        regen_rate = 0

        if hunger_level in ['full', 'satisfied'] and thirst_level in ['hydrated', 'satisfied']:
            # Well fed and hydrated - fast regen
            regen_rate = 2
        elif hunger_level == 'normal' and thirst_level == 'normal':
            # Adequately fed - slow regen
            regen_rate = 0.5
        elif player.hunger >= 40 and player.thirst >= 40:
            # Minimal regen
            regen_rate = 0.2

        # Boost regen with good nutrition
        try:
            from game.models.nutrition import PlayerNutrition
            nutrition_status = PlayerNutrition.objects.filter(player=player).first()
            if nutrition_status:
                # Boost if vitamins/minerals are good
                if nutrition_status.vitamin_c_level >= 80 and nutrition_status.iron_level >= 80:
                    regen_rate *= 1.5  # 50% boost
                elif nutrition_status.vitamin_c_level >= 60 and nutrition_status.iron_level >= 60:
                    regen_rate *= 1.2  # 20% boost
                
                # Apply healing rate modifier
                regen_rate *= nutrition_status.healing_rate
        except Exception:
            pass

        if regen_rate > 0:
            health_gain = regen_rate * minutes_passed
            if health_gain >= 1:
                actual_gain = int(health_gain)
                player.health = min(player.max_health, player.health + actual_gain)
                return actual_gain

        return 0

    @staticmethod
    def get_survival_multipliers(player):
        """
        Realistic stat multipliers based on survival conditions
        Progressive penalties based on hunger/thirst levels
        """
        multipliers = {
            'xp_bonus': 1.0,
            'craft_speed': 1.0,
            'max_energy_mult': 1.0,
            'action_cost_mult': 1.0,
            'movement_speed': 1.0,
            'damage_mult': 1.0,
            'defense_mult': 1.0
        }

        hunger_level = SurvivalService.get_hunger_level(player.hunger)
        thirst_level = SurvivalService.get_thirst_level(player.thirst)

        # Hunger effects (progressive)
        if hunger_level == 'full':
            # Well fed bonus
            multipliers['xp_bonus'] += 0.15
            multipliers['craft_speed'] += 0.1
            multipliers['max_energy_mult'] += 0.1
        elif hunger_level == 'satisfied':
            multipliers['xp_bonus'] += 0.05
        elif hunger_level == 'hungry':
            # Light penalties
            multipliers['max_energy_mult'] -= 0.1
            multipliers['craft_speed'] -= 0.1
        elif hunger_level == 'very_hungry':
            # Moderate penalties
            multipliers['max_energy_mult'] -= 0.25
            multipliers['craft_speed'] -= 0.2
            multipliers['movement_speed'] -= 0.15
            multipliers['damage_mult'] -= 0.1
        elif hunger_level == 'starving':
            # Severe penalties
            multipliers['max_energy_mult'] -= 0.5
            multipliers['craft_speed'] -= 0.4
            multipliers['movement_speed'] -= 0.3
            multipliers['damage_mult'] -= 0.25
            multipliers['action_cost_mult'] += 0.5

        # Thirst effects (more severe than hunger in real life)
        if thirst_level == 'hydrated':
            # Well hydrated bonus
            multipliers['xp_bonus'] += 0.1
            multipliers['max_energy_mult'] += 0.05
        elif thirst_level == 'thirsty':
            # Light penalties
            multipliers['max_energy_mult'] -= 0.15
            multipliers['movement_speed'] -= 0.1
        elif thirst_level == 'very_thirsty':
            # Moderate penalties (confusion, weakness)
            multipliers['max_energy_mult'] -= 0.35
            multipliers['craft_speed'] -= 0.25
            multipliers['movement_speed'] -= 0.25
            multipliers['damage_mult'] -= 0.2
            multipliers['defense_mult'] -= 0.15
        elif thirst_level == 'dehydrated':
            # Critical penalties
            multipliers['max_energy_mult'] -= 0.6
            multipliers['craft_speed'] -= 0.5
            multipliers['movement_speed'] -= 0.4
            multipliers['damage_mult'] -= 0.4
            multipliers['defense_mult'] -= 0.3
            multipliers['action_cost_mult'] += 0.75

        return multipliers

    @staticmethod
    def apply_survival_effects(player, minutes_passed=0):
        """
        Apply realistic negative effects from low survival stats
        Progressive damage only in extreme conditions
        """
        effects_applied = []

        hunger_level = SurvivalService.get_hunger_level(player.hunger)
        thirst_level = SurvivalService.get_thirst_level(player.thirst)

        # Starvation damage (only when starving)
        if hunger_level == 'starving' and minutes_passed > 0:
            # Progressive damage based on how long starving
            damage_rate = 0.5 if player.hunger > 0 else 1.0  # Faster at 0
            damage = max(1, int(damage_rate * minutes_passed))
            player.health = max(0, player.health - damage)
            effects_applied.append(f"Famine: -{damage} santé")

        # Dehydration damage (more severe, starts earlier)
        if thirst_level == 'dehydrated' and minutes_passed > 0:
            # Dehydration is very dangerous
            damage_rate = 1.0 if player.thirst > 5 else 2.0
            damage = max(1, int(damage_rate * minutes_passed))
            player.health = max(0, player.health - damage)
            effects_applied.append(f"Déshydratation: -{damage} santé")

        # Combined starvation + dehydration is deadly
        if hunger_level == 'starving' and thirst_level == 'dehydrated':
            extra_damage = max(1, int(0.5 * minutes_passed))
            player.health = max(0, player.health - extra_damage)
            effects_applied.append(f"Agonie: -{extra_damage} santé")

        # High radiation effects
        if player.radiation > 50:
            # Progressive radiation damage
            rad_threshold = 50
            damage_per_10_rad = int((player.radiation - rad_threshold) / 10)
            if damage_per_10_rad > 0:
                player.health = max(0, player.health - damage_per_10_rad)
                effects_applied.append(f"Radiation: -{damage_per_10_rad} santé")

        if effects_applied:
            player.save()

        return effects_applied

    @staticmethod
    def get_survival_warnings(player):
        """Get realistic warning messages for survival stats"""
        warnings = []

        hunger_level = SurvivalService.get_hunger_level(player.hunger)
        thirst_level = SurvivalService.get_thirst_level(player.thirst)

        # Hunger warnings
        if hunger_level == 'starving':
            warnings.append({
                "type": "danger",
                "message": "💀 FAMINE ! Vous mourez de faim ! Mangez immédiatement !"
            })
        elif hunger_level == 'very_hungry':
            warnings.append({
                "type": "warning",
                "message": "🍖 Très faim ! Vous êtes affaibli, trouvez de la nourriture rapidement !"
            })
        elif hunger_level == 'hungry':
            warnings.append({
                "type": "info",
                "message": "😰 Vous avez faim, pensez à manger bientôt"
            })

        # Thirst warnings (more urgent)
        if thirst_level == 'dehydrated':
            warnings.append({
                "type": "danger",
                "message": "💀 DÉSHYDRATATION CRITIQUE ! Buvez immédiatement ou mourez !"
            })
        elif thirst_level == 'very_thirsty':
            warnings.append({
                "type": "warning",
                "message": "💧 Soif intense ! Vous êtes très affaibli, trouvez de l'eau !"
            })
        elif thirst_level == 'thirsty':
            warnings.append({
                "type": "info",
                "message": "😓 Vous avez soif, hydratez-vous bientôt"
            })

        # Radiation warnings
        if player.radiation > 80:
            warnings.append({
                "type": "danger",
                "message": "☢️ RADIATION MORTELLE ! Quittez cette zone immédiatement !"
            })
        elif player.radiation > 50:
            warnings.append({
                "type": "warning",
                "message": "☢️ Radiation dangereuse ! Trouvez un abri !"
            })

        # Health warnings
        if player.health < 20:
            warnings.append({
                "type": "danger",
                "message": "💔 SANTÉ CRITIQUE ! Vous êtes au bord de la mort !"
            })
        elif player.health < 40:
            warnings.append({
                "type": "warning",
                "message": "❤️ Santé basse, soyez prudent"
            })

        return warnings

    @staticmethod
    def get_survival_status(player):
        """
        Get detailed survival status with realistic descriptions
        """
        statuses = []

        hunger_level = SurvivalService.get_hunger_level(player.hunger)
        thirst_level = SurvivalService.get_thirst_level(player.thirst)

        # Health status
        health_pct = (player.health / player.max_health) * 100 if player.max_health > 0 else 0
        if health_pct >= 90:
            statuses.append({'icon': '💚', 'name': 'Excellente santé', 'type': 'positive', 'description': 'En pleine forme'})
        elif health_pct >= 70:
            statuses.append({'icon': '💚', 'name': 'Bonne santé', 'type': 'positive', 'description': 'Quelques égratignures'})
        elif health_pct >= 50:
            statuses.append({'icon': '💛', 'name': 'Blessé', 'type': 'neutral', 'description': 'Blessures modérées'})
        elif health_pct >= 30:
            statuses.append({'icon': '🧡', 'name': 'Gravement blessé', 'type': 'warning', 'description': 'Blessures sérieuses'})
        else:
            statuses.append({'icon': '❤️', 'name': 'Critique', 'type': 'danger', 'description': 'Au bord de la mort'})

        # Hunger status (realistic descriptions)
        hunger_statuses = {
            'full': {'icon': '🍖', 'name': 'Rassasié', 'type': 'positive', 'description': '+15% XP, +10% vitesse, +10% énergie'},
            'satisfied': {'icon': '😊', 'name': 'Satisfait', 'type': 'positive', 'description': '+5% XP'},
            'normal': {'icon': '🙂', 'name': 'Normal', 'type': 'neutral', 'description': 'Niveau de faim normal'},
            'hungry': {'icon': '😰', 'name': 'Affamé', 'type': 'warning', 'description': '-10% énergie, -10% vitesse craft'},
            'very_hungry': {'icon': '😖', 'name': 'Très faim', 'type': 'warning', 'description': '-25% énergie, -20% craft, -15% vitesse, -10% dégâts'},
            'starving': {'icon': '💀', 'name': 'Famine', 'type': 'danger', 'description': 'Perte de santé ! -50% énergie, -40% craft, -30% vitesse'}
        }
        if hunger_level in hunger_statuses:
            statuses.append(hunger_statuses[hunger_level])

        # Thirst status (realistic descriptions)
        thirst_statuses = {
            'hydrated': {'icon': '💧', 'name': 'Bien hydraté', 'type': 'positive', 'description': '+10% XP, +5% énergie'},
            'satisfied': {'icon': '💧', 'name': 'Hydraté', 'type': 'positive', 'description': 'Hydratation correcte'},
            'normal': {'icon': '💦', 'name': 'Normal', 'type': 'neutral', 'description': 'Niveau de soif normal'},
            'thirsty': {'icon': '😓', 'name': 'Assoiffé', 'type': 'warning', 'description': '-15% énergie, -10% vitesse'},
            'very_thirsty': {'icon': '😵', 'name': 'Très soif', 'type': 'warning', 'description': '-35% énergie, -25% craft, -25% vitesse, -20% dégâts'},
            'dehydrated': {'icon': '💀', 'name': 'Déshydraté', 'type': 'danger', 'description': 'Perte de santé ! -60% énergie, -50% craft, -40% vitesse'}
        }
        if thirst_level in thirst_statuses:
            statuses.append(thirst_statuses[thirst_level])

        # Satiety indicator (new!)
        if player.satiety > 70:
            statuses.append({'icon': '✨', 'name': 'Satiété élevée', 'type': 'positive', 'description': 'La faim revient lentement'})

        # Hydration indicator (new!)
        if player.hydration > 70:
            statuses.append({'icon': '✨', 'name': 'Hydratation élevée', 'type': 'positive', 'description': 'La soif revient lentement'})

        # Radiation status
        if player.radiation > 80:
            statuses.append({'icon': '☢️', 'name': 'Irradié', 'type': 'danger', 'description': 'Radiation mortelle, dégâts importants'})
        elif player.radiation > 50:
            statuses.append({'icon': '☢️', 'name': 'Contaminé', 'type': 'warning', 'description': 'Radiation dangereuse'})
        elif player.radiation > 20:
            statuses.append({'icon': '☢️', 'name': 'Exposé', 'type': 'neutral', 'description': 'Légère contamination'})

        # Health regeneration status
        if player.health < player.max_health:
            if hunger_level in ['full', 'satisfied'] and thirst_level in ['hydrated', 'satisfied']:
                statuses.append({'icon': '💚', 'name': 'Régénération rapide', 'type': 'positive', 'description': '+2 HP/min'})
            elif hunger_level == 'normal' and thirst_level == 'normal':
                statuses.append({'icon': '💚', 'name': 'Régénération lente', 'type': 'positive', 'description': '+0.5 HP/min'})

        return statuses

    @staticmethod
    def consume_food(player, material, quantity=1):
        """
        Realistic food consumption with digestion mechanics
        Food doesn't instantly max out stats
        """
        if not material.is_food:
            raise GameException(f"{material.name} n'est pas consommable")

        now = timezone.now()

        # Calculate restoration (can't exceed max)
        hunger_restored = min(material.hunger_restore * quantity, 100 - player.hunger)
        thirst_restored = min(material.thirst_restore * quantity, 100 - player.thirst)
        energy_restored = min(material.energy_restore * quantity, player.max_energy - player.energy)
        health_restored = min(material.health_restore * quantity, player.max_health - player.health)
        radiation_change = material.radiation_change * quantity

        # Apply immediate effects
        player.hunger = min(100, player.hunger + hunger_restored)
        player.thirst = min(100, player.thirst + thirst_restored)
        player.energy = min(player.max_energy, player.energy + energy_restored)
        player.health = min(player.max_health, player.health + health_restored)

        # Satiety and hydration (longer lasting effects)
        # Eating increases satiety more than hunger
        if hunger_restored > 0:
            satiety_gain = hunger_restored * 1.5  # Satiety lasts longer
            player.satiety = min(100, player.satiety + satiety_gain)
            player.last_meal_time = now

        if thirst_restored > 0:
            hydration_gain = thirst_restored * 1.5
            player.hydration = min(100, player.hydration + hydration_gain)
            player.last_drink_time = now

        # Handle radiation (can be negative to reduce radiation)
        if radiation_change < 0:
            player.radiation = max(0, player.radiation + radiation_change)
        else:
            player.radiation = min(100, player.radiation + radiation_change)

        player.save()

        # Build detailed feedback
        effects = []
        if hunger_restored > 0:
            effects.append(f"+{int(hunger_restored)} faim")
        if thirst_restored > 0:
            effects.append(f"+{int(thirst_restored)} soif")
        if energy_restored > 0:
            effects.append(f"+{int(energy_restored)} énergie")
        if health_restored > 0:
            effects.append(f"+{int(health_restored)} santé")
        if radiation_change < 0:
            effects.append(f"{int(radiation_change)} radiation")
        elif radiation_change > 0:
            effects.append(f"+{int(radiation_change)} radiation ⚠️")

        return {
            'hunger_restored': int(hunger_restored),
            'thirst_restored': int(thirst_restored),
            'energy_restored': int(energy_restored),
            'health_restored': int(health_restored),
            'radiation_change': int(radiation_change),
            'new_hunger': player.hunger,
            'new_thirst': player.thirst,
            'new_satiety': player.satiety,
            'new_hydration': player.hydration,
            'new_energy': player.energy,
            'new_health': player.health,
            'new_radiation': player.radiation,
            'effects_text': ', '.join(effects),
            'hunger_level': SurvivalService.get_hunger_level(player.hunger),
            'thirst_level': SurvivalService.get_thirst_level(player.thirst)
        }

    @staticmethod
    def add_radiation(player, amount):
        """Add radiation to player (from biome or event)"""
        player.radiation = min(100, player.radiation + amount)
        player.save()
        return player.radiation

    @staticmethod
    def check_can_act(player):
        """
        Check if player can perform actions
        More realistic - can act even when very hungry/thirsty (but with penalties)
        """
        if player.health <= 0:
            return False, "💀 Vous êtes mort ! Utilisez /restart pour recommencer"

        # Can't act only if completely starved AND dehydrated
        if player.hunger == 0 and player.thirst == 0:
            return False, "💀 Vous êtes trop affaibli pour agir (mourant de faim et de soif)"

        # Severe warnings but can still act
        hunger_level = SurvivalService.get_hunger_level(player.hunger)
        thirst_level = SurvivalService.get_thirst_level(player.thirst)

        warnings = []
        if hunger_level == 'starving':
            warnings.append("⚠️ Attention : vous mourez de faim")
        if thirst_level == 'dehydrated':
            warnings.append("⚠️ Attention : vous êtes déshydraté")

        if warnings:
            return True, ' | '.join(warnings)

        return True, ""

    @staticmethod
    def get_action_energy_cost(player, base_cost):
        """
        Calculate realistic energy cost based on survival stats
        """
        multipliers = SurvivalService.get_survival_multipliers(player)
        final_cost = base_cost * multipliers['action_cost_mult']
        return int(final_cost)

    @staticmethod
    def adjust_survival_for_environment(player, season, biome, weather, time_of_day):
        """
        Realistic environmental effects on hunger and thirst
        Different conditions affect metabolism
        """
        if not all([season, biome, weather, time_of_day]):
            return

        hunger_loss = 0
        thirst_loss = 0
        radiation_gain = 0
        metabolism_change = 0.0

        biome = biome or ''
        weather = weather or ''
        season = season or ''
        time_of_day = time_of_day or ''

        # Hot/dry environments: increased thirst (realistic)
        hot_biomes = {'desert', 'volcano'}
        if season == 'summer' and biome in hot_biomes:
            thirst_loss += 3
            metabolism_change += 0.1
        if weather in ('clear', 'storm') and biome in hot_biomes:
            thirst_loss += 2

        # Cold environments: increased hunger (body burns calories to stay warm)
        cold_biomes = {'mountain', 'glacier'}
        if season == 'winter' and biome in (cold_biomes | {'plains', 'forest'}):
            hunger_loss += 2
            metabolism_change += 0.1
        if weather in ('snow', 'storm') and biome in cold_biomes:
            hunger_loss += 2

        # Extreme weather increases both
        if weather == 'storm':
            hunger_loss += 1
            thirst_loss += 1
            metabolism_change += 0.05

        # Night requires more calories (body temperature regulation)
        if time_of_day == 'night':
            hunger_loss += 1

        # Slight radiation in harsh/hostile biomes
        if weather == 'storm' and biome in {'volcano', 'glacier', 'urban'}:
            radiation_gain += 1

        # Apply changes
        if hunger_loss > 0:
            player.hunger = max(0, player.hunger - hunger_loss)
        if thirst_loss > 0:
            player.thirst = max(0, player.thirst - thirst_loss)
        if radiation_gain > 0:
            player.radiation = min(100, player.radiation + radiation_gain)
        if metabolism_change != 0:
            player.metabolism_rate = max(0.5, min(2.0, player.metabolism_rate + metabolism_change))

        player.save(update_fields=['hunger', 'thirst', 'radiation', 'metabolism_rate'])

    @staticmethod
    def update_with_activity(player, activity_type='walking', duration_minutes=1):
        """
        Update survival stats based on specific activity
        Different activities consume different amounts
        """
        activity_mult = SurvivalService.ACTIVITY_MULTIPLIERS.get(activity_type, 1.0)

        # Base consumption rates
        hunger_per_min = GameSettings.survival_hunger_decrease_rate() * activity_mult
        thirst_per_min = GameSettings.survival_thirst_decrease_rate() * activity_mult

        # Apply consumption
        hunger_loss = hunger_per_min * duration_minutes * player.metabolism_rate
        thirst_loss = thirst_per_min * duration_minutes * player.metabolism_rate

        player.hunger = max(0, player.hunger - hunger_loss)
        player.thirst = max(0, player.thirst - thirst_loss)

        player.save(update_fields=['hunger', 'thirst'])

        return {
            'hunger_lost': int(hunger_loss),
            'thirst_lost': int(thirst_loss),
            'activity': activity_type,
            'duration': duration_minutes
        }
