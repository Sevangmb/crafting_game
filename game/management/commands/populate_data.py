# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from game.models import Material, Recipe, RecipeIngredient, Workstation, Skill, TalentNode, GameConfig, Vehicle
from django.db import transaction
import json

class Command(BaseCommand):
    help = 'Populate the database with initial materials and recipes'

    def handle(self, *args, **options):
        self.stdout.write('Création des matériaux...')

        # Create basic materials
        wood = Material.objects.get_or_create(
            name='Bois',
            defaults={'description': 'Bûches de bois provenant des arbres', 'rarity': 'common', 'icon': '🪵'}
        )[0]

        stone = Material.objects.get_or_create(
            name='Pierre',
            defaults={'description': 'Roches dures trouvées dans les montagnes', 'rarity': 'common', 'icon': '🪨'}
        )[0]

        iron_ore = Material.objects.get_or_create(
            name='Minerai de Fer',
            defaults={'description': 'Fer brut extrait de la terre', 'rarity': 'uncommon', 'icon': '⛏️'}
        )[0]

        coal = Material.objects.get_or_create(
            name='Charbon',
            defaults={'description': 'Roches noires combustibles', 'rarity': 'common', 'icon': '🪨'}
        )[0]

        gold_ore = Material.objects.get_or_create(
            name='Minerai d\'Or',
            defaults={'description': 'Minerai d\'or précieux', 'rarity': 'rare', 'icon': '✨'}
        )[0]

        diamond = Material.objects.get_or_create(
            name='Diamant',
            defaults={'description': 'Gemmes extrêmement rares et précieuses', 'rarity': 'legendary', 'icon': '💎'}
        )[0]

        # New raw materials
        copper_ore = Material.objects.get_or_create(
            name='Minerai de Cuivre',
            defaults={'description': 'Minerai de cuivre brut', 'rarity': 'common', 'icon': '🟠'}
        )[0]

        tin_ore = Material.objects.get_or_create(
            name='Minerai d\'Étain',
            defaults={'description': 'Minerai d\'étain brut', 'rarity': 'common', 'icon': '⚪'}
        )[0]

        fibers = Material.objects.get_or_create(
            name='Fibres Végétales',
            defaults={'description': 'Fibres naturelles pour fabriquer des cordes', 'rarity': 'common', 'icon': '🧵'}
        )[0]

        flint = Material.objects.get_or_create(
            name='Silex',
            defaults={'description': 'Pierre dure utilisée pour fabriquer des outils simples', 'rarity': 'common', 'icon': '🗿'}
        )[0]

        # New byproduct materials
        branches = Material.objects.get_or_create(
            name='Branches',
            defaults={'description': 'Petites branches récupérées sur les buissons et arbres', 'rarity': 'common', 'icon': '🌿'}
        )[0]
        leaves = Material.objects.get_or_create(
            name='Feuilles',
            defaults={'description': 'Feuilles vertes provenant de la végétation', 'rarity': 'common', 'icon': '🍃'}
        )[0]

        # Hunting/Fishing outputs
        fish = Material.objects.get_or_create(
            name='Poisson',
            defaults={'description': 'Poisson frais', 'rarity': 'common', 'icon': '🐟', 'is_food': True, 'energy_restore': 12}
        )[0]
        meat = Material.objects.get_or_create(
            name='Viande',
            defaults={'description': 'Viande crue de gibier', 'rarity': 'common', 'icon': '🥩', 'is_food': True, 'energy_restore': 15}
        )[0]
        raw_leather = Material.objects.get_or_create(
            name='Cuir brut',
            defaults={'description': "Peau brute provenant d'animaux", 'rarity': 'uncommon', 'icon': '🧥'}
        )[0]

        # Food items
        pomme = Material.objects.get_or_create(
            name='Pomme',
            defaults={
                'description': 'Fruit rouge croquant',
                'rarity': 'common',
                'icon': '🍎',
                'is_food': True,
                'energy_restore': 10
            }
        )[0]

        baie = Material.objects.get_or_create(
            name='Baie',
            defaults={
                'description': 'Petites baies sucrées',
                'rarity': 'common',
                'icon': '🫐',
                'is_food': True,
                'energy_restore': 5
            }
        )[0]

        champignon = Material.objects.get_or_create(
            name='Champignon',
            defaults={
                'description': 'Champignon comestible',
                'rarity': 'common',
                'icon': '🍄',
                'is_food': True,
                'energy_restore': 8
            }
        )[0]

        # Crafted materials
        planks = Material.objects.get_or_create(
            name='Planches',
            defaults={'description': 'Planches de bois traitées', 'rarity': 'common', 'icon': '📏'}
        )[0]

        iron_bar = Material.objects.get_or_create(
            name='Barre de Fer',
            defaults={'description': 'Barres de fer fondues', 'rarity': 'uncommon', 'icon': '🔩'}
        )[0]

        gold_bar = Material.objects.get_or_create(
            name='Barre d\'Or',
            defaults={'description': 'Barres d\'or pur', 'rarity': 'rare', 'icon': '📊'}
        )[0]

        stick = Material.objects.get_or_create(
            name='Bâton',
            defaults={'description': 'Simple bâton en bois', 'rarity': 'common', 'icon': '🥢'}
        )[0]

        pickaxe = Material.objects.get_or_create(
            name='Pioche',
            defaults={'description': 'Outil pour miner les roches et minerais', 'rarity': 'uncommon', 'icon': '⛏️'}
        )[0]

        sword = Material.objects.get_or_create(
            name='Épée',
            defaults={'description': 'Arme pour le combat', 'rarity': 'uncommon', 'icon': '⚔️'}
        )[0]

        # New crafted intermediates and tools
        bronze_bar = Material.objects.get_or_create(
            name='Barre de Bronze',
            defaults={'description': 'Alliage cuivre-étain', 'rarity': 'uncommon', 'icon': '🟤'}
        )[0]

        # New crafted small parts & adhesive
        nails = Material.objects.get_or_create(
            name='Clous',
            defaults={'description': 'Petits clous en métal pour assemblage', 'rarity': 'common', 'icon': '📌'}
        )[0]
        screws = Material.objects.get_or_create(
            name='Vis',
            defaults={'description': 'Vis métalliques pour fixation', 'rarity': 'common', 'icon': '🔩'}
        )[0]
        glue = Material.objects.get_or_create(
            name='Colle',
            defaults={'description': 'Colle artisanale polyvalente', 'rarity': 'common', 'icon': '🧪'}
        )[0]

        # New crafted items using fasteners/adhesive
        wooden_crate = Material.objects.get_or_create(
            name='Caisse en Bois',
            defaults={'description': 'Boîte de stockage en bois', 'rarity': 'common', 'icon': '📦'}
        )[0]
        wooden_shield = Material.objects.get_or_create(
            name='Bouclier en Bois',
            defaults={'description': 'Bouclier simple en bois renforcé', 'rarity': 'uncommon', 'icon': '🛡️'}
        )[0]
        reinforced_bow = Material.objects.get_or_create(
            name='Arc Renforcé',
            defaults={'description': 'Arc renforcé par vis et colle', 'rarity': 'uncommon', 'icon': '🏹'}
        )[0]

        # Materials representing placeable workstations (to craft then convert to ownership)
        mat_workbench = Material.objects.get_or_create(
            name='Établi',
            defaults={'description': 'Matériel pour un établi de base', 'rarity': 'uncommon', 'icon': '🛠️'}
        )[0]
        mat_vice = Material.objects.get_or_create(
            name='Étau',
            defaults={'description': 'Équipement d\'étau', 'rarity': 'uncommon', 'icon': '🗜️'}
        )[0]
        mat_carpentry = Material.objects.get_or_create(
            name='Banc de Menuisier',
            defaults={'description': 'Équipement pour banc de menuisier', 'rarity': 'uncommon', 'icon': '🪚'}
        )[0]
        mat_archer = Material.objects.get_or_create(
            name="Banc d'Archer",
            defaults={'description': 'Équipement pour banc d\'archer', 'rarity': 'uncommon', 'icon': '🏹'}
        )[0]

        rope = Material.objects.get_or_create(
            name='Corde',
            defaults={'description': 'Corde solide tressée à partir de fibres', 'rarity': 'common', 'icon': '🪢'}
        )[0]

        axe = Material.objects.get_or_create(
            name='Hache',
            defaults={'description': 'Outil pour couper le bois', 'rarity': 'uncommon', 'icon': '🪓'}
        )[0]

        shovel = Material.objects.get_or_create(
            name='Pelle',
            defaults={'description': 'Outil pour creuser', 'rarity': 'uncommon', 'icon': '🛠️'}
        )[0]

        hammer = Material.objects.get_or_create(
            name='Marteau',
            defaults={'description': 'Outil pour forger et assembler', 'rarity': 'uncommon', 'icon': '🔨'}
        )[0]

        bow = Material.objects.get_or_create(
            name='Arc',
            defaults={'description': 'Arme de tir à distance', 'rarity': 'uncommon', 'icon': '🏹'}
        )[0]

        fishing_rod = Material.objects.get_or_create(
            name='Canne à Pêche',
            defaults={'description': 'Outil pour pêcher', 'rarity': 'common', 'icon': '🎣'}
        )[0]

        flint_knife = Material.objects.get_or_create(
            name='Couteau en Silex',
            defaults={'description': 'Petit couteau rudimentaire', 'rarity': 'common', 'icon': '🔪'}
        )[0]

        bronze_pickaxe = Material.objects.get_or_create(
            name='Pioche en Bronze',
            defaults={'description': 'Pioche robuste en bronze', 'rarity': 'uncommon', 'icon': '⛏️'}
        )[0]

        stone_axe = Material.objects.get_or_create(
            name='Hache en Pierre',
            defaults={'description': 'Hache rudimentaire en pierre', 'rarity': 'common', 'icon': '🪓'}
        )[0]
        iron_axe = Material.objects.get_or_create(
            name='Hache en Fer',
            defaults={'description': 'Hache solide en fer', 'rarity': 'uncommon', 'icon': '🪓'}
        )[0]

        self.stdout.write(self.style.SUCCESS('Matériaux créés!'))

        # Create basic workstations
        self.stdout.write('Création des stations de travail...')
        workbench = Workstation.objects.get_or_create(
            name='Établi',
            defaults={'description': 'Table de travail de base', 'icon': '🛠️'}
        )[0]
        vice = Workstation.objects.get_or_create(
            name='Étau',
            defaults={'description': "Outil de serrage pour le façonnage métal/bois", 'icon': '🗜️'}
        )[0]
        carpentry_bench = Workstation.objects.get_or_create(
            name='Banc de Menuisier',
            defaults={'description': 'Banc de menuiserie pour assemblages bois', 'icon': '🪚'}
        )[0]
        archer_bench = Workstation.objects.get_or_create(
            name="Banc d'Archer",
            defaults={'description': 'Banc spécialisé pour arcs', 'icon': '🏹'}
        )[0]
        self.stdout.write(self.style.SUCCESS('Stations de travail créées!'))

        self.stdout.write('Création des recettes...')

        def upsert_ingredient(recipe, material, quantity):
            RecipeIngredient.objects.update_or_create(
                recipe=recipe,
                material=material,
                defaults={'quantity': quantity}
            )

        # Recipe: Wood -> Planks
        recipe_planks = Recipe.objects.get_or_create(
            name='Fabriquer des Planches',
            defaults={
                'description': 'Transformer le bois en planches',
                'result_material': planks,
                'result_quantity': 4,
                'icon': '📏'
            }
        )[0]
        upsert_ingredient(recipe_planks, wood, 1)

        # Recipe: Planks -> Sticks
        recipe_sticks = Recipe.objects.get_or_create(
            name='Fabriquer des Bâtons',
            defaults={
                'description': 'Faire des bâtons à partir de planches',
                'result_material': stick,
                'result_quantity': 4,
                'icon': '🥢'
            }
        )[0]
        upsert_ingredient(recipe_sticks, planks, 2)

        # Recipe: Branches -> Stick
        recipe_branches_to_stick = Recipe.objects.get_or_create(
            name='Assembler un Bâton (Branches)',
            defaults={
                'description': 'Assembler des branches pour fabriquer un bâton',
                'result_material': stick,
                'result_quantity': 1,
                'icon': '🥢'
            }
        )[0]
        RecipeIngredient.objects.get_or_create(
            recipe=recipe_branches_to_stick,
            material=branches,
            defaults={'quantity': 2}
        )

        # Recipe: Iron Ore + Coal -> Iron Bar
        recipe_iron = Recipe.objects.get_or_create(
            name='Fondre du Fer',
            defaults={
                'description': 'Fondre le minerai de fer en barres',
                'result_material': iron_bar,
                'result_quantity': 1,
                'icon': '🔩'
            }
        )[0]
        upsert_ingredient(recipe_iron, iron_ore, 1)
        upsert_ingredient(recipe_iron, coal, 1)

        # Recipe: Gold Ore + Coal -> Gold Bar
        recipe_gold = Recipe.objects.get_or_create(
            name='Fondre de l\'Or',
            defaults={
                'description': 'Fondre le minerai d\'or en barres',
                'result_material': gold_bar,
                'result_quantity': 1,
                'icon': '📊'
            }
        )[0]
        upsert_ingredient(recipe_gold, gold_ore, 1)
        upsert_ingredient(recipe_gold, coal, 2)

        # Recipe: Iron Bar -> Nails
        recipe_nails = Recipe.objects.get_or_create(
            name='Forger des Clous',
            defaults={
                'description': 'Transformer une barre de fer en clous',
                'result_material': nails,
                'result_quantity': 8,
                'icon': '📌'
            }
        )[0]
        upsert_ingredient(recipe_nails, iron_bar, 1)

        # Recipe: Iron Bar -> Screws
        recipe_screws = Recipe.objects.get_or_create(
            name='Façonner des Vis',
            defaults={
                'description': 'Usiner une barre de fer en vis',
                'result_material': screws,
                'result_quantity': 6,
                'icon': '🔩'
            }
        )[0]
        upsert_ingredient(recipe_screws, iron_bar, 1)

        # Recipe: Fish -> Glue (traditional fish glue)
        recipe_glue = Recipe.objects.get_or_create(
            name='Préparer de la Colle',
            defaults={
                'description': 'Préparer une colle artisanale à partir de poisson',
                'result_material': glue,
                'result_quantity': 1,
                'icon': '🧪'
            }
        )[0]
        upsert_ingredient(recipe_glue, fish, 2)
        # Assign required workstations for small parts & adhesive
        recipe_nails.required_workstation = vice
        recipe_nails.save()
        recipe_screws.required_workstation = vice
        recipe_screws.save()
        recipe_glue.required_workstation = workbench
        recipe_glue.save()

        # Recipe: Planches + Clous + Colle -> Caisse en Bois
        recipe_crate = Recipe.objects.get_or_create(
            name='Assembler une Caisse en Bois',
            defaults={
                'description': 'Assembler une caisse de stockage en bois',
                'result_material': wooden_crate,
                'result_quantity': 1,
                'icon': '📦'
            }
        )[0]
        upsert_ingredient(recipe_crate, planks, 4)
        upsert_ingredient(recipe_crate, nails, 4)
        upsert_ingredient(recipe_crate, glue, 1)
        recipe_crate.required_workstation = carpentry_bench
        recipe_crate.save()

        # Recipe: Planches + Corde + Clous + Colle -> Bouclier en Bois
        recipe_wooden_shield = Recipe.objects.get_or_create(
            name='Fabriquer un Bouclier en Bois',
            defaults={
                'description': 'Fabriquer un bouclier simple en bois',
                'result_material': wooden_shield,
                'result_quantity': 1,
                'icon': '🛡️'
            }
        )[0]
        upsert_ingredient(recipe_wooden_shield, planks, 3)
        upsert_ingredient(recipe_wooden_shield, rope, 1)
        upsert_ingredient(recipe_wooden_shield, nails, 2)
        upsert_ingredient(recipe_wooden_shield, glue, 1)
        recipe_wooden_shield.required_workstation = workbench
        recipe_wooden_shield.save()

        # Recipe: Arc + Corde + Vis + Colle -> Arc Renforcé
        recipe_reinforced_bow = Recipe.objects.get_or_create(
            name='Renforcer un Arc',
            defaults={
                'description': "Améliorer un arc avec vis et colle",
                'result_material': reinforced_bow,
                'result_quantity': 1,
                'icon': '🏹'
            }
        )[0]
        upsert_ingredient(recipe_reinforced_bow, bow, 1)
        upsert_ingredient(recipe_reinforced_bow, rope, 1)
        upsert_ingredient(recipe_reinforced_bow, screws, 2)
        upsert_ingredient(recipe_reinforced_bow, glue, 1)
        recipe_reinforced_bow.required_workstation = archer_bench
        recipe_reinforced_bow.save()

        # Recipes to craft workstations (produce material with same name)
        recipe_make_workbench = Recipe.objects.get_or_create(
            name='Fabriquer un Établi',
            defaults={
                'description': 'Assembler un établi de base',
                'result_material': mat_workbench,
                'result_quantity': 1,
                'icon': '🛠️'
            }
        )[0]
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_workbench, material=planks, defaults={'quantity': 6})
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_workbench, material=nails, defaults={'quantity': 8})
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_workbench, material=glue, defaults={'quantity': 1})

        recipe_make_vice = Recipe.objects.get_or_create(
            name='Fabriquer un Étau',
            defaults={
                'description': 'Assembler un étau de travail',
                'result_material': mat_vice,
                'result_quantity': 1,
                'icon': '🗜️'
            }
        )[0]
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_vice, material=iron_bar, defaults={'quantity': 3})
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_vice, material=screws, defaults={'quantity': 4})

        recipe_make_carpentry = Recipe.objects.get_or_create(
            name='Fabriquer un Banc de Menuisier',
            defaults={
                'description': 'Assembler un banc de menuisier',
                'result_material': mat_carpentry,
                'result_quantity': 1,
                'icon': '🪚'
            }
        )[0]
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_carpentry, material=planks, defaults={'quantity': 8})
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_carpentry, material=screws, defaults={'quantity': 4})
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_carpentry, material=glue, defaults={'quantity': 1})

        recipe_make_archer = Recipe.objects.get_or_create(
            name="Fabriquer un Banc d'Archer",
            defaults={
                'description': "Assembler un banc d'archer spécialisé",
                'result_material': mat_archer,
                'result_quantity': 1,
                'icon': '🏹'
            }
        )[0]
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_archer, material=planks, defaults={'quantity': 4})
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_archer, material=rope, defaults={'quantity': 2})
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_archer, material=screws, defaults={'quantity': 2})
        RecipeIngredient.objects.get_or_create(recipe=recipe_make_archer, material=glue, defaults={'quantity': 1})

        # Recipe: Sticks + Iron Bars -> Pickaxe
        recipe_pickaxe = Recipe.objects.get_or_create(
            name='Fabriquer une Pioche',
            defaults={
                'description': 'Fabriquer une pioche pour miner',
                'result_material': pickaxe,
                'result_quantity': 1,
                'icon': '⛏️'
            }
        )[0]
        upsert_ingredient(recipe_pickaxe, iron_bar, 3)
        upsert_ingredient(recipe_pickaxe, stick, 2)

        # Recipe: Sticks + Iron Bars -> Sword
        recipe_sword = Recipe.objects.get_or_create(
            name='Fabriquer une Épée',
            defaults={
                'description': 'Fabriquer une épée pour le combat',
                'result_material': sword,
                'result_quantity': 1,
                'icon': '⚔️'
            }
        )[0]
        upsert_ingredient(recipe_sword, iron_bar, 2)
        upsert_ingredient(recipe_sword, stick, 1)

        # Tools: Fishing Rod (Sticks + Rope)
        recipe_fishing_rod = Recipe.objects.get_or_create(
            name='Fabriquer une Canne à Pêche',
            defaults={
                'description': 'Fabriquer une canne à pêche',
                'result_material': fishing_rod,
                'result_quantity': 1,
                'icon': '🎣'
            }
        )[0]
        upsert_ingredient(recipe_fishing_rod, stick, 2)
        upsert_ingredient(recipe_fishing_rod, rope, 1)

        # Tools: Stone Axe (Stone + Stick + Rope)
        recipe_stone_axe = Recipe.objects.get_or_create(
            name='Fabriquer une Hache en Pierre',
            defaults={
                'description': 'Fabriquer une hache rudimentaire en pierre',
                'result_material': stone_axe,
                'result_quantity': 1,
                'icon': '🪓'
            }
        )[0]
        upsert_ingredient(recipe_stone_axe, stone, 2)
        upsert_ingredient(recipe_stone_axe, stick, 1)
        upsert_ingredient(recipe_stone_axe, rope, 1)

        # Tools: Iron Axe (Iron Bar + Stick + Rope)
        recipe_iron_axe = Recipe.objects.get_or_create(
            name='Fabriquer une Hache en Fer',
            defaults={
                'description': 'Fabriquer une hache solide en fer',
                'result_material': iron_axe,
                'result_quantity': 1,
                'icon': '🪓'
            }
        )[0]
        upsert_ingredient(recipe_iron_axe, iron_bar, 2)
        upsert_ingredient(recipe_iron_axe, stick, 1)
        upsert_ingredient(recipe_iron_axe, rope, 1)

        # Recipe: Fibres -> Rope
        recipe_rope = Recipe.objects.get_or_create(
            name='Tresser une Corde',
            defaults={
                'description': 'Assembler des fibres pour créer une corde',
                'result_material': rope,
                'result_quantity': 1,
                'icon': '🪢'
            }
        )[0]
        upsert_ingredient(recipe_rope, fibers, 3)

        # Recipe: Leaves -> Fibres Végétales
        recipe_leaves_to_fibers = Recipe.objects.get_or_create(
            name='Effilocher des Feuilles',
            defaults={
                'description': 'Recycler des feuilles en fibres végétales',
                'result_material': fibers,
                'result_quantity': 1,
                'icon': '🍃'
            }
        )[0]
        RecipeIngredient.objects.get_or_create(
            recipe=recipe_leaves_to_fibers,
            material=leaves,
            defaults={'quantity': 3}
        )

        # Recipe: Copper + Tin + Coal -> Bronze Bar
        recipe_bronze = Recipe.objects.get_or_create(
            name='Fondre du Bronze',
            defaults={
                'description': 'Fondre le cuivre et l\'étain en bronze',
                'result_material': bronze_bar,
                'result_quantity': 1,
                'icon': '🟤'
            }
        )[0]
        upsert_ingredient(recipe_bronze, copper_ore, 1)
        upsert_ingredient(recipe_bronze, tin_ore, 1)
        upsert_ingredient(recipe_bronze, coal, 1)

        # Tools: Axe (Iron + Stick + Rope)
        recipe_axe = Recipe.objects.get_or_create(
            name='Fabriquer une Hache',
            defaults={
                'description': 'Fabriquer une hache pour couper du bois',
                'result_material': axe,
                'result_quantity': 1,
                'icon': '🪓'
            }
        )[0]
        upsert_ingredient(recipe_axe, iron_bar, 2)
        upsert_ingredient(recipe_axe, stick, 1)
        upsert_ingredient(recipe_axe, rope, 1)

        # Tools: Shovel (Iron + Stick)
        recipe_shovel = Recipe.objects.get_or_create(
            name='Fabriquer une Pelle',
            defaults={
                'description': 'Fabriquer une pelle pour creuser',
                'result_material': shovel,
                'result_quantity': 1,
                'icon': '🛠️'
            }
        )[0]
        upsert_ingredient(recipe_shovel, iron_bar, 2)
        upsert_ingredient(recipe_shovel, stick, 1)

        # Tools: Hammer (Iron + Stick)
        recipe_hammer = Recipe.objects.get_or_create(
            name='Fabriquer un Marteau',
            defaults={
                'description': 'Fabriquer un marteau pour forger et assembler',
                'result_material': hammer,
                'result_quantity': 1,
                'icon': '🔨'
            }
        )[0]
        upsert_ingredient(recipe_hammer, iron_bar, 3)
        upsert_ingredient(recipe_hammer, stick, 1)

        # Tools: Bow (Sticks + Rope)
        recipe_bow = Recipe.objects.get_or_create(
            name='Fabriquer un Arc',
            defaults={
                'description': 'Fabriquer un arc pour le tir à distance',
                'result_material': bow,
                'result_quantity': 1,
                'icon': '🏹'
            }
        )[0]
        upsert_ingredient(recipe_bow, stick, 2)
        upsert_ingredient(recipe_bow, rope, 1)

        # Tools: Flint Knife (Flint + Stick)
        recipe_knife = Recipe.objects.get_or_create(
            name='Fabriquer un Couteau en Silex',
            defaults={
                'description': 'Fabriquer un couteau rudimentaire',
                'result_material': flint_knife,
                'result_quantity': 1,
                'icon': '🔪'
            }
        )[0]
        upsert_ingredient(recipe_knife, flint, 1)
        upsert_ingredient(recipe_knife, stick, 1)

        # Tools: Bronze Pickaxe (Bronze Bars + Sticks)
        recipe_bronze_pickaxe = Recipe.objects.get_or_create(
            name='Fabriquer une Pioche en Bronze',
            defaults={
                'description': 'Fabriquer une pioche solide en bronze',
                'result_material': bronze_pickaxe,
                'result_quantity': 1,
                'icon': '⛏️'
            }
        )[0]
        upsert_ingredient(recipe_bronze_pickaxe, bronze_bar, 3)
        upsert_ingredient(recipe_bronze_pickaxe, stick, 2)

        # --- Medieval/Survival tools and stations (canonical names, upsert to avoid duplicates) ---
        self.stdout.write('Ajout outils médiévaux/survie...')

        # Materials (tools)
        maillet_bois = Material.objects.get_or_create(name='Maillet en bois', defaults={'description': 'Maillet simple en bois', 'icon': '🔨'})[0]
        serpe_fer = Material.objects.get_or_create(name='Serpe en fer', defaults={'description': 'Outil pour tailler le feuillage', 'icon': '🌿'})[0]
        couteau_fer = Material.objects.get_or_create(name='Couteau en fer', defaults={'description': 'Couteau durable en fer', 'icon': '🔪'})[0]
        mortier_pilon = Material.objects.get_or_create(name='Mortier et pilon', defaults={'description': 'Broyer plantes et pigments', 'icon': '🪨'})[0]
        ciseau_bois = Material.objects.get_or_create(name='Ciseau à bois', defaults={'description': 'Sculpter le bois', 'icon': '🪵'})[0]
        scie_manuelle = Material.objects.get_or_create(name='Scie manuelle', defaults={'description': 'Couper planches et poutres', 'icon': '🪚'})[0]
        truelle = Material.objects.get_or_create(name='Truelle', defaults={'description': 'Outil de maçonnerie', 'icon': '🧱'})[0]
        maillet_charpentier = Material.objects.get_or_create(name='Maillet de charpentier', defaults={'description': 'Assembler sans fendre', 'icon': '🔨'})[0]
        aiguille_metal = Material.objects.get_or_create(name='Aiguille en métal', defaults={'description': 'Couture solide', 'icon': '🪡'})[0]
        teinture_vegetale = Material.objects.get_or_create(name='Teinture végétale', defaults={'description': 'Teinture naturelle', 'icon': '🧴'})[0]
        torche = Material.objects.get_or_create(name='Torche', defaults={'description': 'Éclaire les zones sombres', 'icon': '🔥'})[0]
        seau_bois = Material.objects.get_or_create(name='Seau en bois', defaults={'description': 'Transport de liquides', 'icon': '🪣'})[0]
        piege_simple = Material.objects.get_or_create(name='Piège simple', defaults={'description': 'Capturer de petits animaux', 'icon': '🪤'})[0]
        filet = Material.objects.get_or_create(name='Filet', defaults={'description': 'Pêche ou capture', 'icon': '🕸️'})[0]

        # Workstations (craftable/installable via material of same name)
        meule_ws = Workstation.objects.get_or_create(name='Meule en Pierre', defaults={'description': 'Aiguiser et moudre', 'icon': '🛞'})[0]
        forge_ws = Workstation.objects.get_or_create(name='Forge en Argile', defaults={'description': 'Fondre et forger métaux', 'icon': '🔥'})[0]
        metier_ws = Workstation.objects.get_or_create(name='Métier à tisser', defaults={'description': 'Tisser des tissus', 'icon': '🧶'})[0]

        mat_meule = Material.objects.get_or_create(name='Meule en Pierre', defaults={'description': 'Station: meule', 'icon': '🛞'})[0]
        mat_forge = Material.objects.get_or_create(name='Forge en Argile', defaults={'description': 'Station: forge', 'icon': '🔥'})[0]
        mat_metier = Material.objects.get_or_create(name='Métier à tisser', defaults={'description': 'Station: tissage', 'icon': '🧶'})[0]

        # Recipes (use existing base materials)
        # Maillet en bois: Bois + Bâton
        recipe_maillet_bois = Recipe.objects.get_or_create(
            name='Fabriquer un Maillet en bois',
            defaults={'description': 'Assembler un maillet simple', 'result_material': maillet_bois, 'result_quantity': 1, 'icon': '🔨'}
        )[0]
        upsert_ingredient(recipe_maillet_bois, wood, 1)
        upsert_ingredient(recipe_maillet_bois, stick, 1)

        # Serpe en fer: Barre de Fer + Bâton + Corde
        recipe_serpe = Recipe.objects.get_or_create(
            name='Forger une Serpe en fer',
            defaults={'description': 'Outil pour tailler le feuillage', 'result_material': serpe_fer, 'result_quantity': 1, 'icon': '🌿'}
        )[0]
        upsert_ingredient(recipe_serpe, iron_bar, 1)
        upsert_ingredient(recipe_serpe, stick, 1)
        upsert_ingredient(recipe_serpe, rope, 1)
        recipe_serpe.required_workstation = forge_ws
        recipe_serpe.save()

        # Couteau en fer: Barre de Fer + Bâton
        recipe_couteau_fer = Recipe.objects.get_or_create(
            name='Forger un Couteau en fer',
            defaults={'description': 'Couteau robuste', 'result_material': couteau_fer, 'result_quantity': 1, 'icon': '🔪'}
        )[0]
        upsert_ingredient(recipe_couteau_fer, iron_bar, 1)
        upsert_ingredient(recipe_couteau_fer, stick, 1)
        recipe_couteau_fer.required_workstation = forge_ws
        recipe_couteau_fer.save()

        # Mortier et pilon: Pierre + Bâton
        recipe_mortier = Recipe.objects.get_or_create(
            name='Façonner un Mortier et pilon',
            defaults={'description': 'Broyer plantes et pigments', 'result_material': mortier_pilon, 'result_quantity': 1, 'icon': '🪨'}
        )[0]
        upsert_ingredient(recipe_mortier, stone, 2)
        upsert_ingredient(recipe_mortier, stick, 1)

        # Meule en Pierre (station): Pierre + Bâton
        recipe_meule = Recipe.objects.get_or_create(
            name='Construire Meule en Pierre',
            defaults={'description': 'Assembler une meule', 'result_material': mat_meule, 'result_quantity': 1, 'icon': '🛞'}
        )[0]
        upsert_ingredient(recipe_meule, stone, 3)
        upsert_ingredient(recipe_meule, stick, 1)
        recipe_meule.required_workstation = workbench
        recipe_meule.save()

        # Forge en Argile (station simplifiée): Pierre + Charbon + Clous
        recipe_forge = Recipe.objects.get_or_create(
            name='Construire Forge en Argile',
            defaults={'description': 'Construire une petite forge', 'result_material': mat_forge, 'result_quantity': 1, 'icon': '🔥'}
        )[0]
        upsert_ingredient(recipe_forge, stone, 4)
        upsert_ingredient(recipe_forge, coal, 2)
        upsert_ingredient(recipe_forge, nails, 2)
        recipe_forge.required_workstation = workbench
        recipe_forge.save()

        # Métier à tisser (station): Bois + Corde + Clous
        recipe_metier = Recipe.objects.get_or_create(
            name='Construire Métier à tisser',
            defaults={'description': 'Assembler un métier à tisser', 'result_material': mat_metier, 'result_quantity': 1, 'icon': '🧶'}
        )[0]
        upsert_ingredient(recipe_metier, wood, 2)
        upsert_ingredient(recipe_metier, rope, 2)
        upsert_ingredient(recipe_metier, nails, 2)
        recipe_metier.required_workstation = carpentry_bench
        recipe_metier.save()

        # Ciseau à bois: Barre de Fer + Bâton + Pierre (pour l'aiguisage)
        recipe_ciseau = Recipe.objects.get_or_create(
            name='Forger un Ciseau à bois',
            defaults={'description': 'Ciseau pour sculpture', 'result_material': ciseau_bois, 'result_quantity': 1, 'icon': '🪵'}
        )[0]
        upsert_ingredient(recipe_ciseau, iron_bar, 1)
        upsert_ingredient(recipe_ciseau, stick, 1)
        upsert_ingredient(recipe_ciseau, stone, 1)
        recipe_ciseau.required_workstation = meule_ws
        recipe_ciseau.save()

        # Scie manuelle: Barre de Fer + Bâton + Clous
        recipe_scie = Recipe.objects.get_or_create(
            name='Assembler une Scie manuelle',
            defaults={'description': 'Scie pour planches', 'result_material': scie_manuelle, 'result_quantity': 1, 'icon': '🪚'}
        )[0]
        upsert_ingredient(recipe_scie, iron_bar, 1)
        upsert_ingredient(recipe_scie, stick, 1)
        upsert_ingredient(recipe_scie, nails, 2)
        recipe_scie.required_workstation = carpentry_bench
        recipe_scie.save()

        # Truelle: Barre de Fer + Bâton
        recipe_truelle = Recipe.objects.get_or_create(
            name='Forger une Truelle',
            defaults={'description': 'Outil de maçonnerie', 'result_material': truelle, 'result_quantity': 1, 'icon': '🧱'}
        )[0]
        upsert_ingredient(recipe_truelle, iron_bar, 1)
        upsert_ingredient(recipe_truelle, stick, 1)
        recipe_truelle.required_workstation = workbench
        recipe_truelle.save()

        # Maillet de charpentier: Bois + Corde
        recipe_maillet_charp = Recipe.objects.get_or_create(
            name='Fabriquer un Maillet de charpentier',
            defaults={'description': 'Maillet pour assemblage', 'result_material': maillet_charpentier, 'result_quantity': 1, 'icon': '🔨'}
        )[0]
        upsert_ingredient(recipe_maillet_charp, wood, 1)
        upsert_ingredient(recipe_maillet_charp, rope, 1)

        # Aiguille en métal: Barre de Fer (petite pièce)
        recipe_aiguille = Recipe.objects.get_or_create(
            name='Forger une Aiguille en métal',
            defaults={'description': 'Aiguille de couture', 'result_material': aiguille_metal, 'result_quantity': 2, 'icon': '🪡'}
        )[0]
        upsert_ingredient(recipe_aiguille, iron_bar, 1)
        recipe_aiguille.required_workstation = vice
        recipe_aiguille.save()

        # Teinture végétale: Feuilles -> Teinture
        recipe_teinture = Recipe.objects.get_or_create(
            name='Préparer une Teinture végétale',
            defaults={'description': 'Teinture naturelle à base de feuilles', 'result_material': teinture_vegetale, 'result_quantity': 1, 'icon': '🧴'}
        )[0]
        upsert_ingredient(recipe_teinture, leaves, 2) if 'leaves' in locals() else None

        # Torche: Bâton + Colle
        recipe_torche = Recipe.objects.get_or_create(
            name='Fabriquer une Torche',
            defaults={'description': 'Torche pour explorer', 'result_material': torche, 'result_quantity': 1, 'icon': '🔥'}
        )[0]
        upsert_ingredient(recipe_torche, stick, 1)
        upsert_ingredient(recipe_torche, glue, 1)

        # Seau en bois: Planches + Clous
        recipe_seau = Recipe.objects.get_or_create(
            name='Assembler un Seau en bois',
            defaults={'description': 'Seau pour transporter', 'result_material': seau_bois, 'result_quantity': 1, 'icon': '🪣'}
        )[0]
        upsert_ingredient(recipe_seau, planks, 3)
        upsert_ingredient(recipe_seau, nails, 2)
        recipe_seau.required_workstation = carpentry_bench
        recipe_seau.save()

        # Piège simple: Bâton + Corde
        recipe_piege = Recipe.objects.get_or_create(
            name='Fabriquer un Piège simple',
            defaults={'description': 'Piège pour petits animaux', 'result_material': piege_simple, 'result_quantity': 1, 'icon': '🪤'}
        )[0]
        upsert_ingredient(recipe_piege, stick, 2)
        upsert_ingredient(recipe_piege, rope, 1)

        # Filet: Corde x3
        recipe_filet = Recipe.objects.get_or_create(
            name='Tisser un Filet',
            defaults={'description': 'Filet pour pêche/capture', 'result_material': filet, 'result_quantity': 1, 'icon': '🕸️'}
        )[0]
        upsert_ingredient(recipe_filet, rope, 3)

        # --- Vissage: chaîne complète du minerai à la vis ---
        self.stdout.write('Ajout chaîne de fabrication: Vis en fer...')

        # Ensure base resources exist
        argile = Material.objects.get_or_create(name='Argile', defaults={'description': 'Terre glaise utilisable pour moules', 'icon': '🧱', 'rarity': 'common'})[0]
        sable = Material.objects.get_or_create(name='Sable', defaults={'description': 'Grains fins pour moules et verrerie', 'icon': '🏖️', 'rarity': 'common'})[0]
        eau = Material.objects.get_or_create(name='Eau', defaults={'description': 'Eau claire', 'icon': '💧', 'rarity': 'common'})[0]

        # Output materials
        tige_metal = Material.objects.get_or_create(name='Tige métallique', defaults={'description': 'Cylindre de métal étiré', 'icon': '⎯', 'rarity': 'common'})[0]
        vis_brute = Material.objects.get_or_create(name='Vis brute', defaults={'description': 'Ébauche filetée avant finition', 'icon': '🔩', 'rarity': 'common'})[0]
        vis_fer = Material.objects.get_or_create(name='Vis en fer', defaults={'description': 'Composant pour assemblage précis', 'icon': '🔩', 'rarity': 'common'})[0]
        moule_vis = Material.objects.get_or_create(name='Moule à vis', defaults={'description': 'Moule pour produire des vis en série', 'icon': '🧰', 'rarity': 'common'})[0]

        # Workstations
        enclume_ws = Workstation.objects.get_or_create(name='Enclume', defaults={'description': 'Mise en forme par martelage', 'icon': '🪨'})[0]
        metallurgie_ws = Workstation.objects.get_or_create(name='Atelier de Métallurgie', defaults={'description': 'Atelier pour coulée et moules', 'icon': '🏭'})[0]

        # 2. Lingot -> Tige métallique
        recipe_tige = Recipe.objects.get_or_create(
            name='Forger une Tige métallique',
            defaults={'description': 'Étirer un lingot en tige', 'result_material': tige_metal, 'result_quantity': 1, 'icon': '⎯'}
        )[0]
        upsert_ingredient(recipe_tige, iron_bar, 1)
        recipe_tige.required_workstation = enclume_ws
        recipe_tige.save()

        # 3. Tige -> Vis brute (filetage)
        recipe_vis_brute = Recipe.objects.get_or_create(
            name='Façonner une Vis brute',
            defaults={'description': 'Filetage manuel sur étau', 'result_material': vis_brute, 'result_quantity': 1, 'icon': '🔩'}
        )[0]
        upsert_ingredient(recipe_vis_brute, tige_metal, 1)
        recipe_vis_brute.required_workstation = vice
        recipe_vis_brute.save()

        # 4. Finition de la tête -> Vis en fer
        recipe_vis_finie = Recipe.objects.get_or_create(
            name="Finition d'une Vis en fer",
            defaults={'description': 'Former la tête et lisser', 'result_material': vis_fer, 'result_quantity': 1, 'icon': '🔩'}
        )[0]
        upsert_ingredient(recipe_vis_finie, vis_brute, 1)
        recipe_vis_finie.required_workstation = workbench
        recipe_vis_finie.save()

        # 5a. Fabriquer un Moule à vis
        recipe_moule_vis = Recipe.objects.get_or_create(
            name='Façonner un Moule à vis',
            defaults={'description': 'Moule argile/sable pour vis', 'result_material': moule_vis, 'result_quantity': 1, 'icon': '🧰'}
        )[0]
        upsert_ingredient(recipe_moule_vis, argile, 2)
        upsert_ingredient(recipe_moule_vis, sable, 1)
        upsert_ingredient(recipe_moule_vis, eau, 1)
        upsert_ingredient(recipe_moule_vis, iron_bar, 1)
        recipe_moule_vis.required_workstation = metallurgie_ws
        recipe_moule_vis.save()

        # 5b. Production en série avec coulée: 1 lingot -> 5 vis
        recipe_serie_vis = Recipe.objects.get_or_create(
            name='Couler des Vis en fer (x5)',
            defaults={'description': 'Coulée de vis via moule (consommables non requis)', 'result_material': vis_fer, 'result_quantity': 5, 'icon': '🔩'}
        )[0]
        upsert_ingredient(recipe_serie_vis, iron_bar, 1)
        recipe_serie_vis.required_workstation = metallurgie_ws
        recipe_serie_vis.save()

        # Existing iron/metal recipes: require forge
        try:
            recipe_iron = Recipe.objects.get(name='Fondre du Fer')
            recipe_iron.required_workstation = forge_ws
            recipe_iron.save(update_fields=['required_workstation'])
        except Recipe.DoesNotExist:
            pass
        try:
            recipe_bronze = Recipe.objects.get(name='Fondre du Bronze')
            recipe_bronze.required_workstation = forge_ws
            recipe_bronze.save(update_fields=['required_workstation'])
        except Recipe.DoesNotExist:
            pass
        try:
            recipe_gold = Recipe.objects.get(name="Fondre de l'Or")
            recipe_gold.required_workstation = forge_ws
            recipe_gold.save(update_fields=['required_workstation'])
        except Recipe.DoesNotExist:
            pass

        # Existing iron tools: require forge
        for nm in [
            'Fabriquer une Hache en Fer',
            'Fabriquer une Pioche',
            'Fabriquer une Épée',
            'Fabriquer un Marteau',
            'Fabriquer une Hache',
            'Fabriquer une Pelle',
        ]:
            try:
                r = Recipe.objects.get(name=nm)
                r.required_workstation = forge_ws
                r.save(update_fields=['required_workstation'])
            except Recipe.DoesNotExist:
                pass

        # Safety: ensure early-game recipes are NOT gated by stations
        self.stdout.write('Vérification exigences de station (recettes de base)...')
        baseline_names = [
            'Tresser une Corde',
            'Fabriquer des Planches',
            'Fabriquer des Bâtons',
            'Fabriquer une Hache en Pierre',
            'Fabriquer un Couteau en Silex',
            'Fabriquer une Torche',
            'Façonner un Mortier et pilon',
        ]
        for nm in baseline_names:
            try:
                r = Recipe.objects.get(name=nm)
                if r.required_workstation_id:
                    r.required_workstation = None
                    r.save(update_fields=['required_workstation'])
            except Recipe.DoesNotExist:
                pass

        # Safety: ensure base stations are craftable (no deadlock)
        base_station_recipe_names = [
            'Fabriquer un Établi',
            'Fabriquer un Étau',
            'Fabriquer un Banc de Menuisier',
            "Fabriquer un Banc d'Archer",
        ]
        for nm in base_station_recipe_names:
            try:
                r = Recipe.objects.get(name=nm)
                if r.required_workstation_id:
                    r.required_workstation = None
                    r.save(update_fields=['required_workstation'])
            except Recipe.DoesNotExist:
                pass

        # Deduplicate any existing duplicate ingredients (historical runs)
        self.stdout.write('Déduplication des ingrédients...')
        with transaction.atomic():
            seen = {}
            for ri in RecipeIngredient.objects.select_related('recipe', 'material').order_by('recipe_id', 'material_id', 'id'):
                key = (ri.recipe_id, ri.material_id)
                if key not in seen:
                    seen[key] = ri
                else:
                    # keep max quantity
                    if ri.quantity > seen[key].quantity:
                        seen[key].quantity = ri.quantity
                        seen[key].save(update_fields=['quantity'])
                    ri.delete()
        self.stdout.write(self.style.SUCCESS('Déduplication terminée.'))

        self.stdout.write(self.style.SUCCESS('Recettes créées!'))

        # === ADDITIONAL MATERIALS ===
        self.stdout.write('Ajout de matériaux supplémentaires...')

        # Gemmes et pierres précieuses
        emeraude = Material.objects.get_or_create(name='Émeraude', defaults={'description': 'Pierre précieuse verte', 'rarity': 'legendary', 'icon': '💚'})[0]
        rubis = Material.objects.get_or_create(name='Rubis', defaults={'description': 'Pierre précieuse rouge', 'rarity': 'legendary', 'icon': '❤️'})[0]
        saphir = Material.objects.get_or_create(name='Saphir', defaults={'description': 'Pierre précieuse bleue', 'rarity': 'legendary', 'icon': '💙'})[0]
        amethyste = Material.objects.get_or_create(name='Améthyste', defaults={'description': 'Pierre semi-précieuse violette', 'rarity': 'rare', 'icon': '💜'})[0]

        # Matériaux naturels additionnels
        bois_dur = Material.objects.get_or_create(name='Bois Dur', defaults={'description': 'Bois d\'arbres anciens très résistant', 'rarity': 'uncommon', 'icon': '🪵'})[0]
        obsidienne = Material.objects.get_or_create(name='Obsidienne', defaults={'description': 'Roche volcanique noire et tranchante', 'rarity': 'rare', 'icon': '🖤'})[0]
        cristal = Material.objects.get_or_create(name='Cristal', defaults={'description': 'Cristal transparent magique', 'rarity': 'rare', 'icon': '💎'})[0]
        soufre = Material.objects.get_or_create(name='Soufre', defaults={'description': 'Minéral jaune inflammable', 'rarity': 'uncommon', 'icon': '🟡'})[0]
        salpetre = Material.objects.get_or_create(name='Salpêtre', defaults={'description': 'Nitrate pour explosifs', 'rarity': 'uncommon', 'icon': '⚪'})[0]

        # Tissus et textiles
        lin = Material.objects.get_or_create(name='Lin', defaults={'description': 'Fibres de lin', 'rarity': 'common', 'icon': '🌾'})[0]
        coton = Material.objects.get_or_create(name='Coton', defaults={'description': 'Fibres de coton', 'rarity': 'common', 'icon': '☁️'})[0]
        tissu = Material.objects.get_or_create(name='Tissu', defaults={'description': 'Tissu simple', 'rarity': 'common', 'icon': '🧵'})[0]
        cuir = Material.objects.get_or_create(name='Cuir', defaults={'description': 'Cuir tanné', 'rarity': 'uncommon', 'icon': '🦌'})[0]

        # Aliments variés
        pain = Material.objects.get_or_create(name='Pain', defaults={'description': 'Pain frais', 'rarity': 'common', 'icon': '🍞', 'is_food': True, 'energy_restore': 20})[0]
        ble = Material.objects.get_or_create(name='Blé', defaults={'description': 'Céréales de blé', 'rarity': 'common', 'icon': '🌾'})[0]
        farine = Material.objects.get_or_create(name='Farine', defaults={'description': 'Farine de blé', 'rarity': 'common', 'icon': '🥛'})[0]
        viande_cuite = Material.objects.get_or_create(name='Viande Cuite', defaults={'description': 'Viande grillée', 'rarity': 'common', 'icon': '🍖', 'is_food': True, 'energy_restore': 30})[0]
        poisson_cuit = Material.objects.get_or_create(name='Poisson Cuit', defaults={'description': 'Poisson grillé', 'rarity': 'common', 'icon': '🐟', 'is_food': True, 'energy_restore': 25})[0]
        ragoût = Material.objects.get_or_create(name='Ragoût', defaults={'description': 'Ragoût nourrissant', 'rarity': 'uncommon', 'icon': '🍲', 'is_food': True, 'energy_restore': 40})[0]

        # Potions et consommables magiques
        potion_soin = Material.objects.get_or_create(name='Potion de Soin', defaults={'description': 'Restaure beaucoup d\'énergie', 'rarity': 'uncommon', 'icon': '🧪', 'is_food': True, 'energy_restore': 50})[0]
        herbe_medicinale = Material.objects.get_or_create(name='Herbe Médicinale', defaults={'description': 'Plante aux propriétés curatives', 'rarity': 'uncommon', 'icon': '🌿'})[0]
        fleur_magique = Material.objects.get_or_create(name='Fleur Magique', defaults={'description': 'Fleur imprégnée de magie', 'rarity': 'rare', 'icon': '🌸'})[0]

        # Équipements et armures
        casque_fer = Material.objects.get_or_create(name='Casque en Fer', defaults={'description': 'Protection pour la tête', 'rarity': 'uncommon', 'icon': '⛑️'})[0]
        plastron_fer = Material.objects.get_or_create(name='Plastron en Fer', defaults={'description': 'Armure de torse', 'rarity': 'uncommon', 'icon': '🛡️'})[0]
        jambières_fer = Material.objects.get_or_create(name='Jambières en Fer', defaults={'description': 'Protection pour les jambes', 'rarity': 'uncommon', 'icon': '👖'})[0]
        bottes_fer = Material.objects.get_or_create(name='Bottes en Fer', defaults={'description': 'Protection pour les pieds', 'rarity': 'uncommon', 'icon': '👢'})[0]

        armure_cuir = Material.objects.get_or_create(name='Armure en Cuir', defaults={'description': 'Armure légère en cuir', 'rarity': 'common', 'icon': '🧥'})[0]

        # Munitions et projectiles
        fleches = Material.objects.get_or_create(name='Flèches', defaults={'description': 'Flèches pour arc', 'rarity': 'common', 'icon': '➹'})[0]

        # Matériaux de construction
        brique = Material.objects.get_or_create(name='Brique', defaults={'description': 'Brique d\'argile cuite', 'rarity': 'common', 'icon': '🧱'})[0]
        mortier = Material.objects.get_or_create(name='Mortier', defaults={'description': 'Ciment pour construction', 'rarity': 'common', 'icon': '🪣'})[0]
        verre = Material.objects.get_or_create(name='Verre', defaults={'description': 'Verre transparent', 'rarity': 'uncommon', 'icon': '🪟'})[0]

        # Mobilier
        table = Material.objects.get_or_create(name='Table en Bois', defaults={'description': 'Table simple', 'rarity': 'common', 'icon': '🪑'})[0]
        chaise = Material.objects.get_or_create(name='Chaise en Bois', defaults={'description': 'Chaise confortable', 'rarity': 'common', 'icon': '🪑'})[0]
        lit = Material.objects.get_or_create(name='Lit', defaults={'description': 'Lit pour se reposer', 'rarity': 'uncommon', 'icon': '🛏️'})[0]
        coffre = Material.objects.get_or_create(name='Coffre', defaults={'description': 'Coffre de stockage', 'rarity': 'common', 'icon': '📦'})[0]

        self.stdout.write(self.style.SUCCESS('Matériaux supplémentaires créés!'))

        # === ADDITIONAL RECIPES ===
        self.stdout.write('Ajout de recettes supplémentaires...')

        # Tissage
        recipe_tissu = Recipe.objects.get_or_create(
            name='Tisser du Tissu',
            defaults={'description': 'Tisser des fibres en tissu', 'result_material': tissu, 'result_quantity': 1, 'icon': '🧵'}
        )[0]
        upsert_ingredient(recipe_tissu, lin, 3)
        recipe_tissu.required_workstation = metier_ws
        recipe_tissu.save()

        # Tannage du cuir
        recipe_cuir = Recipe.objects.get_or_create(
            name='Tanner du Cuir',
            defaults={'description': 'Transformer le cuir brut en cuir utilisable', 'result_material': cuir, 'result_quantity': 1, 'icon': '🦌'}
        )[0]
        upsert_ingredient(recipe_cuir, raw_leather, 1)
        upsert_ingredient(recipe_cuir, eau, 1)

        # Alimentation
        recipe_farine = Recipe.objects.get_or_create(
            name='Moudre de la Farine',
            defaults={'description': 'Moudre le blé en farine', 'result_material': farine, 'result_quantity': 2, 'icon': '🥛'}
        )[0]
        upsert_ingredient(recipe_farine, ble, 3)
        recipe_farine.required_workstation = meule_ws
        recipe_farine.save()

        recipe_pain = Recipe.objects.get_or_create(
            name='Cuire du Pain',
            defaults={'description': 'Faire du pain avec de la farine', 'result_material': pain, 'result_quantity': 2, 'icon': '🍞'}
        )[0]
        upsert_ingredient(recipe_pain, farine, 2)
        upsert_ingredient(recipe_pain, eau, 1)

        recipe_viande_cuite = Recipe.objects.get_or_create(
            name='Cuire de la Viande',
            defaults={'description': 'Griller la viande', 'result_material': viande_cuite, 'result_quantity': 1, 'icon': '🍖'}
        )[0]
        upsert_ingredient(recipe_viande_cuite, meat, 1)
        upsert_ingredient(recipe_viande_cuite, coal, 1)

        recipe_poisson_cuit = Recipe.objects.get_or_create(
            name='Cuire du Poisson',
            defaults={'description': 'Griller le poisson', 'result_material': poisson_cuit, 'result_quantity': 1, 'icon': '🐟'}
        )[0]
        upsert_ingredient(recipe_poisson_cuit, fish, 1)
        upsert_ingredient(recipe_poisson_cuit, coal, 1)

        recipe_ragout = Recipe.objects.get_or_create(
            name='Préparer un Ragoût',
            defaults={'description': 'Mijoter un ragoût copieux', 'result_material': ragoût, 'result_quantity': 1, 'icon': '🍲'}
        )[0]
        upsert_ingredient(recipe_ragout, viande_cuite, 1)
        upsert_ingredient(recipe_ragout, champignon, 2)
        upsert_ingredient(recipe_ragout, eau, 1)

        # Potions
        recipe_potion = Recipe.objects.get_or_create(
            name='Préparer une Potion de Soin',
            defaults={'description': 'Créer une potion curative', 'result_material': potion_soin, 'result_quantity': 1, 'icon': '🧪'}
        )[0]
        upsert_ingredient(recipe_potion, herbe_medicinale, 2)
        upsert_ingredient(recipe_potion, fleur_magique, 1)
        upsert_ingredient(recipe_potion, eau, 1)
        recipe_potion.required_workstation = workbench
        recipe_potion.save()

        # Armures et équipements
        recipe_casque = Recipe.objects.get_or_create(
            name='Forger un Casque en Fer',
            defaults={'description': 'Fabriquer un casque de protection', 'result_material': casque_fer, 'result_quantity': 1, 'icon': '⛑️'}
        )[0]
        upsert_ingredient(recipe_casque, iron_bar, 3)
        recipe_casque.required_workstation = forge_ws
        recipe_casque.save()

        recipe_plastron = Recipe.objects.get_or_create(
            name='Forger un Plastron en Fer',
            defaults={'description': 'Fabriquer une armure de torse', 'result_material': plastron_fer, 'result_quantity': 1, 'icon': '🛡️'}
        )[0]
        upsert_ingredient(recipe_plastron, iron_bar, 5)
        recipe_plastron.required_workstation = forge_ws
        recipe_plastron.save()

        recipe_jambieres = Recipe.objects.get_or_create(
            name='Forger des Jambières en Fer',
            defaults={'description': 'Fabriquer des protections pour les jambes', 'result_material': jambières_fer, 'result_quantity': 1, 'icon': '👖'}
        )[0]
        upsert_ingredient(recipe_jambieres, iron_bar, 4)
        recipe_jambieres.required_workstation = forge_ws
        recipe_jambieres.save()

        recipe_bottes = Recipe.objects.get_or_create(
            name='Forger des Bottes en Fer',
            defaults={'description': 'Fabriquer des bottes protectrices', 'result_material': bottes_fer, 'result_quantity': 1, 'icon': '👢'}
        )[0]
        upsert_ingredient(recipe_bottes, iron_bar, 2)
        recipe_bottes.required_workstation = forge_ws
        recipe_bottes.save()

        recipe_armure_cuir = Recipe.objects.get_or_create(
            name='Fabriquer une Armure en Cuir',
            defaults={'description': 'Assembler une armure légère', 'result_material': armure_cuir, 'result_quantity': 1, 'icon': '🧥'}
        )[0]
        upsert_ingredient(recipe_armure_cuir, cuir, 4)
        upsert_ingredient(recipe_armure_cuir, rope, 2)
        recipe_armure_cuir.required_workstation = workbench
        recipe_armure_cuir.save()

        # Flèches
        recipe_fleches = Recipe.objects.get_or_create(
            name='Fabriquer des Flèches',
            defaults={'description': 'Créer des flèches pour l\'arc', 'result_material': fleches, 'result_quantity': 10, 'icon': '➹'}
        )[0]
        upsert_ingredient(recipe_fleches, stick, 1)
        upsert_ingredient(recipe_fleches, flint, 1)
        upsert_ingredient(recipe_fleches, fibers, 1)

        # Construction
        recipe_brique = Recipe.objects.get_or_create(
            name='Cuire des Briques',
            defaults={'description': 'Cuire l\'argile en briques', 'result_material': brique, 'result_quantity': 4, 'icon': '🧱'}
        )[0]
        upsert_ingredient(recipe_brique, argile, 2)
        upsert_ingredient(recipe_brique, coal, 1)

        recipe_verre = Recipe.objects.get_or_create(
            name='Fabriquer du Verre',
            defaults={'description': 'Fondre le sable en verre', 'result_material': verre, 'result_quantity': 1, 'icon': '🪟'}
        )[0]
        upsert_ingredient(recipe_verre, sable, 3)
        upsert_ingredient(recipe_verre, coal, 2)
        recipe_verre.required_workstation = forge_ws
        recipe_verre.save()

        # Mobilier
        recipe_table = Recipe.objects.get_or_create(
            name='Fabriquer une Table',
            defaults={'description': 'Assembler une table en bois', 'result_material': table, 'result_quantity': 1, 'icon': '🪑'}
        )[0]
        upsert_ingredient(recipe_table, planks, 6)
        upsert_ingredient(recipe_table, nails, 4)
        recipe_table.required_workstation = carpentry_bench
        recipe_table.save()

        recipe_chaise = Recipe.objects.get_or_create(
            name='Fabriquer une Chaise',
            defaults={'description': 'Assembler une chaise', 'result_material': chaise, 'result_quantity': 1, 'icon': '🪑'}
        )[0]
        upsert_ingredient(recipe_chaise, planks, 3)
        upsert_ingredient(recipe_chaise, nails, 2)
        recipe_chaise.required_workstation = carpentry_bench
        recipe_chaise.save()

        recipe_lit = Recipe.objects.get_or_create(
            name='Fabriquer un Lit',
            defaults={'description': 'Construire un lit confortable', 'result_material': lit, 'result_quantity': 1, 'icon': '🛏️'}
        )[0]
        upsert_ingredient(recipe_lit, planks, 8)
        upsert_ingredient(recipe_lit, tissu, 3)
        upsert_ingredient(recipe_lit, nails, 6)
        recipe_lit.required_workstation = carpentry_bench
        recipe_lit.save()

        recipe_coffre = Recipe.objects.get_or_create(
            name='Fabriquer un Coffre',
            defaults={'description': 'Construire un coffre de stockage', 'result_material': coffre, 'result_quantity': 1, 'icon': '📦'}
        )[0]
        upsert_ingredient(recipe_coffre, planks, 8)
        upsert_ingredient(recipe_coffre, iron_bar, 1)
        upsert_ingredient(recipe_coffre, nails, 4)
        recipe_coffre.required_workstation = carpentry_bench
        recipe_coffre.save()

        self.stdout.write(self.style.SUCCESS('Recettes supplémentaires créées!'))

        # === SKILLS ===
        self.stdout.write('Création des compétences...')

        skill_gather = Skill.objects.get_or_create(
            code='gathering',
            defaults={'name': 'Collecte', 'description': 'Maîtrise de la collecte de ressources'}
        )[0]

        skill_craft = Skill.objects.get_or_create(
            code='crafting',
            defaults={'name': 'Artisanat', 'description': 'Compétence en fabrication d\'objets'}
        )[0]

        skill_combat = Skill.objects.get_or_create(
            code='combat',
            defaults={'name': 'Combat', 'description': 'Maîtrise des armes et du combat'}
        )[0]

        skill_mining = Skill.objects.get_or_create(
            code='mining',
            defaults={'name': 'Minage', 'description': 'Expertise en extraction de minerais'}
        )[0]

        skill_woodcut = Skill.objects.get_or_create(
            code='woodcutting',
            defaults={'name': 'Bûcheronnage', 'description': 'Compétence en coupe de bois'}
        )[0]

        skill_cooking = Skill.objects.get_or_create(
            code='cooking',
            defaults={'name': 'Cuisine', 'description': 'Art de préparer la nourriture'}
        )[0]

        skill_alchemy = Skill.objects.get_or_create(
            code='alchemy',
            defaults={'name': 'Alchimie', 'description': 'Création de potions et d\'élixirs'}
        )[0]

        self.stdout.write(self.style.SUCCESS('Compétences créées!'))

        # === TALENT TREES ===
        self.stdout.write('Création des arbres de talents...')

        # Gathering talents
        TalentNode.objects.get_or_create(
            skill=skill_gather,
            code='efficient_gathering',
            defaults={
                'name': 'Collecte Efficace',
                'description': 'Augmente la quantité récoltée de 10%',
                'tier': 1,
                'xp_required': 0,
                'effect_type': 'bonus_gather_amount',
                'effect_value': 10
            }
        )

        TalentNode.objects.get_or_create(
            skill=skill_gather,
            code='reduced_energy_gather',
            defaults={
                'name': 'Collecte Économique',
                'description': 'Réduit le coût en énergie de la collecte de 1',
                'tier': 2,
                'xp_required': 100,
                'prereq_codes': ['efficient_gathering'],
                'effect_type': 'gather_cost_reduction',
                'effect_value': 1
            }
        )

        TalentNode.objects.get_or_create(
            skill=skill_gather,
            code='rare_find',
            defaults={
                'name': 'Trouvaille Rare',
                'description': '5% de chance de doubler la récolte',
                'tier': 3,
                'xp_required': 300,
                'prereq_codes': ['reduced_energy_gather'],
                'effect_type': 'bonus_output_chance',
                'effect_value': 5
            }
        )

        # Crafting talents
        TalentNode.objects.get_or_create(
            skill=skill_craft,
            code='material_efficiency',
            defaults={
                'name': 'Efficacité Matérielle',
                'description': '10% de chance d\'économiser des matériaux',
                'tier': 1,
                'xp_required': 0,
                'effect_type': 'material_cost_reduction',
                'effect_value': 10
            }
        )

        TalentNode.objects.get_or_create(
            skill=skill_craft,
            code='bulk_production',
            defaults={
                'name': 'Production en Masse',
                'description': '10% de production supplémentaire lors du craft',
                'tier': 2,
                'xp_required': 150,
                'prereq_codes': ['material_efficiency'],
                'effect_type': 'bonus_output_amount',
                'effect_value': 10
            }
        )

        TalentNode.objects.get_or_create(
            skill=skill_craft,
            code='master_craftsman',
            defaults={
                'name': 'Maître Artisan',
                'description': 'Double la quantité produite pour les recettes communes',
                'tier': 3,
                'xp_required': 500,
                'prereq_codes': ['bulk_production'],
                'effect_type': 'double_output_common',
                'effect_value': 100
            }
        )

        # Mining talents
        TalentNode.objects.get_or_create(
            skill=skill_mining,
            code='ore_detector',
            defaults={
                'name': 'Détecteur de Minerai',
                'description': '15% de minerai supplémentaire lors du minage',
                'tier': 1,
                'xp_required': 0,
                'effect_type': 'bonus_gather_ore',
                'effect_value': 15
            }
        )

        TalentNode.objects.get_or_create(
            skill=skill_mining,
            code='efficient_smelting',
            defaults={
                'name': 'Fonte Efficace',
                'description': 'Réduit le charbon nécessaire pour la fonte de 50%',
                'tier': 2,
                'xp_required': 200,
                'prereq_codes': ['ore_detector'],
                'effect_type': 'coal_cost_reduction',
                'effect_value': 50,
                'params': {'material': 'coal'}
            }
        )

        # Cooking talents
        TalentNode.objects.get_or_create(
            skill=skill_cooking,
            code='hearty_meals',
            defaults={
                'name': 'Repas Copieux',
                'description': 'La nourriture restaure 25% d\'énergie supplémentaire',
                'tier': 1,
                'xp_required': 0,
                'effect_type': 'food_restore_bonus',
                'effect_value': 25
            }
        )

        TalentNode.objects.get_or_create(
            skill=skill_cooking,
            code='master_chef',
            defaults={
                'name': 'Chef Étoilé',
                'description': 'Chance de créer 2 portions au lieu d\'une',
                'tier': 2,
                'xp_required': 250,
                'prereq_codes': ['hearty_meals'],
                'effect_type': 'double_food_output',
                'effect_value': 50
            }
        )

        self.stdout.write(self.style.SUCCESS('Arbres de talents créés!'))

        # === GAME CONFIGURATIONS ===
        self.stdout.write('Création des configurations de jeu...')

        # XP Formula
        xp_config = GameConfig.objects.get_or_create(
            key='xp_formula',
            defaults={
                'description': 'Formule de calcul de l\'XP par niveau',
                'value': json.dumps({
                    'base': 100,
                    'exponent': 1.2,
                    'multiplier': 1.0
                })
            }
        )[0]

        # Biome material distribution
        biome_config = GameConfig.objects.get_or_create(
            key='biome_materials',
            defaults={
                'description': 'Distribution des matériaux par biome',
                'value': json.dumps({
                    'plains': ['Bois', 'Pierre', 'Fibres Végétales', 'Pomme', 'Blé', 'Lin'],
                    'forest': ['Bois', 'Bois Dur', 'Branches', 'Feuilles', 'Baie', 'Champignon', 'Herbe Médicinale'],
                    'mountain': ['Pierre', 'Minerai de Fer', 'Minerai de Cuivre', 'Minerai d\'Or', 'Charbon', 'Silex', 'Obsidienne'],
                    'water': ['Poisson', 'Sable', 'Argile', 'Eau']
                })
            }
        )[0]

        # Energy costs
        energy_config = GameConfig.objects.get_or_create(
            key='energy_costs',
            defaults={
                'description': 'Coûts en énergie des actions',
                'value': json.dumps({
                    'move': 1,
                    'gather': 5,
                    'craft': 2
                })
            }
        )[0]

        # XP rewards
        xp_reward_config = GameConfig.objects.get_or_create(
            key='xp_rewards',
            defaults={
                'description': 'Récompenses d\'XP par action',
                'value': json.dumps({
                    'gather_multiplier': 2,
                    'craft_multiplier': 10
                })
            }
        )[0]

        # Regeneration rates
        regen_config = GameConfig.objects.get_or_create(
            key='cell_regeneration',
            defaults={
                'description': 'Taux de régénération des cellules',
                'value': json.dumps({
                    'enabled': True,
                    'interval_hours': 24,
                    'percentage': 50
                })
            }
        )[0]

        self.stdout.write(self.style.SUCCESS('Configurations de jeu créées!'))

        # --- Scavenging Materials ---
        self.stdout.write('Ajout matériaux de fouille...')
        conserve = Material.objects.get_or_create(name='Conserve', defaults={'description': 'Nourriture en conserve', 'rarity': 'common', 'icon': '🥫', 'is_food': True, 'energy_restore': 20, 'hunger_restore': 30})[0]
        water = Material.objects.get_or_create(name='Bouteille d\'Eau', defaults={'description': 'Eau potable', 'rarity': 'common', 'icon': '💧', 'is_food': True, 'thirst_restore': 40})[0]
        tissu = Material.objects.get_or_create(name='Tissu', defaults={'description': 'Morceau de tissu', 'rarity': 'common', 'icon': '🧶'})[0]
        ferraille = Material.objects.get_or_create(name='Ferraille', defaults={'description': 'Débris métalliques', 'rarity': 'common', 'icon': '🔩'})[0]
        meds = Material.objects.get_or_create(name='Médicaments', defaults={'description': 'Soins de premiers secours', 'rarity': 'rare', 'icon': '💊', 'is_food': True, 'health_restore': 50, 'radiation_change': -20})[0]
        electronics = Material.objects.get_or_create(name='Composants Électroniques', defaults={'description': 'Composants avancés', 'rarity': 'rare', 'icon': '📟'})[0]

        # --- Vehicles ---
        self.stdout.write('Ajout véhicules...')
        velo = Vehicle.objects.get_or_create(
            name='Vélo',
            defaults={
                'description': 'Un vélo simple pour se déplacer plus vite.',
                'icon': '🚲',
                'carry_bonus': 10.0,
                'speed_bonus': 20,
                'energy_efficiency': 10
            }
        )[0]

        charrette = Vehicle.objects.get_or_create(
            name='Charrette',
            defaults={
                'description': 'Une charrette pour transporter beaucoup de matériel.',
                'icon': '🛒',
                'carry_bonus': 50.0,
                'speed_bonus': -5,
                'energy_efficiency': 0
            }
        )[0]
        
        # Vehicle Recipes
        # Vélo: 5 Iron Bars + 2 Screws + 2 Ferraille
        recipe_velo = Recipe.objects.get_or_create(
            name='Fabriquer un Vélo',
            defaults={
                'description': 'Assembler un vélo',
                'result_material': Material.objects.get_or_create(name='Vélo', defaults={'description': 'Véhicule', 'icon': '🚲'})[0], # Dummy material if needed or just use name match
                'result_quantity': 1,
                'icon': '🚲'
            }
        )[0]
        # Ensure Vehicle material exists for inventory display if needed, though Vehicle model is separate.
        # Our system uses Material for inventory. So we need a Material 'Vélo' too?
        # Yes, Inventory links to Material. So we need Materials for Vehicles.
        # Let's ensure they exist as Materials too.
        mat_velo = Material.objects.get_or_create(name='Vélo', defaults={'description': 'Un vélo (Véhicule)', 'icon': '🚲', 'weight': 15.0})[0]
        mat_charrette = Material.objects.get_or_create(name='Charrette', defaults={'description': 'Une charrette (Véhicule)', 'icon': '🛒', 'weight': 20.0})[0]
        
        # Update recipes to point to these materials
        recipe_velo.result_material = mat_velo
        recipe_velo.save()
        
        upsert_ingredient(recipe_velo, iron_bar, 5)
        upsert_ingredient(recipe_velo, screws, 2)
        # If ferraille not available yet, use iron ore or something? No we added it above.
        upsert_ingredient(recipe_velo, ferraille, 2)
        recipe_velo.required_workstation = workbench
        recipe_velo.save()

        recipe_charrette = Recipe.objects.get_or_create(
            name='Fabriquer une Charrette',
            defaults={
                'description': 'Assembler une charrette',
                'result_material': mat_charrette,
                'result_quantity': 1,
                'icon': '🛒'
            }
        )[0]
        upsert_ingredient(recipe_charrette, planks, 10)
        upsert_ingredient(recipe_charrette, nails, 4)
        upsert_ingredient(recipe_charrette, iron_bar, 2)
        recipe_charrette.required_workstation = carpentry_bench
        recipe_charrette.save()

        self.stdout.write(self.style.SUCCESS('Véhicules et données de fouille ajoutés!'))
        self.stdout.write(self.style.SUCCESS('Base de données enrichie avec succès!'))
