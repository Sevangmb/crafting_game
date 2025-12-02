import { useEffect } from 'react';
import useConfigStore from '../stores/useConfigStore';

/**
 * Hook to load and access game configurations
 * Automatically loads configs on first use
 */
export const useGameConfig = () => {
    const {
        categoryIcons,
        categoryNames,
        rarityColors,
        rarityChipColors,
        biomeConfig,
        toolRequirements,
        mapConfig,
        loaded,
        loading,
        error,
        loadConfigs,
    } = useConfigStore();

    // Auto-load configs on mount if not already loaded
    useEffect(() => {
        if (!loaded && !loading) {
            loadConfigs();
        }
    }, [loaded, loading, loadConfigs]);

    return {
        // Configuration data
        categoryIcons,
        categoryNames,
        rarityColors,
        rarityChipColors,
        biomeConfig,
        toolRequirements,
        mapConfig,

        // State
        loaded,
        loading,
        error,

        // Actions
        loadConfigs,
    };
};

export default useGameConfig;
