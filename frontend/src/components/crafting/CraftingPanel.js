import React, { useEffect, useCallback } from 'react';
import { useGameStore } from '../../stores/useGameStore';
import {
    Paper,
    Typography,
    Button,
    Box,
    Tooltip,
    IconButton,
    Tabs,
    Tab,
    List,
    ListItem,
    ListItemText,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Chip
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewCompactIcon from '@mui/icons-material/ViewCompact';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { groupRecipesByCategory } from '../../utils/gameLogic';
import { useCrafting, useRecipeFilters } from '../../hooks';

// Import new components
import CraftingFilters from './CraftingFilters';
import RecipeList from './RecipeList';

function CraftingPanel({ inventory, onCraft }) {
    // Custom Hooks
    const {
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
    } = useCrafting(inventory, onCraft);

    const {
        globalSearch, setGlobalSearch,
        rarityFilter, setRarityFilter,
        workstationFilter, setWorkstationFilter,
        energyFilter, setEnergyFilter,
        craftableOnly, setCraftableOnly,
        hasAllIngredients, setHasAllIngredients,
        filteredAndSortedRecipes
    } = useRecipeFilters(recipes, inventory, canCraft);

    // UI State
    const [viewMode, setViewMode] = React.useState('expanded');
    const [showFilters, setShowFilters] = React.useState(false);
    const [activeTab, setActiveTab] = React.useState(0);

    const craftingExpandedCategories = useGameStore((state) => state.craftingExpandedCategories);
    const toggleCraftingCategory = useGameStore((state) => state.toggleCraftingCategory);

    const groupedRecipes = React.useMemo(() => groupRecipesByCategory(filteredAndSortedRecipes), [filteredAndSortedRecipes]);

    const handleKeyDown = useCallback((event) => {
        if (event.ctrlKey || event.metaKey) {
            if (event.key === 'Enter') {
                event.preventDefault();
                const firstCraftable = filteredAndSortedRecipes.find(recipe => canCraft(recipe));
                if (firstCraftable) {
                    handleCraft(firstCraftable.id);
                }
            }
        }
    }, [filteredAndSortedRecipes, canCraft, handleCraft]);

    useEffect(() => {
        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);

    const handleTabChange = (event, newValue) => {
        setActiveTab(newValue);
    };

    return (
        <Box sx={{ height: 'calc(100vh - 250px)', display: 'flex', flexDirection: 'column' }}>
            {/* Title Header */}
            <Box sx={{
                px: 2,
                py: 1.5,
                bgcolor: 'background.paper',
                borderBottom: 1,
                borderColor: 'divider',
                display: 'flex',
                alignItems: 'center',
                gap: 2
            }}>
                <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1.5, color: 'primary.main', fontWeight: 600 }}>
                    🔨 Atelier de Fabrication
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '0.875rem' }}>
                    Créez des objets et améliorez votre équipement
                </Typography>
            </Box>

            <Paper sx={{ flex: 1, borderRadius: 0, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <Box sx={{ p: 1.5, borderBottom: 1, borderColor: 'divider' }}>
                    <Box sx={{
                        display: 'flex',
                        flexDirection: { xs: 'column', sm: 'row' },
                        alignItems: { xs: 'stretch', sm: 'center' },
                        justifyContent: 'space-between',
                        gap: 1
                    }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 600, fontSize: '0.85rem' }}>
                            Fabrication
                        </Typography>
                    <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <Tooltip title="Basculer les filtres">
                            <IconButton size="small" onClick={() => setShowFilters(!showFilters)}>
                                <FilterListIcon />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title="Vue compacte">
                            <IconButton
                                size="small"
                                onClick={() => setViewMode(viewMode === 'expanded' ? 'compact' : 'expanded')}
                            >
                                {viewMode === 'compact' ? <ViewListIcon /> : <ViewCompactIcon />}
                            </IconButton>
                        </Tooltip>
                        <Button
                            variant="outlined"
                            size="small"
                            onClick={fetchDuplicates}
                            disabled={dupLoading}
                            sx={{ display: { xs: 'none', md: 'inline-flex' } }}
                        >
                            🔎 Duplicatas
                        </Button>
                        <Button
                            variant="contained"
                            size="small"
                            color="error"
                            onClick={deleteDuplicates}
                            disabled={delLoading}
                            sx={{ display: { xs: 'none', md: 'inline-flex' } }}
                        >
                            🗑️ Supprimer
                        </Button>
                    </Box>
                </Box>

                <CraftingFilters
                    globalSearch={globalSearch}
                    setGlobalSearch={setGlobalSearch}
                    rarityFilter={rarityFilter}
                    setRarityFilter={setRarityFilter}
                    workstationFilter={workstationFilter}
                    setWorkstationFilter={setWorkstationFilter}
                    energyFilter={energyFilter}
                    setEnergyFilter={setEnergyFilter}
                    craftableOnly={craftableOnly}
                    setCraftableOnly={setCraftableOnly}
                    hasAllIngredients={hasAllIngredients}
                    setHasAllIngredients={setHasAllIngredients}
                    allWorkstations={allWorkstations}
                    filteredCount={filteredAndSortedRecipes.length}
                    showFilters={showFilters}
                />
            </Box>

            <Tabs
                value={activeTab}
                onChange={handleTabChange}
                sx={{
                    borderBottom: 1,
                    borderColor: 'divider',
                    '& .MuiTab-root': {
                        minHeight: 48,
                        textTransform: 'none',
                        fontSize: '0.875rem'
                    }
                }}
            >
                <Tab
                    label="Recettes"
                    icon={<ViewListIcon />}
                    iconPosition="start"
                    sx={{ minHeight: 48 }}
                />
            </Tabs>

            <Box sx={{ flex: 1, overflow: 'hidden' }}>
                {activeTab === 0 && (
                    <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                        {(duplicates?.duplicates_by_name?.length || duplicates?.duplicates_by_result_material?.length) ? (
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" gutterBottom>Doublons détectés</Typography>
                                <Accordion sx={{ mb: 1 }}>
                                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>Par nom de recette ({duplicates.duplicates_by_name.length})</AccordionSummary>
                                    <AccordionDetails>
                                        <List dense>
                                            {duplicates.duplicates_by_name.map((d) => (
                                                <ListItem key={d.name}>
                                                    <ListItemText
                                                        primary={`${d.name} (${d.count})`}
                                                        secondary={d.items.map(i => `#${i.id} → ${i.result_material__name || '—'}`).join(', ')}
                                                    />
                                                </ListItem>
                                            ))}
                                        </List>
                                    </AccordionDetails>
                                </Accordion>
                                <Accordion>
                                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>Par matériau résultat ({duplicates.duplicates_by_result_material.length})</AccordionSummary>
                                    <AccordionDetails>
                                        <List dense>
                                            {duplicates.duplicates_by_result_material.map((d) => (
                                                <ListItem key={d.result_material_id}>
                                                    <ListItemText
                                                        primary={`${d.result_material_name || 'Matériau'} (${d.count})`}
                                                        secondary={d.items.map(i => `#${i.id} ${i.name}`).join(', ')}
                                                    />
                                                </ListItem>
                                            ))}
                                        </List>
                                    </AccordionDetails>
                                </Accordion>
                            </Box>
                        ) : null}

                        {playerWorkstations.length > 0 && (
                            <Box sx={{ mb: 2 }}>
                                <Typography variant="subtitle2" gutterBottom>
                                    Stations possédées:
                                </Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                    {playerWorkstations.map((pw) => (
                                        <Chip
                                            key={pw.id}
                                            icon={<span>{pw.workstation.icon}</span>}
                                            label={`${pw.workstation.name} x${pw.quantity}`}
                                            color="info"
                                            size="small"
                                        />
                                    ))}
                                </Box>
                            </Box>
                        )}

                        <RecipeList
                            groupedRecipes={groupedRecipes}
                            craftQuantities={craftQuantities}
                            handleQuantityChange={handleQuantityChange}
                            handleCraft={handleCraft}
                            canCraft={canCraft}
                            expandedCategories={craftingExpandedCategories}
                            toggleCategory={toggleCraftingCategory}
                            viewMode={viewMode}
                            inventory={inventory}
                        />
                    </Box>
                )}
            </Box>
        </Paper>
        </Box>
    );
}

export default CraftingPanel;
