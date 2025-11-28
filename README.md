# Crafting Game avec OpenStreetMap

Un jeu de craft et d'exploration utilisant OpenStreetMap comme base pour la carte. Les joueurs peuvent se déplacer sur une grille, récolter des matériaux et fabriquer des objets.

## Fonctionnalités

- Carte interactive basée sur OpenStreetMap divisée en cellules
- Système de déplacement en grille (Nord, Sud, Est, Ouest)
- Collecte de matériaux dans chaque cellule
- Système de craft avec des recettes
- Gestion d'inventaire
- Système d'énergie et d'expérience
- Interface Material-UI moderne

## Technologies

### Backend
- Django 4.2
- Django REST Framework
- SQLite
- Python 3.x

### Frontend
- React
- Material-UI
- React-Leaflet (OpenStreetMap)
- Axios

## Installation

### Backend

1. Créer l'environnement virtuel (optionnel mais recommandé):
```bash
cd crafting_game
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Installer les dépendances:
```bash
pip install django djangorestframework django-cors-headers
```

3. Appliquer les migrations:
```bash
python manage.py migrate
```

4. Créer un superutilisateur:
```bash
python manage.py createsuperuser
```

5. Peupler la base de données avec les matériaux et recettes:
```bash
python manage.py populate_data
```

6. Lancer le serveur Django:
```bash
python manage.py runserver
```

Le backend sera accessible sur http://localhost:8000

### Frontend

1. Aller dans le dossier frontend:
```bash
cd frontend
```

2. Installer les dépendances:
```bash
npm install
```

3. Lancer l'application React:
```bash
npm start
```

Le frontend sera accessible sur http://localhost:3000

## Utilisation

1. Créez un compte ou connectez-vous avec le superutilisateur créé
2. Explorez la carte avec les boutons de déplacement (Nord, Sud, Est, Ouest)
3. Récoltez des matériaux dans chaque cellule (coûte 5 points d'énergie)
4. Consultez votre inventaire dans l'onglet "Inventory"
5. Fabriquez des objets dans l'onglet "Crafting"

## Matériaux disponibles

- Bois (Wood)
- Pierre (Stone)
- Minerai de fer (Iron Ore)
- Charbon (Coal)
- Minerai d'or (Gold Ore)
- Diamant (Diamond)

## Objets craftables

- Planches (4 planches depuis 1 bois)
- Bâtons (4 bâtons depuis 2 planches)
- Lingot de fer (1 lingot depuis 1 minerai de fer + 1 charbon)
- Lingot d'or (1 lingot depuis 1 minerai d'or + 2 charbons)
- Pioche (1 pioche depuis 3 lingots de fer + 2 bâtons)
- Épée (1 épée depuis 2 lingots de fer + 1 bâton)

## Architecture

### Backend (Django)

**Models:**
- `Material`: Les matériaux de base
- `Recipe`: Les recettes de craft
- `RecipeIngredient`: Les ingrédients d'une recette
- `Player`: Le profil du joueur
- `Inventory`: L'inventaire du joueur
- `MapCell`: Une cellule de la carte
- `CellMaterial`: Les matériaux disponibles dans une cellule
- `GatheringLog`: Historique des récoltes
- `CraftingLog`: Historique des crafts

**API Endpoints:**
- `/api/materials/` - Liste des matériaux
- `/api/recipes/` - Liste des recettes
- `/api/players/me/` - Profil du joueur
- `/api/players/{id}/move/` - Déplacer le joueur
- `/api/inventory/` - Inventaire du joueur
- `/api/map/current/` - Cellule actuelle
- `/api/map/{id}/gather/` - Récolter un matériau
- `/api/crafting/craft/` - Fabriquer un objet

### Frontend (React)

**Components:**
- `Login`: Écran de connexion
- `GameMap`: Carte OpenStreetMap avec contrôles de mouvement
- `PlayerStats`: Statistiques du joueur (énergie, niveau, XP)
- `Inventory`: Liste des matériaux possédés
- `CraftingPanel`: Interface de craft avec recettes

## Admin Django

Accédez à l'interface d'administration sur http://localhost:8000/admin pour:
- Gérer les joueurs
- Ajouter/modifier des matériaux
- Créer de nouvelles recettes
- Voir les logs de craft et récolte

## Développement futur

Idées d'amélioration:
- Régénération automatique des matériaux dans les cellules
- Système de combat
- Multi-joueur avec vision des autres joueurs
- Biomes avec matériaux spécifiques
- Quêtes et objectifs
- Commerce entre joueurs
- Construction de bâtiments
