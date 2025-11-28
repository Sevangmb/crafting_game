# Système de Survie (Day R Survival inspired)

## 📊 Vue d'ensemble

Le système de survie ajoute des mécaniques inspirées de Day R Survival pour rendre le gameplay plus immersif et challengeant.

## ✅ Fonctionnalités implémentées (Phase 1)

### 1. Stats de Survie du Joueur

Nouveaux champs dans le modèle `Player`:

```python
# Stats de survie
hunger = 0-100          # Faim, diminue de 5 points/heure
thirst = 0-100          # Soif, diminue de 10 points/heure (2x plus rapide)
radiation = 0-100       # Radiation, se réduit naturellement de 2 points/heure

# Capacité d'inventaire
max_carry_weight = 50.0  # Poids max de base
current_carry_weight     # Calculé automatiquement
effective_carry_capacity # Base + force * 2 + bonus équipement
is_overencumbered        # True si surcharge
```

### 2. Système de Poids

Chaque matériau a maintenant un poids :

```python
# Dans Material
weight = 1.0  # En kilogrammes
weight_capacity_bonus = 0.0  # Pour sacs à dos

# Exemples de poids:
- Gemmes: 0.1-0.3kg
- Fruits: 0.05-0.3kg
- Bois: 0.5-1.8kg
- Pierre/Minerai: 2-5kg
- Outils: 2-3kg
```

**Capacité de transport:**
- Base: 50kg
- Bonus de Force: (strength - 10) * 2kg
- Bonus d'équipement: sacs à dos futurs

### 3. Effets de la Nourriture

Les aliments restaurent maintenant plusieurs stats :

```python
# Dans Material
hunger_restore = 0       # Points de faim restaurés
thirst_restore = 0       # Points de soif restaurés
energy_restore = 0       # Énergie (système existant)
radiation_change = 0     # Peut réduire radiation (négatif)

# Exemples:
- Pomme: +10 faim, +5 soif
- Viande: +30 faim, +0 soif
- Soupe de légumes: +45 faim, +30 soif
```

### 4. Système de Durabilité

Les outils s'usent avec l'utilisation :

```python
# Dans Material
max_durability = 0  # 0 = durabilité infinie

# Exemples:
- Pioche: 100 durabilité
- Hache: 100 durabilité
- Épée: 150 durabilité

# Dans Inventory
durability_current = X  # Durabilité actuelle
durability_max = X      # Durabilité maximale
```

**Consommation de durabilité:**
- Gather: -1 durabilité
- Mine: -2 durabilité
- Attaque: -1 durabilité
- 20% de chance de ne pas consommer

**Efficacité selon la durabilité:**
- 100-50%: 100% efficacité
- 50-25%: 80% efficacité
- 25-10%: 60% efficacité
- <10%: 40% efficacité

### 5. Effets de Survie

**Faim basse (<30):**
- Coût énergétique des actions +50%
- Pénalité d'énergie max
- À 0: -5 santé (dégâts de famine)

**Soif basse (<20):**
- Coût énergétique des actions +50%
- Pénalité d'énergie max sévère
- À 0: -10 santé (déshydratation)

**Radiation élevée (>50):**
- Dégâts de radiation progressifs
- >80: Radiation mortelle

## 📡 API Updates

### Endpoint `/api/players/me/`

Retourne maintenant:

```json
{
  "id": 1,
  "energy": 80,
  "max_energy": 100,
  "health": 95,
  "max_health": 100,

  "hunger": 75,
  "max_hunger": 100,
  "thirst": 60,
  "max_thirst": 100,
  "radiation": 0,

  "current_carry_weight": 12.5,
  "effective_carry_capacity": 58.0,
  "is_overencumbered": false,

  "survival_warnings": [
    {
      "type": "info",
      "message": "😰 Vous avez faim"
    }
  ]
}
```

### Endpoint `/api/inventory/{id}/consume/`

Retourne maintenant:

```json
{
  "message": "⚡ +15 énergie | 🍖 +30 faim | 💧 +0 soif",
  "energy": 95,
  "hunger": 105,
  "thirst": 60,
  "radiation": 0
}
```

### Serializers mis à jour

- `MaterialSerializer`: inclut weight, max_durability, hunger_restore, thirst_restore
- `InventorySerializer`: inclut durability_current, durability_max, durability_percentage
- `PlayerSerializer`: inclut toutes les nouvelles stats de survie

## 🎮 Services créés

### `SurvivalService`

```python
# Mise à jour automatique des stats
SurvivalService.update_survival_stats(player)

# Consommation de nourriture
SurvivalService.consume_food(player, material, quantity)

# Ajout de radiation
SurvivalService.add_radiation(player, amount)

# Vérifications
can_act, reason = SurvivalService.check_can_act(player)
cost = SurvivalService.get_action_energy_cost(player, base_cost)
```

### `DurabilityService`

```python
# Initialiser durabilité d'un nouvel objet
DurabilityService.initialize_durability(inventory_item, material)

# Consommer durabilité
broke, remaining = DurabilityService.consume_durability(inventory_item, amount)

# Utiliser outil équipé
tool_name, broke, remaining = DurabilityService.consume_tool_durability(
    player, action_type='gather'
)

# Vérifier efficacité
efficiency = DurabilityService.get_tool_efficiency(inventory_item)
has_tool, efficiency, tool_name = DurabilityService.check_tool_for_gathering(player, biome)
```

## 🔧 Commande d'initialisation

```bash
python manage.py init_survival
```

Initialise les poids et effets de survie pour tous les matériaux existants.

## 📝 TODO - Phase 2 (À implémenter)

### Intégration dans les actions

- [ ] Intégrer durabilité dans gathering
- [ ] Intégrer durabilité dans combat
- [ ] Vérifier surcharge avant actions
- [ ] Appliquer coûts énergétiques basés sur survie

### Système de Véhicules

- [ ] Modèle Vehicle
- [ ] Carburant et consommation
- [ ] Multiplicateur de vitesse
- [ ] Bonus de capacité d'inventaire

### Système de Quêtes

- [ ] Modèle Quest
- [ ] Objectifs et récompenses
- [ ] Quêtes principales/secondaires
- [ ] Quêtes journalières

### Météo et Saisons

- [ ] Système de saisons
- [ ] Effets météorologiques
- [ ] Modification des spawns selon saison

### NPCs et Commerce

- [ ] Modèle NPC
- [ ] Système de troc
- [ ] Villages et marchands

### Découverte de Recettes

- [ ] Recettes verrouillées par défaut
- [ ] Système de découverte
- [ ] Livres de recettes

### Eau et Cuisine

- [ ] Eau sale vs eau propre
- [ ] Cuisson de viande
- [ ] Spoilage de nourriture

## 🎨 Frontend (À faire)

### Barres de Survie

Ajouter des barres visuelles pour :
- Faim (🍖)
- Soif (💧)
- Radiation (☢️)

### Indicateur de Poids

```
Poids: 12.5kg / 58kg [████████░░]
```

### Durabilité des Outils

Afficher durabilité dans l'inventaire avec barre de progression et code couleur.

### Alertes de Survie

Toast notifications pour:
- Faim/Soif critique
- Radiation élevée
- Outil cassé
- Surcharge

## 📊 Équilibrage

### Taux de Déclin

| Stat | Taux | Temps pour vide |
|------|------|-----------------|
| Faim | -5/h | 20 heures |
| Soif | -10/h | 10 heures |
| Radiation | +2/h (naturel) | Varie |

### Restauration Alimentaire

| Type | Faim | Soif | Exemple |
|------|------|------|---------|
| Fruit | 5-25 | 5-15 | Pomme |
| Légume | 8-20 | 5-12 | Carotte |
| Viande | 25-60 | 0 | Viande de sanglier |
| Plat cuisiné | 35-55 | 15-30 | Soupe |

### Durabilité

| Outil | Durabilité | Actions |
|-------|------------|---------|
| Pioche | 100 | ~100 gathers |
| Hache | 100 | ~100 chops |
| Épée | 150 | ~150 attacks |

## 🚀 Comment tester

1. Démarrer le serveur:
```bash
python manage.py runserver
```

2. Login et récupérer joueur:
```bash
GET /api/players/me/
```

3. Vérifier nouvelles stats:
```json
{
  "hunger": 100,
  "thirst": 100,
  "current_carry_weight": 0
}
```

4. Consommer nourriture:
```bash
POST /api/inventory/{id}/consume/
```

5. Vérifier mise à jour:
```json
{
  "hunger": 110,  # Restauré
  "thirst": 105   # Restauré
}
```

## 🎯 Impact sur le Gameplay

1. **Gestion de ressources** : Joueurs doivent gérer faim/soif en plus de l'énergie
2. **Planification** : Déplacements et exploration nécessitent préparation
3. **Crafting stratégique** : Cuisiner devient important pour survie
4. **Économie d'inventaire** : Poids force choix entre matériaux
5. **Maintenance des outils** : Outils doivent être remplacés/réparés
6. **Exploration risquée** : Zones à radiation ajoutent du danger

---

**Statut**: ✅ Phase 1 complète - Backend fonctionnel
**Prochaine étape**: Intégration frontend + Phase 2
