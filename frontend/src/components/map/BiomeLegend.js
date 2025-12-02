import React from 'react';
import { Box, Paper, Typography, Chip } from '@mui/material';
import {
    Terrain,
    Forest,
    Landscape,
    Water,
    AcUnit,
    Whatshot,
} from '@mui/icons-material';

const biomes = [
    {
        name: 'Plaines',
        color: '#10b981',
        icon: <Terrain />,
        description: 'Ressources de base, bois, pierre',
    },
    {
        name: 'Forêt',
        color: '#059669',
        icon: <Forest />,
        description: 'Bois dur, champignons, herbes',
    },
    {
        name: 'Montagne',
        color: '#78716c',
        icon: <Landscape />,
        description: 'Minerais, pierre, charbon',
    },
    {
        name: 'Eau',
        color: '#3b82f6',
        icon: <Water />,
        description: 'Poisson, sable, argile',
    },
    {
        name: 'Glacier',
        color: '#60a5fa',
        icon: <AcUnit />,
        description: 'Cristaux de glace, ressources rares',
    },
    {
        name: 'Volcan',
        color: '#ef4444',
        icon: <Whatshot />,
        description: 'Obsidienne, soufre, ressources ignées',
    },
];

function BiomeLegend() {
    return (
        <Paper
            elevation={1}
            sx={{
                p: 2,
                borderRadius: 2,
                bgcolor: 'background.paper',
            }}
        >
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 500, mb: 1.5 }}>
                Légende des biomes
            </Typography>
            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 1.5 }}>
                {biomes.map((biome) => (
                    <Box
                        key={biome.name}
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                            p: 1,
                            borderRadius: 1.5,
                            bgcolor: 'background.default',
                            border: '1px solid rgba(148, 163, 184, 0.4)',
                        }}
                    >
                        <Box
                            sx={{
                                width: 32,
                                height: 32,
                                borderRadius: '50%',
                                bgcolor: biome.color,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                flexShrink: 0,
                                fontSize: 18,
                            }}
                        >
                            {biome.icon}
                        </Box>
                        <Box sx={{ flex: 1 }}>
                            <Typography variant="subtitle2" sx={{ fontWeight: 500, mb: 0.25 }}>
                                {biome.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                                {biome.description}
                            </Typography>
                        </Box>
                    </Box>
                ))}
            </Box>
        </Paper>
    );
}

export default BiomeLegend;
