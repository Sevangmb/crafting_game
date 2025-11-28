from django.db import migrations


def create_initial_skills(apps, schema_editor):
    """Create initial skills for the game"""
    Skill = apps.get_model('game', 'Skill')
    
    skills = [
        {
            'code': 'gathering',
            'name': 'Récolte',
            'description': 'Compétence de récolte de base pour collecter des ressources dans la nature.'
        },
        {
            'code': 'mining',
            'name': 'Minage',
            'description': 'Expertise dans l\'extraction de minéraux et de pierres précieuses.'
        },
        {
            'code': 'woodcutting',
            'name': 'Bûcheronnage',
            'description': 'Maîtrise de la coupe et de la récolte du bois.'
        },
        {
            'code': 'fishing',
            'name': 'Pêche',
            'description': 'Art de la pêche dans les différents points d\'eau.'
        },
        {
            'code': 'crafting',
            'name': 'Artisanat',
            'description': 'Création d\'objets et d\'outils à partir de matériaux bruts.'
        },
        {
            'code': 'cooking',
            'name': 'Cuisine',
            'description': 'Préparation de plats nourrissants et de potions.'
        },
        {
            'code': 'combat',
            'name': 'Combat',
            'description': 'Maîtrise des techniques de combat et de défense.'
        },
        {
            'code': 'magic',
            'name': 'Magie',
            'description': 'Contrôle des forces magiques pour divers effets.'
        },
    ]
    
    for skill_data in skills:
        Skill.objects.get_or_create(
            code=skill_data['code'],
            defaults={
                'name': skill_data['name'],
                'description': skill_data['description']
            }
        )


def create_initial_talents(apps, schema_editor):
    """Create initial talent nodes for each skill"""
    Skill = apps.get_model('game', 'Skill')
    TalentNode = apps.get_model('game', 'TalentNode')
    
    talents = [
        # Gathering
        {
            'skill_code': 'gathering',
            'code': 'efficient_gathering',
            'name': 'Récolte efficace',
            'description': 'Réduit de 5% l\'énergie dépensée lors de la récolte.',
            'tier': 1,
            'xp_required': 100,
            'effect_type': 'energy_cost_reduction',
            'effect_value': 5,
            'params': {'skill': 'gathering'}
        },
        {
            'skill_code': 'gathering',
            'code': 'bountiful_harvest',
            'name': 'Récolte abondante',
            'description': '10% de chance d\'obtenir des ressources supplémentaires lors de la récolte.',
            'tier': 2,
            'xp_required': 250,
            'effect_type': 'bonus_yield_chance',
            'effect_value': 10,
            'prereq_codes': ['efficient_gathering']
        },
        
        # Mining
        {
            'skill_code': 'mining',
            'code': 'efficient_mining',
            'name': 'Minage efficace',
            'description': 'Réduit de 5% l\'énergie dépensée lors du minage.',
            'tier': 1,
            'xp_required': 100,
            'effect_type': 'energy_cost_reduction',
            'effect_value': 5,
            'params': {'skill': 'mining'}
        },
        
        # Woodcutting
        {
            'skill_code': 'woodcutting',
            'code': 'efficient_woodcutting',
            'name': 'Bûcheronnage efficace',
            'description': 'Réduit de 5% l\'énergie dépensée lors du bûcheronnage.',
            'tier': 1,
            'xp_required': 100,
            'effect_type': 'energy_cost_reduction',
            'effect_value': 5,
            'params': {'skill': 'woodcutting'}
        },
        
        # Fishing
        {
            'skill_code': 'fishing',
            'code': 'efficient_fishing',
            'name': 'Pêche efficace',
            'description': 'Réduit de 5% l\'énergie dépensée lors de la pêche.',
            'tier': 1,
            'xp_required': 100,
            'effect_type': 'energy_cost_reduction',
            'effect_value': 5,
            'params': {'skill': 'fishing'}
        },
        
        # Crafting
        {
            'skill_code': 'crafting',
            'code': 'efficient_crafting',
            'name': 'Artisanat efficace',
            'description': 'Réduit de 5% l\'énergie dépensée lors de l\'artisanat.',
            'tier': 1,
            'xp_required': 100,
            'effect_type': 'energy_cost_reduction',
            'effect_value': 5,
            'params': {'skill': 'crafting'}
        },
        {
            'skill_code': 'crafting',
            'code': 'master_crafter',
            'name': 'Maître artisan',
            'description': 'Augmente de 5% les chances de créer un objet de qualité supérieure.',
            'tier': 2,
            'xp_required': 250,
            'effect_type': 'quality_increase_chance',
            'effect_value': 5,
            'prereq_codes': ['efficient_crafting']
        },
    ]
    
    for talent_data in talents:
        try:
            skill = Skill.objects.get(code=talent_data['skill_code'])
            prereq_codes = talent_data.pop('prereq_codes', [])
            
            talent, created = TalentNode.objects.update_or_create(
                code=talent_data['code'],
                defaults={
                    'skill': skill,
                    'name': talent_data['name'],
                    'description': talent_data['description'],
                    'tier': talent_data['tier'],
                    'xp_required': talent_data['xp_required'],
                    'effect_type': talent_data['effect_type'],
                    'effect_value': talent_data['effect_value'],
                    'params': talent_data.get('params', {})
                }
            )
            
            # Set prerequisites if any
            if prereq_codes:
                prereqs = TalentNode.objects.filter(code__in=prereq_codes)
                talent.prereq_codes = [p.code for p in prereqs]
                talent.save()
                
        except Skill.DoesNotExist:
            print(f"Skill {talent_data['skill_code']} not found for talent {talent_data['code']}")


def reverse_func(apps, schema_editor):
    """Reverse the migration"""
    Skill = apps.get_model('game', 'Skill')
    TalentNode = apps.get_model('game', 'TalentNode')
    
    # Delete all talents first to avoid foreign key constraint
    TalentNode.objects.all().delete()
    Skill.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0009_add_initial_game_configs'),
    ]

    operations = [
        migrations.RunPython(create_initial_skills, reverse_func),
        migrations.RunPython(create_initial_talents, reverse_func),
    ]
