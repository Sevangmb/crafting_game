import React from 'react';
import { Paper, Typography, Box, Grid, Tooltip, LinearProgress } from '@mui/material';
import { Shield, Hardware, DirectionsRun } from '@mui/icons-material';
import { useEquipment } from '../../hooks';

const SLOT_ICONS = {
    head: '🪖',
    chest: '👕',
    hands: '🧤',
    legs: '👖',
    feet: '👢',
    backpack: '🎒',
    main_hand: '⚔️',
    off_hand: '🛡️',
    accessory: '💍'
};

const SLOT_NAMES = {
    head: 'Tête',
    chest: 'Torse',
    hands: 'Mains',
    legs: 'Jambes',
    feet: 'Pieds',
    backpack: 'Sac à dos',
    main_hand: 'Main droite',
    off_hand: 'Main gauche',
    accessory: 'Accessoire'
};

function EquipmentSlot({ slot, item, onUnequip }) {
    const getTooltipContent = () => {
        if (!item) return `Emplacement: ${SLOT_NAMES[slot]}`;

        const stats = [];
        if (item.material.defense > 0) stats.push(`🛡️ Défense: +${item.material.defense}`);
        if (item.material.attack > 0) stats.push(`⚔️ Attaque: +${item.material.attack}`);
        if (item.material.speed_bonus > 0) stats.push(`⚡ Vitesse: +${item.material.speed_bonus}%`);
        if (item.material.carry_capacity_bonus > 0) stats.push(`🎒 Capacité: +${item.material.carry_capacity_bonus}kg`);

        return (
            <Box>
                <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                    {item.material.name}
                </Typography>
                {item.material.description && (
                    <Typography variant="caption" sx={{ display: 'block', mb: 1, opacity: 0.9 }}>
                        {item.material.description}
                    </Typography>
                )}
                {stats.length > 0 && (
                    <Box>
                        {stats.map((stat, i) => (
                            <Typography key={i} variant="caption" sx={{ display: 'block', color: '#4caf50' }}>
                                {stat}
                            </Typography>
                        ))}
                    </Box>
                )}
                <Typography variant="caption" sx={{ display: 'block', mt: 1, fontStyle: 'italic', opacity: 0.7 }}>
                    Cliquez pour déséquiper
                </Typography>
            </Box>
        );
    };

    return (
        <Tooltip title={getTooltipContent()} arrow placement="top">
            <Paper
                sx={{
                    width: 70,
                    height: 70,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: item ? 'pointer' : 'default',
                    bgcolor: item ? '#333' : '#1a1a1a',
                    border: item ? '2px solid #ff9800' : '1px dashed #444',
                    position: 'relative',
                    transition: 'all 0.2s',
                    '&:hover': {
                        bgcolor: item ? '#444' : '#222',
                        borderColor: item ? '#ffb74d' : '#666',
                        transform: item ? 'scale(1.05)' : 'none'
                    }
                }}
                onClick={() => item && onUnequip(slot)}
            >
                {item ? (
                    <Box sx={{ textAlign: 'center', width: '100%', px: 0.5 }}>
                        <Typography variant="h5">{item.material.icon}</Typography>
                        <Typography variant="caption" sx={{ fontSize: '0.55rem', display: 'block', lineHeight: 1, mb: 0.5, color: '#fff', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                            {item.material.name}
                        </Typography>
                        {item.material.max_durability > 0 && (
                            <Box sx={{ width: '100%', mt: 0.5 }}>
                                <LinearProgress
                                    variant="determinate"
                                    value={(item.material.durability_current / item.material.max_durability) * 100 || 0}
                                    sx={{
                                        height: 2,
                                        borderRadius: 0.5,
                                        bgcolor: 'rgba(255,255,255,0.1)',
                                        '& .MuiLinearProgress-bar': {
                                            bgcolor: (item.material.durability_current / item.material.max_durability) > 0.5 ? '#4caf50' :
                                                (item.material.durability_current / item.material.max_durability) > 0.2 ? '#ff9800' : '#f44336'
                                        }
                                    }}
                                />
                            </Box>
                        )}
                    </Box>
                ) : (
                    <Typography variant="h5" sx={{ opacity: 0.2, filter: 'grayscale(100%)' }}>
                        {SLOT_ICONS[slot]}
                    </Typography>
                )}
                <Typography
                    variant="caption"
                    sx={{
                        position: 'absolute',
                        bottom: 2,
                        fontSize: '0.55rem',
                        color: '#666',
                        fontFamily: 'monospace'
                    }}
                >
                    {SLOT_NAMES[slot]}
                </Typography>
            </Paper>
        </Tooltip>
    );
}

function EquipmentPanel({ player }) {
    const { unequipItem, getEquippedItem } = useEquipment();

    const slots = ['head', 'chest', 'hands', 'legs', 'feet', 'backpack', 'main_hand', 'off_hand', 'accessory'];

    return (
        <Box sx={{ width: '100%' }}>
            <Grid container spacing={1} justifyContent="center" sx={{ mb: 3 }}>
                {slots.map(slot => (
                    <Grid item key={slot}>
                        <EquipmentSlot
                            slot={slot}
                            item={getEquippedItem(slot)}
                            onUnequip={unequipItem}
                        />
                    </Grid>
                ))}
            </Grid>

            <Box sx={{ p: 2, bgcolor: '#222', borderRadius: 1, border: '1px solid #333' }}>
                <Typography variant="caption" sx={{ color: '#888', fontFamily: 'monospace', display: 'block', mb: 1 }}>
                    STATS TOTALES
                </Typography>
                <Grid container spacing={2}>
                    <Grid item xs={4}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Shield sx={{ fontSize: '1rem', color: '#4488ff' }} />
                            <Box>
                                <Typography variant="caption" sx={{ color: '#666', fontSize: '0.6rem' }}>DÉFENSE</Typography>
                                <Typography variant="body2" sx={{ color: '#fff', fontFamily: 'monospace' }}>{player?.total_defense || 0}</Typography>
                            </Box>
                        </Box>
                    </Grid>
                    <Grid item xs={4}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Hardware sx={{ fontSize: '1rem', color: '#ff4444' }} />
                            <Box>
                                <Typography variant="caption" sx={{ color: '#666', fontSize: '0.6rem' }}>ATTAQUE</Typography>
                                <Typography variant="body2" sx={{ color: '#fff', fontFamily: 'monospace' }}>{player?.total_attack || 0}</Typography>
                            </Box>
                        </Box>
                    </Grid>
                    <Grid item xs={4}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <DirectionsRun sx={{ fontSize: '1rem', color: '#ffaa00' }} />
                            <Box>
                                <Typography variant="caption" sx={{ color: '#666', fontSize: '0.6rem' }}>VITESSE</Typography>
                                <Typography variant="body2" sx={{ color: '#fff', fontFamily: 'monospace' }}>{player?.total_speed_bonus || 0}%</Typography>
                            </Box>
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </Box>
    );
}

export default EquipmentPanel;
