import { useFilters } from './useFilters';

/**
 * Hook spécialisé pour le filtrage de l'inventaire
 * Utilise le hook générique useFilters avec une configuration spécifique
 */
export const useInventoryFilters = (inventory) => {
    const config = {
        searchFields: ['material.name'],
        categoryField: 'material.category',
        rarityField: 'material.rarity',
        defaultSort: 'name',
        isGrouped: true,
        enableViewMode: true,
        enableCategoryExpansion: true,
        autoExpandOnSearch: true
    };

    const result = useFilters(inventory, config);

    // Alias pour compatibilité avec le code existant
    return {
        ...result,
        filteredInventory: result.filteredItems
    };
};
