import { create } from 'zustand';
import { configAPI } from '../services/api';
import logger from '../utils/logger';

// Default configurations in case API is not available
const DEFAULT_CONFIGS = {
    category_icons: {
        'bois': '🌲',
        'minerais': '⛏️',
        'nourriture': '🍎',
        'gemmes': '💎',
        'magie': '✨',
        'divers': '📦',
        'outils': '🔧',
        'armes': '⚔️',
        'armures': '🛡️',
        'ressources': '📦',
        'consommables': '🧪',
        'quêtes': '📜',
    },
    category_names: {
        'bois': 'Bois',
        'minerais': 'Minerais',
        'nourriture': 'Nourriture',
        'gemmes': 'Gemmes',
        'magie': 'Objets magiques',
        'divers': 'Divers',
        'outils': 'Outils',
        'armes': 'Armes',
        'armures': 'Armures',
        'ressources': 'Ressources',
        'consommables': 'Consommables',
        'quêtes': 'Objets de quête',
    },
    rarity_colors: {
        'common': '#ffffff',
        'uncommon': '#1eff00',
        'rare': '#0070dd',
        'epic': '#a335ee',
        'legendary': '#ff8000',
    },
    rarity_chip_colors: {
        'common': 'default',
        'uncommon': 'success',
        'rare': 'primary',
        'epic': 'secondary',
        'legendary': 'warning',
    },
    biome_config: {
        'plains': {
            'name': 'Plaines',
            'color': '#8bc34a',
            'materials': ['herbe', 'fleurs', 'baies'],
            'discover_xp': 10,
        },
        'forest': {
            'name': 'Forêt',
            'color': '#2e7d32',
            'materials': ['bois', 'champignons', 'baies'],
            'discover_xp': 15,
        },
        'mountain': {
            'name': 'Montagne',
            'color': '#9e9e9e',
            'materials': ['pierre', 'minerai de fer', 'charbon'],
            'discover_xp': 20,
        },
        'water': {
            'name': 'Point d\'eau',
            'color': '#2196f3',
            'materials': ['poisson', 'algues', 'coquillages'],
            'discover_xp': 15,
        },
        'desert': {
            'name': 'Désert',
            'color': '#ffeb3b',
            'materials': ['sable', 'cactus', 'os'],
            'discover_xp': 25,
        },
    },
    tool_requirements: {
        'mining': {
            'name': 'Pioche',
            'required_level': 1,
            'materials': [
                {'name': 'Bois', 'quantity': 2},
                {'name': 'Pierre', 'quantity': 1},
            ],
            'energy_saving': 0.2,
            'efficiency': 1.2,
        },
        'woodcutting': {
            'name': 'Hache',
            'required_level': 1,
            'materials': [
                {'name': 'Bois', 'quantity': 1},
                {'name': 'Pierre', 'quantity': 1},
            ],
            'energy_saving': 0.15,
            'efficiency': 1.15,
        },
        'fishing': {
            'name': 'Canne à pêche',
            'required_level': 5,
            'materials': [
                {'name': 'Bois', 'quantity': 2},
                {'name': 'Corde', 'quantity': 1},
            ],
            'energy_saving': 0.25,
            'efficiency': 1.3,
        },
    },
    map_config: {
        'grid_size': 1000,
        'cell_size': 100,
        'discovery_radius': 3,
        'regeneration_rate': 0.1,
        'max_resources': 100,
        'min_resources': 10,
    },
    xp_formula: {
        'base': 100,
        'exponent': 1.2,
        'multiplier': 1.0
    },
    energy_config: {
        'base_energy': 100,
        'regen_rate': 5,
        'regen_interval': 300
    },
    crafting_config: {
        'base_success_rate': 0.8,
        'critical_fail_chance': 0.05,
        'critical_success_chance': 0.05
    }
};

/**
 * Store for game configuration data loaded from the database
 */
const useConfigStore = create((set, get) => ({
    // Configuration data
    categoryIcons: {},
    categoryNames: {},
    rarityColors: {},
    rarityChipColors: {},
    biomeConfig: {},
    toolRequirements: {},
    mapConfig: {},
    xpFormula: {},
    energyConfig: {},
    craftingConfig: {},
    allConfigs: {},

    // Loading state
    loaded: false,
    loading: false,
    error: null,

    /**
     * Load all configurations from the API
     */
    loadConfigs: async () => {
        const { loading, loaded } = get();

        // Don't reload if already loaded or currently loading
        if (loaded || loading) {
            logger.debug('useConfigStore', 'Configs already loaded or loading');
            return;
        }

        set({ loading: true, error: null });

        try {
            logger.debug('useConfigStore', 'Loading configurations from API...');
            
            // Try to load from API first
            let configs = { ...DEFAULT_CONFIGS };
            
            try {
                const response = await configAPI.getAllConfigs();
                if (response && response.data) {
                    configs = { ...configs, ...response.data };
                    logger.debug('useConfigStore', 'Configurations loaded from API:', configs);
                }
            } catch (apiError) {
                logger.warn('Failed to load configurations from API, using defaults', apiError);
                // Continue with default configs
            }

            // Ensure all required configs are set
            const mergedConfigs = { ...DEFAULT_CONFIGS, ...configs };

            set({
                categoryIcons: mergedConfigs.category_icons || {},
                categoryNames: mergedConfigs.category_names || {},
                rarityColors: mergedConfigs.rarity_colors || {},
                rarityChipColors: mergedConfigs.rarity_chip_colors || {},
                biomeConfig: mergedConfigs.biome_config || {},
                toolRequirements: mergedConfigs.tool_requirements || {},
                mapConfig: mergedConfigs.map_config || {},
                xpFormula: mergedConfigs.xp_formula || {},
                energyConfig: mergedConfigs.energy_config || {},
                craftingConfig: mergedConfigs.crafting_config || {},
                allConfigs: mergedConfigs,
                loaded: true,
                loading: false,
            });
        } catch (error) {
            logger.error('Failed to load game configurations:', error);
            set({
                error: error.message,
                loading: false,
                // Fallback to default configs on error
                ...Object.entries(DEFAULT_CONFIGS).reduce((acc, [key, value]) => ({
                    ...acc,
                    [key.replace(/_([a-z])/g, g => g[1].toUpperCase())]: value
                }), {})
            });
        }
    },

    /**
     * Get a specific configuration value by key path
     * @param {string} path - Dot notation path to the config value (e.g., 'biome_config.forest.name')
     * @param {*} defaultValue - Default value if not found
     */
    getConfig: (path, defaultValue = null) => {
        const { allConfigs } = get();
        return path.split('.').reduce((obj, key) => 
            (obj && obj[key] !== undefined) ? obj[key] : defaultValue, allConfigs);
    },

    /**
     * Reset the store (for testing or logout)
     */
    reset: () => {
        set({
            categoryIcons: {},
            categoryNames: {},
            rarityColors: {},
            rarityChipColors: {},
            biomeConfig: {},
            toolRequirements: {},
            mapConfig: {},
            xpFormula: {},
            energyConfig: {},
            craftingConfig: {},
            allConfigs: {},
            loaded: false,
            loading: false,
            error: null,
        });
    },
}));

export default useConfigStore;
