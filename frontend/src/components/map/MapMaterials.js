import React from 'react';
import { Paper, Typography, Box, Button, List, ListItem, ListItemText, Chip, Divider } from '@mui/material';
import { getRequiredTool, hasRequiredTool } from '../../utils/gameLogic';
import BiomeLegend from './BiomeLegend';

function MapMaterials({ materials, onGather, onGatherAll, loading, flatInventory }) {
    return (
        <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 500 }}>
                Matériaux disponibles dans cette cellule
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                <Button
                    variant="outlined"
                    color="primary"
                    size="small"
                    disabled={loading || !materials?.length}
                    onClick={onGatherAll}
                >
                    {loading ? 'Collecte en cours...' : 'Tout collecter'}
                </Button>
            </Box>
            <Box>
                <List>
                    {materials && materials.length > 0 ? (
                        materials.map((cellMaterial) => {
                            const requiredTool = getRequiredTool(cellMaterial.material.name);
                            const hasRequired = hasRequiredTool(requiredTool, flatInventory);

                            const disabled = loading || cellMaterial.quantity <= 0;
                            return (
                                <ListItem
                                    key={cellMaterial.id}
                                    disableGutters
                                    sx={{
                                        mb: 1,
                                        gap: 1,
                                        alignItems: 'stretch',
                                        flexDirection: 'column'
                                    }}
                                >
                                    <Button
                                        variant="outlined"
                                        color="primary"
                                        fullWidth
                                        disabled={disabled}
                                        onClick={() => onGather(cellMaterial.material.id)}
                                        sx={{
                                            justifyContent: 'flex-start',
                                            py: 1.5,
                                            px: 2,
                                            textAlign: 'left'
                                        }}
                                    >
                                        <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%', gap: 0.5 }}>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                {typeof cellMaterial.material.icon === 'string' && cellMaterial.material.icon.startsWith('http') ? (
                                                    <Box
                                                        component="img"
                                                        src={cellMaterial.material.icon}
                                                        alt={cellMaterial.material.name}
                                                        sx={{ width: 32, height: 32, borderRadius: 0.75, objectFit: 'cover' }}
                                                    />
                                                ) : (
                                                    <Typography variant="body1" component="span" sx={{ fontSize: '1.2rem' }}>
                                                        {cellMaterial.material.icon}
                                                    </Typography>
                                                )}
                                                <Typography variant="body1" component="span" sx={{ fontWeight: 600 }}>
                                                    {cellMaterial.material.name}
                                                </Typography>
                                            </Box>
                                            <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
                                                <Chip
                                                    label={`Disponible: ${cellMaterial.quantity}`}
                                                    size="small"
                                                    color="success"
                                                    variant="outlined"
                                                />
                                                <Chip
                                                    label={cellMaterial.material.rarity}
                                                    size="small"
                                                    variant="outlined"
                                                />
                                                {requiredTool && !hasRequired && (
                                                    <Chip
                                                        label={`Outil: ${requiredTool}`}
                                                        size="small"
                                                        color="warning"
                                                    />
                                                )}
                                            </Box>
                                        </Box>
                                    </Button>
                                </ListItem>
                            );
                        })
                    ) : (
                        <ListItem>
                            <ListItemText primary="Aucun matériau disponible dans cette cellule" />
                        </ListItem>
                    )}
                </List>
            </Box>

            <Divider sx={{ my: 2 }} />
            <BiomeLegend />
        </Paper>
    );
}

export default MapMaterials;
