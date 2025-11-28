# Système de Quêtes - Documentation Complète

**Date**: 26 Novembre 2025
**Status**: ✅ Complété et Opérationnel

---

## 🎯 Vue d'Ensemble

Un système de quêtes complet a été intégré au jeu, offrant des missions avec objectifs, progression, et récompenses. Le système inclut également des événements dynamiques sur la carte.

---

## ✨ Fonctionnalités Implémentées

### 1. Système de Quêtes

**Modèles créés:**
- **Quest** - Définition des quêtes avec objectifs et récompenses
- **PlayerQuest** - Suivi de progression des joueurs
- **DynamicEvent** - Événements aléatoires sur la carte

**Types de quêtes supportés:**
- 🌾 **Gather** - Récolter des matériaux
- 🔨 **Craft** - Fabriquer des objets
- 🗺️ **Explore** - Explorer le monde
- ⚔️ **Combat** - Vaincre des monstres
- 📦 **Delivery** - Livraisons
- 💬 **Talk** - Dialogues avec PNJ

**Niveaux de difficulté:**
- Facile (Easy)
- Moyen (Medium)
- Difficile (Hard)
- Épique (Epic)

---

## 📊 Structure des Données

### Modèle Quest

```python
class Quest(models.Model):
    # Informations de base
    name = CharField(max_length=200)
    description = TextField()
    story_text = TextField()  # Narration
    icon = CharField(max_length=50)

    # Propriétés
    quest_type = CharField(choices=QUEST_TYPES)
    difficulty = CharField(choices=QUEST_DIFFICULTIES)
    required_level = IntegerField(default=1)

    # Objectifs (JSON)
    requirements = JSONField(default=dict)
    # Format: {
    #   'gather': [{'material_id': 1, 'quantity': 10}],
    #   'craft': [{'recipe_id': 5, 'quantity': 3}],
    #   'visit': [{'grid_x': 5, 'grid_y': 10}],
    #   'defeat': [{'mob_id': 2, 'quantity': 5}]
    # }

    # Récompenses
    reward_xp = IntegerField(default=0)
    reward_money = IntegerField(default=0)
    reward_items = JSONField(default=list)
    # Format: [{'material_id': 1, 'quantity': 5}]

    # Système de chaîne
    prerequisite_quest = ForeignKey('self', null=True, blank=True)
    is_repeatable = BooleanField(default=False)
    cooldown_hours = IntegerField(default=24)
```

### Modèle PlayerQuest

```python
class PlayerQuest(models.Model):
    player = ForeignKey(Player)
    quest = ForeignKey(Quest)
    status = CharField(choices=[
        'available', 'active', 'completed',
        'failed', 'abandoned'
    ])

    # Progression (JSON)
    progress = JSONField(default=dict)
    # Format: {
    #   'gather': {'material_1': 5, 'material_2': 10},
    #   'craft': {'recipe_5': 2},
    #   'visit': {'5,10': True},
    #   'defeat': {'mob_2': 3}
    # }

    # Timestamps
    accepted_at = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    can_repeat_at = DateTimeField(null=True)
    times_completed = IntegerField(default=0)

    def progress_percentage(self):
        # Calcule le pourcentage de complétion
        ...
```

---

## 🔌 API Endpoints

### Quêtes

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/quests/` | GET | Liste toutes les quêtes actives |
| `/api/quests/{id}/` | GET | Détails d'une quête |
| `/api/quests/available/` | GET | Quêtes disponibles pour le joueur |
| `/api/quests/active/` | GET | Quêtes actives du joueur |
| `/api/quests/completed/` | GET | Quêtes complétées |
| `/api/quests/{id}/accept/` | POST | Accepter une quête |
| `/api/quests/{id}/abandon/` | POST | Abandonner une quête |
| `/api/quests/stats/` | GET | Statistiques du joueur |

### Événements Dynamiques

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/events/` | GET | Liste des événements actifs |
| `/api/events/nearby/` | GET | Événements à proximité (`?radius=5`) |
| `/api/events/{id}/participate/` | POST | Participer à un événement |

---

## 🎮 Intégration avec le Gameplay

### Tracking Automatique

Le système de quêtes est automatiquement intégré avec:

**1. Système de Récolte (`map_service.py`)**
```python
# Après chaque récolte
completed_quests = QuestService.update_quest_progress(
    player,
    'gather',
    material_id=material_id,
    quantity=gathered_amount
)
```

**2. Système de Crafting (`crafting_service.py`)**
```python
# Après chaque fabrication
completed_quests = QuestService.update_quest_progress(
    player,
    'craft',
    recipe_id=recipe_id,
    quantity=quantity
)
```

**3. Système de Mouvement (`player_service.py`)**
```python
# Après chaque déplacement
completed_quests = QuestService.update_quest_progress(
    player,
    'visit',
    grid_x=player.grid_x,
    grid_y=player.grid_y
)
```

**4. Système de Combat**
```python
# Après chaque victoire
completed_quests = QuestService.update_quest_progress(
    player,
    'defeat',
    mob_id=mob_id,
    quantity=1
)
```

### Réponse API Enrichie

Les endpoints de récolte et crafting retournent maintenant les quêtes complétées:

```json
{
  "message": "Récolté 5x Bois",
  "gathered": 5,
  "remaining": 45,
  "quests_completed": [
    {
      "quest": {
        "name": "Premiers Pas dans ce Monde",
        "icon": "🌱",
        "description": "Récoltez votre premier matériau..."
      },
      "rewards": {
        "xp": 50,
        "money": 10,
        "items": [],
        "level_up": false
      }
    }
  ]
}
```

---

## 📋 Quêtes Initiales

### 7 Quêtes Créées

#### 1. 🌱 Premiers Pas dans ce Monde
- **Type**: Gather
- **Difficulté**: Facile
- **Objectif**: Récolter 5x Bois
- **Récompense**: 50 XP, 10 coins

#### 2. 🔨 Le Forgeron en Formation
- **Type**: Craft
- **Difficulté**: Facile
- **Objectif**: Fabriquer Planches + Bâtons
- **Récompense**: 100 XP, 25 coins

#### 3. ⛏️ Collecteur de Ressources
- **Type**: Gather
- **Difficulté**: Facile
- **Objectif**: Récolter 10x Bois + 10x Pierre
- **Récompense**: 150 XP, 50 coins, 5x Bois

#### 4. 🗺️ L'Explorateur
- **Type**: Explore
- **Difficulté**: Facile
- **Objectif**: Explorer 3 nouvelles cellules
- **Récompense**: 75 XP, 30 coins
- **Répétable**: Oui (24h cooldown)

#### 5. ⚙️ Le Chasseur de Fer
- **Type**: Gather
- **Difficulté**: Moyen
- **Niveau requis**: 3
- **Objectif**: Récolter 5x Minerai de Fer
- **Récompense**: 200 XP, 75 coins, 10x Pierre
- **Répétable**: Oui (48h cooldown)

#### 6. 🛠️ Artisan Productif
- **Type**: Craft
- **Difficulté**: Moyen
- **Niveau requis**: 4
- **Objectif**: Fabriquer 10 objets (n'importe lesquels)
- **Récompense**: 300 XP, 100 coins, 20x Bois + 20x Pierre
- **Répétable**: Oui (72h cooldown)

#### 7. 🌍 Le Grand Voyageur
- **Type**: Explore
- **Difficulté**: Difficile
- **Niveau requis**: 5
- **Objectif**: Explorer 20 nouvelles cellules
- **Récompense**: 500 XP, 200 coins
- **Répétable**: Oui (168h cooldown)

---

## 🛠️ Service Quest

Le `QuestService` gère toute la logique des quêtes:

### Méthodes Principales

**`get_available_quests(player)`**
- Retourne les quêtes disponibles pour le joueur
- Vérifie niveau, prérequis, cooldowns

**`get_active_quests(player)`**
- Retourne les quêtes en cours

**`accept_quest(player, quest_id)`**
- Accepte une quête
- Vérifie toutes les conditions
- Crée/Met à jour PlayerQuest

**`update_quest_progress(player, action_type, **kwargs)`**
- Met à jour automatiquement la progression
- Retourne les quêtes complétées
- Appelé par gather/craft/move/combat

**`complete_quest(player, player_quest_id)`**
- Complète une quête
- Distribue les récompenses (XP, argent, items)
- Gère le level-up
- Configure le cooldown si répétable

**`abandon_quest(player, player_quest_id)`**
- Abandonne une quête active

---

## 👨‍💼 Interface Admin Django

**Admin Quest:**
- Liste avec filtres (type, difficulté, répétabilité)
- Recherche par nom/description
- Édition des objectifs JSON
- Configuration des récompenses

**Admin PlayerQuest:**
- Vue de la progression par joueur
- Filtres par statut et difficulté
- Affichage du pourcentage de progression
- Timestamps des actions

**Admin DynamicEvent:**
- Gestion des événements
- Liste des participants
- Filtres par type et statut
- Localisation sur la carte

---

## 🎨 Frontend Integration (À Développer)

### Composants Suggérés

**1. QuestsTab.js** - Onglet principal
```javascript
// Affiche:
// - Quêtes disponibles
// - Quêtes actives avec progression
// - Quêtes complétées (historique)
```

**2. QuestCard.js** - Carte de quête
```javascript
// Affiche:
// - Icône et nom
// - Description et histoire
// - Objectifs avec checkboxes
// - Barre de progression
// - Boutons Accepter/Abandonner
```

**3. QuestNotification.js** - Notification
```javascript
// Affiche quand:
// - Quête acceptée
// - Quête complétée
// - Récompenses reçues
```

**4. QuestTracker.js** - Tracker HUD
```javascript
// Overlay affichant:
// - Quêtes actives (miniature)
// - Progression en temps réel
```

### API Service Frontend

```javascript
// frontend/src/services/questAPI.js
export const questAPI = {
  getAvailable: () => api.get('/quests/available/'),
  getActive: () => api.get('/quests/active/'),
  getCompleted: () => api.get('/quests/completed/'),
  accept: (questId) => api.post(`/quests/${questId}/accept/`),
  abandon: (questId) => api.post(`/quests/${questId}/abandon/`),
  getStats: () => api.get('/quests/stats/')
};
```

---

## 🔮 Fonctionnalités Futures

### Court Terme
- [ ] Onglet Quêtes dans l'UI frontend
- [ ] Notifications visuelles de progression
- [ ] Tracker de quêtes actives (HUD)

### Moyen Terme
- [ ] Quêtes avec dialogues PNJ
- [ ] Système de réputation
- [ ] Quêtes de guilde/faction
- [ ] Récompenses uniques (titres, cosmétiques)

### Long Terme
- [ ] Générateur de quêtes procédurales
- [ ] Quêtes à choix multiples
- [ ] Quêtes collaboratives (multi-joueurs)
- [ ] Événements mondiaux temporaires

---

## 📝 Fichiers Créés/Modifiés

### Backend (Nouveaux)
- `game/models.py` - +170 lignes (Quest, PlayerQuest, DynamicEvent)
- `game/services/quest_service.py` - Service complet (370 lignes)
- `game/views/quest_views.py` - API endpoints (240 lignes)
- `game/serializers.py` - +55 lignes (3 serializers)
- `game/management/commands/populate_quests.py` - Script de peuplement (200 lignes)
- `game/migrations/0034_quest_dynamicevent_playerquest.py` - Migration

### Backend (Modifiés)
- `game/urls.py` - Ajout routes quêtes
- `game/admin.py` - +55 lignes (3 admins)
- `game/services/map_service.py` - Intégration tracking (15 lignes)
- `game/services/crafting_service.py` - Intégration tracking (15 lignes)

**Total: ~1115 lignes de code ajoutées**

---

## 🚀 Commandes Essentielles

### Création des Données
```bash
# Créer les quêtes initiales
python manage.py populate_quests

# Accéder à l'admin
http://localhost:8000/admin
```

### Test API
```bash
# Liste des quêtes
curl http://localhost:8000/api/quests/

# Quêtes disponibles
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/quests/available/

# Accepter une quête
curl -X POST -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/quests/1/accept/
```

---

## ✅ Status de l'Implémentation

### Backend: 100% ✅
- ✅ Modèles de données
- ✅ Service de gestion
- ✅ API REST complète
- ✅ Intégration avec gameplay existant
- ✅ Tracking automatique
- ✅ Interface admin
- ✅ Migration et données initiales
- ✅ Tests fonctionnels

### Frontend: 0% ⏳
- ⏳ Composants React
- ⏳ Intégration UI
- ⏳ Notifications
- ⏳ Tracker HUD

---

## 💡 Exemples d'Utilisation

### Backend - Créer une Quête

```python
quest = Quest.objects.create(
    name="Maître Artisan",
    description="Devenez un artisan légendaire",
    icon="🏆",
    quest_type="craft",
    difficulty="epic",
    required_level=10,
    requirements={
        'craft': [
            {'recipe_id': 5, 'quantity': 50},
            {'recipe_id': 10, 'quantity': 20}
        ]
    },
    reward_xp=1000,
    reward_money=500,
    reward_items=[
        {'material_id': 15, 'quantity': 1}
    ],
    is_repeatable=False
)
```

### Backend - Vérifier Progression

```python
from game.services.quest_service import QuestService

# Mettre à jour après récolte
completed = QuestService.update_quest_progress(
    player,
    'gather',
    material_id=1,
    quantity=5
)

# Afficher quêtes complétées
for quest_data in completed:
    print(f"Complété: {quest_data['quest'].name}")
    print(f"XP: +{quest_data['rewards']['xp']}")
```

---

## 🎯 Conclusion

Le système de quêtes est **pleinement opérationnel** côté backend. Il offre:

- ✨ Variété de types de quêtes
- 📊 Tracking automatique de progression
- 🎁 Système de récompenses complet
- 🔄 Support des quêtes répétables
- 🔗 Chaînes de quêtes avec prérequis
- ⚙️ Interface admin complète
- 📡 API REST documentée

**Prochaine étape**: Créer l'interface utilisateur frontend pour que les joueurs puissent voir et interagir avec les quêtes!

---

**Développé le**: 26 Novembre 2025
**Version**: 1.0.0 - Quest System Complete
