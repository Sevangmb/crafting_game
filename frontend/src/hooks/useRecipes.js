import { useMemo } from 'react';
import { useGameStore } from '../stores/useGameStore';
import { useGameLogic } from './useGameLogic';
import { useInventory } from './useInventory';

/**
 * Hook personnalisé pour les recettes et le crafting
 */
export const useRecipes = () => {
  const recipes = useGameStore((state) => state.recipes);
  const setRecipes = useGameStore((state) => state.setRecipes);
  const craftingHistory = useGameStore((state) => state.craftingHistory);
  const addCraftingHistory = useGameStore((state) => state.addCraftingHistory);

  const { flatInventory } = useInventory();

  // Utiliser les statistiques centralisées
  const { craftingStats } = useGameLogic();

  // Vérifier si une recette peut être craftée
  const canCraftRecipe = (recipe, quantity = 1) => {
    if (!recipe || !recipe.ingredients) return false;

    return recipe.ingredients.every((ingredient) => {
      const inventoryItem = flatInventory.find(
        (item) => item.material.id === ingredient.material.id
      );
      return inventoryItem && inventoryItem.quantity >= ingredient.quantity * quantity;
    });
  };

  // Obtenir les recettes craftables
  const craftableRecipes = useMemo(() => {
    return recipes.filter((recipe) => canCraftRecipe(recipe));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [recipes, flatInventory]);

  // Obtenir le nombre de fois qu'une recette peut être craftée
  const getMaxCraftable = (recipe) => {
    if (!recipe || !recipe.ingredients || recipe.ingredients.length === 0) {
      return 0;
    }

    const maxQuantities = recipe.ingredients.map((ingredient) => {
      const inventoryItem = flatInventory.find(
        (item) => item.material.id === ingredient.material.id
      );
      if (!inventoryItem) return 0;
      return Math.floor(inventoryItem.quantity / ingredient.quantity);
    });

    return Math.min(...maxQuantities);
  };

  return {
    recipes,
    setRecipes,
    craftingHistory,
    addCraftingHistory,
    stats: craftingStats,
    // Helpers
    canCraftRecipe,
    craftableRecipes,
    getMaxCraftable,
  };
};
