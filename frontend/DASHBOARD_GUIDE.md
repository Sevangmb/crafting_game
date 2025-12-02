# Guide d'Utilisation du Dashboard

## Accès au Dashboard

1. Connectez-vous à l'application
2. Cliquez sur l'icône **📊 Dashboard** dans l'AppBar (en haut à droite)
3. Le tableau de bord s'ouvre dans un dialog plein écran

## Sections du Dashboard

### 📈 Statistiques Principales (Cartes en Haut)

**Carte Niveau** (Violet)
- Niveau actuel du joueur
- Points d'expérience (XP)

**Carte Énergie** (Rose)
- Énergie actuelle
- Énergie maximum

**Carte Objets** (Bleu)
- Nombre d'objets uniques
- Quantité totale dans l'inventaire

**Carte Crafts** (Vert)
- Nombre total de fabrications effectuées

### 📊 Graphiques

**Distribution par Rareté** (Camembert)
- Répartition des items par niveau de rareté
- Couleurs :
  - 🔴 Legendary (Rouge)
  - 🟣 Epic (Violet)
  - 🔵 Rare (Bleu)
  - 🟢 Uncommon (Vert)
  - ⚪ Common (Gris)

**Top 5 Items** (Barres)
- Les 5 items avec les plus grandes quantités
- Permet d'identifier rapidement les ressources abondantes

**Recettes les plus Craftées** (Barres Horizontales)
- Top 5 des recettes utilisées
- Historique limité aux 50 derniers crafts

**Inventaire par Type** (Compteurs)
- 🍎 Nourriture - Items consommables
- ⚒️ Matériaux - Items de craft

**Profil Joueur** (Détails)
- Position sur la grille (X, Y)
- Énergie actuelle / maximum
- Niveau et XP

## Fonctionnement de l'Historique de Crafting

### Enregistrement Automatique
Chaque fois que vous craftez un item :
1. Le craft est enregistré dans le store Zustand
2. Les informations sauvegardées :
   - Nom de la recette
   - Quantité craftée
   - Matériau résultant
   - Horodatage

### Limite de l'Historique
- Maximum **50 crafts** conservés
- Les plus récents en premier (LIFO)
- Réinitialisation possible via le restart de partie

## Astuces d'Utilisation

### Pour Maximiser les Stats
1. **Craftez régulièrement** pour augmenter le compteur de crafts
2. **Diversifiez les recettes** pour voir différentes barres dans le graphe
3. **Collectez des items rares** pour enrichir le camembert

### Pour Analyser votre Progression
- Vérifiez le **ratio nourriture/matériaux** pour équilibrer votre inventaire
- Consultez les **top items** pour identifier les ressources à consommer
- Suivez les **recettes favorites** pour optimiser votre stratégie

### Performance
- Le dashboard recalcule les stats en temps réel
- Tous les graphiques sont **responsives**
- Utilisez le **scroll** pour voir toutes les sections

## Intégration avec le Store Zustand

### State Utilisé
```javascript
// Player
const player = useGameStore(state => state.player);

// Inventory
const inventory = useGameStore(state => state.inventory);

// Crafting History
const craftingHistory = useGameStore(state => state.craftingHistory);
```

### Mise à Jour Automatique
Le dashboard se met à jour automatiquement quand :
- ✅ Vous craftez un item (historique +1)
- ✅ Vous récoltez des matériaux (inventaire actualisé)
- ✅ Vous consommez de la nourriture (stats joueur mises à jour)
- ✅ Vous gagnez de l'XP ou montez de niveau

## Debug avec DevTools

Le store Zustand est configuré avec les **devtools** activées.

### Pour inspecter le state :
1. Ouvrez les DevTools du navigateur (F12)
2. Allez dans l'onglet **Redux DevTools** (extension requise)
3. Vous verrez toutes les actions et le state du store "GameStore"

### Actions à surveiller :
- `setInventory` - Mise à jour de l'inventaire
- `addCraftingHistory` - Nouveau craft enregistré
- `setPlayer` - Mise à jour du joueur
- `setRecipes` - Chargement des recettes

## Personnalisation Potentielle

### Couleurs des Charts
Modifiez les constantes dans `Dashboard.js` :
```javascript
const RARITY_COLORS = {
  common: '#9e9e9e',
  uncommon: '#4caf50',
  rare: '#2196f3',
  epic: '#9c27b0',
  legendary: '#f44336',
};
```

### Nombre de Top Items
Changez `.slice(0, 5)` dans le calcul de `topItems` :
```javascript
const topItems = [...inventory]
  .sort((a, b) => b.quantity - a.quantity)
  .slice(0, 10) // Top 10 au lieu de 5
```

### Taille de l'Historique
Modifiez le slice dans `recipesSlice.js` :
```javascript
craftingHistory: [craft, ...state.craftingHistory]
  .slice(0, 100) // 100 au lieu de 50
```

## Troubleshooting

### Le Dashboard est vide
- ✅ Vérifiez que vous avez des items dans l'inventaire
- ✅ Craftez au moins un item pour voir les stats de crafting
- ✅ Rechargez la page si les données ne s'affichent pas

### Les Graphiques ne s'affichent pas
- ✅ Assurez-vous que Recharts est installé : `npm install recharts`
- ✅ Vérifiez la console pour les erreurs
- ✅ Testez avec un inventaire non vide

### L'Historique de Crafting est vide
- ✅ Craftez un item depuis l'onglet "Fabrication"
- ✅ Vérifiez que `addCraftingHistory` est appelé dans `CraftingPanel.js`

## Support et Évolutions

Pour toute question ou suggestion d'amélioration :
- Consultez `ARCHITECTURE.md` pour les détails techniques
- Vérifiez le code source dans `src/components/Dashboard/`
- Utilisez les DevTools Zustand pour debugger le state
