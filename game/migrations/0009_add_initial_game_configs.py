from django.db import migrations


def create_initial_configs(apps, schema_editor):
    GameConfig = apps.get_model('game', 'GameConfig')
    
    # Configuration des catégories d'objets
    category_icons = {
        'bois': '🌲',
        'minerais': '⛏️',
        'nourriture': '🍎',
        'gemmes': '💎',
        'magie': '✨',
        'divers': '📦',
        'outils': '🔧',
        'armes': '⚔️',
        'armures': '🛡️',
        'ressources': '📦',
        'consommables': '🧪',
        'quêtes': '📜',
    }

    category_names = {
        'bois': 'Bois',
        'minerais': 'Minerais',
        'nourriture': 'Nourriture',
        'gemmes': 'Gemmes',
        'magie': 'Objets magiques',
        'divers': 'Divers',
        'outils': 'Outils',
        'armes': 'Armes',
        'armures': 'Armures',
        'ressources': 'Ressources',
        'consommables': 'Consommables',
        'quêtes': 'Objets de quête',
    }

    rarity_colors = {
        'common': '#ffffff',
        'uncommon': '#1eff00',
        'rare': '#0070dd',
        'epic': '#a335ee',
        'legendary': '#ff8000',
    }

    rarity_chip_colors = {
        'common': 'default',
        'uncommon': 'success',
        'rare': 'primary',
        'epic': 'secondary',
        'legendary': 'warning',
    }

    biome_config = {
        'plains': {
            'name': 'Plaines',
            'color': '#8bc34a',
            'materials': ['herbe', 'fleurs', 'baies'],
            'discover_xp': 10,
        },
        'forest': {
            'name': 'Forêt',
            'color': '#2e7d32',
            'materials': ['bois', 'champignons', 'baies'],
            'discover_xp': 15,
        },
        'mountain': {
            'name': 'Montagne',
            'color': '#9e9e9e',
            'materials': ['pierre', 'minerai de fer', 'charbon'],
            'discover_xp': 20,
        },
        'water': {
            'name': 'Point d\'eau',
            'color': '#2196f3',
            'materials': ['poisson', 'algues', 'coquillages'],
            'discover_xp': 15,
        },
        'desert': {
            'name': 'Désert',
            'color': '#ffeb3b',
            'materials': ['sable', 'cactus', 'os'],
            'discover_xp': 25,
        },
    }

    tool_requirements = {
        'mining': {
            'name': 'Pioche',
            'required_level': 1,
            'materials': [
                {'name': 'Bois', 'quantity': 2},
                {'name': 'Pierre', 'quantity': 1},
            ],
            'energy_saving': 0.2,  # 20% d'énergie en moins pour la récolte
            'efficiency': 1.2,  # 20% de ressources en plus
        },
        'woodcutting': {
            'name': 'Hache',
            'required_level': 1,
            'materials': [
                {'name': 'Bois', 'quantity': 1},
                {'name': 'Pierre', 'quantity': 1},
            ],
            'energy_saving': 0.15,
            'efficiency': 1.15,
        },
        'fishing': {
            'name': 'Canne à pêche',
            'required_level': 5,
            'materials': [
                {'name': 'Bois', 'quantity': 2},
                {'name': 'Corde', 'quantity': 1},
            ],
            'energy_saving': 0.25,
            'efficiency': 1.3,
        },
    }

    map_config = {
        'grid_size': 1000,  # Taille de la grille en mètres
        'cell_size': 100,   # Taille d'une cellule en mètres
        'discovery_radius': 3,  # Rayon de découverte en cellules
        'regeneration_rate': 0.1,  # 10% de régénération par jour
        'max_resources': 100,  # Quantité maximale de ressources par cellule
        'min_resources': 10,   # Quantité minimale de ressources par cellule
    }

    # Création des configurations
    configs = [
        ('category_icons', category_icons, 'Icônes pour les catégories d\'objets'),
        ('category_names', category_names, 'Noms des catégories d\'objets'),
        ('rarity_colors', rarity_colors, 'Couleurs pour les raretés'),
        ('rarity_chip_colors', rarity_chip_colors, 'Couleurs des puces de rareté'),
        ('biome_config', biome_config, 'Configuration des biomes'),
        ('tool_requirements', tool_requirements, 'Configuration des outils'),
        ('map_config', map_config, 'Configuration de la carte'),
        ('xp_formula', {'base': 100, 'exponent': 1.2, 'multiplier': 1.0}, 'Formule de calcul de l\'XP'),
        ('energy_config', {'base_energy': 100, 'regen_rate': 5, 'regen_interval': 300}, 'Configuration de l\'énergie'),
        ('crafting_config', {'base_success_rate': 0.8, 'critical_fail_chance': 0.05, 'critical_success_chance': 0.05}, 'Configuration du craft'),
    ]

    for key, value, description in configs:
        GameConfig.objects.update_or_create(
            key=key,
            defaults={
                'value': value,
                'description': description,
            }
        )


def reverse_func(apps, schema_editor):
    # Suppression des configurations lors d'un rollback
    GameConfig = apps.get_model('game', 'GameConfig')
    GameConfig.objects.filter(key__in=[
        'category_icons', 'category_names', 'rarity_colors', 'rarity_chip_colors',
        'biome_config', 'tool_requirements', 'map_config', 'xp_formula',
        'energy_config', 'crafting_config'
    ]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0008_gameconfig'),
    ]

    operations = [
        migrations.RunPython(create_initial_configs, reverse_func),
    ]
