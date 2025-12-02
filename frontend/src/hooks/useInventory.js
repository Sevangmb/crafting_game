import { useMemo } from 'react';
import { useGameStore } from '../stores/useGameStore';
import { useGameLogic } from './useGameLogic';

/**
 * Hook personnalisé pour accéder facilement à l'inventaire
 */
export const useInventory = () => {
  const inventory = useGameStore((state) => state.inventory);
  const setInventory = useGameStore((state) => state.setInventory);
  const addInventoryItem = useGameStore((state) => state.addInventoryItem);

  // Utiliser le hook centralisé pour la logique
  const { inventoryStats, flatInventory } = useGameLogic();

  // Helpers pour la recherche d'items
  const findItemByMaterialId = (materialId) => {
    return flatInventory.find((item) => item.material.id === materialId);
  };

  const hasItem = (materialId, quantity = 1) => {
    const item = findItemByMaterialId(materialId);
    return item ? item.quantity >= quantity : false;
  };

  const getItemQuantity = (materialId) => {
    const item = findItemByMaterialId(materialId);
    return item ? item.quantity : 0;
  };

  const filterByType = (isFood) => {
    return flatInventory.filter((item) => item.material.is_food === isFood);
  };

  const filterByRarity = (rarity) => {
    return flatInventory.filter((item) => item.material.rarity === rarity);
  };

  return {
    inventory,
    flatInventory,
    setInventory,
    addInventoryItem,
    stats: inventoryStats,
    // Helpers
    findItemByMaterialId,
    hasItem,
    getItemQuantity,
    filterByType,
    filterByRarity,
    // Données dérivées
    foodItems: filterByType(true),
    materialItems: filterByType(false),
  };
};
