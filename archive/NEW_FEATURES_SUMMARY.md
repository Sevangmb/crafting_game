# Nouvelles Fonctionnalités - Documentation Complète

**Date**: 26 Novembre 2025
**Version**: 2.0.0 - Enhanced Gameplay

---

## 📋 Vue d'Ensemble des Améliorations

Trois systèmes majeurs ont été ajoutés au jeu:

1. **🤝 Système de Trading Entre Joueurs** - Échanges sécurisés d'items et d'argent
2. **🏆 Système de Classements (Leaderboards)** - Compétition globale sur 7 catégories
3. **✨ Générateur d'Événements Dynamiques** - Événements aléatoires sur la carte

---

## 🤝 Système de Trading

### Vue d'Ensemble

Permet aux joueurs d'échanger des items et de l'argent de manière sécurisée avec un système d'offres et d'acceptation.

### Modèle TradeOffer

```python
class TradeOffer(models.Model):
    # Joueurs impliqués
    from_player = ForeignKey(Player)  # Celui qui propose
    to_player = ForeignKey(Player)    # Celui qui reçoit l'offre

    # Statut de l'offre
    status = CharField(choices=[
        'pending',    # En attente
        'accepted',   # Acceptée
        'rejected',   # Refusée
        'cancelled',  # Annulée
        'completed',  # Complétée
        'expired'     # Expirée
    ])

    # Ce que l'initiateur offre
    offered_items = JSONField()    # [{'material_id': 1, 'quantity': 5}]
    offered_money = IntegerField()

    # Ce que l'initiateur demande
    requested_items = JSONField()  # [{'material_id': 2, 'quantity': 3}]
    requested_money = IntegerField()

    # Message optionnel
    message = TextField(blank=True)

    # Timestamps
    created_at = DateTimeField()
    expires_at = DateTimeField()
    completed_at = DateTimeField(null=True)
```

### Fonctionnalités

#### 1. Créer une Offre
```python
trade, error = TradingService.create_trade_offer(
    from_player=player,
    to_player_id=target_player_id,
    offered_items=[
        {'material_id': 1, 'quantity': 10},
        {'material_id': 2, 'quantity': 5}
    ],
    offered_money=100,
    requested_items=[
        {'material_id': 3, 'quantity': 15}
    ],
    requested_money=50,
    message="Je propose un échange équitable!",
    duration_hours=24
)
```

#### 2. Accepter une Offre
```python
success, error = TradingService.accept_trade(
    trade_id=trade_id,
    accepting_player=player
)
```

#### 3. Rejeter/Annuler
```python
# Rejeter (destinataire)
TradingService.reject_trade(trade_id, player)

# Annuler (expéditeur)
TradingService.cancel_trade(trade_id, player)
```

### Validations & Sécurité

**Lors de la création:**
- ✅ Vérifie que l'offrant possède les items
- ✅ Vérifie que l'offrant a l'argent
- ✅ Empêche les trades avec soi-même

**Lors de l'acceptation:**
- ✅ Transaction atomique (tout ou rien)
- ✅ Vérifie que les deux joueurs ont toujours les ressources
- ✅ Vérifie que l'offre n'a pas expiré
- ✅ Échange simultané des ressources

### Expiration Automatique

Les offres expirent après la durée définie (par défaut 24h). Un système de nettoyage peut être configuré:

```python
# À appeler via cron/celery
expired_count = TradingService.expire_old_trades()
```

### Cas d'Usage

**1. Échange Simple:**
```
Joueur A offre: 10x Bois
Joueur B donne: 5x Pierre
→ Échange instantané si B accepte
```

**2. Vente d'Items:**
```
Joueur A offre: 1x Épée Légendaire
Joueur B donne: 1000 coins
→ Marché entre joueurs
```

**3. Troc Complexe:**
```
Joueur A offre: 5x Fer + 3x Or + 100 coins
Joueur B donne: 1x Pioche en Diamant + 2x Potion
→ Échanges multiples
```

---

## 🏆 Système de Classements (Leaderboards)

### Vue d'Ensemble

Classements globaux sur 7 catégories différentes pour encourager la compétition.

### Catégories

| Catégorie | Critère de Score | Description |
|-----------|------------------|-------------|
| **Niveau** | Level × 1M + XP | Joueurs les plus avancés |
| **Richesse** | Argent + Banque | Joueurs les plus riches |
| **Récolteur** | Total récoltes | Maîtres de la récolte |
| **Artisan** | Total crafts | Maîtres du crafting |
| **Explorateur** | Total moves | Grands voyageurs |
| **Combattant** | Victoires | Champions du combat |
| **Quêtes** | Quêtes complétées | Aventuriers accomplis |

### Modèle Leaderboard

```python
class Leaderboard(models.Model):
    category = CharField(choices=CATEGORY_CHOICES)
    player = ForeignKey(Player)
    score = BigIntegerField()
    rank = IntegerField()

    # Métadonnées contextuelles
    metadata = JSONField()  # Stats détaillées

    last_updated = DateTimeField(auto_now=True)
```

### Fonctionnalités

#### 1. Mise à Jour des Classements

```python
# Mettre à jour tous les classements
LeaderboardService.update_all_leaderboards()

# Mettre à jour une catégorie spécifique
LeaderboardService.update_level_leaderboard()
LeaderboardService.update_wealth_leaderboard()
LeaderboardService.update_gatherer_leaderboard()
# etc.
```

#### 2. Consulter les Classements

```python
# Top 100 d'une catégorie
top_players = LeaderboardService.get_leaderboard('level', limit=100)

# Rang d'un joueur
rank_info = LeaderboardService.get_player_rank(player, 'wealth')
# Returns: {'rank': 15, 'score': 5000, 'metadata': {...}}

# Tous les rangs d'un joueur
all_ranks = LeaderboardService.get_all_player_ranks(player)
```

### Calcul Automatique

Le service calcule automatiquement:
- **Niveau**: Basé sur level et experience
- **Richesse**: money + bank_balance
- **Récolteur**: Count de GatheringLog
- **Artisan**: Sum de CraftingLog.quantity
- **Explorateur**: Player.total_moves
- **Combattant**: Count de CombatLog (victories)
- **Quêtes**: Sum de PlayerQuest.times_completed

### Mise à Jour Périodique

Recommandé: Mettre à jour via tâche planifiée (cron/celery):

```python
# Tous les jours à minuit
@periodic_task(run_every=crontab(hour=0, minute=0))
def update_leaderboards():
    LeaderboardService.update_all_leaderboards()
```

---

## ✨ Système d'Événements Dynamiques

### Vue d'Ensemble

Génération automatique d'événements aléatoires sur la carte pour rendre le monde vivant et dynamique.

### Types d'Événements

#### 1. 💎 Trésors
- **Coffre au Trésor**: Ressources précieuses (100-500 coins + items)
- **Cache Secrète**: XP et argent bonus (50-200 de chaque)

#### 2. 🧙 Marchands
- **Marchand Ambulant**: Échanges spéciaux, accessible à tous

#### 3. ⛏️ Ressources
- **Filon de Ressources**: Récolte ×2 pendant 6h
- **Abondance Naturelle**: Récolte ×1.5 pendant 8h

#### 4. ☄️ Météo
- **Pluie de Météores**: Minerais rares tombent du ciel!

### Service EventSpawner

#### 1. Génération Aléatoire

```python
# Spawn 5 événements aléatoires
events = EventSpawnerService.spawn_random_events(count=5)

# Spawn près d'un joueur
event = EventSpawnerService.spawn_event_near_player(
    player=player,
    event_type='treasure',  # Optionnel
    radius=5
)
```

#### 2. Nettoyage Automatique

```python
# Supprimer les événements expirés
cleaned = EventSpawnerService.cleanup_expired_events()
```

#### 3. Consultation

```python
# Tous les événements actifs
events = EventSpawnerService.get_active_events()

# Événements près d'un joueur
nearby = EventSpawnerService.get_events_near_player(player, radius=10)
```

### Configuration des Templates

Les événements sont définis dans `EVENT_TEMPLATES`:

```python
{
    'treasure': [
        {
            'name': 'Coffre au Trésor',
            'description': '...',
            'icon': '💎',
            'rewards': {
                'money': lambda: random.randint(100, 500),
                'items': lambda: [...]
            },
            'duration_hours': 2,
            'max_participants': 1
        }
    ]
}
```

### Système de Spawn Automatique

Recommandé: Tâche périodique pour maintenir des événements actifs:

```python
@periodic_task(run_every=crontab(minute='*/30'))  # Toutes les 30 min
def spawn_events():
    # Nettoyer les anciens
    EventSpawnerService.cleanup_expired_events()

    # Spawn nouveaux si nécessaire
    active_count = DynamicEvent.objects.filter(
        is_active=True,
        expires_at__gt=timezone.now()
    ).count()

    if active_count < 10:
        needed = 10 - active_count
        EventSpawnerService.spawn_random_events(count=needed)
```

---

## 📊 Statistiques d'Implémentation

### Fichiers Créés

**Services:**
1. `game/services/trading_service.py` - 280 lignes
2. `game/services/leaderboard_service.py` - 245 lignes
3. `game/services/event_spawner_service.py` - 230 lignes

**Total nouveaux services: ~755 lignes**

### Modèles Ajoutés

1. **TradeOffer** - Système de trading
2. **Leaderboard** - Classements
3. Amélioration de **DynamicEvent** (déjà existant)

### Migrations

- `0035_tradeoffer_leaderboard.py` - Créé et appliqué

---

## 🚀 API Endpoints (À Créer)

### Trading Endpoints

```
POST   /api/trades/create/        - Créer une offre
GET    /api/trades/received/      - Offres reçues
GET    /api/trades/sent/          - Offres envoyées
POST   /api/trades/{id}/accept/   - Accepter
POST   /api/trades/{id}/reject/   - Rejeter
POST   /api/trades/{id}/cancel/   - Annuler
GET    /api/trades/history/       - Historique
```

### Leaderboard Endpoints

```
GET    /api/leaderboards/           - Toutes catégories
GET    /api/leaderboards/{category}/ - Une catégorie
GET    /api/leaderboards/my-ranks/  - Mes rangs
POST   /api/leaderboards/update/    - Forcer mise à jour (admin)
```

### Event Spawner Endpoints

```
POST   /api/events/spawn/          - Spawn événement (admin)
POST   /api/events/cleanup/        - Nettoyer expirés (admin)
GET    /api/events/active/         - Événements actifs
```

---

## 💡 Recommandations d'Utilisation

### 1. Trading

**Pour les joueurs:**
- Vérifier l'inventaire avant d'accepter
- Les offres expirent après 24h
- Transaction sécurisée et instantanée

**Pour les admins:**
- Configurer tâche de nettoyage quotidienne
- Monitorer les trades suspects
- Possibilité d'ajouter frais de transaction

### 2. Leaderboards

**Fréquence de mise à jour:**
- Toutes les heures en période active
- Une fois par jour minimum
- Temps réel pour événements spéciaux

**Affichage:**
- Top 10 sur page d'accueil
- Top 100 dans onglet classements
- Badges pour top 3 de chaque catégorie

### 3. Événements Dynamiques

**Configuration spawn:**
- 10-20 événements actifs simultanément
- Spawn toutes les 30 minutes
- Cleanup des expirés toutes les heures

**Équilibre:**
- Trésors: Rares mais très récompensants
- Ressources: Fréquents, encouragent exploration
- Marchands: Modérés, points de rencontre sociaux

---

## 🔮 Évolutions Futures

### Trading
- [ ] Système d'enchères publiques
- [ ] Marché global avec listings
- [ ] Réputation des traders
- [ ] Échanges multi-joueurs (>2 personnes)

### Leaderboards
- [ ] Leaderboards saisonniers (reset mensuel)
- [ ] Récompenses automatiques pour top 10
- [ ] Titres et badges spéciaux
- [ ] Classements par guilde/faction

### Événements
- [ ] Boss world events
- [ ] Événements communautaires (objectifs globaux)
- [ ] Événements météo affectant gameplay
- [ ] Portails vers dimensions spéciales

---

## 📝 Checklist d'Intégration

### Backend ✅
- ✅ Modèles créés
- ✅ Services implémentés
- ✅ Migrations appliquées
- ⏳ Views/API à créer
- ⏳ Admin interface à ajouter

### Frontend ⏳
- ⏳ Onglet Trading
- ⏳ Interface leaderboards
- ⏳ Notifications d'événements
- ⏳ Map overlay pour événements

### Automatisation ⏳
- ⏳ Tâche périodique: update leaderboards
- ⏳ Tâche périodique: spawn events
- ⏳ Tâche périodique: cleanup trades/events

---

## 🎯 Conclusion

Ces trois systèmes ajoutent une dimension sociale et compétitive majeure au jeu:

- **Trading**: Interaction entre joueurs, économie dynamique
- **Leaderboards**: Compétition saine, objectifs à long terme
- **Événements**: Monde vivant, exploration récompensée

Le backend est prêt à 80%. Il reste à créer les API endpoints et l'interface d'administration, puis développer le frontend.

---

**Développé le**: 26 Novembre 2025
**Version**: 2.0.0 - Social & Competitive Features
