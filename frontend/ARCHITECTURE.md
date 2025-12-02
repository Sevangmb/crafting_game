# Architecture Frontend - Jeu de Crafting

## Stack Technique

### ✅ Inventaire
- **TanStack Table v8** (headless table) - Gestion des colonnes, tri, filtres
- **@tanstack/react-virtual** - Virtualisation des lignes pour performance
- **MUI Components** - Interface Material Design
- Implémentation : `src/components/Inventory.js`

### ✅ Éditeur de Recettes (DAG)
- **React Flow** (@xyflow/react v12) - Visualisation du graphe
- **Dagre** - Layout automatique des nodes
- **MUI Dialog** - Modal d'affichage
- Implémentation :
  - `src/components/RecipeFlow/RecipeFlowEditor.js`
  - `src/components/RecipeFlow/RecipeFlowDialog.js`
  - `src/components/RecipeFlow/MaterialNode.js`
  - `src/components/RecipeFlow/RecipeNode.js`

### ✅ Dashboard avec Charts
- **Recharts** - Bibliothèque de charts React
- **MUI Cards** - Conteneurs pour les visualisations
- Types de charts implémentés :
  - **PieChart** - Distribution par rareté
  - **BarChart** - Top items et recettes
  - **Cards avec gradients** - Statistiques clés
- Implémentation :
  - `src/components/Dashboard/Dashboard.js`
  - `src/components/Dashboard/DashboardDialog.js`

### ✅ State Management - Zustand
- **Store centralisé** avec slices modulaires
- **DevTools** activés pour debugging
- Structure :
  ```
  src/stores/
  ├── useGameStore.js      # Store principal
  ├── playerSlice.js       # État du joueur
  ├── inventorySlice.js    # Items et matériaux
  ├── recipesSlice.js      # Recettes et historique
  └── uiSlice.js          # État de l'interface
  ```

## Structure des Stores Zustand

### PlayerSlice
- `player` - Données du joueur (level, XP, énergie, position)
- `isAuthenticated` - État d'authentification
- `currentCell` - Cellule actuelle de la carte
- Actions : `setPlayer`, `updatePlayer`, `resetPlayer`

### InventorySlice
- `inventory` - Liste des items du joueur
- `materials` - Liste de tous les matériaux du jeu
- `loading` - État de chargement
- Actions : `setInventory`, `addInventoryItem`, `updateInventoryItem`, `removeInventoryItem`
- Selector calculé : `getInventoryStats()` - Statistiques agrégées

### RecipesSlice
- `recipes` - Liste des recettes disponibles
- `craftingHistory` - Historique des crafts (max 50 derniers)
- Actions : `setRecipes`, `addCraftingHistory`, `clearCraftingHistory`
- Selector calculé : `getCraftingStats()` - Top recettes, total crafts

### UiSlice
- `currentTab` - Onglet actif (0: Inventaire, 1: Fabrication)
- `recipeFlowOpen` - État du dialog de recettes
- `dashboardOpen` - État du dashboard
- `restartDialogOpen` - État du dialog de redémarrage
- `menuAnchorEl` - Ancre pour le menu
- Actions : toggle et setters pour chaque état

## Fonctionnalités du Dashboard

### Statistiques en temps réel
- **Niveau et XP** - Progression du joueur
- **Énergie** - État actuel et maximum
- **Inventaire** - Nombre d'objets et quantité totale
- **Crafts** - Nombre total de fabrications

### Visualisations
1. **Distribution par rareté** (PieChart)
   - Répartition des items par niveau de rareté
   - Couleurs codées par rareté

2. **Top 5 items** (BarChart)
   - Items avec les plus grandes quantités
   - Couleurs variées par item

3. **Recettes les plus craftées** (BarChart horizontal)
   - Historique des fabrications
   - Top 5 des recettes utilisées

4. **Inventaire par type** (Cards)
   - Séparation nourriture / matériaux
   - Compteurs visuels

5. **Profil joueur** (Cards)
   - Position sur la grille
   - Statistiques détaillées

## Intégration dans l'App

### Nouvelle icône dans l'AppBar
```jsx
<IconButton onClick={() => setDashboardOpen(true)}>
  <DashboardIcon />
</IconButton>
```

### Historique de crafting
Le `CraftingPanel` enregistre automatiquement chaque craft dans le store :
```javascript
addCraftingHistory({
  recipeId: recipe.id,
  recipeName: recipe.name,
  quantity: quantity,
  resultMaterial: recipe.result_material?.name,
});
```

## Avantages de cette Architecture

### Performance
- ✅ Virtualisation de l'inventaire (pas de limite de taille)
- ✅ Selectors Zustand optimisés pour éviter les re-renders
- ✅ Memoization des calculs de stats

### Maintenabilité
- ✅ Séparation claire des responsabilités (slices)
- ✅ State centralisé et prévisible
- ✅ DevTools pour debugging

### Scalabilité
- ✅ Ajout facile de nouveaux slices
- ✅ Charts modulaires et réutilisables
- ✅ Store extensible sans refactoring majeur

### UX
- ✅ Interface Material Design cohérente
- ✅ Visualisations interactives et colorées
- ✅ Feedback visuel immédiat
- ✅ Responsive design

## Prochaines Évolutions Possibles

1. **Persistence** - LocalStorage pour sauvegarder l'historique
2. **Analytics** - Plus de métriques (temps de jeu, distance parcourue)
3. **Export** - Télécharger les statistiques en CSV
4. **Comparaisons** - Graphes d'évolution temporelle
5. **Achievements** - Système de succès basé sur les stats

## Commandes de Développement

```bash
# Depuis frontend/
npm start        # Démarrer le dev server
npm run build    # Build de production
npm test         # Lancer les tests
```

## Dépendances Clés

```json
{
  "@tanstack/react-table": "^8.21.3",
  "@tanstack/react-virtual": "^3.13.12",
  "@xyflow/react": "^12.9.0",
  "@mui/material": "^7.3.4",
  "recharts": "^3.3.0",
  "zustand": "^5.0.8",
  "dagre": "^0.8.5"
}
```
