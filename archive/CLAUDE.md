# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A crafting and exploration game using OpenStreetMap as the map base. Players move on a grid, gather materials from cells with different biomes, craft items using recipes, and consume food to restore energy. Built with Django REST Framework backend and React Material-UI frontend.

## Development Commands

### Backend (Django)

Run from project root directory:

```bash
# Start virtual environment (Windows)
venv\Scripts\activate

# Start virtual environment (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install django djangorestframework django-cors-headers

# Run migrations
python manage.py migrate

# Populate initial data (materials and recipes)
python manage.py populate_data

# Create superuser
python manage.py createsuperuser

# Start Django server (http://localhost:8000)
python manage.py runserver

# Access admin panel
# http://localhost:8000/admin
```

### Frontend (React)

Run from `frontend/` directory:

```bash
# Install dependencies
npm install

# Start development server (http://localhost:3000)
npm start

# Build production bundle
npm build

# Run tests
npm test
```

## Architecture

### Backend Structure

Django REST API with token authentication. The `game` app contains all models, views, and serializers.

**Core Models:**
- `Player`: User profile with position (lat/lon and grid coordinates), energy, level, experience. Linked to Django User via OneToOne.
- `MapCell`: Grid cell at (grid_x, grid_y) with center coordinates, biome type (plains/forest/mountain/water), and last regeneration timestamp.
- `Material`: Items in the game with name, rarity, icon, and food properties (is_food, energy_restore).
- `Inventory`: Links Player to Material with quantity. Unique constraint on (player, material).
- `CellMaterial`: Links MapCell to Material with current and max quantity.
- `Recipe`: Defines crafting outputs (result_material, result_quantity).
- `RecipeIngredient`: Links Recipe to Material ingredients with required quantity.
- `GatheringLog` and `CraftingLog`: Activity logs.

**Key API Endpoints:**
- `GET /api/players/me/` - Get current player profile (creates if doesn't exist)
- `POST /api/players/{id}/move/` - Move player (direction: north/south/east/west). Costs 1 energy, creates new MapCells on demand with biome-specific materials
- `POST /api/players/restart/` - Reset player to initial state, clear inventory and logs
- `GET /api/map/current/` - Get current cell with available materials
- `POST /api/map/{id}/gather/` - Gather material from cell (costs 5 energy, adds 2*quantity XP)
- `GET /api/inventory/` - Get player's inventory (only items with quantity > 0)
- `POST /api/inventory/{id}/consume/` - Consume food item to restore energy
- `POST /api/crafting/craft/` - Craft items (checks ingredients, deducts from inventory, adds result, grants 10*quantity XP)
- `GET /api/materials/` - List all materials
- `GET /api/recipes/` - List all recipes with ingredients

**Biome System:**
- Cell (0,0) is always plains at Valence center (44.933°N, 4.893°E)
- New cells randomly assigned plains/forest/mountain biome
- Water cells block movement
- Each biome spawns specific materials with rarity-based quantities
- Material quantities: legendary (1-5), rare (5-15), uncommon (10-30), common (15-50)

**Energy System:**
- Players start with 100/100 energy
- Moving costs 1 energy per cell
- Gathering costs 5 energy per action
- Food items restore energy when consumed

### Frontend Structure

React app with Material-UI components. Uses Axios with token authentication interceptor.

**Main Components:**
- `App.js`: Root component managing auth state, player data, inventory, and tabs
- `Login.js`: Authentication form
- `GameMap.js`: Leaflet map showing player position with N/S/E/W movement buttons and current cell materials
- `PlayerStats.js`: Displays energy bar, level, and XP progress
- `Inventory.js`: Lists player's materials with consume button for food items
- `CraftingPanel.js`: Shows available recipes, checks craftable status, handles crafting with quantity input

**API Service (`services/api.js`):**
- Centralized Axios instance with base URL http://localhost:8000/api
- Token stored in localStorage, added to headers via interceptor
- Exports: authAPI, playerAPI, materialsAPI, recipesAPI, inventoryAPI, mapAPI, craftingAPI

**State Management:**
- Player and inventory state managed in App.js
- Token-based auth persisted in localStorage
- Automatic data refresh after movement, gathering, crafting, and consumption

### Data Flow

1. Player moves: Frontend calls `playerAPI.move()` → Backend updates Player position, creates/fetches MapCell with biome materials → Frontend refreshes map
2. Player gathers: Frontend calls `mapAPI.gather()` with cell and material IDs → Backend checks energy, deducts from CellMaterial, adds to Inventory, creates GatheringLog → Frontend refreshes inventory
3. Player crafts: Frontend calls `craftingAPI.craft()` with recipe ID and quantity → Backend verifies ingredients, deducts materials, adds result, creates CraftingLog → Frontend refreshes inventory
4. Player consumes food: Frontend calls `inventoryAPI.consume()` → Backend checks if food, deducts quantity, restores energy → Frontend refreshes player stats

### Authentication

- Django REST Framework Token Authentication
- Login endpoint: `POST /api/auth/login/` (returns token)
- Token stored in localStorage on frontend
- Token sent in Authorization header: `Token <token>`
- 401 responses trigger logout and redirect to login

### Database

SQLite database (`db.sqlite3`) in project root. Models use Django ORM.

**Important Relationships:**
- Player.user → User (OneToOne)
- Inventory: unique_together (player, material)
- CellMaterial: unique_together (cell, material)
- Recipe → RecipeIngredient (ForeignKey with related_name='ingredients')
- MapCell: unique_together (grid_x, grid_y)

### Custom Management Command

`python manage.py populate_data` creates initial materials and recipes:
- Base materials: Wood, Stone, Iron Ore, Coal, Gold Ore, Diamond
- Crafted materials: Planks, Stick, Iron Bar, Gold Bar, Pickaxe, Sword
- Recipes: Wood→Planks(4), Planks(2)→Stick(4), Iron Ore+Coal→Iron Bar, Gold Ore+Coal(2)→Gold Bar, Iron Bar(3)+Stick(2)→Pickaxe, Iron Bar(2)+Stick→Sword

### Configuration Notes

- Backend runs on port 8000, frontend on port 3000
- CORS enabled for all origins (CORS_ALLOW_ALL_ORIGINS = True)
- REST Framework uses TokenAuthentication and SessionAuthentication
- Default permission: IsAuthenticatedOrReadOnly
- Database: SQLite at project root
- Static files: STATIC_URL = 'static/'
- DEBUG = True (change for production)
- SECRET_KEY is hardcoded (change for production)

## Key Implementation Details

**Grid Movement:**
- Each cell represents approximately 100m
- Latitude offset: ±0.0009 per cell (N/S)
- Longitude offset: ±0.0009 per cell (E/W)
- Negative grid coordinates allowed

**Player Creation:**
- Player objects auto-created on first `/api/players/me/` call if user exists but has no Player
- Default spawn: Valence center (44.933, 4.893) at grid (0, 0)

**Material Gathering:**
- Random gather amount: 1-5 items per action
- Limited by available CellMaterial.quantity
- Materials can be depleted (quantity reaches 0)

**Recipe System:**
- Recipes can have multiple ingredients (RecipeIngredient)
- Crafting supports batch quantities (multiplies ingredient requirements and results)
- All ingredients must be available in exact or greater quantities

**Food/Energy System:**
- Materials with is_food=True can be consumed
- Consumption restores energy_restore amount
- Energy capped at max_energy (100 by default)
- Players can run out of energy but game continues
