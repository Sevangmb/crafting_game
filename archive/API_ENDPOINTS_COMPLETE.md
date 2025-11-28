# API Endpoints - Guide Complet

**Date**: 26 Novembre 2025
**Version**: 2.0 - Systèmes Sociaux et Compétitifs
**Base URL**: `http://localhost:8000/api/`

---

## 🎮 Vue d'Ensemble

Ce document liste tous les endpoints API disponibles dans le jeu, incluant les nouveaux systèmes de **Quêtes**, **Trading**, **Leaderboards** et **Événements Dynamiques**.

---

## 🔐 Authentification

Tous les endpoints (sauf `/auth/login/`) nécessitent un token d'authentification.

**Header requis:**
```
Authorization: Token <votre_token>
```

### Login
```http
POST /api/auth/login/
```
**Body:**
```json
{
  "username": "string",
  "password": "string"
}
```
**Response:**
```json
{
  "token": "abc123...",
  "user_id": 1,
  "username": "admin"
}
```

---

## 👤 Joueur (Player)

### Obtenir le profil
```http
GET /api/players/me/
```
**Response:** Profil complet du joueur avec inventaire, équipements, statistiques.

### Se déplacer
```http
POST /api/players/{id}/move/
```
**Body:**
```json
{
  "direction": "north|south|east|west"
}
```
**Response:** Nouveau profil avec position mise à jour.

### Redémarrer
```http
POST /api/players/restart/
```
Remet le joueur à la position initiale et vide l'inventaire.

---

## 🗺️ Carte (Map)

### Cellule actuelle
```http
GET /api/map/current/
```
**Response:** Détails de la cellule (biome, matériaux, bâtiments, événements).

### Récolter des matériaux
```http
POST /api/map/{id}/gather/
```
**Body:**
```json
{
  "material_id": 1
}
```
**Response:** Matériaux récoltés + XP gagnée.

### État du monde
```http
GET /api/map/world_state/
```
**Response:** Vue d'ensemble de la carte, joueurs en ligne, événements actifs.

---

## 🎒 Inventaire

### Liste de l'inventaire
```http
GET /api/inventory/
```
**Response:** Liste des items possédés (quantité > 0 uniquement).

### Consommer un item
```http
POST /api/inventory/{id}/consume/
```
**Response:** Item consommé, énergie restaurée.

---

## 🔨 Crafting

### Liste des recettes
```http
GET /api/recipes/
```
**Response:** Toutes les recettes avec ingrédients requis.

### Fabriquer un item
```http
POST /api/crafting/craft/
```
**Body:**
```json
{
  "recipe_id": 1,
  "quantity": 5
}
```
**Response:** Items fabriqués + XP gagnée.

---

## 📜 Système de Quêtes

### Liste des quêtes
```http
GET /api/quests/
```
**Query params:**
- `difficulty`: easy|medium|hard|epic
- `quest_type`: gather|craft|explore|defeat|delivery|talk

### Quêtes disponibles
```http
GET /api/quests/available/
```
**Response:** Quêtes que le joueur peut accepter (niveau requis, prérequis satisfaits).

### Quêtes actives
```http
GET /api/quests/active/
```
**Response:** Quêtes en cours avec progression.

### Quêtes complétées
```http
GET /api/quests/completed/
```
**Response:** Historique des quêtes terminées.

### Accepter une quête
```http
POST /api/quests/{id}/accept/
```
**Response:** Quête ajoutée aux quêtes actives.

### Abandonner une quête
```http
POST /api/quests/{id}/abandon/
```
**Response:** Quête retirée des actives, progression perdue.

### Statistiques
```http
GET /api/quests/stats/
```
**Response:**
```json
{
  "total_completed": 15,
  "total_active": 3,
  "total_abandoned": 2,
  "total_xp_earned": 5000,
  "total_money_earned": 1200
}
```

---

## 🤝 Système de Trading

### Créer une offre
```http
POST /api/trades/create_offer/
```
**Body:**
```json
{
  "to_player_id": 2,
  "offered_items": [
    {"material_id": 1, "quantity": 10},
    {"material_id": 2, "quantity": 5}
  ],
  "offered_money": 100,
  "requested_items": [
    {"material_id": 3, "quantity": 15}
  ],
  "requested_money": 50,
  "message": "Échange équitable!",
  "duration_hours": 24
}
```
**Response:** Offre créée avec ID.

### Offres reçues
```http
GET /api/trades/received/
```
**Response:** Liste des offres que d'autres joueurs vous ont envoyées (status: pending).

### Offres envoyées
```http
GET /api/trades/sent/
```
**Response:** Liste des offres que vous avez créées.

### Historique
```http
GET /api/trades/history/
```
**Query params:**
- `limit`: nombre max d'entrées (défaut: 50)

**Response:** Toutes vos trades (completed, rejected, cancelled, expired).

### Accepter une offre
```http
POST /api/trades/{id}/accept/
```
**Response:** Échange réalisé, items et argent transférés.

### Rejeter une offre
```http
POST /api/trades/{id}/reject/
```
**Response:** Offre refusée (destinataire uniquement).

### Annuler une offre
```http
POST /api/trades/{id}/cancel/
```
**Response:** Offre annulée (expéditeur uniquement).

### Statistiques de trading
```http
GET /api/trades/stats/
```
**Response:**
```json
{
  "total_sent": 20,
  "total_received": 15,
  "completed_as_sender": 12,
  "completed_as_receiver": 8,
  "total_completed": 20,
  "pending_sent": 3,
  "pending_received": 2
}
```

---

## 🏆 Système de Leaderboards

### Toutes les catégories
```http
GET /api/leaderboards/
```
**Query params:**
- `category`: level|wealth|gatherer|crafter|explorer|combatant|quests
- `limit`: nombre d'entrées (défaut: 100)

**Response:** Classement de la catégorie spécifiée.

### Catégories disponibles
```http
GET /api/leaderboards/categories/
```
**Response:**
```json
[
  {"value": "level", "label": "Niveau"},
  {"value": "wealth", "label": "Richesse"},
  {"value": "gatherer", "label": "Récolteur"},
  {"value": "crafter", "label": "Artisan"},
  {"value": "explorer", "label": "Explorateur"},
  {"value": "combatant", "label": "Combattant"},
  {"value": "quests", "label": "Quêtes"}
]
```

### Classements groupés
```http
GET /api/leaderboards/by_category/
```
**Query params:**
- `limit`: top N par catégorie (défaut: 10)

**Response:** Top 10 de chaque catégorie dans un seul appel.

### Mes rangs
```http
GET /api/leaderboards/my_ranks/
```
**Response:**
```json
{
  "level": {"rank": 5, "score": 50000, "metadata": {...}},
  "wealth": {"rank": 12, "score": 5000, "metadata": {...}},
  ...
}
```

### Top joueurs
```http
GET /api/leaderboards/top_players/
```
**Response:** Top 10 de chaque catégorie avec détails des joueurs.

### Rang d'un joueur spécifique
```http
GET /api/leaderboards/player_rank/
```
**Query params:**
- `player_id`: ID du joueur
- `category`: catégorie de classement

**Response:**
```json
{
  "player_id": 2,
  "player_name": "Alice",
  "category": "wealth",
  "rank": 15,
  "score": 5000,
  "metadata": {"money": 3000, "bank_balance": 2000}
}
```

### Mettre à jour tous les classements (Admin)
```http
POST /api/leaderboards/update_all/
```
**Response:** Nombre d'entrées mises à jour.

### Mettre à jour une catégorie (Admin)
```http
POST /api/leaderboards/update_category/
```
**Body:**
```json
{
  "category": "level"
}
```
**Response:** Nombre d'entrées mises à jour pour cette catégorie.

---

## ✨ Système d'Événements Dynamiques

### Événements actifs
```http
GET /api/events/
```
**Query params:**
- `event_type`: treasure|merchant|resource|weather
- `is_active`: true|false

**Response:** Liste des événements sur la carte.

### Participer à un événement
```http
POST /api/events/{id}/participate/
```
**Response:** Récompenses distribuées si éligible.

### Événements près de moi
```http
GET /api/events/nearby/
```
**Query params:**
- `radius`: rayon en cellules (défaut: 10)

**Response:** Événements dans le rayon spécifié.

### Spawn d'événement (Admin)
```http
POST /api/events/spawn/
```
**Body:**
```json
{
  "event_type": "treasure",
  "count": 5
}
```
**Response:** Événements créés.

### Nettoyage des événements expirés (Admin)
```http
POST /api/events/cleanup/
```
**Response:** Nombre d'événements supprimés.

---

## 🏗️ Bâtiments

### Types de bâtiments
```http
GET /api/building-types/
```
**Response:** Liste des bâtiments constructibles.

### Mes bâtiments
```http
GET /api/buildings/
```
**Response:** Bâtiments possédés par le joueur.

### Construire
```http
POST /api/buildings/construct/
```
**Body:**
```json
{
  "building_type_id": 1,
  "cell_id": 123
}
```
**Response:** Bâtiment créé, construction commencée.

---

## 🎯 Achievements

### Liste des achievements
```http
GET /api/achievements/
```
**Response:** Tous les achievements du jeu.

### Mes achievements
```http
GET /api/achievements/mine/
```
**Response:** Progression du joueur sur chaque achievement.

### Statistiques
```http
GET /api/achievements/stats/
```
**Response:**
```json
{
  "total_unlocked": 15,
  "total_achievements": 50,
  "completion_percentage": 30,
  "total_xp_earned": 5000
}
```

---

## 🛒 Magasins (Shops)

### Liste des magasins
```http
GET /api/shops/
```
**Query params:**
- `biome`: plains|forest|mountain|water

**Response:** Magasins disponibles dans le biome spécifié.

### Articles d'un magasin
```http
GET /api/shops/{id}/items/
```
**Response:** Liste des items vendus avec prix d'achat et de vente.

### Acheter
```http
POST /api/shops/{id}/buy/
```
**Body:**
```json
{
  "shop_item_id": 1,
  "quantity": 5
}
```
**Response:** Items achetés, argent déduit.

### Vendre
```http
POST /api/shops/{id}/sell/
```
**Body:**
```json
{
  "material_id": 1,
  "quantity": 10
}
```
**Response:** Items vendus, argent reçu.

### Historique des transactions
```http
GET /api/transactions/
```
**Query params:**
- `transaction_type`: buy|sell|trade|quest_reward|other
- `limit`: nombre d'entrées (défaut: 50)

**Response:** Historique des transactions financières.

---

## ⚔️ Combat

### Chercher un mob
```http
POST /api/combat/search/
```
**Response:** Mob trouvé (si disponible dans la cellule actuelle).

### Démarrer un combat
```http
POST /api/combat/start/
```
**Body:**
```json
{
  "mob_id": 1
}
```
**Response:** État du combat initialisé.

### Action de combat
```http
POST /api/combat/action/
```
**Body:**
```json
{
  "action": "attack|defend|special|flee"
}
```
**Response:** Résultat de l'action, état du combat mis à jour.

### Historique des combats
```http
GET /api/combat/history/
```
**Response:** Liste des combats passés (victoires/défaites).

---

## 🚗 Véhicules

### Liste des véhicules
```http
GET /api/vehicles/
```
**Response:** Véhicules possédés par le joueur.

### Équiper un véhicule
```http
POST /api/vehicles/{id}/equip/
```
**Response:** Véhicule équipé, bonus de vitesse appliqué.

### Déséquiper
```http
POST /api/vehicles/unequip/
```
**Response:** Véhicule retiré, bonus supprimé.

---

## 🏦 Banque

### Banques disponibles
```http
GET /api/banks/current/
```
**Response:** Banques dans la cellule actuelle.

### Déposer de l'argent
```http
POST /api/banks/deposit/
```
**Body:**
```json
{
  "amount": 1000
}
```
**Response:** Argent transféré du portefeuille à la banque.

### Retirer de l'argent
```http
POST /api/banks/withdraw/
```
**Body:**
```json
{
  "amount": 500
}
```
**Response:** Argent transféré de la banque au portefeuille.

---

## ⚙️ Configuration (GameConfig)

### Toutes les configs
```http
GET /api/config/
```
**Response:** Liste des paramètres de configuration du jeu.

### Obtenir une config spécifique
```http
GET /api/config/{id}/
```
**Response:** Valeur de la configuration demandée.

### Mettre à jour (Admin)
```http
PUT /api/config/{id}/
```
**Body:**
```json
{
  "value": "{\"energy_cost_per_craft\": 3}"
}
```
**Response:** Configuration mise à jour.

---

## 📊 Formats de Réponse Communs

### PlayerSerializer
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  },
  "current_x": 44.933,
  "current_y": 4.893,
  "grid_x": 0,
  "grid_y": 0,
  "energy": 95,
  "max_energy": 100,
  "health": 100,
  "max_health": 100,
  "level": 5,
  "experience": 1250,
  "money": 500,
  "inventory": [...],
  "equipped_items": [...]
}
```

### InventorySerializer
```json
{
  "id": 1,
  "material": {
    "id": 1,
    "name": "Bois",
    "icon": "🪵",
    "rarity": "common"
  },
  "quantity": 25,
  "durability_current": 100,
  "durability_max": 100,
  "durability_percentage": 100
}
```

### QuestSerializer
```json
{
  "id": 1,
  "name": "Premier Pas",
  "description": "Récoltez vos premiers matériaux",
  "quest_type": "gather",
  "difficulty": "easy",
  "required_level": 1,
  "requirements": {
    "gather": [
      {"material_id": 1, "quantity": 10}
    ]
  },
  "reward_xp": 100,
  "reward_money": 50,
  "reward_items": [],
  "is_repeatable": false
}
```

---

## 🔄 Codes d'Erreur HTTP

- **200 OK**: Succès
- **201 Created**: Ressource créée
- **400 Bad Request**: Données invalides
- **401 Unauthorized**: Token manquant ou invalide
- **403 Forbidden**: Permissions insuffisantes
- **404 Not Found**: Ressource introuvable
- **500 Internal Server Error**: Erreur serveur

---

## 💡 Exemples d'Utilisation

### Workflow typique: Accepter et compléter une quête

1. **Voir les quêtes disponibles:**
```http
GET /api/quests/available/
```

2. **Accepter une quête:**
```http
POST /api/quests/1/accept/
```

3. **Récolter des matériaux (progression automatique):**
```http
POST /api/map/123/gather/
Body: {"material_id": 1}
```

4. **Vérifier progression:**
```http
GET /api/quests/active/
```

5. **La quête est auto-complétée et récompenses distribuées!**

### Workflow typique: Créer et accepter un trade

1. **Créer une offre:**
```http
POST /api/trades/create_offer/
Body: {
  "to_player_id": 2,
  "offered_items": [{"material_id": 1, "quantity": 10}],
  "offered_money": 0,
  "requested_items": [{"material_id": 3, "quantity": 5}],
  "requested_money": 0
}
```

2. **Le destinataire voit l'offre:**
```http
GET /api/trades/received/
```

3. **Le destinataire accepte:**
```http
POST /api/trades/1/accept/
```

4. **Échange réalisé instantanément!**

---

## 📈 Recommandations

### Mise à jour des leaderboards
Pour maintenir des classements à jour, configurer une tâche périodique (cron/celery):
```python
# Tous les jours à minuit
POST /api/leaderboards/update_all/
```

### Spawn d'événements
Pour un monde dynamique, spawner régulièrement:
```python
# Toutes les 30 minutes
POST /api/events/spawn/
Body: {"count": 5}
```

### Nettoyage
Supprimer régulièrement les données expirées:
```python
# Toutes les heures
POST /api/events/cleanup/
```

---

## 🎉 Conclusion

L'API est maintenant complète avec:
- ✅ **Core gameplay**: Mouvement, récolte, crafting
- ✅ **Progression**: XP, levels, achievements
- ✅ **Quêtes**: 7 quêtes initiales, système complet
- ✅ **Social**: Trading entre joueurs
- ✅ **Compétition**: 7 catégories de classements
- ✅ **Monde vivant**: Événements dynamiques
- ✅ **Économie**: Magasins, banques, transactions
- ✅ **Combat**: Mobs, équipements, véhicules

**Le backend est prêt pour le développement frontend!**

---

**Dernière mise à jour**: 26 Novembre 2025
**Contact**: Support technique via `/api/help/`
