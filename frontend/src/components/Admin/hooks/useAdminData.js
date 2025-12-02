import { useState, useEffect } from 'react';
import { materialsAPI, workstationAPI, recipesAPI, recipeIngredientsAPI, mobsAPI, vehicleTypesAPI, weaponsAPI, clothingAPI, configAPI, buildingAPI, achievementsAPI } from '../../../services/api';

export const useAdminData = (open) => {
    // Materials state
    const [materials, setMaterials] = useState([]);
    const [matLoading, setMatLoading] = useState(false);
    const [matSelection, setMatSelection] = useState([]);

    // Workstations state
    const [workstations, setWorkstations] = useState([]);
    const [wsLoading, setWsLoading] = useState(false);
    const [wsSelection, setWsSelection] = useState([]);

    // Recipes state
    const [recipes, setRecipes] = useState([]);
    const [recLoading, setRecLoading] = useState(false);
    const [recSelection, setRecSelection] = useState([]);

    // Ingredients state
    const [ingredients, setIngredients] = useState([]);
    const [ingLoading, setIngLoading] = useState(false);
    const [ingSelection, setIngSelection] = useState([]);

    // Mobs (animals)
    const [mobs, setMobs] = useState([]);
    const [mobsLoading, setMobsLoading] = useState(false);
    const [mobsSelection, setMobsSelection] = useState([]);

    // Weapons
    const [weapons, setWeapons] = useState([]);
    const [weaponsLoading, setWeaponsLoading] = useState(false);
    const [weaponsSelection, setWeaponsSelection] = useState([]);

    // Clothing
    const [clothing, setClothing] = useState([]);
    const [clothingLoading, setClothingLoading] = useState(false);
    const [clothingSelection, setClothingSelection] = useState([]);

    // Vehicle types
    const [vehicleTypes, setVehicleTypes] = useState([]);
    const [vehicleTypesLoading, setVehicleTypesLoading] = useState(false);
    const [vehicleTypesSelection, setVehicleTypesSelection] = useState([]);

    // Game configuration
    const [configs, setConfigs] = useState([]);
    const [configsLoading, setConfigsLoading] = useState(false);
    const [configsSelection, setConfigsSelection] = useState([]);

    // Achievements (read-only)
    const [achievements, setAchievements] = useState([]);
    const [achievementsLoading, setAchievementsLoading] = useState(false);

    // Building types (read-only list)
    const [buildingTypes, setBuildingTypes] = useState([]);
    const [buildingTypesLoading, setBuildingTypesLoading] = useState(false);

    // Player buildings (read-only list)
    const [buildings, setBuildings] = useState([]);
    const [buildingsLoading, setBuildingsLoading] = useState(false);

    const loadMaterials = async () => {
        setMatLoading(true);
        try {
            const res = await materialsAPI.getAll();
            setMaterials(res.data || []);
        } finally {
            setMatLoading(false);
        }
    };

    const loadWorkstations = async () => {
        setWsLoading(true);
        try {
            const res = await workstationAPI.getAll();
            setWorkstations(res.data || []);
        } finally {
            setWsLoading(false);
        }
    };

    const loadRecipes = async () => {
        setRecLoading(true);
        try {
            const res = await recipesAPI.getAll();
            setRecipes(res.data || []);
        } finally {
            setRecLoading(false);
        }
    };

    const loadIngredients = async () => {
        setIngLoading(true);
        try {
            const res = await recipeIngredientsAPI.getAll();
            setIngredients(res.data || []);
        } finally {
            setIngLoading(false);
        }
    };

    const loadMobs = async () => {
        setMobsLoading(true);
        try {
            const res = await mobsAPI.getAll();
            setMobs(res.data || []);
        } finally {
            setMobsLoading(false);
        }
    };

    const loadWeapons = async () => {
        setWeaponsLoading(true);
        try {
            const res = await weaponsAPI.getAll();
            setWeapons(res.data || []);
        } finally {
            setWeaponsLoading(false);
        }
    };

    const loadClothing = async () => {
        setClothingLoading(true);
        try {
            const res = await clothingAPI.getAll();
            setClothing(res.data || []);
        } finally {
            setClothingLoading(false);
        }
    };

    const loadVehicleTypes = async () => {
        setVehicleTypesLoading(true);
        try {
            const res = await vehicleTypesAPI.getAll();
            setVehicleTypes(res.data || []);
        } finally {
            setVehicleTypesLoading(false);
        }
    };

    const loadConfigs = async () => {
        setConfigsLoading(true);
        try {
            const res = await configAPI.getAll();
            setConfigs(res.data || []);
        } finally {
            setConfigsLoading(false);
        }
    };

    const loadAchievements = async () => {
        setAchievementsLoading(true);
        try {
            const res = await achievementsAPI.getAll();
            setAchievements(res.data || []);
        } finally {
            setAchievementsLoading(false);
        }
    };

    const loadBuildingTypes = async () => {
        setBuildingTypesLoading(true);
        try {
            const res = await buildingAPI.getTypes();
            setBuildingTypes(res.data || []);
        } finally {
            setBuildingTypesLoading(false);
        }
    };

    const loadBuildings = async () => {
        setBuildingsLoading(true);
        try {
            const res = await buildingAPI.getMyBuildings();
            setBuildings(res.data || []);
        } finally {
            setBuildingsLoading(false);
        }
    };

    useEffect(() => {
        if (open) {
            loadMaterials();
            loadWorkstations();
            loadRecipes();
            loadIngredients();
            loadMobs();
            loadWeapons();
            loadClothing();
            loadVehicleTypes();
            loadConfigs();
            loadAchievements();
            loadBuildingTypes();
            loadBuildings();
        }
    }, [open]);

    const addEmptyRow = async (type, isStaff) => {
        if (!isStaff) return;
        if (type === 'materials') {
            const created = await materialsAPI.create({ name: 'Nouveau Matériau', description: '', icon: '📦', rarity: 'common', is_food: false, energy_restore: 0 });
            await loadMaterials();
            return created?.data?.id;
        } else if (type === 'workstations') {
            const created = await workstationAPI.create({ name: 'Nouvelle Station', description: '', icon: '🏗️' });
            await loadWorkstations();
            return created?.data?.id;
        } else if (type === 'recipes') {
            const defaultMaterialId = materials?.[0]?.id;
            if (!defaultMaterialId) return;
            const created = await recipesAPI.create({ name: 'Nouvelle Recette', description: '', icon: '🧪', result_material_id: defaultMaterialId, result_quantity: 1, required_workstation_id: null });
            await loadRecipes();
            return created?.data?.id;
        } else if (type === 'ingredients') {
            const defaultRecipeId = recipes?.[0]?.id;
            const defaultMaterialId = materials?.[0]?.id;
            if (!defaultRecipeId || !defaultMaterialId) return;
            const created = await recipeIngredientsAPI.create({ recipe: defaultRecipeId, material: defaultMaterialId, quantity: 1 });
            await loadIngredients();
            return created?.data?.id;
        } else if (type === 'mobs') {
            const created = await mobsAPI.create({ name: 'Nouvel Animal', description: '', icon: '🐾', level: 1, health: 20, attack: 5, defense: 0, xp_reward: 10, aggression_level: 'neutral', spawn_rate: 0.3 });
            await loadMobs();
            return created?.data?.id;
        } else if (type === 'weapons') {
            const created = await weaponsAPI.create({ name: 'Nouvelle Arme', description: '', icon: '🗡️', attack: 1, defense: 0, weight: 0.0, slot: 'main_hand' });
            await loadWeapons();
            return created?.data?.id;
        } else if (type === 'clothing') {
            const created = await clothingAPI.create({ name: 'Nouveau Vêtement', description: '', icon: '👕', defense: 0, weight: 0.0, slot: 'chest' });
            await loadClothing();
            return created?.data?.id;
        } else if (type === 'vehicleTypes') {
            const created = await vehicleTypesAPI.create({ name: 'Nouveau Véhicule', description: '', icon: '🚲', carry_bonus: 0.0, speed_bonus: 0, energy_efficiency: 0, max_durability: 100 });
            await loadVehicleTypes();
            return created?.data?.id;
        } else if (type === 'configs') {
            const created = await configAPI.create({ key: 'nouvelle_cle', value: '{}', description: '' });
            await loadConfigs();
            return created?.data?.id;
        }
    };

    const deleteSelected = async (type, isStaff) => {
        if (!isStaff) return;
        if (type === 'materials') {
            for (const id of matSelection) {
                await materialsAPI.delete(id);
            }
            await loadMaterials();
            setMatSelection([]);
        } else if (type === 'workstations') {
            for (const id of wsSelection) {
                await workstationAPI.delete(id);
            }
            await loadWorkstations();
            setWsSelection([]);
        } else if (type === 'recipes') {
            for (const id of recSelection) {
                await recipesAPI.delete(id);
            }
            await loadRecipes();
            setRecSelection([]);
        } else if (type === 'ingredients') {
            for (const id of ingSelection) {
                await recipeIngredientsAPI.delete(id);
            }
            await loadIngredients();
            setIngSelection([]);
        } else if (type === 'mobs') {
            for (const id of mobsSelection) {
                await mobsAPI.delete(id);
            }
            await loadMobs();
            setMobsSelection([]);
        } else if (type === 'weapons') {
            for (const id of weaponsSelection) {
                await weaponsAPI.delete(id);
            }
            await loadWeapons();
            setWeaponsSelection([]);
        } else if (type === 'clothing') {
            for (const id of clothingSelection) {
                await clothingAPI.delete(id);
            }
            await loadClothing();
            setClothingSelection([]);
        } else if (type === 'vehicleTypes') {
            for (const id of vehicleTypesSelection) {
                await vehicleTypesAPI.delete(id);
            }
            await loadVehicleTypes();
            setVehicleTypesSelection([]);
        }
    };

    const processRowUpdate = async (newRow, oldRow, type, isStaff) => {
        if (!isStaff) return oldRow;
        try {
            if (type === 'materials') {
                await materialsAPI.update(newRow.id, newRow);
                return newRow;
            } else if (type === 'workstations') {
                await workstationAPI.update(newRow.id, newRow);
                return newRow;
            } else if (type === 'recipes') {
                // Map nested reads to admin write fields
                const payload = {
                    name: newRow.name,
                    description: newRow.description || '',
                    icon: newRow.icon || '',
                    result_material_id: newRow.result_material_id || newRow.result_material?.id,
                    result_quantity: Number(newRow.result_quantity) || 1,
                    required_workstation_id: newRow.required_workstation_id ?? (newRow.required_workstation?.id || null),
                };
                await recipesAPI.update(newRow.id, payload);
                return newRow;
            } else if (type === 'ingredients') {
                const payload = {
                    recipe: newRow.recipe?.id || newRow.recipe,
                    material: newRow.material?.id || newRow.material,
                    quantity: Number(newRow.quantity) || 1,
                };
                await recipeIngredientsAPI.update(newRow.id, payload);
                return newRow;
            } else if (type === 'mobs') {
                await mobsAPI.update(newRow.id, newRow);
                return newRow;
            } else if (type === 'weapons') {
                await weaponsAPI.update(newRow.id, newRow);
                return newRow;
            } else if (type === 'clothing') {
                await clothingAPI.update(newRow.id, newRow);
                return newRow;
            } else if (type === 'vehicleTypes') {
                await vehicleTypesAPI.update(newRow.id, newRow);
                return newRow;
            } else if (type === 'configs') {
                const payload = {
                    key: newRow.key,
                    value: newRow.value,
                    description: newRow.description || '',
                };
                await configAPI.update(newRow.id, payload);
                return newRow;
            }
        } catch (e) {
            console.error('Update failed', e);
            return oldRow;
        }
    };

    return {
        materials, matLoading, matSelection, setMatSelection,
        workstations, wsLoading, wsSelection, setWsSelection,
        recipes, recLoading, recSelection, setRecSelection,
        ingredients, ingLoading, ingSelection, setIngSelection,
        mobs, mobsLoading, mobsSelection, setMobsSelection,
        weapons, weaponsLoading, weaponsSelection, setWeaponsSelection,
        clothing, clothingLoading, clothingSelection, setClothingSelection,
        vehicleTypes, vehicleTypesLoading, vehicleTypesSelection, setVehicleTypesSelection,
        configs, configsLoading, configsSelection, setConfigsSelection,
        achievements, achievementsLoading,
        buildingTypes, buildingTypesLoading,
        buildings, buildingsLoading,
        addEmptyRow, deleteSelected, processRowUpdate
    };
};
