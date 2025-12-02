import React from 'react';
import {
    Box,
    Typography,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    List,
    Chip
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { CATEGORY_ICONS, CATEGORY_NAMES } from '../../utils/gameLogic';
import RecipeItem from './RecipeItem';

function RecipeList({
    groupedRecipes,
    craftQuantities,
    handleQuantityChange,
    handleCraft,
    canCraft,
    expandedCategories,
    toggleCategory,
    viewMode,
    inventory
}) {
    // Helper to check if any recipe in a list is craftable
    const hasCraftableRecipe = (list) => {
        return list.some(recipe => canCraft(recipe));
    };

    if (Object.keys(groupedRecipes).length === 0) {
        return (
            <Box sx={{
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                height: 200,
                textAlign: 'center',
                p: 3,
                borderRadius: 1,
                bgcolor: 'background.paper'
            }}>
                <Box>
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                        🔍 Aucune recette trouvée
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        Essayez d'ajuster vos filtres ou votre recherche
                    </Typography>
                </Box>
            </Box>
        );
    }

    return (
        <Box>
            {Object.entries(groupedRecipes).map(([category, list]) => (
                list.length === 0 ? null : (
                    <Accordion
                        key={category}
                        expanded={!!expandedCategories?.[category]}
                        onChange={() => toggleCategory(category)}
                        sx={{ mb: 1 }}
                    >
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                {CATEGORY_ICONS[category]} {CATEGORY_NAMES[category]}
                                <Chip
                                    label={`${list.length} recette${list.length > 1 ? 's' : ''}`}
                                    size="small"
                                    sx={{ ml: 1 }}
                                    color={hasCraftableRecipe(list) ? 'success' : 'default'}
                                    variant={hasCraftableRecipe(list) ? 'filled' : 'outlined'}
                                />
                            </Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                            <List>
                                {list.map((recipe) => (
                                    <RecipeItem
                                        key={recipe.id}
                                        recipe={recipe}
                                        quantity={craftQuantities[recipe.id] || 1}
                                        onQuantityChange={handleQuantityChange}
                                        onCraft={handleCraft}
                                        canCraft={canCraft(recipe, craftQuantities[recipe.id] || 1)}
                                        viewMode={viewMode}
                                        inventory={inventory}
                                    />
                                ))}
                            </List>
                        </AccordionDetails>
                    </Accordion>
                )
            ))}
        </Box>
    );
}

export default RecipeList;
