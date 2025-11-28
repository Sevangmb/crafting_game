"""
Catégories pour organiser les matériaux et recettes
"""

# Catégories de matériaux
MATERIAL_CATEGORIES = {
    'materiaux_bruts': {
        'name': 'Matériaux Bruts',
        'icon': '🌿',
        'materials': [
            'Bois', 'Pierre', 'Minerai de Fer', 'Minerai d\'Or', 'Charbon', 
            'Minerai de Cuivre', 'Minerai d\'Argent', 'Minerai de Platine',
            'Sable', 'Argile', 'Caillou', 'Gravier', 'Minerai d\'Étain'
        ]
    },
    'materiaux_elabores': {
        'name': 'Matériaux Élaborés',
        'icon': '🛠️',
        'materials': [
            'Planche', 'Barre de Fer', 'Barre d\'Or', 'Barre de Cuivre',
            'Barre d\'Argent', 'Barre de Platine', 'Brique', 'Verre',
            'Barre d\'Étain', 'Alliage de Bronze', 'Alliage d\'Acier'
        ]
    },
    'nourriture': {
        'name': 'Nourriture',
        'icon': '🍎',
        'materials': [
            'Pomme', 'Banane', 'Raisin', 'Fraise', 'Orange', 'Myrtille',
            'Carotte', 'Tomate', 'Salade', 'Poivron', 'Aubergine', 'Brocoli',
            'Champignon', 'Pain', 'Poisson', 'Viande', 'Œuf', 'Lait',
            'Fromage', 'Beurre', 'Farine', 'Sucre', 'Sel', 'Épices'
        ]
    },
    'outils': {
        'name': 'Outils',
        'icon': '⚒️',
        'materials': [
            'Pioche', 'Hache', 'Marteau', 'Pelle', 'Faux', 'Couteau',
            'Pince', 'Tournevis', 'Scie', 'Mètre', 'Équerre', 'Niveau',
            'Burin', 'Lime', 'Ciseaux', 'Perceuse', 'Pince à épiler'
        ]
    },
    'armes': {
        'name': 'Armes',
        'icon': '⚔️',
        'materials': [
            'Épée', 'Bouclier', 'Arc', 'Flèche', 'Dague', 'Hache de guerre',
            'Masse d\'armes', 'Lance', 'Arbalète', 'Coutelas', 'Gourdin',
            'Javeline', 'Fronde', 'Cimeterre', 'Rapière', 'Glaive'
        ]
    },
    'materiaux_magiques': {
        'name': 'Matériaux Magiques',
        'icon': '✨',
        'materials': [
            'Cristal de mana', 'Poussière d\'étoile', 'Essence de feu',
            'Essence de glace', 'Essence de foudre', 'Pierre de lune',
            'Pierre solaire', 'Cristal d\'arc-en-ciel', 'Orbe mystique',
            'Parchemin ancien', 'Rune de puissance', 'Essence d\'âme'
        ]
    },
    'gemmes': {
        'name': 'Gemmes et Pierres Précieuses',
        'icon': '💎',
        'materials': [
            'Diamant', 'Rubis', 'Saphir', 'Émeraude', 'Topaze', 'Améthyste',
            'Opale', 'Jade', 'Perle', 'Onyx', 'Quartz', 'Aigue-marine',
            'Grenat', 'Turquoise', 'Lapis-lazuli', 'Jaspe', 'Malachite'
        ]
    },
    'textiles': {
        'name': 'Textiles et Cuir',
        'icon': '🧵',
        'materials': [
            'Laine', 'Coton', 'Soie', 'Lin', 'Cuir', 'Fourrure', 'Corde',
            'Tissu épais', 'Tissu fin', 'Cuir renforcé', 'Cuir de dragon',
            'Soie d\'araignée', 'Tissu enchanté', 'Cuir magique'
        ]
    },
    'potions': {
        'name': 'Potions et Composants',
        'icon': '🧪',
        'materials': [
            'Potion de soin', 'Potion de mana', 'Potion de force',
            'Potion de vitesse', 'Potion d\'invisibilité', 'Antidote',
            'Élixir de vie', 'Huile de pierre', 'Poudre de fée',
            'Extrait de mandragore', 'Larmes de phénix', 'Sang de dragon'
        ]
    },
    'divers': {
        'name': 'Divers',
        'icon': '📦',
        'materials': [
            'Clé', 'Pièce d\'or', 'Parchemin', 'Encre', 'Plume', 'Cire',
            'Coffre', 'Sceau', 'Boussole', 'Carte', 'Livre', 'Parchemin vide',
            'Cristal de téléportation', 'Bâton lumineux', 'Bombe fumigène'
        ]
    }
}

# Catégories de recettes
RECIPE_CATEGORIES = {
    'outillage': {
        'name': 'Outillage',
        'icon': '⚒️',
        'subcategories': {
            'outils_miniers': {
                'name': 'Outils Miniers',
                'recipes': [
                    'Fabriquer une pioche en pierre',
                    'Fabriquer une pioche en fer',
                    'Fabriquer une pioche en diamant',
                    'Fabriquer une pelle',
                    'Fabriquer une pioche en or'
                ]
            },
            'outils_forestiers': {
                'name': 'Outils Forestiers',
                'recipes': [
                    'Fabriquer une hache en pierre',
                    'Fabriquer une hache en fer',
                    'Fabriquer une serpe',
                    'Fabriquer une faux',
                    'Fabriquer un sécateur'
                ]
            },
            'outils_divers': {
                'name': 'Outils Divers',
                'recipes': [
                    'Fabriquer un marteau',
                    'Fabriquer un tournevis',
                    'Fabriquer une pince',
                    'Fabriquer une scie',
                    'Fabriquer un burin'
                ]
            }
        }
    },
    'construction': {
        'name': 'Construction',
        'icon': '🏗️',
        'subcategories': {
            'materiaux': {
                'name': 'Matériaux de Construction',
                'recipes': [
                    'Fabriquer des briques',
                    'Fabriquer du verre',
                    'Fabriquer du ciment',
                    'Fabriquer des tuiles',
                    'Fabriquer des poutres'
                ]
            },
            'meubles': {
                'name': 'Meubles',
                'recipes': [
                    'Fabriquer une table',
                    'Fabriquer une chaise',
                    'Fabriquer un lit',
                    'Fabriquer une étagère',
                    'Fabriquer un coffre'
                ]
            },
            'decoration': {
                'name': 'Décoration',
                'recipes': [
                    'Fabriquer un tapis',
                    'Fabriquer un tableau',
                    'Fabriquer une statue',
                    'Fabriquer un vase',
                    'Fabriquer un chandelier'
                ]
            }
        }
    },
    'cuisine': {
        'name': 'Cuisine',
        'icon': '🍳',
        'subcategories': {
            'plats_principaux': {
                'name': 'Plats Principaux',
                'recipes': [
                    'Cuisiner une quiche',
                    'Cuisiner une pizza',
                    'Cuisiner une omelette',
                    'Cuisiner un ragoût',
                    'Cuisiner un gratin'
                ]
            },
            'desserts': {
                'name': 'Desserts',
                'recipes': [
                    'Cuisiner un gâteau',
                    'Cuisiner des cookies',
                    'Cuisiner une tarte',
                    'Cuisiner un flan',
                    'Cuisiner une crème brûlée'
                ]
            },
            'boissons': {
                'name': 'Boissons',
                'recipes': [
                    'Préparer un jus de fruit',
                    'Préparer un smoothie',
                    'Préparer un thé',
                    'Préparer un café',
                    'Préparer un cocktail sans alcool'
                ]
            }
        }
    },
    'armurerie': {
        'name': 'Armurerie',
        'icon': '🛡️',
        'subcategories': {
            'armes_courtes': {
                'name': 'Armes Courbes',
                'recipes': [
                    'Forger une dague',
                    'Forger une épée courte',
                    'Forger un poignard',
                    'Forger un ciseau à bois',
                    'Forger un rasoir'
                ]
            },
            'armes_longues': {
                'name': 'Armes Longues',
                'recipes': [
                    'Forger une épée longue',
                    'Forger une rapière',
                    'Forger un cimeterre',
                    'Forger une épée à deux mains',
                    'Forger une lance'
                ]
            },
            'armures': {
                'name': 'Armures',
                'recipes': [
                    'Forger un casque',
                    'Forger un plastron',
                    'Forger des jambières',
                    'Forger des bottes',
                    'Forger un bouclier'
                ]
            }
        }
    },
    'alchimie': {
        'name': 'Alchimie',
        'icon': '🧪',
        'subcategories': {
            'potions': {
                'name': 'Potions',
                'recipes': [
                    'Préparer une potion de soin',
                    'Préparer une potion de mana',
                    'Préparer une potion de force',
                    'Préparer une potion de vitesse',
                    'Préparer une potion d\'invisibilité'
                ]
            },
            'poisons': {
                'name': 'Poisons',
                'recipes': [
                    'Préparer un poison lent',
                    'Préparer un poison violent',
                    'Préparer un poison paralysant',
                    'Préparer un poison de confusion',
                    'Préparer un antidote'
                ]
            },
            'encens': {
                'name': 'Encens et Parfums',
                'recipes': [
                    'Préparer un encens apaisant',
                    'Préparer un parfum envoûtant',
                    'Préparer un encens de méditation',
                    'Préparer un parfum de séduction',
                    'Préparer un encens de purification'
                ]
            }
        }
    },
    'artisanat': {
        'name': 'Artisanat',
        'icon': '🎨',
        'subcategories': {
            'bijoux': {
                'name': 'Bijoux',
                'recipes': [
                    'Fabriquer une bague',
                    'Fabriquer un collier',
                    'Fabriquer un bracelet',
                    'Fabriquer des boucles d\'oreilles',
                    'Fabriquer une couronne'
                ]
            },
            'vêtements': {
                'name': 'Vêtements',
                'recipes': [
                    'Coudre une tunique',
                    'Coudre une robe',
                    'Coudre un pantalon',
                    'Coudre une cape',
                    'Coudre des gants'
                ]
            },
            'accessoires': {
                'name': 'Accessoires',
                'recipes': [
                    'Fabriquer un sac',
                    'Fabriquer une ceinture',
                    'Fabriquer un chapeau',
                    'Fabriquer des bottes',
                    'Fabriquer une écharpe'
                ]
            }
        }
    },
    'magie': {
        'name': 'Magie',
        'icon': '🔮',
        'subcategories': {
            'parchemins': {
                'name': 'Parchemins',
                'recipes': [
                    'Créer un parchemin de boule de feu',
                    'Créer un parchemin de soin',
                    'Créer un parchemin de téléportation',
                    'Créer un parchemin d\'invisibilité',
                    'Créer un parchemin de protection'
                ]
            },
            'artefacts': {
                'name': 'Artefacts',
                'recipes': [
                    'Créer un bâton de feu',
                    'Créer une baguette de glace',
                    'Créer un anneau de régénération',
                    'Créer une amulette de protection',
                    'Créer une pierre de rappel'
                ]
            },
            'runes': {
                'name': 'Runes',
                'recipes': [
                    'Graver une rune de feu',
                    'Graver une rune de glace',
                    'Graver une rune de foudre',
                    'Graver une rune de vie',
                    'Graver une rune de protection'
                ]
            }
        }
    },
    'agriculture': {
        'name': 'Agriculture',
        'icon': '🌱',
        'subcategories': {
            'outils': {
                'name': 'Outils Agricoles',
                'recipes': [
                    'Fabriquer une faucille',
                    'Fabriquer un râteau',
                    'Fabriquer une binette',
                    'Fabriquer un arrosoir',
                    'Fabriquer un panier'
                ]
            },
            'graines': {
                'name': 'Graines et Plants',
                'recipes': [
                    'Préparer des graines de blé',
                    'Préparer des graines de carotte',
                    'Préparer des graines de tomate',
                    'Préparer des graines de pomme de terre',
                    'Préparer des graines de fraise'
                ]
            },
            'engrais': {
                'name': 'Engrais et Soins',
                'recipes': [
                    'Fabriquer un engrais naturel',
                    'Fabriquer un pesticide',
                    'Fabriquer un fongicide',
                    'Fabriquer un accélérateur de croissance',
                    'Fabriquer un produit de conservation'
                ]
            }
        }
    },
    'menuiserie': {
        'name': 'Menuiserie',
        'icon': '🪑',
        'subcategories': {
            'meubles': {
                'name': 'Meubles',
                'recipes': [
                    'Fabriquer une table en bois',
                    'Fabriquer une chaise en bois',
                    'Fabriquer une étagère en bois',
                    'Fabriquer un lit en bois',
                    'Fabriquer une armoire en bois'
                ]
            },
            'ustensiles': {
                'name': 'Ustensiles',
                'recipes': [
                    'Fabriquer une cuillère en bois',
                    'Fabriquer une fourchette en bois',
                    'Fabriquer un bol en bois',
                    'Fabriquer une assiette en bois',
                    'Fabriquer un verre en bois'
                ]
            },
            'décoration': {
                'name': 'Décoration',
                'recipes': [
                    'Fabriquer un cadre en bois',
                    'Fabriquer une statue en bois',
                    'Fabriquer un jouet en bois',
                    'Fabriquer un instrument de musique en bois',
                    'Fabriquer un coffret en bois'
                ]
            }
        }
    },
    'métallurgie': {
        'name': 'Métallurgie',
        'icon': '🔥',
        'subcategories': {
            'lingots': {
                'name': 'Lingots et Alliages',
                'recipes': [
                    'Fondre du minerai de fer',
                    'Fondre du minerai d\'or',
                    'Fondre du minerai d\'argent',
                    'Créer un alliage de bronze',
                    'Créer un alliage d\'acier'
                ]
            },
            'composants': {
                'name': 'Composants',
                'recipes': [
                    'Forger un ressort',
                    'Forger un engrenage',
                    'Forger une chaîne',
                    'Forger une charnière',
                    'Forger un cadenas'
                ]
            },
            'outils_avancés': {
                'name': 'Outils Avancés',
                'recipes': [
                    'Forger une scie circulaire',
                    'Forger une perceuse',
                    'Forger une pince coupante',
                    'Forger un marteau-piqueur',
                    'Forger une clé à molette'
                ]
            }
        }
    }
}
