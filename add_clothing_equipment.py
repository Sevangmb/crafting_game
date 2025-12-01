#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script pour ajouter tous les vêtements et équipements au jeu
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from game.models import Material

# Catégories de vêtements et équipements
CLOTHING_DATA = {
    # ========== VETEMENTS COURANTS ==========
    'quotidien': [
        {'name': 'T-shirt Coton', 'icon': '👕', 'price': 15, 'weight': 0.2, 'protection': 1, 'durability': 50,
         'desc': 'T-shirt en coton pour usage quotidien'},
        {'name': 'T-shirt Technique', 'icon': '👕', 'price': 25, 'weight': 0.15, 'protection': 1, 'durability': 80,
         'desc': 'T-shirt respirant en tissu technique'},
        {'name': 'Chemise Decontractee', 'icon': '👔', 'price': 30, 'weight': 0.3, 'protection': 2, 'durability': 60,
         'desc': 'Chemise decontractee pour tous les jours'},
        {'name': 'Chemise Flanelle', 'icon': '👔', 'price': 35, 'weight': 0.4, 'protection': 3, 'durability': 70,
         'desc': 'Chemise en flanelle chaude'},
        {'name': 'Sweat-shirt', 'icon': '🧥', 'price': 40, 'weight': 0.5, 'protection': 4, 'durability': 100,
         'desc': 'Sweat confortable pour mi-saison'},
        {'name': 'Hoodie', 'icon': '🧥', 'price': 45, 'weight': 0.6, 'protection': 5, 'durability': 100,
         'desc': 'Sweat a capuche polyvalent'},
        {'name': 'Polaire', 'icon': '🧥', 'price': 50, 'weight': 0.4, 'protection': 6, 'durability': 90,
         'desc': 'Veste polaire isolante'},
        {'name': 'Veste Coupe-vent', 'icon': '🧥', 'price': 60, 'weight': 0.3, 'protection': 5, 'durability': 120,
         'desc': 'Veste legere resistant au vent'},
        {'name': 'Jean', 'icon': '👖', 'price': 50, 'weight': 0.6, 'protection': 5, 'durability': 150,
         'desc': 'Jean classique resistant'},
        {'name': 'Pantalon Cargo', 'icon': '👖', 'price': 60, 'weight': 0.7, 'protection': 6, 'durability': 140,
         'desc': 'Pantalon cargo avec multiples poches'},
        {'name': 'Pantalon Technique', 'icon': '👖', 'price': 80, 'weight': 0.5, 'protection': 7, 'durability': 180,
         'desc': 'Pantalon stretch technique'},
        {'name': 'Short', 'icon': '🩳', 'price': 25, 'weight': 0.3, 'protection': 2, 'durability': 80,
         'desc': 'Short pour temps chaud'},
        {'name': 'Chaussettes Respirantes', 'icon': '🧦', 'price': 10, 'weight': 0.1, 'protection': 1, 'durability': 40,
         'desc': 'Chaussettes techniques respirantes'},
        {'name': 'Baskets', 'icon': '👟', 'price': 70, 'weight': 0.8, 'protection': 5, 'durability': 200,
         'desc': 'Baskets confortables pour marche'},
        {'name': 'Blouson Cuir', 'icon': '🧥', 'price': 150, 'weight': 1.2, 'protection': 15, 'durability': 300,
         'desc': 'Blouson en cuir resistant'},
        {'name': 'Blouson Denim', 'icon': '🧥', 'price': 80, 'weight': 0.9, 'protection': 8, 'durability': 200,
         'desc': 'Veste en denim robuste'},
        {'name': 'Doudoune Legere', 'icon': '🧥', 'price': 100, 'weight': 0.6, 'protection': 12, 'durability': 150,
         'desc': 'Doudoune compactable isolante'},
        {'name': 'Doudoune Epaisse', 'icon': '🧥', 'price': 150, 'weight': 1.0, 'protection': 20, 'durability': 180,
         'desc': 'Doudoune grand froid'},
        {'name': 'Manteau Long', 'icon': '🧥', 'price': 120, 'weight': 1.5, 'protection': 15, 'durability': 200,
         'desc': 'Manteau long elegant'},
        {'name': 'Trench-coat', 'icon': '🧥', 'price': 140, 'weight': 1.3, 'protection': 14, 'durability': 220,
         'desc': 'Trench resistant a la pluie'},
        {'name': 'Parka', 'icon': '🧥', 'price': 180, 'weight': 1.8, 'protection': 25, 'durability': 250,
         'desc': 'Parka chaude et impermeable'},
        {'name': 'Bonnet', 'icon': '🧢', 'price': 15, 'weight': 0.1, 'protection': 2, 'durability': 100,
         'desc': 'Bonnet chaud pour hiver'},
        {'name': 'Casquette', 'icon': '🧢', 'price': 20, 'weight': 0.1, 'protection': 1, 'durability': 120,
         'desc': 'Casquette protection soleil'},
        {'name': 'Gants Laine', 'icon': '🧤', 'price': 20, 'weight': 0.15, 'protection': 3, 'durability': 80,
         'desc': 'Gants en laine chauds'},
        {'name': 'Echarpe', 'icon': '🧣', 'price': 25, 'weight': 0.2, 'protection': 3, 'durability': 100,
         'desc': 'Echarpe chaude'},
        {'name': 'Tour de Cou', 'icon': '🧣', 'price': 15, 'weight': 0.1, 'protection': 2, 'durability': 90,
         'desc': 'Tour de cou multifonction'},
        {'name': 'Veste Impermeable', 'icon': '🧥', 'price': 120, 'weight': 0.8, 'protection': 10, 'durability': 200,
         'desc': 'Veste Gore-Tex impermeable'},
    ],

    # ========== SPORT & OUTDOOR ==========
    'sport': [
        {'name': 'T-shirt Dry-Fit', 'icon': '👕', 'price': 35, 'weight': 0.15, 'protection': 1, 'durability': 100,
         'desc': 'T-shirt ultra-respirant pour sport'},
        {'name': 'Short Running', 'icon': '🩳', 'price': 30, 'weight': 0.2, 'protection': 1, 'durability': 120,
         'desc': 'Short leger pour course'},
        {'name': 'Legging Compression', 'icon': '👖', 'price': 50, 'weight': 0.3, 'protection': 3, 'durability': 150,
         'desc': 'Legging compression performance'},
        {'name': 'Veste Softshell', 'icon': '🧥', 'price': 100, 'weight': 0.6, 'protection': 8, 'durability': 180,
         'desc': 'Veste softshell respirante'},
        {'name': 'Veste Hardshell', 'icon': '🧥', 'price': 150, 'weight': 0.5, 'protection': 10, 'durability': 250,
         'desc': 'Veste anti-pluie/vent impermeable'},
        {'name': 'Sous-vetement Thermique', 'icon': '👕', 'price': 40, 'weight': 0.2, 'protection': 5, 'durability': 120,
         'desc': 'Sous-vetement chaud isolant'},
        {'name': 'Chaussures Randonnee', 'icon': '👢', 'price': 120, 'weight': 1.2, 'protection': 15, 'durability': 400,
         'desc': 'Chaussures montantes randonnee'},
        {'name': 'Chaussettes Merinos', 'icon': '🧦', 'price': 20, 'weight': 0.1, 'protection': 2, 'durability': 100,
         'desc': 'Chaussettes merinos anti-odeur'},
        {'name': 'Gilet Hydratation', 'icon': '🎒', 'price': 80, 'weight': 0.4, 'protection': 2, 'durability': 200,
         'desc': 'Gilet avec poche a eau'},
        {'name': 'Gants Tactiles', 'icon': '🧤', 'price': 30, 'weight': 0.1, 'protection': 3, 'durability': 100,
         'desc': 'Gants compatibles smartphone'},
        {'name': 'Lunettes UV Polarisees', 'icon': '🕶️', 'price': 60, 'weight': 0.05, 'protection': 2, 'durability': 150,
         'desc': 'Lunettes protection UV'},
        {'name': 'Poncho Pluie', 'icon': '🧥', 'price': 25, 'weight': 0.3, 'protection': 8, 'durability': 80,
         'desc': 'Poncho impermeable compact'},
    ],

    # ========== PROTECTION URBAINE ==========
    'urbain': [
        {'name': 'Gilet Haute Visibilite', 'icon': '🦺', 'price': 15, 'weight': 0.3, 'protection': 1, 'durability': 100,
         'desc': 'Gilet jaune reflechissant'},
        {'name': 'Casque Velo', 'icon': '⛑️', 'price': 50, 'weight': 0.4, 'protection': 20, 'durability': 200,
         'desc': 'Casque protection velo/trottinette'},
        {'name': 'Genouilleres', 'icon': '🦿', 'price': 30, 'weight': 0.4, 'protection': 15, 'durability': 150,
         'desc': 'Genouilleres protection sport'},
        {'name': 'Coudieres', 'icon': '💪', 'price': 25, 'weight': 0.3, 'protection': 12, 'durability': 150,
         'desc': 'Coudieres protection sport'},
        {'name': 'Protection Dorsale', 'icon': '🛡️', 'price': 80, 'weight': 0.6, 'protection': 30, 'durability': 250,
         'desc': 'Protection dos sport extreme'},
        {'name': 'Masque Anti-Pollution', 'icon': '😷', 'price': 20, 'weight': 0.05, 'protection': 5, 'durability': 50,
         'desc': 'Masque filtrant FFP2'},
        {'name': 'Veste Moto Renforcee', 'icon': '🧥', 'price': 300, 'weight': 2.0, 'protection': 50, 'durability': 500,
         'desc': 'Veste moto avec coques D3O'},
        {'name': 'Jean Moto Kevlar', 'icon': '👖', 'price': 200, 'weight': 1.5, 'protection': 40, 'durability': 450,
         'desc': 'Jean kevlar avec protections'},
        {'name': 'Gants Moto', 'icon': '🧤', 'price': 80, 'weight': 0.3, 'protection': 25, 'durability': 200,
         'desc': 'Gants moto homologues'},
        {'name': 'Bottes Moto', 'icon': '👢', 'price': 180, 'weight': 1.5, 'protection': 35, 'durability': 400,
         'desc': 'Bottes moto renforcees'},
    ],

    # ========== TACTIQUE & PROFESSIONNEL ==========
    'tactique': [
        {'name': 'Casque Balistique', 'icon': '⛑️', 'price': 500, 'weight': 1.5, 'protection': 80, 'durability': 1000,
         'desc': 'Casque balistique niveau IIIA'},
        {'name': 'Gilet Pare-balles Souple', 'icon': '🦺', 'price': 800, 'weight': 3.0, 'protection': 100, 'durability': 800,
         'desc': 'Gilet soft armor niveau II'},
        {'name': 'Plaque Balistique Niveau III', 'icon': '🛡️', 'price': 400, 'weight': 2.5, 'protection': 150, 'durability': 2000,
         'desc': 'Plaque rigide anti-rifle'},
        {'name': 'Plaque Balistique Niveau IV', 'icon': '🛡️', 'price': 600, 'weight': 3.0, 'protection': 200, 'durability': 3000,
         'desc': 'Plaque ceramique haut niveau'},
        {'name': 'Gants Tactiques Anti-coupure', 'icon': '🧤', 'price': 60, 'weight': 0.2, 'protection': 20, 'durability': 300,
         'desc': 'Gants kevlar tactiques'},
        {'name': 'Veste Tactique MOLLE', 'icon': '🦺', 'price': 200, 'weight': 1.5, 'protection': 30, 'durability': 600,
         'desc': 'Veste avec systeme MOLLE'},
        {'name': 'Poches Modulaires MOLLE', 'icon': '🎒', 'price': 30, 'weight': 0.3, 'protection': 0, 'durability': 200,
         'desc': 'Pochettes attachables MOLLE'},
        {'name': 'Genouilleres Tactiques', 'icon': '🦿', 'price': 50, 'weight': 0.4, 'protection': 25, 'durability': 300,
         'desc': 'Genouilleres renforcees pro'},
        {'name': 'Chaussures Intervention', 'icon': '👢', 'price': 150, 'weight': 1.3, 'protection': 30, 'durability': 500,
         'desc': 'Chaussures montantes tactiques'},
        {'name': 'Tenue Ignifugee', 'icon': '🧥', 'price': 400, 'weight': 2.5, 'protection': 60, 'durability': 400,
         'desc': 'Combinaison resistant au feu'},
    ],

    # ========== TRAVAIL & INDUSTRIE ==========
    'travail': [
        {'name': 'Casque de Chantier', 'icon': '⛑️', 'price': 25, 'weight': 0.5, 'protection': 30, 'durability': 500,
         'desc': 'Casque securite chantier'},
        {'name': 'Lunettes de Protection', 'icon': '🥽', 'price': 15, 'weight': 0.1, 'protection': 10, 'durability': 150,
         'desc': 'Lunettes anti-projection'},
        {'name': 'Gants Anti-coupure', 'icon': '🧤', 'price': 20, 'weight': 0.2, 'protection': 15, 'durability': 200,
         'desc': 'Gants protection anti-coupure'},
        {'name': 'Gants Anti-chaleur', 'icon': '🧤', 'price': 30, 'weight': 0.3, 'protection': 20, 'durability': 150,
         'desc': 'Gants isolation thermique'},
        {'name': 'Chaussures Securite S3', 'icon': '👢', 'price': 80, 'weight': 1.4, 'protection': 40, 'durability': 600,
         'desc': 'Chaussures securite norme S3'},
        {'name': 'Pantalon Renforce Cordura', 'icon': '👖', 'price': 90, 'weight': 1.0, 'protection': 25, 'durability': 400,
         'desc': 'Pantalon ultra-resistant'},
        {'name': 'Gilet Fluorescent', 'icon': '🦺', 'price': 12, 'weight': 0.2, 'protection': 1, 'durability': 100,
         'desc': 'Gilet haute visibilite'},
        {'name': 'Casque Anti-bruit', 'icon': '🎧', 'price': 40, 'weight': 0.4, 'protection': 5, 'durability': 300,
         'desc': 'Protection auditive'},
        {'name': 'Genouilleres Pro', 'icon': '🦿', 'price': 35, 'weight': 0.5, 'protection': 20, 'durability': 250,
         'desc': 'Genouilleres carreleur/jardinage'},
        {'name': 'Tablier Cuir Soudeur', 'icon': '👔', 'price': 70, 'weight': 1.2, 'protection': 35, 'durability': 400,
         'desc': 'Tablier protection soudage'},
        {'name': 'Vetements Anti-pluie Pro', 'icon': '🧥', 'price': 60, 'weight': 1.0, 'protection': 15, 'durability': 250,
         'desc': 'Ensemble impermeable agricole'},
        {'name': 'Harnais Antichute', 'icon': '🪢', 'price': 200, 'weight': 2.0, 'protection': 100, 'durability': 1000,
         'desc': 'Harnais securite travail hauteur'},
    ],

    # ========== PROTECTION DISCRETE ==========
    'discret': [
        {'name': 'Veste Kevlar Casual', 'icon': '🧥', 'price': 400, 'weight': 2.0, 'protection': 70, 'durability': 600,
         'desc': 'Veste look civil avec soft-armor'},
        {'name': 'Hoodie Anti-coupure', 'icon': '🧥', 'price': 150, 'weight': 0.8, 'protection': 35, 'durability': 300,
         'desc': 'Sweat renforce discret'},
        {'name': 'Gants Tactiles Anti-coupure', 'icon': '🧤', 'price': 45, 'weight': 0.15, 'protection': 18, 'durability': 200,
         'desc': 'Gants smartphone anti-lame'},
        {'name': 'Sac Anti-lame', 'icon': '🎒', 'price': 120, 'weight': 0.8, 'protection': 20, 'durability': 400,
         'desc': 'Sac a dos renforce anti-vol'},
        {'name': 'Chaussures Renforcees Urbain', 'icon': '👟', 'price': 140, 'weight': 1.0, 'protection': 25, 'durability': 450,
         'desc': 'Chaussures protection discrete'},
        {'name': 'Coque Dorsale Fine', 'icon': '🛡️', 'price': 80, 'weight': 0.5, 'protection': 30, 'durability': 350,
         'desc': 'Protection dos sous vetement'},
        {'name': 'Tour de Cou Filtrant', 'icon': '🧣', 'price': 25, 'weight': 0.1, 'protection': 8, 'durability': 120,
         'desc': 'Tour de cou masque/filtre'},
        {'name': 'Lunettes Anti-eblouissement', 'icon': '🕶️', 'price': 50, 'weight': 0.05, 'protection': 5, 'durability': 150,
         'desc': 'Lunettes protection discrete'},
    ],
}

def create_clothing_items():
    """Create all clothing and equipment items"""
    created_count = 0
    updated_count = 0

    for category, items in CLOTHING_DATA.items():
        print(f'\n=== {category.upper()} ===')

        for item_data in items:
            name = item_data['name']

            # Check if exists
            material, created = Material.objects.get_or_create(
                name=name,
                defaults={
                    'description': item_data['desc'],
                    'icon': item_data['icon'],
                    'category': 'equipement',
                    'rarity': 'common' if item_data['price'] < 100 else 'uncommon' if item_data['price'] < 300 else 'rare',
                    'weight': item_data['weight'],
                    'is_equipment': True,
                    'is_food': False,
                    'max_durability': item_data['durability'],
                    'defense': item_data['protection'],
                    'attack': 0,
                    'speed_bonus': 0,
                    'equipment_slot': 'body',  # Most are body items
                }
            )

            if created:
                print(f'  [+] {name} (Protection: {item_data["protection"]}, Prix: {item_data["price"]})')
                created_count += 1
            else:
                # Update existing
                material.description = item_data['desc']
                material.icon = item_data['icon']
                material.weight = item_data['weight']
                material.max_durability = item_data['durability']
                material.defense = item_data['protection']
                material.save()
                print(f'  [~] {name} (mis a jour)')
                updated_count += 1

    print(f'\n=== RESUME ===')
    print(f'Crees: {created_count}')
    print(f'Mis a jour: {updated_count}')
    print(f'Total: {created_count + updated_count}')

    return created_count, updated_count

if __name__ == '__main__':
    print('Creation des vetements et equipements...')
    create_clothing_items()
    print('\nTermine!')
