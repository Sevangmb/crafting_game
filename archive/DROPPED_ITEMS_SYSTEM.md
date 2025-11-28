# Système de Dépôt d'Objets au Sol - Documentation

## ✅ Fonctionnalités Implémentées

Le système permet aux joueurs de déposer des objets de leur inventaire sur le sol et de les ramasser plus tard. Les objets déposés persistent sur la carte et sont visibles par tous les joueurs qui passent sur cette cellule.

---

## 🎯 Fonctionnalités Principales

### 1. Dépôt d'Objets (Drop)

**Depuis l'inventaire**:
- Bouton "Déposer" sur chaque item (vue grille et liste)
- Dialog de confirmation pour choisir la quantité
- Validation de la quantité disponible
- Retrait automatique de l'inventaire
- Objet créé sur la cellule actuelle du joueur

**Caractéristiques**:
- ✅ Supporte la sélection de quantité (1 à max)
- ✅ Préserve la durabilité des outils
- ✅ Enregistre qui a déposé l'objet
- ✅ Timestamp de dépôt

### 2. Ramassage d'Objets (Pickup)

**Sur la carte**:
- Section "📦 Objets au sol" affichée si des items sont présents
- Liste de tous les objets déposés sur la cellule
- Bouton "Ramasser" pour chaque objet
- Vérification automatique de capacité de poids
- Ajout à l'inventaire avec durabilité préservée

**Affichage**:
- Icône et nom du matériau
- Quantité
- Durabilité (si applicable)
- Nom du joueur qui a déposé
- Bouton de ramassage

---

## 🗄️ Modèle de Données

### DroppedItem Model

```python
class DroppedItem(models.Model):
    """Items dropped on the ground by players"""
    cell = ForeignKey(MapCell)                    # Cellule où l'objet est déposé
    material = ForeignKey(Material)               # Type de matériau
    quantity = IntegerField(default=1)            # Quantité

    # Durabilité (pour outils)
    durability_current = IntegerField(default=0)
    durability_max = IntegerField(default=0)

    # Traçabilité
    dropped_by = ForeignKey(Player, null=True)    # Qui a déposé
    dropped_at = DateTimeField(auto_now_add=True) # Quand

    # Auto-nettoyage (optionnel)
    expires_at = DateTimeField(null=True)         # Expiration
```

**Relations**:
- `MapCell.dropped_items` - Tous les objets sur cette cellule
- `Player.items_dropped` - Tous les objets déposés par ce joueur

---

## 🔌 API Endpoints

### POST /api/inventory/drop/

Dépose un objet de l'inventaire sur le sol.

**Request**:
```json
{
  "inventory_id": 123,
  "quantity": 5
}
```

**Response Success**:
```json
{
  "success": true,
  "message": "✅ Déposé 5x Pierre sur le sol",
  "dropped_item_id": 456,
  "player": { /* PlayerSerializer data */ }
}
```

**Response Error**:
```json
{
  "error": "Quantité insuffisante. Disponible: 3"
}
```

**Validations**:
- ✅ Inventory item existe et appartient au joueur
- ✅ Quantité valide (> 0 et ≤ disponible)
- ✅ Cellule actuelle du joueur

---

### POST /api/inventory/pickup/

Ramasse un objet déposé sur le sol.

**Request**:
```json
{
  "dropped_item_id": 456
}
```

**Response Success**:
```json
{
  "success": true,
  "message": "✅ Ramassé 5x Pierre",
  "player": { /* PlayerSerializer data */ }
}
```

**Response Error**:
```json
{
  "error": "Trop lourd ! Cet objet pèse 5.0kg. Capacité: 48.0/50.0kg"
}
```

**Validations**:
- ✅ Objet existe
- ✅ Joueur sur la même cellule
- ✅ Capacité de poids suffisante
- ✅ L'objet est supprimé après ramassage

---

## 🎨 Interface Utilisateur

### 1. Bouton "Déposer" dans l'Inventaire

**Vue Grille**:
```jsx
<Box sx={{ display: 'flex', gap: 1 }}>
    {isConsumable && (
        <Button color="success">Utiliser</Button>
    )}
    <Button
        color="error"
        variant="outlined"
        onClick={() => onDrop(item.id, item.material.name, item.quantity)}
    >
        Déposer
    </Button>
</Box>
```

**Vue Liste**: Boutons identiques disponibles

### 2. Dialog de Confirmation

```jsx
<Dialog open={dropDialog.open}>
    <DialogTitle>Déposer {dropDialog.itemName}</DialogTitle>
    <DialogContent>
        <TextField
            type="number"
            label="Quantité"
            value={dropQuantity}
            min={1}
            max={dropDialog.maxQuantity}
        />
    </DialogContent>
    <DialogActions>
        <Button onClick={cancel}>Annuler</Button>
        <Button onClick={confirm} color="error">Déposer</Button>
    </DialogActions>
</Dialog>
```

### 3. Affichage sur la Carte

**Section "Objets au sol"**:
```jsx
{currentCell.dropped_items?.length > 0 && (
    <Paper>
        <Typography>📦 Objets au sol</Typography>
        <List>
            {currentCell.dropped_items.map(dropped => (
                <ListItem>
                    <Typography>{dropped.material.icon}</Typography>
                    <Box>
                        <Typography>{dropped.quantity}x {dropped.material.name}</Typography>
                        {dropped.durability_max > 0 && (
                            <Typography variant="caption">
                                Durabilité: {dropped.durability_current}/{dropped.durability_max}
                            </Typography>
                        )}
                        {dropped.dropped_by_name && (
                            <Typography variant="caption">
                                Déposé par: {dropped.dropped_by_name}
                            </Typography>
                        )}
                    </Box>
                    <Button color="success" onClick={pickup}>
                        Ramasser
                    </Button>
                </ListItem>
            ))}
        </List>
    </Paper>
)}
```

---

## 🔄 Flux d'Utilisation

### Scénario 1: Déposer un objet

1. **Joueur ouvre son inventaire**
2. **Clique sur "Déposer" sur un item**
3. **Dialog s'ouvre avec choix de quantité**
4. **Joueur sélectionne la quantité et confirme**
5. **Backend**:
   - Vérifie quantité disponible
   - Crée DroppedItem sur cellule actuelle
   - Retire de l'inventaire
   - Préserve durabilité si outil
6. **Frontend**:
   - Affiche notification de succès
   - Rafraîchit inventaire
   - Ferme dialog

### Scénario 2: Ramasser un objet

1. **Joueur se déplace sur une cellule**
2. **Section "📦 Objets au sol" s'affiche**
3. **Joueur clique sur "Ramasser"**
4. **Backend**:
   - Vérifie joueur sur même cellule
   - Vérifie capacité de poids
   - Ajoute à inventaire
   - Préserve durabilité
   - Supprime DroppedItem
5. **Frontend**:
   - Affiche notification
   - Rafraîchit carte et inventaire
   - Objet disparaît de la liste

---

## 🛡️ Sécurité et Validations

### Backend Validations

**Dépôt (Drop)**:
- ✅ Item existe dans inventaire du joueur
- ✅ Quantité > 0
- ✅ Quantité ≤ quantité disponible
- ✅ Cellule actuelle existe ou est créée

**Ramassage (Pickup)**:
- ✅ DroppedItem existe
- ✅ Joueur sur même cellule (grid_x, grid_y)
- ✅ Poids additionnel ≤ capacité restante
- ✅ Suppression atomique de l'objet

### Frontend Validations

- ✅ Quantité limitée au max disponible
- ✅ Boutons désactivés pendant chargement
- ✅ Messages d'erreur clairs
- ✅ Rafraîchissement automatique après actions

---

## 📊 Cas d'Usage

### 1. Transfert d'objets entre joueurs
```
Joueur A dépose 10x Pierre à (5, 3)
Joueur B arrive à (5, 3)
Joueur B ramasse 10x Pierre
```

### 2. Stockage temporaire
```
Joueur A surchargé de 15kg
Dépose 5x Minerai de Fer (3kg chacun)
Continue son exploration
Revient plus tard ramasser
```

### 3. Drop de tools usés
```
Pioche à 5/100 durabilité
Joueur dépose la pioche cassée
Autre joueur peut la ramasser pour réparer
```

### 4. Commerce entre joueurs
```
Joueur A dépose 20x Bois
Joueur B dépose 10x Pierre au même endroit
Échange tacite de ressources
```

---

## 🚀 Améliorations Futures Possibles

### 1. Système d'Expiration
```python
expires_at = timezone.now() + timedelta(hours=24)
```
- Items disparaissent après 24h
- Tâche cron pour nettoyage automatique

### 2. Protection d'Items
```python
is_protected = BooleanField(default=False)
protected_for = ForeignKey(Player, null=True)
```
- Items protégés pour X minutes
- Seul le déposeur peut ramasser

### 3. Sacs/Conteneurs
```python
class Container(models.Model):
    name = models.CharField()
    capacity = models.IntegerField()
    items = ManyToMany(DroppedItem)
```
- Sacs déposables avec multiple items
- Coffres permanents

### 4. Notifications
- Alerte si quelqu'un ramasse vos items
- Historique des drops/pickups
- Log d'activité

### 5. Marqueurs sur la Carte
- Icône spécial sur cellules avec items
- Compteur d'items au sol
- Filtrage par type

---

## 📝 Fichiers Modifiés/Créés

### Backend

- ✅ `game/models.py` - Ajout du modèle DroppedItem
- ✅ `game/migrations/0023_droppeditem.py` - Migration base de données
- ✅ `game/serializers.py` - DroppedItemSerializer
- ✅ `game/views/inventory_views.py` - Endpoints drop/pickup
- ✅ `game/views/map_views.py` - Inclusion dropped_items dans cell

### Frontend

- ✅ `frontend/src/services/api.js` - inventoryAPI.drop() et .pickup()
- ✅ `frontend/src/components/inventory/Inventory.js` - Dialog drop, handler
- ✅ `frontend/src/components/inventory/InventoryItem.js` - Bouton déposer
- ✅ `frontend/src/components/map/GameMap.js` - Section objets au sol

---

## ✅ Statut

**Phase Drop System**: ✅ COMPLÈTE

- Backend model: ✅ Implémenté
- Database migration: ✅ Appliquée
- API endpoints: ✅ Implémentés
- Frontend UI: ✅ Implémenté
- Pickup functionality: ✅ Implémenté
- Tests: ✅ Compilation réussie

**Date**: 2025-01-25
**Version**: Drop System v1.0

---

## 🎮 Guide d'Utilisation Rapide

### Pour Déposer
1. Ouvrez votre inventaire (onglet Inventaire)
2. Trouvez l'item à déposer
3. Cliquez sur "Déposer"
4. Choisissez la quantité
5. Confirmez

### Pour Ramasser
1. Allez sur une cellule avec des objets (section "📦 Objets au sol")
2. Cliquez sur "Ramasser" à côté de l'objet voulu
3. L'objet est ajouté à votre inventaire

**Note**: Assurez-vous d'avoir assez de capacité de poids avant de ramasser !
