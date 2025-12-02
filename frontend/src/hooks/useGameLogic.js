import { useMemo } from 'react';
import { useGameStore } from '../stores/useGameStore';
import {
  calculateInventoryStats,
  calculateCraftingStats,
  groupRecipesByCategory,
  groupInventoryByCategory,
} from '../utils/gameLogic';

// Hook pour centraliser la logique métier du jeu
export const useGameLogic = () => {
  const inventory = useGameStore((state) => state.inventory);
  const recipes = useGameStore((state) => state.recipes);
  const craftingHistory = useGameStore((state) => state.craftingHistory);

  // Statistiques d'inventaire calculées
  const inventoryStats = useMemo(() => calculateInventoryStats(inventory), [inventory]);

  // Statistiques de crafting calculées
  const craftingStats = useMemo(() => calculateCraftingStats(craftingHistory), [craftingHistory]);

  // Recettes groupées par catégories
  const groupedRecipes = useMemo(() => groupRecipesByCategory(recipes), [recipes]);

  // Inventaire groupé par catégories
  const groupedInventory = useMemo(() => groupInventoryByCategory(inventory), [inventory]);

  // Inventaire aplati pour les recherches
  const flatInventory = useMemo(() => {
    if (Array.isArray(inventory)) return inventory;
    return Object.values(inventory || {}).flat();
  }, [inventory]);

  return {
    inventoryStats,
    craftingStats,
    groupedRecipes,
    groupedInventory,
    flatInventory,
  };
};