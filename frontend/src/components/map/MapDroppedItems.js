import React from 'react';
import { Paper, Typography, List, ListItem, Box, Button } from '@mui/material';

function MapDroppedItems({ droppedItems, onPickup, loading }) {
    if (!droppedItems || droppedItems.length === 0) return null;

    return (
        <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                📦 Objets au sol
            </Typography>
            <List>
                {droppedItems.map((dropped) => (
                    <ListItem
                        key={dropped.id}
                        sx={{
                            border: 1,
                            borderColor: 'divider',
                            borderRadius: 1,
                            mb: 1,
                            bgcolor: 'background.paper',
                        }}
                    >
                        <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
                            <Typography variant="h5">{dropped.material.icon}</Typography>
                            <Box sx={{ flex: 1 }}>
                                <Typography variant="subtitle1" fontWeight="bold">
                                    {dropped.quantity}x {dropped.material.name}
                                </Typography>
                                {dropped.durability_max > 0 && (
                                    <Typography variant="caption" color="text.secondary">
                                        Durabilité: {dropped.durability_current}/{dropped.durability_max}
                                    </Typography>
                                )}
                                {dropped.dropped_by_name && (
                                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                                        Déposé par: {dropped.dropped_by_name}
                                    </Typography>
                                )}
                            </Box>
                            <Button
                                variant="contained"
                                color="success"
                                size="small"
                                disabled={loading}
                                onClick={() => onPickup(dropped.id)}
                            >
                                Ramasser
                            </Button>
                        </Box>
                    </ListItem>
                ))}
            </List>
        </Paper>
    );
}

export default MapDroppedItems;
