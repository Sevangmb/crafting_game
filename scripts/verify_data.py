#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de vérification de la cohérence de la base de données du jeu
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from game.models import Material, Recipe, RecipeIngredient, Skill, TalentNode, Workstation, GameConfig

def verify_data():
    """Vérifie la cohérence de toutes les données"""

    print("=" * 80)
    print("VÉRIFICATION DE LA BASE DE DONNÉES")
    print("=" * 80)

    # Compter les objets
    print("\n[1] STATISTIQUES GÉNÉRALES")
    print("-" * 80)
    print(f"Matériaux:           {Material.objects.count()}")
    print(f"Recettes:            {Recipe.objects.count()}")
    print(f"Stations:            {Workstation.objects.count()}")
    print(f"Compétences:         {Skill.objects.count()}")
    print(f"Talents:             {TalentNode.objects.count()}")
    print(f"Configurations:      {GameConfig.objects.count()}")

    # Vérifier les aliments
    print("\n[2] ALIMENTS")
    print("-" * 80)
    foods = Material.objects.filter(is_food=True).order_by('-energy_restore')
    print(f"Total d'aliments: {foods.count()}")
    for food in foods:
        print(f"  - {food.name}: +{food.energy_restore} énergie")

    # Vérifier les recettes avec stations
    print("\n[3] RECETTES PAR STATION")
    print("-" * 80)

    # Recettes sans station
    no_station = Recipe.objects.filter(required_workstation__isnull=True).count()
    print(f"Sans station requise: {no_station} recettes")

    # Par station
    for station in Workstation.objects.all():
        count = Recipe.objects.filter(required_workstation=station).count()
        if count > 0:
            print(f"{station.name}: {count} recettes")

    # Vérifier les rarités
    print("\n[4] MATÉRIAUX PAR RARETÉ")
    print("-" * 80)
    rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
    for rarity in rarities:
        count = Material.objects.filter(rarity=rarity).count()
        print(f"{rarity.capitalize()}: {count} matériaux")

    # Vérifier les talents par compétence
    print("\n[5] TALENTS PAR COMPÉTENCE")
    print("-" * 80)
    for skill in Skill.objects.all():
        talents = TalentNode.objects.filter(skill=skill)
        print(f"{skill.name} ({skill.code}): {talents.count()} talents")
        for talent in talents.order_by('tier', 'xp_required'):
            prereqs = ", ".join(talent.prereq_codes) if talent.prereq_codes else "Aucun"
            print(f"  [Tier {talent.tier}] {talent.name} (XP: {talent.xp_required}, Prérequis: {prereqs})")

    # Vérifier l'intégrité des recettes
    print("\n[6] VÉRIFICATION DE L'INTÉGRITÉ DES RECETTES")
    print("-" * 80)
    errors = []

    for recipe in Recipe.objects.all():
        # Vérifier que le résultat existe
        if not recipe.result_material:
            errors.append(f"Recette '{recipe.name}': Pas de matériau résultat")

        # Vérifier qu'il y a des ingrédients
        ingredients = recipe.ingredients.all()
        if ingredients.count() == 0:
            errors.append(f"Recette '{recipe.name}': Pas d'ingrédients")

        # Vérifier que tous les ingrédients existent
        for ing in ingredients:
            if not ing.material:
                errors.append(f"Recette '{recipe.name}': Ingrédient manquant")

    if errors:
        print("ERREURS DETECTEES:")
        for error in errors:
            print(f"  X {error}")
    else:
        print("OK - Toutes les recettes sont valides")

    # Vérifier l'intégrité des talents
    print("\n[7] VÉRIFICATION DE L'INTÉGRITÉ DES TALENTS")
    print("-" * 80)
    talent_errors = []

    for talent in TalentNode.objects.all():
        # Vérifier que la compétence existe
        if not talent.skill:
            talent_errors.append(f"Talent '{talent.name}': Pas de compétence associée")

        # Vérifier les prérequis
        if talent.prereq_codes:
            for prereq_code in talent.prereq_codes:
                prereq_exists = TalentNode.objects.filter(
                    skill=talent.skill,
                    code=prereq_code
                ).exists()
                if not prereq_exists:
                    talent_errors.append(f"Talent '{talent.name}': Prérequis '{prereq_code}' introuvable")

    if talent_errors:
        print("ERREURS DETECTEES:")
        for error in talent_errors:
            print(f"  X {error}")
    else:
        print("OK - Tous les talents sont valides")

    # Afficher les configurations
    print("\n[8] CONFIGURATIONS DE JEU")
    print("-" * 80)
    for config in GameConfig.objects.all():
        print(f"{config.key}:")
        print(f"  {config.description}")
        value = config.get_value()
        if isinstance(value, dict):
            for k, v in value.items():
                print(f"    - {k}: {v}")
        else:
            print(f"    Valeur: {value}")

    print("\n" + "=" * 80)
    print("VÉRIFICATION TERMINÉE")
    print("=" * 80)

if __name__ == '__main__':
    verify_data()
