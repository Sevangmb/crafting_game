"""
Management command to populate game configurations in database
"""
from django.core.management.base import BaseCommand
from game.models import GameConfig


class Command(BaseCommand):
    help = 'Populate game configurations in database'

    def handle(self, *args, **options):
        configs = [
            # Energy configs
            {
                'key': 'energy_base_regen_per_minute',
                'value': '1',
                'description': 'Base energy regeneration per minute'
            },
            {
                'key': 'energy_move_cost',
                'value': '1',
                'description': 'Energy cost for moving one cell'
            },
            {
                'key': 'energy_gather_cost',
                'value': '5',
                'description': 'Energy cost for gathering materials'
            },
            {
                'key': 'energy_combat_base_cost',
                'value': '5',
                'description': 'Base energy cost for combat'
            },

            # Movement configs
            {
                'key': 'movement_grid_offset',
                'value': '0.0009',
                'description': 'Latitude/longitude offset per grid cell (~100m)'
            },
            {
                'key': 'movement_agility_reduction_factor',
                'value': '0.01',
                'description': 'Energy cost reduction per point of agility'
            },
            {
                'key': 'movement_speed_bonus_factor',
                'value': '0.005',
                'description': 'Energy cost reduction per speed bonus point'
            },

            # Combat configs
            {
                'key': 'combat_flee_base_chance',
                'value': '0.5',
                'description': 'Base chance to flee from combat (50%)'
            },
            {
                'key': 'combat_flee_agility_bonus',
                'value': '0.01',
                'description': 'Flee chance increase per agility point (1%)'
            },
            {
                'key': 'combat_perfect_victory_xp_bonus',
                'value': '50',
                'description': 'Bonus XP for perfect victory (no damage taken)'
            },
            {
                'key': 'combat_quick_victory_xp_bonus',
                'value': '25',
                'description': 'Bonus XP for quick victory (≤3 rounds)'
            },
            {
                'key': 'combat_level_up_health_bonus',
                'value': '10',
                'description': 'Max health increase per level up'
            },
            {
                'key': 'combat_level_5_stat_bonus',
                'value': '2',
                'description': 'Stat points gained every 5 levels (str/agi/int)'
            },
            {
                'key': 'combat_level_5_luck_bonus',
                'value': '1',
                'description': 'Luck points gained every 5 levels'
            },
            {
                'key': 'combat_death_health_restore',
                'value': '1',
                'description': 'Health restored after death'
            },

            # Crafting configs
            {
                'key': 'crafting_base_xp_gain',
                'value': '8',
                'description': 'Base XP gained from crafting'
            },
            {
                'key': 'crafting_xp_per_item',
                'value': '10',
                'description': 'Crafting XP per item crafted'
            },

            # Gathering configs
            {
                'key': 'gathering_xp_multiplier',
                'value': '2',
                'description': 'XP = quantity * multiplier when gathering'
            },
            {
                'key': 'gathering_min_amount',
                'value': '1',
                'description': 'Minimum materials gathered per action'
            },
            {
                'key': 'gathering_max_amount',
                'value': '5',
                'description': 'Maximum materials gathered per action'
            },

            # Biome environment multipliers
            {
                'key': 'biome_bonus_forest_wood',
                'value': '1.10',
                'description': 'Wood gathering bonus in forest biome (10%)'
            },
            {
                'key': 'biome_bonus_forest_branches',
                'value': '1.25',
                'description': 'Branches gathering bonus in forest biome (25%)'
            },
            {
                'key': 'biome_bonus_mountain_stone',
                'value': '1.05',
                'description': 'Stone gathering bonus in mountain biome (5%)'
            },
            {
                'key': 'biome_bonus_mountain_iron',
                'value': '1.15',
                'description': 'Iron gathering bonus in mountain biome (15%)'
            },
            {
                'key': 'biome_bonus_mountain_coal',
                'value': '1.20',
                'description': 'Coal gathering bonus in mountain biome (20%)'
            },
            {
                'key': 'biome_bonus_mountain_diamond',
                'value': '1.30',
                'description': 'Diamond gathering bonus in mountain biome (30%)'
            },
            {
                'key': 'biome_bonus_water_fish',
                'value': '1.10',
                'description': 'Fish gathering bonus in water biome (10%)'
            },
            {
                'key': 'biome_bonus_water_algae',
                'value': '1.10',
                'description': 'Algae gathering bonus in water biome (10%)'
            },

            # Material quantity ranges by rarity
            {
                'key': 'material_qty_legendary_min',
                'value': '1',
                'description': 'Minimum quantity for legendary materials'
            },
            {
                'key': 'material_qty_legendary_max',
                'value': '5',
                'description': 'Maximum quantity for legendary materials'
            },
            {
                'key': 'material_qty_rare_min',
                'value': '5',
                'description': 'Minimum quantity for rare materials'
            },
            {
                'key': 'material_qty_rare_max',
                'value': '15',
                'description': 'Maximum quantity for rare materials'
            },
            {
                'key': 'material_qty_uncommon_min',
                'value': '10',
                'description': 'Minimum quantity for uncommon materials'
            },
            {
                'key': 'material_qty_uncommon_max',
                'value': '30',
                'description': 'Maximum quantity for uncommon materials'
            },
            {
                'key': 'material_qty_common_min',
                'value': '15',
                'description': 'Minimum quantity for common materials'
            },
            {
                'key': 'material_qty_common_max',
                'value': '50',
                'description': 'Maximum quantity for common materials'
            },

            # Player starting values
            {
                'key': 'player_start_energy',
                'value': '100',
                'description': 'Starting energy for new players'
            },
            {
                'key': 'player_start_health',
                'value': '100',
                'description': 'Starting health for new players'
            },
            {
                'key': 'player_start_lat',
                'value': '44.933',
                'description': 'Starting latitude (Valence center)'
            },
            {
                'key': 'player_start_lon',
                'value': '4.893',
                'description': 'Starting longitude (Valence center)'
            },
            {
                'key': 'player_start_strength',
                'value': '10',
                'description': 'Starting strength stat'
            },
            {
                'key': 'player_start_agility',
                'value': '10',
                'description': 'Starting agility stat'
            },
            {
                'key': 'player_start_intelligence',
                'value': '10',
                'description': 'Starting intelligence stat'
            },
            {
                'key': 'player_start_luck',
                'value': '5',
                'description': 'Starting luck stat'
            },

            # Survival system
            {
                'key': 'survival_hunger_decrease_rate',
                'value': '1',
                'description': 'Hunger decrease per minute'
            },
            {
                'key': 'survival_thirst_decrease_rate',
                'value': '1.5',
                'description': 'Thirst decrease per minute'
            },
            {
                'key': 'survival_radiation_decay_rate',
                'value': '0.5',
                'description': 'Radiation decay per minute in safe zones'
            },
        ]

        created_count = 0
        updated_count = 0

        for config_data in configs:
            config, created = GameConfig.objects.get_or_create(
                key=config_data['key'],
                defaults={
                    'value': config_data['value'],
                    'description': config_data['description']
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Created config: {config_data['key']}")
                )
            else:
                # Update description if it changed
                if config.description != config_data['description']:
                    config.description = config_data['description']
                    config.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"Updated description: {config_data['key']}")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully populated {created_count} new configs, '
                f'updated {updated_count} descriptions'
            )
        )
