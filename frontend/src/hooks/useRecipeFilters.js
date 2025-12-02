import { useMemo, useState } from 'react';
import { useGameStore, selectPlayer } from '../stores/useGameStore';
import { useFilters } from './useFilters';

/**
 * Hook spécialisé pour le filtrage des recettes
 * Utilise le hook générique useFilters avec des filtres personnalisés pour le crafting
 */
export const useRecipeFilters = (recipes, inventory, canCraft) => {
    const player = useGameStore(selectPlayer);

    // Configuration des filtres personnalisés pour les recettes
    const customFilters = useMemo(() => [
        {
            key: 'craftableOnly',
            label: 'Fabricable uniquement',
            defaultValue: false,
            test: (recipe) => canCraft(recipe)
        },
        {
            key: 'hasAllIngredients',
            label: 'Tous les ingrédients',
            defaultValue: false,
            test: (recipe) => {
                const flatInventory = Object.values(inventory).flat();
                return recipe.ingredients.every((ingredient) => {
                    const inventoryItem = flatInventory.find((item) => item.material.id === ingredient.material.id);
                    return inventoryItem && inventoryItem.quantity >= ingredient.quantity;
                });
            }
        }
    ], [inventory, canCraft]);

    const config = {
        searchFields: ['name', 'description', 'result_material.name'],
        categoryField: 'category',
        rarityField: 'result_material.rarity',
        defaultSort: 'name',
        isGrouped: false,
        customFilters
    };

    const filterResult = useFilters(recipes, config);

    // Filtres supplémentaires spécifiques aux recettes (workstation, energy)
    const {
        customFilterStates,
        setCustomFilter,
        filteredItems,
        ...rest
    } = filterResult;

    // États additionnels pour les filtres de recettes
    const [workstationFilter, setWorkstationFilter] = useState('all');
    const [energyFilter, setEnergyFilter] = useState('all');

    // Appliquer les filtres supplémentaires
    const filteredAndSortedRecipes = useMemo(() => {
        let filtered = [...filteredItems];

        if (workstationFilter !== 'all') {
            if (workstationFilter === 'none') {
                filtered = filtered.filter(recipe => !recipe.required_workstation);
            } else {
                filtered = filtered.filter(recipe => recipe.required_workstation?.id === parseInt(workstationFilter));
            }
        }

        if (energyFilter !== 'all') {
            const playerEnergy = player?.energy || 0;
            if (energyFilter === 'affordable') {
                filtered = filtered.filter(recipe => recipe.energy_cost <= playerEnergy);
            } else if (energyFilter === 'expensive') {
                filtered = filtered.filter(recipe => recipe.energy_cost > playerEnergy);
            }
        }

        return filtered;
    }, [filteredItems, workstationFilter, energyFilter, player]);

    return {
        ...rest,
        globalSearch: rest.searchTerm,
        setGlobalSearch: rest.setSearchTerm,
        workstationFilter,
        setWorkstationFilter,
        energyFilter,
        setEnergyFilter,
        craftableOnly: customFilterStates.craftableOnly,
        setCraftableOnly: (value) => setCustomFilter('craftableOnly', value),
        hasAllIngredients: customFilterStates.hasAllIngredients,
        setHasAllIngredients: (value) => setCustomFilter('hasAllIngredients', value),
        filteredAndSortedRecipes
    };
};

