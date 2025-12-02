import React from 'react';
import { AppBar, Toolbar, Box, Typography, Button, Chip, LinearProgress, Tooltip } from '@mui/material';
import {
    Settings,
    Refresh,
    Logout,
    Star,
    Bolt,
    Favorite,
    Restaurant,
    WaterDrop,
    Science,
    MonetizationOn,
    Place
} from '@mui/icons-material';
import TimeDisplay from '../common/TimeDisplay';

function TopBar({ player, onOpenAdmin, onRestart, onLogout }) {
    const getStatBar = (current, max, color, width = 60) => {
        const percentage = Math.min(100, Math.max(0, (current / max) * 100));
        return (
            <Box sx={{ width }}>
                <LinearProgress
                    variant="determinate"
                    value={percentage}
                    sx={{
                        height: 4,
                        borderRadius: 1,
                        bgcolor: 'rgba(0,0,0,0.3)',
                        '& .MuiLinearProgress-bar': {
                            bgcolor: color,
                            borderRadius: 1
                        }
                    }}
                />
            </Box>
        );
    };

    return (
        <AppBar position="static" elevation={3} sx={{
            background: 'linear-gradient(90deg, #1976d2 0%, #1565c0 100%)'
        }}>
            <Toolbar variant="dense" sx={{ justifyContent: 'space-between', py: 0.5, minHeight: 48 }}>
                {/* Left: Title & Version */}
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Typography variant="h6" component="div" sx={{
                        fontWeight: 700,
                        fontSize: '1.1rem',
                        letterSpacing: 0.5,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1
                    }}>
                        🏗️ Craft OSM
                    </Typography>

                    <Chip
                        label="v2.2"
                        size="small"
                        sx={{
                            bgcolor: 'rgba(255,255,255,0.2)',
                            color: 'white',
                            fontWeight: 'bold',
                            fontSize: '0.65rem',
                            height: 20
                        }}
                    />

                    <TimeDisplay />
                </Box>

                {/* Center: Player Info & Stats */}
                {player && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        {/* Identity Group */}
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, bgcolor: 'rgba(0,0,0,0.1)', px: 1, py: 0.25, borderRadius: 1 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <Star sx={{ color: '#FFD700', fontSize: '1rem' }} />
                                <Typography variant="subtitle2" sx={{ color: 'white', fontWeight: 700, fontSize: '0.9rem' }}>
                                    {player?.user?.username || 'Joueur'}
                                </Typography>
                            </Box>

                            <Chip
                                label={`Lvl ${player.level}`}
                                size="small"
                                sx={{
                                    bgcolor: 'rgba(255, 215, 0, 0.2)',
                                    color: '#FFD700',
                                    fontWeight: 'bold',
                                    border: '1px solid #FFD700',
                                    height: 20,
                                    fontSize: '0.7rem'
                                }}
                            />

                            <Tooltip title="Argent">
                                <Chip
                                    icon={<MonetizationOn sx={{ fontSize: '0.9rem !important', color: '#FFD700 !important' }} />}
                                    label={player.money || 0}
                                    size="small"
                                    sx={{
                                        bgcolor: 'rgba(0,0,0,0.2)',
                                        color: '#FFD700',
                                        fontWeight: 'bold',
                                        height: 20,
                                        fontSize: '0.75rem',
                                        '& .MuiChip-label': { px: 1 }
                                    }}
                                />
                            </Tooltip>

                            <Tooltip title="Position (X, Y)">
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, ml: 0.5 }}>
                                    <Place sx={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }} />
                                    <Typography sx={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.9)', fontFamily: 'monospace' }}>
                                        {player.grid_x},{player.grid_y}
                                    </Typography>
                                </Box>
                            </Tooltip>
                        </Box>

                        {/* Stats Group */}
                        <Box sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1.5,
                            bgcolor: 'rgba(0,0,0,0.2)',
                            px: 1.5,
                            py: 0.25,
                            borderRadius: 1
                        }}>
                            <Tooltip title={`Énergie: ${player.energy}/${player.max_energy}`}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                    <Bolt sx={{ fontSize: '0.9rem', color: '#ffc107' }} />
                                    {getStatBar(player.energy, player.max_energy, '#ffc107')}
                                </Box>
                            </Tooltip>

                            <Tooltip title={`Santé: ${player.health}/${player.max_health}`}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                    <Favorite sx={{ fontSize: '0.9rem', color: '#f44336' }} />
                                    {getStatBar(player.health, player.max_health, '#f44336')}
                                </Box>
                            </Tooltip>

                            <Tooltip title={`Faim: ${player.hunger}/${player.max_hunger}`}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                    <Restaurant sx={{ fontSize: '0.9rem', color: '#ff9800' }} />
                                    {getStatBar(player.hunger, player.max_hunger, '#ff9800')}
                                </Box>
                            </Tooltip>

                            <Tooltip title={`Soif: ${player.thirst}/${player.max_thirst}`}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                    <WaterDrop sx={{ fontSize: '0.9rem', color: '#2196f3' }} />
                                    {getStatBar(player.thirst, player.max_thirst, '#2196f3')}
                                </Box>
                            </Tooltip>

                            <Tooltip title={`Radiation: ${player.radiation}/100`}>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                    <Science sx={{ fontSize: '0.9rem', color: '#9c27b0' }} />
                                    {getStatBar(player.radiation, 100, '#9c27b0', 40)}
                                </Box>
                            </Tooltip>
                        </Box>
                    </Box>
                )}

                {/* Right Actions */}
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {player?.is_staff && (
                        <Tooltip title="Administration">
                            <Button
                                color="inherit"
                                onClick={onOpenAdmin}
                                sx={{ minWidth: 40, px: 1 }}
                            >
                                <Settings fontSize="small" />
                            </Button>
                        </Tooltip>
                    )}

                    <Tooltip title="Recommencer">
                        <Button
                            color="inherit"
                            onClick={onRestart}
                            sx={{ minWidth: 40, px: 1, color: 'error.light' }}
                        >
                            <Refresh fontSize="small" />
                        </Button>
                    </Tooltip>

                    <Tooltip title="Quitter">
                        <Button
                            color="inherit"
                            onClick={onLogout}
                            sx={{ minWidth: 40, px: 1 }}
                        >
                            <Logout fontSize="small" />
                        </Button>
                    </Tooltip>
                </Box>
            </Toolbar>
        </AppBar>
    );
}

export default TopBar;
