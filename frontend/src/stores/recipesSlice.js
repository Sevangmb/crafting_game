// Slice pour les recettes
export const createRecipesSlice = (set, get) => ({
  recipes: [],
  craftingHistory: [],

  setRecipes: (recipes) => set({ recipes }),

  addCraftingHistory: (craft) =>
    set((state) => ({
      craftingHistory: [
        {
          ...craft,
          timestamp: new Date().toISOString(),
        },
        ...state.craftingHistory,
      ].slice(0, 50), // Garder seulement les 50 derniers
    })),

  clearCraftingHistory: () => set({ craftingHistory: [] }),

  // Statistiques calculées
  getCraftingStats: () => {
    const state = get();
    const totalCrafts = state.craftingHistory.length;
    
    // Compter les crafts par recette
    const craftsByRecipe = state.craftingHistory.reduce((acc, craft) => {
      const recipeName = craft.recipeName || 'Unknown';
      acc[recipeName] = (acc[recipeName] || 0) + (craft.quantity || 1);
      return acc;
    }, {});

    // Top 5 des recettes les plus craftées
    const topRecipes = Object.entries(craftsByRecipe)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([name, count]) => ({ name, count }));

    return {
      totalCrafts,
      craftsByRecipe,
      topRecipes,
    };
  },
});
