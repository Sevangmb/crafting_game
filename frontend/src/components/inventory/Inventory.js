import React, { useState } from 'react';
import {
    Paper,
    Box,
    Typography,
    Grid,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    List,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { inventoryAPI, equipmentAPI } from '../../services/api';
import { useGameStore } from '../../stores/useGameStore';
import { CATEGORY_ICONS, CATEGORY_NAMES } from '../../utils/gameLogic';
import { useInventoryFilters } from '../../hooks';
import logger from '../../utils/logger';

// Import new components
import InventoryItem from './InventoryItem';

function Inventory({ inventory, onConsume }) {
    const [dropDialog, setDropDialog] = useState({ open: false, itemId: null, itemName: '', maxQuantity: 1 });
    const [dropQuantity, setDropQuantity] = useState(1);
    const {
        searchTerm,
        setSearchTerm,
        expandedCategories,
        toggleCategory,
        filteredInventory,
    } = useInventoryFilters(inventory);

    const showNotification = useGameStore((state) => state.showNotification);

    const handleConsume = async (itemId) => {
        try {
            const response = await inventoryAPI.consume(itemId);
            showNotification(response.data.message, 'success');
            if (onConsume) onConsume();
        } catch (error) {
            logger.error('Failed to consume item:', error);
            showNotification('Impossible d\'utiliser cet objet', 'error');
        }
    };

    const handleDropClick = (itemId, itemName, maxQuantity) => {
        setDropDialog({ open: true, itemId, itemName, maxQuantity });
        setDropQuantity(Math.min(1, maxQuantity));
    };

    const handleDropConfirm = async () => {
        try {
            const response = await inventoryAPI.drop(dropDialog.itemId, dropQuantity);
            showNotification(response.data.message, 'success');
            setDropDialog({ open: false, itemId: null, itemName: '', maxQuantity: 1 });
            if (onConsume) onConsume(); // Refresh inventory
        } catch (error) {
            logger.error('Failed to drop item:', error);
            showNotification(error.response?.data?.error || 'Impossible de déposer cet objet', 'error');
        }
    };

    const handleEquip = async (materialId, slot) => {
        try {
            const response = await equipmentAPI.equip(materialId, slot);
            showNotification(response.data.message || 'Équipement équipé!', 'success');
            if (onConsume) onConsume(); // Refresh inventory
        } catch (error) {
            logger.error('Failed to equip item:', error);
            showNotification(error.response?.data?.error || 'Impossible d\'équiper cet objet', 'error');
        }
    };

    const handleDropAll = async () => {
        try {
            // Get all items from inventory
            const allItems = Object.values(filteredInventory.data).flat();

            if (allItems.length === 0) {
                showNotification('Aucun objet à déposer', 'info');
                return;
            }

            let successCount = 0;
            let errorCount = 0;

            // Drop each item one by one
            for (const item of allItems) {
                try {
                    await inventoryAPI.drop(item.id, item.quantity);
                    successCount++;
                } catch (error) {
                    logger.error('Failed to drop item:', error);
                    errorCount++;
                }
                // Small delay to avoid overwhelming the server
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            if (successCount > 0) {
                showNotification(`✅ Déposé ${successCount} type(s) d'objets`, 'success');
            }
            if (errorCount > 0) {
                showNotification(`⚠️ ${errorCount} objet(s) n'ont pas pu être déposés`, 'warning');
            }

            // Refresh inventory
            if (onConsume) onConsume();
        } catch (error) {
            logger.error('Failed to drop all items:', error);
            showNotification('Erreur lors du dépôt des objets', 'error');
        }
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
                    🎒 Inventaire
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary', fontSize: '0.875rem' }}>
                    Gérez vos ressources et équipements
                </Typography>
            </Box>

            {/* Search and Actions Bar */}
            <Box sx={{ px: 1.5, py: 1.5, borderBottom: 1, borderColor: 'divider', display: 'flex', gap: 1.5, alignItems: 'center', bgcolor: 'background.paper' }}>
                <TextField
                    fullWidth
                    size="small"
                    placeholder="Rechercher des objets..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    sx={{
                        '& .MuiOutlinedInput-root': {
                            bgcolor: 'background.default',
                            fontSize: '0.875rem',
                        }
                    }}
                />
                <Button
                    variant="contained"
                    color="error"
                    size="small"
                    onClick={handleDropAll}
                    disabled={filteredInventory.count === 0}
                    sx={{ whiteSpace: 'nowrap', minWidth: 120, fontSize: '0.75rem' }}
                >
                    🗑️ Supprimer
                </Button>
            </Box>

            {/* Category List */}
            <Box sx={{ flex: 1, overflow: 'auto', bgcolor: 'background.default' }}>
                {Object.keys(filteredInventory.data).length === 0 ? (
                    <Box sx={{ textAlign: 'center', mt: 8, color: 'text.secondary' }}>
                        <Typography variant="body1">Aucun objet trouvé</Typography>
                    </Box>
                ) : (
                    Object.entries(filteredInventory.data).map(([category, items]) => (
                        <Accordion
                            key={category}
                            expanded={expandedCategories[category] !== false}
                            onChange={() => toggleCategory(category)}
                            sx={{
                                bgcolor: 'background.paper',
                                borderRadius: 0,
                                boxShadow: 'none',
                                borderBottom: 1,
                                borderColor: 'divider',
                                '&:before': { display: 'none' },
                                '&.Mui-expanded': {
                                    margin: 0,
                                }
                            }}
                        >
                            <AccordionSummary
                                expandIcon={<ExpandMoreIcon sx={{ fontSize: 20 }} />}
                                sx={{
                                    minHeight: 48,
                                    px: 1.5,
                                    '&.Mui-expanded': {
                                        minHeight: 48,
                                    },
                                    '& .MuiAccordionSummary-content': {
                                        my: 1,
                                    }
                                }}
                            >
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%' }}>
                                    <Typography sx={{ fontSize: '1.2rem' }}>
                                        {CATEGORY_ICONS[category] || '📦'}
                                    </Typography>
                                    <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.9rem' }}>
                                        {CATEGORY_NAMES[category] || category}
                                    </Typography>
                                    <Box sx={{
                                        ml: 'auto',
                                        bgcolor: items.length > 0 ? '#66bb6a' : 'grey.700',
                                        color: 'white',
                                        px: 1.5,
                                        py: 0.25,
                                        borderRadius: 1,
                                        fontSize: '0.75rem',
                                        fontWeight: 700,
                                        minWidth: 40,
                                        textAlign: 'center'
                                    }}>
                                        {items.length} recettes
                                    </Box>
                                </Box>
                            </AccordionSummary>
                            <AccordionDetails sx={{ p: 0, bgcolor: 'background.default' }}>
                                <List sx={{ p: 0 }}>
                                    {items.map((item) => (
                                        <InventoryItem
                                            key={item.id}
                                            item={item}
                                            onConsume={handleConsume}
                                            onDrop={handleDropClick}
                                            onEquip={handleEquip}
                                            viewMode="list"
                                        />
                                    ))}
                                </List>
                            </AccordionDetails>
                        </Accordion>
                    ))
                )}
            </Box>

            {/* Drop Item Dialog */}
            <Dialog open={dropDialog.open} onClose={() => setDropDialog({ ...dropDialog, open: false })}>
                <DialogTitle>Déposer {dropDialog.itemName}</DialogTitle>
                <DialogContent>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        Combien voulez-vous déposer sur le sol?
                    </Typography>
                    <TextField
                        autoFocus
                        type="number"
                        label="Quantité"
                        fullWidth
                        value={dropQuantity}
                        onChange={(e) => setDropQuantity(Math.max(1, Math.min(dropDialog.maxQuantity, parseInt(e.target.value) || 1)))}
                        inputProps={{ min: 1, max: dropDialog.maxQuantity }}
                        helperText={`Maximum: ${dropDialog.maxQuantity}`}
                    />
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setDropDialog({ ...dropDialog, open: false })}>Annuler</Button>
                    <Button onClick={handleDropConfirm} variant="contained" color="error">
                        Déposer
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}

export default Inventory;
