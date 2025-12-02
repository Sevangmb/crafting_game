import { useState, useMemo, useCallback, useEffect } from 'react';

/**
 * Hook générique avancé pour gérer le filtrage et le tri d'une liste d'items
 * Supporte les cas d'usage de l'inventaire, des recettes et autres collections
 * @param {Array|Object} items - Liste des items à filtrer ou objet groupé par catégories
 * @param {Object} config - Configuration du filtrage
 * @returns {Object} État et fonctions de filtrage
 */
export const useFilters = (items = [], config = {}) => {
    const {
        searchFields = ['name'], // Champs à rechercher
        categoryField = 'category',
        rarityField = 'rarity',
        defaultSort = 'name',
        isGrouped = false, // Si true, items est un objet {category: [items]}
        customFilters = [], // Filtres personnalisés [{key, label, test: (item) => boolean}]
        enableViewMode = false, // Active la gestion du mode d'affichage
        enableCategoryExpansion = false, // Active la gestion de l'expansion des catégories
        autoExpandOnSearch = false // Auto-expand les catégories lors d'une recherche
    } = config;

    // États des filtres de base
    const [searchTerm, setSearchTerm] = useState('');
    const [categoryFilter, setCategoryFilter] = useState('all');
    const [rarityFilter, setRarityFilter] = useState('all');
    const [sortBy, setSortBy] = useState(defaultSort);

    // États UI optionnels
    const [viewMode, setViewMode] = useState('grid');
    const [showFilters, setShowFilters] = useState(false);
    const [expandedCategories, setExpandedCategories] = useState({});

    // États pour filtres personnalisés
    const [customFilterStates, setCustomFilterStates] = useState(() => {
        const initial = {};
        customFilters.forEach(filter => {
            initial[filter.key] = filter.defaultValue ?? false;
        });
        return initial;
    });

    /**
     * Convertit les items en format plat si nécessaire
     */
    const flatItems = useMemo(() => {
        if (isGrouped) {
            return Object.values(items).flat();
        }
        return Array.isArray(items) ? items : [];
    }, [items, isGrouped]);

    /**
     * Filtre et trie les items selon les critères
     */
    const filteredItems = useMemo(() => {
        let filtered = [...flatItems];

        // Filtrage par recherche textuelle
        if (searchTerm) {
            filtered = filtered.filter(item => {
                return searchFields.some(field => {
                    const value = getNestedValue(item, field);
                    return value && value.toLowerCase().includes(searchTerm.toLowerCase());
                });
            });
        }

        // Filtrage par catégorie
        if (categoryFilter !== 'all') {
            filtered = filtered.filter(item => {
                const category = getNestedValue(item, categoryField);
                return category === categoryFilter;
            });
        }

        // Filtrage par rareté
        if (rarityFilter !== 'all') {
            filtered = filtered.filter(item => {
                const rarity = getNestedValue(item, rarityField);
                return rarity === rarityFilter;
            });
        }

        // Filtres personnalisés
        customFilters.forEach(filter => {
            if (customFilterStates[filter.key]) {
                filtered = filtered.filter(filter.test);
            }
        });

        // Tri
        filtered.sort((a, b) => {
            switch (sortBy) {
                case 'name':
                    const nameA = getNestedValue(a, 'name') || '';
                    const nameB = getNestedValue(b, 'name') || '';
                    return nameA.localeCompare(nameB);

                case 'quantity':
                    return (b.quantity || 0) - (a.quantity || 0);

                case 'rarity':
                    const rarityA = getNestedValue(a, rarityField) || '';
                    const rarityB = getNestedValue(b, rarityField) || '';
                    return rarityA.localeCompare(rarityB);

                case 'recent':
                    const dateA = new Date(a.updated_at || 0);
                    const dateB = new Date(b.updated_at || 0);
                    return dateB - dateA;

                default:
                    return 0;
            }
        });

        return filtered;
    }, [flatItems, searchTerm, categoryFilter, rarityFilter, sortBy, searchFields, categoryField, rarityField, customFilters, customFilterStates]);

    /**
     * Regroupe les items filtrés par catégorie si nécessaire
     */
    const groupedFilteredItems = useMemo(() => {
        if (!isGrouped) return filteredItems;

        const grouped = {};
        let totalCount = 0;

        filteredItems.forEach(item => {
            const category = getNestedValue(item, categoryField) || 'other';
            if (!grouped[category]) {
                grouped[category] = [];
            }
            grouped[category].push(item);
            totalCount++;
        });

        return { data: grouped, count: totalCount };
    }, [filteredItems, isGrouped, categoryField]);

    /**
     * Auto-expand les catégories lors d'une recherche
     */
    useEffect(() => {
        if (autoExpandOnSearch && searchTerm && isGrouped) {
            const allExpanded = {};
            const grouped = groupedFilteredItems.data || {};
            Object.keys(grouped).forEach(cat => allExpanded[cat] = true);
            setExpandedCategories(allExpanded);
        }
    }, [searchTerm, autoExpandOnSearch, isGrouped, groupedFilteredItems]);

    /**
     * Toggle l'expansion d'une catégorie
     */
    const toggleCategory = useCallback((category) => {
        setExpandedCategories(prev => ({
            ...prev,
            [category]: !prev[category]
        }));
    }, []);

    /**
     * Réinitialise tous les filtres
     */
    const resetFilters = useCallback(() => {
        setSearchTerm('');
        setCategoryFilter('all');
        setRarityFilter('all');
        setSortBy(defaultSort);
        const resetCustom = {};
        customFilters.forEach(filter => {
            resetCustom[filter.key] = filter.defaultValue ?? false;
        });
        setCustomFilterStates(resetCustom);
    }, [defaultSort, customFilters]);

    /**
     * Met à jour un filtre personnalisé
     */
    const setCustomFilter = useCallback((key, value) => {
        setCustomFilterStates(prev => ({
            ...prev,
            [key]: value
        }));
    }, []);

    /**
     * Obtient les catégories uniques des items
     */
    const availableCategories = useMemo(() => {
        const categories = new Set();
        flatItems.forEach(item => {
            const category = getNestedValue(item, categoryField);
            if (category) categories.add(category);
        });
        return Array.from(categories);
    }, [flatItems, categoryField]);

    /**
     * Obtient les raretés uniques des items
     */
    const availableRarities = useMemo(() => {
        const rarities = new Set();
        flatItems.forEach(item => {
            const rarity = getNestedValue(item, rarityField);
            if (rarity) rarities.add(rarity);
        });
        return Array.from(rarities);
    }, [flatItems, rarityField]);

    const result = {
        // Items filtrés
        filteredItems: isGrouped ? groupedFilteredItems : filteredItems,

        // États des filtres
        searchTerm,
        categoryFilter,
        rarityFilter,
        sortBy,

        // Setters
        setSearchTerm,
        setCategoryFilter,
        setRarityFilter,
        setSortBy,

        // Utilitaires
        resetFilters,
        availableCategories,
        availableRarities,

        // Statistiques
        totalItems: flatItems.length,
        filteredCount: isGrouped ? groupedFilteredItems.count : filteredItems.length,

        // Filtres personnalisés
        customFilterStates,
        setCustomFilter
    };

    // Ajouter les états UI optionnels
    if (enableViewMode) {
        result.viewMode = viewMode;
        result.setViewMode = setViewMode;
        result.showFilters = showFilters;
        result.setShowFilters = setShowFilters;
    }

    if (enableCategoryExpansion) {
        result.expandedCategories = expandedCategories;
        result.toggleCategory = toggleCategory;
    }

    return result;
};

/**
 * Fonction helper pour accéder aux propriétés imbriquées
 * @param {Object} obj - Objet source
 * @param {String} path - Chemin vers la propriété (ex: 'material.name')
 */
function getNestedValue(obj, path) {
    return path.split('.').reduce((current, key) => current?.[key], obj);
}

export default useFilters;
