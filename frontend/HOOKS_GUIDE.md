# Guide des Hooks Personnalisés

## Vue d'ensemble

Les hooks personnalisés simplifient l'accès au store Zustand et fournissent des helpers utiles pour les opérations courantes.

## 📦 Hooks Disponibles

### usePlayer()

Accès simplifié aux données du joueur.

```javascript
import { usePlayer } from '../hooks';

const MyComponent = () => {
  const { player, energyPercent, isLowEnergy, hasEnergy } = usePlayer();
  
  // Vérifier si le joueur a assez d'énergie
  if (hasEnergy(5)) {
    // Effectuer une action
  }
};
```

**Retourne:**
- `player` - Objet du joueur
- `setPlayer` - Définir les données du joueur
- `updatePlayer` - Mettre à jour partiellement
- `currentCell` - Cellule actuelle
- `setCurrentCell` - Définir la cellule
- `hasEnergy(amount)` - Helper: vérifie l'énergie
- `energyPercent` - Pourcentage d'énergie (0-100)
- `isLowEnergy` - true si énergie < 20

### useInventory()

Gestion de l'inventaire avec helpers.

```javascript
import { useInventory } from '../hooks';

const MyComponent = () => {
  const {
    inventory,
    stats,
    hasItem,
    getItemQuantity,
    foodItems,
    materialItems
  } = useInventory();
  
  // Vérifier si on a un item
  if (hasItem(materialId, 5)) {
    console.log('Vous avez au moins 5 de cet item');
  }
  
  // Obtenir la quantité
  const quantity = getItemQuantity(materialId);
};
```

**Retourne:**
- `inventory` - Liste complète
- `setInventory` - Définir l'inventaire
- `addInventoryItem` - Ajouter un item
- `stats` - Statistiques calculées (total, foodCount, etc.)
- `findItemByMaterialId(id)` - Trouver un item
- `hasItem(id, qty)` - Vérifier la possession
- `getItemQuantity(id)` - Obtenir la quantité
- `filterByType(isFood)` - Filtrer par type
- `filterByRarity(rarity)` - Filtrer par rareté
- `foodItems` - Items de nourriture uniquement
- `materialItems` - Matériaux uniquement

### useRecipes()

Gestion des recettes et du crafting.

```javascript
import { useRecipes } from '../hooks';

const MyComponent = () => {
  const {
    recipes,
    craftableRecipes,
    canCraftRecipe,
    getMaxCraftable,
    stats
  } = useRecipes();
  
  // Vérifier si craftable
  if (canCraftRecipe(recipe, 2)) {
    console.log('Peut crafter 2x cette recette');
  }
  
  // Obtenir le max craftable
  const max = getMaxCraftable(recipe);
};
```

**Retourne:**
- `recipes` - Liste des recettes
- `setRecipes` - Définir les recettes
- `craftingHistory` - Historique (max 50)
- `addCraftingHistory` - Ajouter au log
- `stats` - Stats (totalCrafts, topRecipes)
- `canCraftRecipe(recipe, qty)` - Vérifier si craftable
- `craftableRecipes` - Recettes actuellement craftables
- `getMaxCraftable(recipe)` - Nombre max craftable

### useNotifications()

Simplification des notifications.

```javascript
import { useNotifications } from '../hooks';

const MyComponent = () => {
  const { success, error, warning, info } = useNotifications();
  
  // Afficher une notification
  success('Action réussie!');
  error('Une erreur est survenue');
  warning('Attention!');
  info('Information utile');
};
```

**Méthodes:**
- `success(message)` - Notification verte
- `error(message)` - Notification rouge
- `warning(message)` - Notification orange
- `info(message)` - Notification bleue
- `show(message, severity)` - Méthode générique

## 🎯 Avantages

### 1. Code Plus Propre

**Avant (sans hooks):**
```javascript
const player = useGameStore((state) => state.player);
const energyPercent = player ? (player.energy / player.max_energy) * 100 : 0;
const isLowEnergy = player ? player.energy < 20 : false;
```

**Après (avec hooks):**
```javascript
const { player, energyPercent, isLowEnergy } = usePlayer();
```

### 2. Réutilisabilité

Les helpers sont disponibles partout:
```javascript
const { hasItem, getItemQuantity } = useInventory();
const { canCraftRecipe, getMaxCraftable } = useRecipes();
```

### 3. Performance

Les hooks utilisent `useMemo` pour optimiser les calculs:
- Stats calculées une seule fois
- Recettes craftables mises en cache
- Filtres optimisés

### 4. Type Safety

Les hooks retournent des objets typés avec des méthodes explicites.

## 📊 Statistiques Calculées

### inventoryStats
```javascript
{
  total: 15,           // Nombre d'items uniques
  foodCount: 5,        // Items de nourriture
  materialCount: 10,   // Items matériaux
  rarityCount: {       // Par rareté
    common: 8,
    rare: 5,
    legendary: 2
  }
}
```

### craftingStats
```javascript
{
  totalCrafts: 42,     // Total de crafts
  topRecipes: [        // Top 5 recettes
    { name: 'Épée', count: 15 },
    { name: 'Pioche', count: 10 }
  ]
}
```

## 🔨 Exemples d'Usage

### Vérifier avant de crafter

```javascript
const CraftButton = ({ recipe }) => {
  const { canCraftRecipe, getMaxCraftable } = useRecipes();
  const { success, error } = useNotifications();
  
  const handleCraft = async () => {
    if (!canCraftRecipe(recipe)) {
      error('Ingrédients insuffisants');
      return;
    }
    
    // Craft l'item
    success('Item crafté!');
  };
  
  const max = getMaxCraftable(recipe);
  
  return (
    <Button onClick={handleCraft} disabled={max === 0}>
      Crafter (max: {max})
    </Button>
  );
};
```

### Afficher les stats

```javascript
const InventorySummary = () => {
  const { stats, foodItems, materialItems } = useInventory();
  
  return (
    <Box>
      <Typography>Total: {stats.total}</Typography>
      <Typography>Nourriture: {foodItems.length}</Typography>
      <Typography>Matériaux: {materialItems.length}</Typography>
    </Box>
  );
};
```

### Vérifier l'énergie

```javascript
const MoveButton = ({ direction }) => {
  const { hasEnergy, isLowEnergy } = usePlayer();
  const { warning } = useNotifications();
  
  const handleMove = () => {
    if (!hasEnergy(1)) {
      warning('Pas assez d\'énergie!');
      return;
    }
    // Déplacement
  };
  
  return (
    <Button 
      onClick={handleMove}
      color={isLowEnergy ? 'error' : 'primary'}
    >
      {direction}
    </Button>
  );
};
```

## 🎨 Composants Créés

### PlayerStatsCompact

Composant réutilisable pour afficher les stats du joueur dans l'AppBar.

**Usage:**
```javascript
import PlayerStatsCompact from './components/PlayerStats/PlayerStatsCompact';

<AppBar>
  <Toolbar>
    <PlayerStatsCompact />
  </Toolbar>
</AppBar>
```

**Affiche:**
- Niveau & XP
- Énergie avec barre de progression
- Localisation actuelle

## 🚀 Bonnes Pratiques

### 1. Utiliser les hooks dans les composants

```javascript
// ✅ BON
const MyComponent = () => {
  const { player } = usePlayer();
  const { inventory } = useInventory();
  // ...
};

// ❌ MAUVAIS - accès direct au store
const MyComponent = () => {
  const player = useGameStore(state => state.player);
  const inventory = useGameStore(state => state.inventory);
  // ...
};
```

### 2. Destructurer uniquement ce dont vous avez besoin

```javascript
// ✅ BON - optimisé
const { hasEnergy, isLowEnergy } = usePlayer();

// ❌ MOINS BON - charge tout
const playerHook = usePlayer();
```

### 3. Utiliser les helpers

```javascript
// ✅ BON
const { hasItem } = useInventory();
if (hasItem(materialId, 5)) { /* ... */ }

// ❌ MOINS BON
const { inventory } = useInventory();
const item = inventory.find(i => i.material.id === materialId);
if (item && item.quantity >= 5) { /* ... */ }
```

## 📚 Import Centralisé

Tous les hooks sont exportés depuis `hooks/index.js`:

```javascript
// Import multiple
import { usePlayer, useInventory, useRecipes, useNotifications } from '../hooks';

// Ou import individuel
import { usePlayer } from '../hooks/usePlayer';
```

## 🔄 Intégration avec le Store

Les hooks utilisent le store Zustand en interne mais fournissent une API plus simple:

```
usePlayer() → playerSlice (Zustand)
useInventory() → inventorySlice (Zustand)
useRecipes() → recipesSlice (Zustand)
useNotifications() → notificationSlice (Zustand)
```

Tout reste synchronisé via le store centralisé!
