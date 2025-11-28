"""
Management command to populate initial quests
"""
from django.core.management.base import BaseCommand
from game.models import Quest, Material, Recipe, Mob
import logging

logger = logging.getLogger(__name__)


def create_quest(name, description, story_text, icon, quest_type, difficulty,
                 required_level, requirements, reward_xp, reward_money,
                 reward_items=None, chain_id=None, chain_order=0,
                 is_daily=False, is_repeatable=False, cooldown_hours=24):
    """Helper to create quest data dict"""
    return {
        'name': name,
        'description': description,
        'story_text': story_text,
        'icon': icon,
        'quest_type': quest_type,
        'difficulty': difficulty,
        'required_level': required_level,
        'chain_id': chain_id,
        'chain_order': chain_order,
        'requirements': requirements,
        'reward_xp': reward_xp,
        'reward_money': reward_money,
        'reward_items': reward_items or [],
        'is_daily': is_daily,
        'is_repeatable': is_repeatable,
        'cooldown_hours': cooldown_hours,
    }


def create_chain_quest(chain_id, order, name, description, story_text,
                       icon, quest_type, difficulty, level, requirements,
                       xp, money, items=None):
    """Helper for chain quests"""
    return create_quest(
        name, description, story_text, icon, quest_type, difficulty, level,
        requirements, xp, money, items, chain_id=chain_id, chain_order=order
    )


def create_daily_quest(name, description, icon, quest_type, requirements, xp, money):
    """Helper for daily quests"""
    return create_quest(
        name, description, f"{description} Chaque jour compte!",
        icon, quest_type, 'easy', 1, requirements, xp, money,
        is_daily=True
    )


class Command(BaseCommand):
    help = 'Populate initial quests for the game'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating initial quests...')

        quests_data = []

        # Get material and recipe IDs
        try:
            bois = Material.objects.get(name='Bois')
            pierre = Material.objects.get(name='Pierre')
            fer = Material.objects.get(name='Minerai de Fer')
            planches = Material.objects.get(name='Planches')
            stick = Material.objects.get(name='Bâton')

            recipe_planches = Recipe.objects.filter(result_material=planches).first()
            recipe_stick = Recipe.objects.filter(result_material=stick).first()

        except (Material.DoesNotExist, Recipe.DoesNotExist) as e:
            self.stdout.write(self.style.ERROR(f'Erreur: Matériaux de base manquants - {e}'))
            return

        # ===== CHAÎNE 1: Le Chemin de l'Artisan =====
        quests_data.extend([
            create_chain_quest(
                'artisan_path', 1, 'Premiers Pas dans ce Monde',
                'Récoltez votre premier matériau pour commencer votre aventure.',
                'Vous vous réveillez dans un monde inconnu. Pour survivre, vous devrez apprendre à récolter des ressources.',
                '🌱', 'gather', 'easy', 1,
                {'gather': [{'material_id': bois.id, 'quantity': 5}]},
                50, 10
            ),
            create_chain_quest(
                'artisan_path', 2, 'Le Forgeron en Formation',
                'Fabriquez vos premiers outils de base.',
                'Maintenant que vous avez des ressources, apprenez à les transformer en outils utiles.',
                '🔨', 'craft', 'easy', 1,
                {'craft': [
                    {'recipe_id': recipe_planches.id, 'quantity': 1} if recipe_planches else {'material_id': planches.id, 'quantity': 4},
                    {'recipe_id': recipe_stick.id, 'quantity': 1} if recipe_stick else {'material_id': stick.id, 'quantity': 4}
                ]},
                100, 25
            ),
            create_chain_quest(
                'artisan_path', 3, 'Collecteur de Ressources',
                'Récoltez différents types de matériaux pour diversifier vos ressources.',
                'Un bon aventurier sait qu\'il faut collecter une variété de ressources.',
                '⛏️', 'gather', 'easy', 2,
                {'gather': [
                    {'material_id': bois.id, 'quantity': 10},
                    {'material_id': pierre.id, 'quantity': 10}
                ]},
                150, 50, [{'material_id': bois.id, 'quantity': 5}]
            ),
            create_chain_quest(
                'artisan_path', 4, 'Le Chasseur de Fer',
                'Récoltez du minerai de fer, une ressource précieuse.',
                'Le fer est essentiel pour fabriquer des outils avancés. Trouvez-en!',
                '⚙️', 'gather', 'medium', 3,
                {'gather': [{'material_id': fer.id, 'quantity': 5}]},
                200, 75, [{'material_id': pierre.id, 'quantity': 10}]
            ),
            create_chain_quest(
                'artisan_path', 5, 'Maître Artisan',
                'Fabriquez 10 objets pour prouver votre maîtrise.',
                'La pratique rend parfait. Montrez que vous êtes devenu un véritable artisan!',
                '🛠️', 'craft', 'medium', 4,
                {},  # Will track total crafts
                500, 200, [
                    {'material_id': bois.id, 'quantity': 20},
                    {'material_id': pierre.id, 'quantity': 20}
                ]
            ),
        ])

        # ===== CHAÎNE 2: L'Explorateur =====
        quests_data.extend([
            create_chain_quest(
                'explorer_path', 1, 'Premiers Pas d\'Explorateur',
                'Visitez 5 nouvelles cellules pour découvrir le monde.',
                'Le monde est vaste et plein de merveilles. Commencez votre exploration!',
                '🗺️', 'explore', 'easy', 1,
                {},  # Will track moves
                75, 30
            ),
            create_chain_quest(
                'explorer_path', 2, 'Voyageur Confirmé',
                'Parcourez 15 nouvelles cellules.',
                'Vous prenez goût à l\'aventure. Continuez d\'explorer!',
                '🧭', 'explore', 'medium', 3,
                {},
                200, 100
            ),
            create_chain_quest(
                'explorer_path', 3, 'Le Grand Voyageur',
                'Parcourez 30 nouvelles cellules pour devenir un explorateur légendaire.',
                'Les véritables aventuriers ne connaissent pas de limites. Parcourez le monde!',
                '🌍', 'explore', 'hard', 5,
                {},
                500, 200
            ),
        ])

        # ===== QUÊTES QUOTIDIENNES =====
        quests_data.extend([
            create_daily_quest(
                'Récolte Quotidienne',
                'Récoltez 20 unités de n\'importe quel matériau.',
                '📦', 'gather', {},
                100, 50
            ),
            create_daily_quest(
                'Fabrication Quotidienne',
                'Fabriquez 5 objets de n\'importe quel type.',
                '⚒️', 'craft', {},
                150, 75
            ),
            create_daily_quest(
                'Exploration Quotidienne',
                'Visitez 10 nouvelles cellules.',
                '🧭', 'explore', {},
                120, 60
            ),
        ])

        # Create quests
        created_count = 0
        updated_count = 0

        for quest_data in quests_data:
            quest, created = Quest.objects.update_or_create(
                name=quest_data['name'],
                defaults=quest_data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  [+] Cree: {quest.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'  [*] Mis a jour: {quest.name}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nTermine! {created_count} quetes creees, {updated_count} mises a jour'
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Total: {Quest.objects.count()} quetes dans la base de donnees'
            )
        )
