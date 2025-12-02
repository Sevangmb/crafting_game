import { useState, useEffect, useCallback } from 'react';
import { useGameStore, selectPlayer } from '../stores/useGameStore';
import { recipesAPI, craftingAPI, workstationAPI } from '../services/api';
import { useAchievements } from './useAchievements';
import logger from '../utils/logger';

export const useCrafting = (inventory, onCraft) => {
    const [recipes, setRecipes] = useState([]);
    const [craftQuantities, setCraftQuantities] = useState({});
    const [playerWorkstations, setPlayerWorkstations] = useState([]);
    const [allWorkstations, setAllWorkstations] = useState([]);
    const [dupLoading, setDupLoading] = useState(false);
    const [duplicates, setDuplicates] = useState({ duplicates_by_name: [], duplicates_by_result_material: [] });
    const [delLoading, setDelLoading] = useState(false);

    const addCraftingHistory = useGameStore((state) => state.addCraftingHistory);
    const setRecipesStore = useGameStore((state) => state.setRecipes);
    const showNotification = useGameStore((state) => state.showNotification);
    const player = useGameStore(selectPlayer);
    const { handleAchievements } = useAchievements();

    const fetchRecipes = useCallback(async () => {
        try {
            const response = await recipesAPI.getAll();
            setRecipes(response.data);
            setRecipesStore(response.data);
            const initialQuantities = {};
            response.data.forEach((recipe) => {
                initialQuantities[recipe.id] = 1;
            });
            setCraftQuantities(initialQuantities);
        } catch (error) {
            logger.error('Failed to fetch recipes:', error);
        }
    }, [setRecipesStore]);

    const fetchWorkstations = useCallback(async () => {
        try {
            const [playerWsResponse, allWsResponse] = await Promise.all([
                workstationAPI.getPlayerWorkstations(),
                workstationAPI.getAll(),
            ]);
            setPlayerWorkstations(playerWsResponse.data);
            setAllWorkstations(allWsResponse.data);
        } catch (error) {
            logger.error('Failed to fetch workstations:', error);
        }
    }, []);

    const fetchDuplicates = useCallback(async () => {
        setDupLoading(true);
        try {
            const res = await recipesAPI.getDuplicates();
            setDuplicates(res.data || { duplicates_by_name: [], duplicates_by_result_material: [] });
            showNotification('Audit des doublons terminé', 'info');
        } catch (e) {
            logger.error('Failed to fetch duplicates:', e);
            showNotification('Échec de l\'audit des doublons', 'error');
        } finally {
            setDupLoading(false);
        }
    }, [showNotification]);

    const deleteDuplicates = useCallback(async () => {
        setDelLoading(true);
        try {
            const res = await recipesAPI.deleteDuplicates();
            showNotification(`Doublons supprimés: ${res.data?.removed_ids?.length || 0}`, 'success');
            await fetchDuplicates();
            await fetchRecipes();
        } catch (e) {
            logger.error('Failed to delete duplicates:', e);
            showNotification("Échec de la suppression des doublons (réservé admin)", 'error');
        } finally {
            setDelLoading(false);
        }
    }, [fetchDuplicates, fetchRecipes, showNotification]);

    useEffect(() => {
        fetchRecipes();
        fetchWorkstations();
    }, [fetchRecipes, fetchWorkstations]);

    const hasRequiredWorkstation = useCallback((recipe) => {
        if (!recipe.required_workstation) return true;
        return playerWorkstations.some(
            (pw) => pw.workstation.id === recipe.required_workstation.id && pw.quantity >= 1
        );
    }, [playerWorkstations]);

    const canCraft = useCallback((recipe, quantity = 1) => {
        if (!recipe || !inventory) return false;
        if (recipe.energy_cost > (player?.energy || 0)) return false;
        if (!hasRequiredWorkstation(recipe)) return false;

        const flatInventory = Object.values(inventory).flat();
        return recipe.ingredients.every((ingredient) => {
            const inventoryItem = flatInventory.find((item) => item.material?.id === ingredient.material?.id);
            return inventoryItem && inventoryItem.quantity >= ingredient.quantity * quantity;
        });
    }, [inventory, player, hasRequiredWorkstation]);

    const handleCraft = useCallback(async (recipeId) => {
        const quantity = craftQuantities[recipeId] || 1;
        const recipe = recipes.find((r) => r.id === recipeId);

        try {
            const response = await craftingAPI.craft(recipeId, quantity);

            // Handle achievements
            handleAchievements(response);

            if (recipe) {
                addCraftingHistory({
                    recipeId: recipe.id,
                    recipeName: recipe.name,
                    quantity: quantity,
                    resultMaterial: recipe.result_material?.name,
                });
            }
            showNotification(response.data.message, 'success');
            if (onCraft) onCraft();
            fetchWorkstations();
        } catch (error) {
            logger.error('Failed to craft:', error);
            showNotification(error.response?.data?.error || 'Échec de la fabrication', 'error');
        }
    }, [craftQuantities, recipes, addCraftingHistory, showNotification, onCraft, fetchWorkstations, handleAchievements]);

    const handleQuantityChange = useCallback((recipeId, value) => {
        const quantity = Math.max(1, parseInt(value) || 1);
        setCraftQuantities((prev) => ({
            ...prev,
            [recipeId]: quantity,
        }));
    }, []);

    return {
        recipes,
        craftQuantities,
        playerWorkstations,
        allWorkstations,
        duplicates,
        dupLoading,
        delLoading,
        fetchDuplicates,
        deleteDuplicates,
        handleCraft,
        handleQuantityChange,
        canCraft
    };
};
