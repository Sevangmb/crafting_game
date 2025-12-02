import React from 'react';
import {
    ListItem,
    Box,
    Typography,
    Chip,
    Button,
    Tooltip,
    TextField,
    Alert
} from '@mui/material';
import { getRarityColor } from '../../utils/gameLogic';
import { useGameStore, selectPlayer } from '../../stores/useGameStore';

const RecipeItem = React.memo(({
    recipe,
    quantity,
    onQuantityChange,
    onCraft,
    canCraft,
    viewMode = 'expanded',
    inventory = []
}) => {
    const player = useGameStore(selectPlayer);
    const flatInventory = inventory ? Object.values(inventory).flat() : [];

    const energyCost = recipe.energy_cost * quantity;
    const playerEnergy = player?.energy || 0;
    const hasEnoughEnergy = playerEnergy >= energyCost;

    // Helper to check workstation requirement
    const hasRequiredWorkstation = (recipe) => {
        // This logic might need to be passed down or re-implemented if we don't pass playerWorkstations
        // For now, let's assume the parent handles the "canCraft" logic which includes workstation checks
        // But for UI display, we might need to know.
        // Ideally, we should pass `hasStation` as a prop.
        return true; // Placeholder if we don't have the data here. 
        // Actually, let's trust the `canCraft` prop for the button state, 
        // but for the specific warning message, we might need more info.
        // Let's keep it simple for now and rely on generic "canCraft".
    };

    if (viewMode === 'compact') {
        return (
            <ListItem
                sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    p: 1,
                }}
            >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                    <Typography variant="subtitle1" sx={{ flex: 1 }}>
                        {recipe.icon} {recipe.name}
                    </Typography>
                    <Chip
                        label={`x${recipe.result_quantity * quantity}`}
                        size="small"
                        color="primary"
                    />
                    <Chip
                        label={`${energyCost}⚡`}
                        size="small"
                        color={hasEnoughEnergy ? 'success' : 'error'}
                    />
                    <Button
                        variant="contained"
                        size="small"
                        onClick={() => onCraft(recipe.id)}
                        disabled={!canCraft || !hasEnoughEnergy}
                    >
                        Craft
                    </Button>
                </Box>
            </ListItem>
        );
    }

    return (
        <ListItem
            sx={{
                flexDirection: 'column',
                alignItems: 'stretch',
                border: 1,
                borderColor: 'divider',
                borderRadius: 1,
                mb: 2,
                p: 2,
                backgroundColor: canCraft && hasEnoughEnergy ? 'rgba(76, 175, 80, 0.04)' : 'transparent',
            }}
        >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h6">
                        {recipe.icon} {recipe.name}
                    </Typography>
                    {recipe.result_material?.rarity && (
                        <Chip
                            label={recipe.result_material.rarity}
                            size="small"
                            sx={{
                                bgcolor: getRarityColor(recipe.result_material.rarity, 0.15),
                                color: getRarityColor(recipe.result_material.rarity),
                                textTransform: 'capitalize',
                                fontSize: '0.7rem'
                            }}
                        />
                    )}
                </Box>
                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Tooltip title={`Coût énergie: ${energyCost}`}>
                        <Chip
                            label={`${energyCost}⚡`}
                            color={hasEnoughEnergy ? 'success' : 'error'}
                            size="small"
                        />
                    </Tooltip>
                    <Chip
                        label={canCraft ? 'Peut fabriquer' : 'Matériaux manquants'}
                        color={canCraft ? 'success' : 'error'}
                        size="small"
                    />
                </Box>
            </Box>

            <Typography variant="body2" color="text.secondary" gutterBottom>
                {recipe.description}
            </Typography>

            {recipe.required_workstation && (
                <Box sx={{ my: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                        Station requise:
                    </Typography>
                    <Chip
                        icon={<span>{recipe.required_workstation.icon}</span>}
                        label={recipe.required_workstation.name}
                        // We don't have the exact check here easily without passing more props, 
                        // so we'll default to a neutral color or rely on parent passing a prop if needed.
                        // For now, let's just show the station.
                        color="default"
                        size="small"
                        variant="outlined"
                    />
                </Box>
            )}

            <Box sx={{ my: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                    Ingrédients:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {recipe.ingredients && recipe.ingredients.map((ingredient) => {
                        const inventoryItem = flatInventory.find((item) => item.material.id === ingredient.material.id);
                        const have = inventoryItem?.quantity || 0;
                        const need = ingredient.quantity * quantity;
                        return (
                            <Tooltip key={ingredient.id} title={`${ingredient.material.name} - Nécessaire: ${need}, Possédé: ${have}`}>
                                <Chip
                                    label={`${ingredient.material.icon} ${ingredient.material.name} (${have}/${need})`}
                                    color={have >= need ? 'success' : 'error'}
                                    size="small"
                                    variant="outlined"
                                />
                            </Tooltip>
                        );
                    })}
                </Box>
            </Box>

            <Box sx={{ my: 1 }}>
                <Typography variant="subtitle2" gutterBottom>
                    Résultat:
                </Typography>
                <Chip
                    label={`${recipe.result_material.icon} ${recipe.result_material.name} x${recipe.result_quantity * quantity}`}
                    color="primary"
                    size="small"
                />
            </Box>

            <Box sx={{ display: 'flex', gap: 1, mt: 1, alignItems: 'center' }}>
                <TextField
                    type="number"
                    label="Quantité"
                    size="small"
                    value={quantity}
                    onChange={(e) => onQuantityChange(recipe.id, e.target.value)}
                    inputProps={{ min: 1 }}
                    sx={{ width: 100 }}
                />
                <Tooltip title={!hasEnoughEnergy ? `Énergie insuffisante (${playerEnergy}/${energyCost})` : ''}>
                    <span>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={() => onCraft(recipe.id)}
                            disabled={!canCraft || !hasEnoughEnergy}
                            fullWidth
                            sx={{ minWidth: 120 }}
                        >
                            Fabriquer x{quantity}
                        </Button>
                    </span>
                </Tooltip>
                <Typography variant="caption" color="text.secondary">
                    Ctrl+Enter pour craft rapide
                </Typography>
            </Box>
        </ListItem>
    );
});

export default RecipeItem;
