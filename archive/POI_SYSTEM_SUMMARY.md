# Système de Points d'Intérêt (POI) - Documentation

## ✅ Fonctionnalités Implémentées

Le système POI permet aux joueurs d'interagir avec des lieux réels (restaurants, magasins, pharmacies, etc.) sur la carte OpenStreetMap et d'acheter des objets avec de l'énergie.

### 1. Backend - Service POI

**Fichier**: `game/services/poi_service.py`

**Types de POI supportés**:
- 🍽️ **Restaurant** - Nourriture cuite, eau purifiée
- 🍔 **Fast Food** - Nourriture rapide à prix réduit
- ☕ **Café** - Petite restauration, boissons
- 🛒 **Supermarché** - Nourriture crue et cuite, ingrédients
- 👕 **Magasin de Vêtements** - Équipements (veste, bottes, sac à dos)
- 🔧 **Quincaillerie** - Outils (pioche, hache, pelle)
- ⚕️ **Pharmacie** - Soins (bandages, anti-radiation, stimulants)
- ⛽ **Station-Service** - Carburant et jerrycans

**Méthodes principales**:
```python
POIService.get_poi_from_osm_features(features)
# Extrait les POIs interactifs depuis les données OSM

POIService.get_poi_menu(poi_type)
# Récupère le menu/inventaire d'un type de POI

POIService.purchase_item(player, poi_type, material_id, quantity)
# Effectue un achat (déduction d'énergie, ajout à l'inventaire)
```

**Système de prix**:
- Monnaie: Énergie (⚡)
- Vérification de capacité de poids
- Stock limité ou illimité selon l'item
- Durabilité max pour les outils achetés

### 2. Backend - API Endpoints

**Fichier**: `game/views/poi_views.py`

**Endpoints disponibles**:

```
GET /api/poi/current-pois/
```
- Récupère tous les POIs de la cellule actuelle
- Retourne: liste de POIs avec nom, type, icon, osm_id

```
GET /api/poi/menu/{poi_type}/
```
- Récupère le menu d'un type de POI spécifique
- Exemple: `/api/poi/menu/restaurant/`
- Retourne: liste d'articles avec prix, effets, stock

```
POST /api/poi/purchase/
```
- Effectue un achat
- Body: `{poi_type, material_id, quantity}`
- Vérifie: énergie suffisante, capacité de poids
- Retourne: message de succès + données joueur mises à jour

### 3. Frontend - API Service

**Fichier**: `frontend/src/services/api.js`

```javascript
export const poiAPI = {
  getCurrentPOIs: () => api.get('/poi/current-pois/'),
  getMenu: (poiType) => api.get(`/poi/menu/${poiType}/`),
  purchase: (poiType, materialId, quantity) =>
    api.post('/poi/purchase/', { poi_type: poiType, material_id: materialId, quantity })
};
```

### 4. Frontend - Composant POIDialog

**Fichier**: `frontend/src/components/poi/POIDialog.js`

**Fonctionnalités**:
- Dialog modal pour afficher le menu d'un POI
- Liste des articles avec:
  - Icône et description du matériau
  - Prix en énergie
  - Effets (faim, soif, énergie restaurés)
  - Indication de stock limité
  - Sélection de quantité
  - Calcul du prix total
- Gestion des erreurs (énergie insuffisante, surcharge)
- Messages de succès avec auto-fermeture
- Mise à jour automatique des stats joueur après achat

### 5. Frontend - Intégration dans GameMap

**Fichier**: `frontend/src/components/map/GameMap.js`

**Modifications**:
- Chargement automatique des POIs lors du changement de cellule
- Section "Lieux d'Intérêt" affichée si POIs disponibles
- Boutons cliquables pour chaque POI avec icône
- Ouverture du dialog POI au clic
- Rafraîchissement des données joueur après achat

**Interface**:
```jsx
{pois.length > 0 && (
    <Paper>
        <Typography>🏪 Lieux d'Intérêt</Typography>
        <Box>
            {pois.map(poi => (
                <Button onClick={() => handlePOIClick(poi)}>
                    {poi.icon} {poi.name}
                </Button>
            ))}
        </Box>
    </Paper>
)}
```

## 📊 Exemples de POI et Inventaires

### Restaurant
| Article | Prix (⚡) | Effets |
|---------|----------|--------|
| Viande Cuite | 15 | +Faim |
| Poisson Cuit | 12 | +Faim |
| Pain | 8 | +Faim |
| Soupe | 10 | +Faim, +Soif |
| Eau Purifiée | 5 | +Soif |

### Supermarché
| Article | Prix (⚡) | Stock |
|---------|----------|-------|
| Viande Crue | 8 | Illimité |
| Poisson Cru | 6 | Illimité |
| Baie | 3 | Illimité |
| Pomme | 4 | Illimité |
| Pain | 5 | Illimité |

### Magasin de Vêtements
| Article | Prix (⚡) | Stock |
|---------|----------|-------|
| Veste en Cuir | 50 | Limité (3) |
| Bottes | 40 | Limité (2) |
| Gants | 30 | Limité (2) |
| Sac à Dos | 80 | Limité (1) |

### Quincaillerie
| Article | Prix (⚡) | Stock |
|---------|----------|-------|
| Pioche | 60 | Limité (2) |
| Hache | 50 | Limité (2) |
| Pelle | 45 | Limité (2) |
| Corde | 20 | Illimité |

### Pharmacie
| Article | Prix (⚡) | Stock |
|---------|----------|-------|
| Bandage | 25 | Illimité |
| Anti-Radiation | 50 | Limité (5) |
| Stimulant | 40 | Limité (3) |

## 🎮 Expérience Utilisateur

### Flux d'utilisation
1. **Déplacement**: Le joueur se déplace sur la carte
2. **Détection**: Le système charge automatiquement les POIs de la cellule via OSM
3. **Affichage**: Section "Lieux d'Intérêt" apparaît si POIs présents
4. **Interaction**: Clic sur un POI ouvre le dialog de menu
5. **Achat**:
   - Sélection de quantité
   - Vérification automatique (énergie, poids)
   - Déduction d'énergie
   - Ajout à l'inventaire avec durabilité max
6. **Feedback**: Message de succès ou d'erreur détaillé

### Vérifications de sécurité
- ✅ Énergie suffisante (prix × quantité)
- ✅ Capacité de poids non dépassée
- ✅ Matériau existe dans la base de données
- ✅ Quantité positive et valide
- ✅ Type de POI reconnu

### Messages d'erreur
```json
// Énergie insuffisante
{
  "error": "Pas assez d'énergie ! Requis: 45, Disponible: 30"
}

// Surcharge
{
  "error": "Trop lourd ! Cet achat pèse 12.5kg. Capacité: 48.0/50.0kg"
}

// Article indisponible
{
  "error": "Cet article n'est pas disponible ici."
}
```

## 🔧 Détails Techniques

### Mapping OSM → POI
Le système utilise les tags OpenStreetMap pour identifier les POIs:
```python
osm_to_poi = {
    ('amenity', 'restaurant'): 'restaurant',
    ('amenity', 'fast_food'): 'fast_food',
    ('amenity', 'cafe'): 'cafe',
    ('shop', 'supermarket'): 'supermarket',
    ('shop', 'clothes'): 'clothes',
    ('shop', 'hardware'): 'hardware',
    ('amenity', 'pharmacy'): 'pharmacy',
    ('amenity', 'fuel'): 'fuel',
}
```

### Stockage des données OSM
- Les features OSM sont déjà stockées dans `MapCell.osm_features` (JSONField)
- Le service POI extrait les POIs pertinents à la volée
- Pas de modèle POI séparé nécessaire (utilise les données OSM existantes)

### Gestion de l'inventaire
```python
# Création ou mise à jour de l'item
inventory_item, created = Inventory.objects.get_or_create(
    player=player,
    material=material,
    defaults={'quantity': 0}
)
inventory_item.quantity += quantity

# Si l'item a de la durabilité, la définir au max
if material.max_durability > 0:
    inventory_item.durability_max = material.max_durability
    inventory_item.durability_current = material.max_durability
```

## 🚀 Extensions Possibles

### Système de quêtes POI
- Missions de livraison entre POIs
- Achats en gros avec réduction
- Programme de fidélité

### POI personnalisés
- Maisons de joueurs comme POIs
- Commerce entre joueurs
- Ateliers de réparation

### Horaires d'ouverture
- POIs fermés la nuit
- Heures de pointe avec prix variables
- Événements spéciaux

### Réputation
- Réductions avec réputation élevée
- Accès à des items rares
- Services exclusifs

### Stock dynamique
- Réapprovisionnement périodique
- Pénurie de certains items
- Items saisonniers

## 📝 Fichiers Modifiés/Créés

### Backend
- ✅ `game/services/poi_service.py` (NOUVEAU)
- ✅ `game/views/poi_views.py` (NOUVEAU)
- ✅ `game/urls.py` (modifié - ajout endpoint POI)

### Frontend
- ✅ `frontend/src/services/api.js` (modifié - ajout poiAPI)
- ✅ `frontend/src/components/poi/POIDialog.js` (NOUVEAU)
- ✅ `frontend/src/components/map/GameMap.js` (modifié - intégration POI)

## ✅ Statut

**Phase POI**: ✅ COMPLÈTE
- Backend service: ✅ Implémenté
- API endpoints: ✅ Implémentés
- Frontend service: ✅ Implémenté
- UI Dialog: ✅ Implémenté
- Intégration carte: ✅ Complète
- Tests: ✅ Compilation réussie

**Date**: 2025-01-25
**Version**: POI System v1.0
