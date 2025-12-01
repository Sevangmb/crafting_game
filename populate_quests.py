"""
Script to populate the database with initial quests
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crafting_game.settings')
django.setup()

from game.models import Quest, Material, Mob, Recipe

def create_quests():
    """Create initial quests for the game"""

    # Get some materials and mobs for quest requirements
    try:
        wood = Material.objects.get(name="Bois")
        stone = Material.objects.get(name="Pierre")
        iron_ore = Material.objects.get(name__icontains="Minerai de fer")
    except Material.DoesNotExist:
        print("⚠️  Materials not found. Please populate materials first.")
        return

    # Try to get a mob for combat quests
    try:
        deer = Mob.objects.filter(name__icontains="Cerf").first()
        if not deer:
            deer = Mob.objects.first()
    except:
        deer = None

    quests_data = [
        # ============= TUTORIAL / STARTER QUESTS =============
        {
            'name': '🌱 Premiers Pas',
            'description': 'Bienvenue dans le monde ! Récoltez quelques ressources de base pour commencer votre aventure.',
            'story_text': 'Vous venez de vous réveiller dans ce monde inconnu. Il est temps de rassembler des ressources pour survivre.',
            'icon': '🌱',
            'quest_type': 'gather',
            'difficulty': 'easy',
            'required_level': 1,
            'requirements': {
                'gather': [
                    {'material_id': wood.id, 'quantity': 10},
                    {'material_id': stone.id, 'quantity': 5}
                ]
            },
            'reward_xp': 50,
            'reward_money': 10,
            'reward_items': [],
            'chain_id': 'tutorial',
            'chain_order': 1,
        },
        {
            'name': '🔨 L\'Artisanat de Base',
            'description': 'Apprenez l\'artisanat en créant vos premiers outils.',
            'story_text': 'Avec les ressources que vous avez récoltées, vous pouvez maintenant créer vos premiers outils.',
            'icon': '🔨',
            'quest_type': 'craft',
            'difficulty': 'easy',
            'required_level': 1,
            'requirements': {
                'craft': [
                    {'recipe_id': 1, 'quantity': 1}  # Adjust recipe_id based on your recipes
                ]
            },
            'reward_xp': 75,
            'reward_money': 15,
            'reward_items': [
                {'material_id': wood.id, 'quantity': 5}
            ],
            'chain_id': 'tutorial',
            'chain_order': 2,
        },

        # ============= EXPLORATION QUESTS =============
        {
            'name': '🗺️ Explorateur Novice',
            'description': 'Explorez les environs et visitez 5 nouvelles zones.',
            'story_text': 'Le monde est vaste et plein de merveilles. Partez à la découverte !',
            'icon': '🗺️',
            'quest_type': 'explore',
            'difficulty': 'easy',
            'required_level': 2,
            'requirements': {
                'visit': [
                    {'grid_x': 1, 'grid_y': 1},
                    {'grid_x': 2, 'grid_y': 2},
                    {'grid_x': 3, 'grid_y': 3},
                    {'grid_x': 4, 'grid_y': 4},
                    {'grid_x': 5, 'grid_y': 5}
                ]
            },
            'reward_xp': 100,
            'reward_money': 25,
            'reward_items': [],
            'chain_id': None,
            'chain_order': 0,
        },

        # ============= GATHERING QUESTS =============
        {
            'name': '🪵 Récolte de Bois',
            'description': 'Récoltez 50 unités de bois pour construire des structures.',
            'story_text': 'Le bois est la ressource la plus importante pour la construction. Vous en aurez besoin en grande quantité.',
            'icon': '🪵',
            'quest_type': 'gather',
            'difficulty': 'easy',
            'required_level': 2,
            'requirements': {
                'gather': [
                    {'material_id': wood.id, 'quantity': 50}
                ]
            },
            'reward_xp': 80,
            'reward_money': 20,
            'reward_items': [],
            'chain_id': None,
            'chain_order': 0,
            'is_repeatable': True,
            'is_daily': True,
            'cooldown_hours': 24,
        },
        {
            'name': '⛏️ Mineur Débutant',
            'description': 'Récoltez 30 unités de pierre et 10 de minerai de fer.',
            'story_text': 'Les minerais sont essentiels pour créer des outils et équipements avancés.',
            'icon': '⛏️',
            'quest_type': 'gather',
            'difficulty': 'medium',
            'required_level': 3,
            'requirements': {
                'gather': [
                    {'material_id': stone.id, 'quantity': 30},
                    {'material_id': iron_ore.id, 'quantity': 10}
                ]
            },
            'reward_xp': 150,
            'reward_money': 40,
            'reward_items': [],
            'chain_id': 'mining',
            'chain_order': 1,
        },

        # ============= COMBAT QUESTS =============
        {
            'name': '⚔️ Premier Sang',
            'description': 'Chassez votre premier animal sauvage.',
            'story_text': 'La chasse est dangereuse mais nécessaire pour survivre. Prouvez votre valeur.',
            'icon': '⚔️',
            'quest_type': 'combat',
            'difficulty': 'easy',
            'required_level': 3,
            'requirements': {
                'defeat': [
                    {'mob_id': deer.id if deer else 1, 'quantity': 1}
                ]
            },
            'reward_xp': 100,
            'reward_money': 30,
            'reward_items': [],
            'chain_id': 'combat',
            'chain_order': 1,
        },
        {
            'name': '🏹 Chasseur Expérimenté',
            'description': 'Chassez 10 animaux pour prouver vos compétences.',
            'story_text': 'Vous commencez à maîtriser l\'art de la chasse. Continuez à vous perfectionner.',
            'icon': '🏹',
            'quest_type': 'combat',
            'difficulty': 'medium',
            'required_level': 5,
            'requirements': {
                'defeat': [
                    {'mob_id': deer.id if deer else 1, 'quantity': 10}
                ]
            },
            'reward_xp': 250,
            'reward_money': 75,
            'reward_items': [],
            'chain_id': 'combat',
            'chain_order': 2,
            'is_repeatable': True,
            'cooldown_hours': 48,
        },

        # ============= CRAFTING QUESTS =============
        {
            'name': '🛠️ Artisan en Herbe',
            'description': 'Créez 5 objets différents pour développer vos compétences.',
            'story_text': 'L\'artisanat est un art qui demande de la pratique. Créez divers objets pour progresser.',
            'icon': '🛠️',
            'quest_type': 'craft',
            'difficulty': 'medium',
            'required_level': 4,
            'requirements': {
                'craft': [
                    {'recipe_id': 1, 'quantity': 5}  # Adjust based on your recipes
                ]
            },
            'reward_xp': 200,
            'reward_money': 50,
            'reward_items': [
                {'material_id': iron_ore.id, 'quantity': 5}
            ],
            'chain_id': 'crafting',
            'chain_order': 1,
        },

        # ============= ADVANCED QUESTS =============
        {
            'name': '💎 Chercheur de Trésors',
            'description': 'Trouvez des ressources rares dans différents biomes.',
            'story_text': 'Les trésors les plus précieux sont cachés dans les endroits les plus dangereux.',
            'icon': '💎',
            'quest_type': 'gather',
            'difficulty': 'hard',
            'required_level': 8,
            'requirements': {
                'gather': [
                    {'material_id': iron_ore.id, 'quantity': 25}
                ]
            },
            'reward_xp': 500,
            'reward_money': 150,
            'reward_items': [],
            'chain_id': None,
            'chain_order': 0,
        },
        {
            'name': '🌟 Maître Artisan',
            'description': 'Atteignez le sommet de l\'artisanat en créant des objets légendaires.',
            'story_text': 'Seuls les artisans les plus talentueux peuvent créer des objets de cette qualité.',
            'icon': '🌟',
            'quest_type': 'craft',
            'difficulty': 'epic',
            'required_level': 15,
            'requirements': {
                'craft': [
                    {'recipe_id': 1, 'quantity': 10}  # Adjust for legendary recipes
                ]
            },
            'reward_xp': 1000,
            'reward_money': 500,
            'reward_items': [
                {'material_id': wood.id, 'quantity': 100},
                {'material_id': stone.id, 'quantity': 50}
            ],
            'chain_id': 'crafting',
            'chain_order': 5,
        },
    ]

    created_count = 0
    updated_count = 0

    for quest_data in quests_data:
        quest, created = Quest.objects.update_or_create(
            name=quest_data['name'],
            defaults=quest_data
        )

        if created:
            created_count += 1
            print(f"✅ Created quest: {quest.name}")
        else:
            updated_count += 1
            print(f"🔄 Updated quest: {quest.name}")

    # Set up quest chain prerequisites
    print("\n📊 Setting up quest chain prerequisites...")

    # Tutorial chain
    tutorial_quests = Quest.objects.filter(chain_id='tutorial').order_by('chain_order')
    for i, quest in enumerate(tutorial_quests):
        if i > 0:
            quest.prerequisite_quest = tutorial_quests[i-1]
            quest.save()
            print(f"  ⛓️  {quest.name} -> requires {tutorial_quests[i-1].name}")

    # Mining chain
    mining_quests = Quest.objects.filter(chain_id='mining').order_by('chain_order')
    for i, quest in enumerate(mining_quests):
        if i > 0:
            quest.prerequisite_quest = mining_quests[i-1]
            quest.save()
            print(f"  ⛓️  {quest.name} -> requires {mining_quests[i-1].name}")

    # Combat chain
    combat_quests = Quest.objects.filter(chain_id='combat').order_by('chain_order')
    for i, quest in enumerate(combat_quests):
        if i > 0:
            quest.prerequisite_quest = combat_quests[i-1]
            quest.save()
            print(f"  ⛓️  {quest.name} -> requires {combat_quests[i-1].name}")

    # Crafting chain
    crafting_quests = Quest.objects.filter(chain_id='crafting').order_by('chain_order')
    for i, quest in enumerate(crafting_quests):
        if i > 0:
            quest.prerequisite_quest = crafting_quests[i-1]
            quest.save()
            print(f"  ⛓️  {quest.name} -> requires {crafting_quests[i-1].name}")

    print(f"\n{'='*60}")
    print(f"✨ Quest population complete!")
    print(f"   📝 Created: {created_count} quests")
    print(f"   🔄 Updated: {updated_count} quests")
    print(f"   📊 Total: {Quest.objects.count()} quests in database")
    print(f"{'='*60}")

if __name__ == '__main__':
    print("🚀 Starting quest population...\n")
    create_quests()
    print("\n✅ Done!")
