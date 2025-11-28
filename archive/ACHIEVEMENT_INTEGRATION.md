# Intégration complète du système d'Achievements

**Date:** 21 novembre 2024

## ✅ Backend - 100% Complété

### 📦 Fichiers créés/modifiés

#### Nouveaux fichiers backend
- ✅ `game/models.py` - Ajout des modèles `Achievement` et `PlayerAchievement`
- ✅ `game/services/achievement_service.py` - Service complet de gestion des achievements
- ✅ `game/views/achievement_views.py` - ViewSet REST pour les achievements
- ✅ `game/serializers.py` - Ajout de `AchievementSerializer` et `PlayerAchievementSerializer`
- ✅ `game/management/commands/populate_achievements.py` - Commande pour peupler les achievements
- ✅ `game/migrations/0015_achievement_playerachievement.py` - Migration initiale
- ✅ `game/migrations/0016_alter_playerachievement_player.py` - Migration ajustement
- ✅ `game/admin.py` - Interface admin pour gérer les achievements
- ✅ `game/urls.py` - Routes API pour les achievements

#### Fichiers modifiés
- ✅ `game/services/map_service.py` - Intégration du tracking dans `gather_material()`
- ✅ `game/services/crafting_service.py` - Intégration du tracking dans `craft_recipe()`
- ✅ `game/services/player_service.py` - Intégration du tracking dans `move_player()`
- ✅ `game/views/player_views.py` - Ajout des achievements dans la réponse de mouvement

### 🎯 API Endpoints créés

Tous les endpoints sont préfixés par `/api/achievements/`

1. **GET /api/achievements/**
   - Liste tous les achievements (masque les hidden non-débloqués)
   - Accessible aux utilisateurs authentifiés

2. **GET /api/achievements/{id}/**
   - Détails d'un achievement spécifique

3. **GET /api/achievements/my_progress/**
   - Progression du joueur actuel
   - Retourne les achievements complétés et en cours

4. **GET /api/achievements/by_category/**
   - Achievements groupés par catégorie (Exploration, Gathering, Crafting, etc.)
   - Inclut les statistiques par catégorie

5. **GET /api/achievements/recent/**
   - Les 10 derniers achievements débloqués

### 📊 Données peuplées

**17 Achievements initiaux** répartis en 6 catégories :

#### Exploration (3)
- 👣 **Premier Pas** - 1 déplacement (10 XP)
- 🗺️ **Explorateur** - 100 déplacements (100 XP)
- 🌍 **Grand Voyageur** - 1000 déplacements (500 XP)

#### Gathering (3)
- 🌾 **Première Récolte** - 1 récolte (10 XP)
- 🧺 **Collecteur** - 50 récoltes (50 XP)
- 👑 **Maître Collecteur** - 500 récoltes (250 XP)

#### Crafting (3)
- 🔨 **Premier Craft** - 1 craft (10 XP)
- ⚒️ **Artisan** - 25 crafts (50 XP)
- 🏭 **Maître Artisan** - 100 crafts (200 XP)

#### Progression (3)
- ⭐ **Niveau 5** - Niveau 5 atteint (50 XP)
- ⭐⭐ **Niveau 10** - Niveau 10 atteint (100 XP)
- ⭐⭐⭐ **Niveau 20** - Niveau 20 atteint (500 XP)

#### Collection (3)
- 🪓 **Bûcheron** - 10 récoltes de Bois (25 XP)
- ⛏️ **Mineur** - 10 récoltes de Pierre (25 XP)
- 💎 **Chercheur de Diamants** - 1 Diamant [CACHÉ] (100 XP)

#### Combat (2)
- ⚔️ **Premier Sang** - 1 monstre vaincu (20 XP)
- 🏹 **Chasseur** - 10 monstres vaincus (100 XP)

### ⚙️ Fonctionnement

#### Tracking automatique
Les achievements sont automatiquement trackés lors des actions :

```python
# Exemple de récolte
gather_material(player, cell, material_id)
  → Incrémente les compteurs d'achievements
  → Vérifie les conditions de complétion
  → Attribue les XP bonus si complété
  → Retourne les achievements débloqués dans la réponse
```

#### Types de tracking supportés
- **gather_count** - Nombre total de récoltes
- **craft_count** - Nombre total de crafts
- **move_count** - Nombre de déplacements
- **level_reached** - Niveau du joueur
- **material_collected** - Matériau spécifique récolté
- **recipe_crafted** - Recette spécifique craftée
- **biome_visited** - Biome visité
- **mob_defeated** - Monstre vaincu

#### Format de réponse API

Lorsqu'un achievement est débloqué, il apparaît dans la réponse :

```json
{
  "message": "Récolté 3x Bois",
  "gathered": 3,
  "remaining": 47,
  "achievements_unlocked": [
    {
      "name": "Première Récolte",
      "description": "Récoltez votre premier matériau",
      "icon": "🌾",
      "reward_xp": 10
    }
  ]
}
```

### 🔧 Utilisation dans le code

#### Vérifier les achievements manuellement

```python
from game.services.achievement_service import check_achievements

# Après une action
new_achievements = check_achievements(
    player,
    'gather',  # Type d'événement
    material_name='Bois'  # Données contextuelles
)

# Retourne une liste d'achievements débloqués
for achievement in new_achievements:
    print(f"Débloqué: {achievement.name}")
```

#### Récupérer la progression d'un joueur

```python
from game.services.achievement_service import AchievementService

result = AchievementService.get_player_achievements(player)

# result['completed'] - Achievements complétés
# result['in_progress'] - Achievements en cours
```

### 👨‍💼 Interface Admin Django

Les achievements sont gérables via l'admin Django :

**Achievements** (`/admin/game/achievement/`)
- Liste avec filtres par catégorie et type
- Recherche par nom et description
- Création/édition d'achievements personnalisés

**Player Achievements** (`/admin/game/playerachievement/`)
- Vue de la progression de chaque joueur
- Filtres par statut et catégorie
- Recherche par joueur et achievement

---

## 🎨 Frontend - À implémenter

Le backend est prêt ! Pour compléter l'intégration côté frontend :

### API Service

Créer `frontend/src/services/achievementsAPI.js` :

```javascript
import api from './api';

export const achievementsAPI = {
  // Récupérer tous les achievements
  getAll: () => api.get('/achievements/'),

  // Progression du joueur
  getMyProgress: () => api.get('/achievements/my_progress/'),

  // Par catégorie
  getByCategory: () => api.get('/achievements/by_category/'),

  // Récents
  getRecent: () => api.get('/achievements/recent/'),
};
```

### Composants suggérés

1. **AchievementsTab.js** - Onglet principal
   - Liste des achievements par catégorie
   - Barre de progression
   - Filtres par statut (All / Completed / In Progress)

2. **AchievementCard.js** - Carte individuelle
   - Icône, nom, description
   - Barre de progression
   - Badge "Completed" si débloqué

3. **AchievementNotification.js** - Toast notification
   - S'affiche quand un achievement est débloqué
   - Animation, son (optionnel)
   - Auto-disparaît après 5 secondes

4. **AchievementBadge.js** - Badge mini
   - Pour afficher dans le profil joueur
   - Total achievements débloqués

### Gestion des notifications

Dans `App.js` ou un composant parent, écouter les achievements dans les réponses API :

```javascript
// Après gather, craft, move
const handleGather = async (cellId, materialId) => {
  const response = await mapAPI.gather(cellId, materialId);

  // Vérifier les achievements débloqués
  if (response.data.achievements_unlocked) {
    response.data.achievements_unlocked.forEach(ach => {
      showNotification({
        type: 'achievement',
        title: `Achievement débloqué !`,
        message: `${ach.icon} ${ach.name}`,
        description: ach.description,
        xp: ach.reward_xp
      });
    });
  }

  // Mettre à jour l'inventaire...
};
```

### Zustand Store (optionnel)

Ajouter au store existant :

```javascript
// Dans useGameStore.js
achievements: [],
achievementProgress: {},

setAchievements: (achievements) => set({ achievements }),
setAchievementProgress: (progress) => set({ achievementProgress: progress }),

fetchAchievements: async () => {
  const { data } = await achievementsAPI.getByCategory();
  set({ achievements: data });
},
```

---

## 📝 Tests

### Tester le backend

```bash
# 1. Migrations appliquées
python manage.py migrate

# 2. Achievements peuplés
python manage.py populate_achievements

# 3. Créer un utilisateur de test
python manage.py createsuperuser

# 4. Lancer le serveur
python manage.py runserver

# 5. Tester les endpoints
curl http://localhost:8000/api/achievements/
curl http://localhost:8000/api/achievements/my_progress/
```

### Tester le tracking

1. Se connecter au jeu
2. Effectuer un déplacement → Achievement "Premier Pas" se débloque
3. Récolter un matériau → Achievement "Première Récolte" se débloque
4. Crafter un objet → Achievement "Premier Craft" se débloque

Les achievements apparaissent dans la réponse API avec `achievements_unlocked`.

---

## 🚀 Commandes utiles

```bash
# Peupler les achievements
python manage.py populate_achievements

# Accéder à l'admin
# http://localhost:8000/admin

# Shell Django pour tests
python manage.py shell
>>> from game.models import Player, Achievement, PlayerAchievement
>>> achievements = Achievement.objects.all()
>>> for ach in achievements:
...     print(f"{ach.icon} {ach.name}")
```

---

## 📚 Documentation API complète

### GET /api/achievements/my_progress/

**Réponse:**
```json
{
  "completed": [
    {
      "achievement": {
        "id": 1,
        "name": "Premier Pas",
        "description": "Effectuez votre premier déplacement",
        "icon": "👣",
        "category": "exploration",
        "requirement_type": "move_count",
        "requirement_value": 1,
        "reward_xp": 10,
        "hidden": false
      },
      "progress": 1,
      "completed_at": "2024-11-21T10:30:00Z"
    }
  ],
  "in_progress": [
    {
      "achievement": {
        "id": 2,
        "name": "Explorateur",
        "description": "Parcourez 100 cases",
        "icon": "🗺️",
        "category": "exploration",
        "requirement_type": "move_count",
        "requirement_value": 100,
        "reward_xp": 100,
        "hidden": false
      },
      "progress": 15,
      "max_progress": 100
    }
  ],
  "stats": {
    "total_completed": 1,
    "total_available": 17
  }
}
```

### GET /api/achievements/by_category/

**Réponse:**
```json
[
  {
    "category": "exploration",
    "achievements": [
      {
        "id": 1,
        "name": "Premier Pas",
        "progress": 1,
        "completed": true,
        "progress_percentage": 100
      },
      {
        "id": 2,
        "name": "Explorateur",
        "progress": 15,
        "completed": false,
        "progress_percentage": 15
      }
    ],
    "completed_count": 1,
    "total_count": 3
  }
]
```

---

## ✨ Résumé

### Ce qui est fait ✅
- ✅ Modèles Achievement et PlayerAchievement
- ✅ Service de tracking automatique
- ✅ API REST complète avec 5 endpoints
- ✅ Integration dans gather, craft, move
- ✅ 17 achievements initiaux
- ✅ Interface admin Django
- ✅ Migrations appliquées
- ✅ Récompenses XP automatiques
- ✅ Achievements cachés supportés
- ✅ Tests backend fonctionnels

### Ce qui reste à faire 🔨
- 🔨 Frontend: Composants React pour l'affichage
- 🔨 Frontend: Notifications visuelles
- 🔨 Frontend: Onglet Achievements dans l'UI
- 🔨 Frontend: Son/animation pour débloquage (optionnel)

Le système backend est **100% opérationnel** et prêt à être utilisé ! 🎉
