from django.core.management.base import BaseCommand
from game.models import Skill, TalentNode

class Command(BaseCommand):
    help = 'Populate default talent tree'

    def handle(self, *args, **options):
        # Get or create crafting skill
        crafting, _ = Skill.objects.get_or_create(code='crafting', defaults={'name': 'Artisanat'})

        # Create talent nodes if they don't exist
        talents_data = [
            {
                'code': 'economy_1',
                'name': 'Économie I',
                'description': '-5% matériaux requis',
                'tier': 1,
                'xp_required': 50,
                'prereq_codes': [],
                'effect_type': 'material_cost_reduction',
                'effect_value': 5
            },
            {
                'code': 'speed_1',
                'name': 'Vitesse I',
                'description': '-10% temps de craft',
                'tier': 2,
                'xp_required': 120,
                'prereq_codes': ['economy_1'],
                'effect_type': 'craft_speed_bonus',
                'effect_value': 10
            },
            {
                'code': 'economy_2',
                'name': 'Économie II',
                'description': '-10% matériaux requis',
                'tier': 3,
                'xp_required': 220,
                'prereq_codes': ['speed_1'],
                'effect_type': 'material_cost_reduction',
                'effect_value': 10
            },
            {
                'code': 'bonus_output_1',
                'name': 'Bonus sortie I',
                'description': '5% de chance d\'obtenir +1',
                'tier': 4,
                'xp_required': 320,
                'prereq_codes': ['economy_2'],
                'effect_type': 'bonus_output_chance',
                'effect_value': 5
            },
            {
                'code': 'economy_3',
                'name': 'Économie III',
                'description': '-15% matériaux requis',
                'tier': 5,
                'xp_required': 500,
                'prereq_codes': ['bonus_output_1'],
                'effect_type': 'material_cost_reduction',
                'effect_value': 15
            },
            {
                'code': 'master_crafter',
                'name': 'Maître Artisan',
                'description': '10% chance de ne pas consommer de matériaux',
                'tier': 6,
                'xp_required': 800,
                'prereq_codes': ['economy_3'],
                'effect_type': 'no_material_consumption_chance',
                'effect_value': 10
            }
        ]

        for talent_data in talents_data:
            TalentNode.objects.update_or_create(
                skill=crafting,
                code=talent_data['code'],
                defaults=talent_data
            )

        # Gathering Skill
        gathering, _ = Skill.objects.get_or_create(code='gathering', defaults={'name': 'Récolte'})
        
        gathering_talents = [
            {
                'code': 'efficient_gather_1',
                'name': 'Récolte Efficace I',
                'description': '-1 coût énergie récolte',
                'tier': 1,
                'xp_required': 50,
                'prereq_codes': [],
                'effect_type': 'gather_cost_reduction',
                'effect_value': 1
            },
            {
                'code': 'abundance_1',
                'name': 'Abondance I',
                'description': '10% chance double récolte',
                'tier': 2,
                'xp_required': 150,
                'prereq_codes': ['efficient_gather_1'],
                'effect_type': 'double_yield_chance',
                'effect_value': 10
            },
            {
                'code': 'keen_eye_1',
                'name': 'Œil de Lynx I',
                'description': 'Augmente qualité objets (bonus)',
                'tier': 3,
                'xp_required': 300,
                'prereq_codes': ['abundance_1'],
                'effect_type': 'quality_bonus_chance',
                'effect_value': 10
            },
            {
                'code': 'master_gatherer',
                'name': 'Maître Récolteur',
                'description': '-1 coût énergie supplémentaire',
                'tier': 4,
                'xp_required': 500,
                'prereq_codes': ['keen_eye_1'],
                'effect_type': 'gather_cost_reduction',
                'effect_value': 1
            },
            {
                'code': 'abundance_2',
                'name': 'Abondance II',
                'description': '20% chance double récolte',
                'tier': 5,
                'xp_required': 800,
                'prereq_codes': ['master_gatherer'],
                'effect_type': 'double_yield_chance',
                'effect_value': 20
            },
            {
                'code': 'legendary_harvest',
                'name': 'Récolte Légendaire',
                'description': '5% chance triple récolte',
                'tier': 6,
                'xp_required': 1200,
                'prereq_codes': ['abundance_2'],
                'effect_type': 'triple_yield_chance',
                'effect_value': 5
            }
        ]

        for t in gathering_talents:
            TalentNode.objects.update_or_create(
                skill=gathering,
                code=t['code'],
                defaults=t
            )

        # Hunting Skill
        hunting, _ = Skill.objects.get_or_create(code='hunting', defaults={'name': 'Chasse'})
        
        hunting_talents = [
            {
                'code': 'tracker_1',
                'name': 'Traqueur I',
                'description': '-1 coût énergie chasse',
                'tier': 1,
                'xp_required': 50,
                'prereq_codes': [],
                'effect_type': 'hunt_cost_reduction',
                'effect_value': 1
            },
            {
                'code': 'precise_shot_1',
                'name': 'Coups Précis I',
                'description': '+2 Dégâts',
                'tier': 2,
                'xp_required': 150,
                'prereq_codes': ['tracker_1'],
                'effect_type': 'damage_bonus',
                'effect_value': 2
            },
            {
                'code': 'expert_skinner_1',
                'name': 'Dépeceur Expert I',
                'description': '10% chance butin supplémentaire',
                'tier': 3,
                'xp_required': 300,
                'prereq_codes': ['precise_shot_1'],
                'effect_type': 'loot_bonus_chance',
                'effect_value': 10
            },
            {
                'code': 'seasoned_hunter',
                'name': 'Chasseur Aguerri',
                'description': '-1 coût énergie supplémentaire',
                'tier': 4,
                'xp_required': 500,
                'prereq_codes': ['expert_skinner_1'],
                'effect_type': 'hunt_cost_reduction',
                'effect_value': 1
            },
            {
                'code': 'precise_shot_2',
                'name': 'Coups Précis II',
                'description': '+5 Dégâts total',
                'tier': 5,
                'xp_required': 800,
                'prereq_codes': ['seasoned_hunter'],
                'effect_type': 'damage_bonus',
                'effect_value': 5
            },
            {
                'code': 'legendary_hunter',
                'name': 'Chasseur Légendaire',
                'description': '20% chance butin rare',
                'tier': 6,
                'xp_required': 1200,
                'prereq_codes': ['precise_shot_2'],
                'effect_type': 'rare_loot_chance',
                'effect_value': 20
            }
        ]

        for t in hunting_talents:
            TalentNode.objects.update_or_create(
                skill=hunting,
                code=t['code'],
                defaults=t
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated talent tree with all tiers')
        )