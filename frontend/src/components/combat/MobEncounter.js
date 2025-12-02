import React from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Box,
    Typography,
    Chip,
    Paper,
    Grid
} from '@mui/material';
import { Gavel, DirectionsRun, Visibility } from '@mui/icons-material';

function MobEncounter({ open, mob, onFight, onFlee, onClose }) {
    if (!mob) return null;

    const getAggressionColor = (level) => {
        switch (level) {
            case 'passive':
                return 'success';
            case 'neutral':
                return 'warning';
            case 'aggressive':
                return 'error';
            default:
                return 'default';
        }
    };

    const getAggressionLabel = (level) => {
        switch (level) {
            case 'passive':
                return 'Passif';
            case 'neutral':
                return 'Neutre';
            case 'aggressive':
                return 'Agressif';
            default:
                return level;
        }
    };

    return (
        <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
            <DialogTitle sx={{ bgcolor: 'warning.main', color: 'white' }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Visibility sx={{ mr: 1 }} />
                    <Typography variant="h6">Rencontre !</Typography>
                </Box>
            </DialogTitle>

            <DialogContent sx={{ p: 3 }}>
                <Paper sx={{ p: 3, textAlign: 'center', bgcolor: 'grey.50' }}>
                    <Typography variant="h2" sx={{ mb: 2 }}>
                        {mob.icon}
                    </Typography>
                    <Typography variant="h5" gutterBottom fontWeight="bold">
                        {mob.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {mob.description}
                    </Typography>

                    <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 2 }}>
                        <Chip label={`Niveau ${mob.level}`} color="primary" />
                        <Chip
                            label={getAggressionLabel(mob.aggression)}
                            color={getAggressionColor(mob.aggression)}
                        />
                    </Box>

                    <Grid container spacing={2} sx={{ mt: 2 }}>
                        <Grid item xs={4}>
                            <Paper sx={{ p: 1, bgcolor: 'error.light', color: 'white' }}>
                                <Typography variant="caption">Vie</Typography>
                                <Typography variant="h6">{mob.health}</Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={4}>
                            <Paper sx={{ p: 1, bgcolor: 'warning.light', color: 'white' }}>
                                <Typography variant="caption">Attaque</Typography>
                                <Typography variant="h6">{mob.attack}</Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={4}>
                            <Paper sx={{ p: 1, bgcolor: 'info.light', color: 'white' }}>
                                <Typography variant="caption">Défense</Typography>
                                <Typography variant="h6">{mob.defense}</Typography>
                            </Paper>
                        </Grid>
                    </Grid>
                </Paper>

                {mob.aggression === 'aggressive' && (
                    <Box sx={{ mt: 2, p: 1, bgcolor: 'error.light', borderRadius: 1 }}>
                        <Typography variant="body2" color="white" textAlign="center">
                            ⚠️ Attention ! Cet animal est agressif !
                        </Typography>
                    </Box>
                )}
            </DialogContent>

            <DialogActions sx={{ p: 2, justifyContent: 'space-between' }}>
                <Button
                    variant="outlined"
                    color="warning"
                    startIcon={<DirectionsRun />}
                    onClick={onFlee}
                >
                    Fuir
                </Button>
                <Button
                    variant="contained"
                    color="error"
                    startIcon={<Gavel />}
                    onClick={onFight}
                >
                    Combattre
                </Button>
            </DialogActions>
        </Dialog>
    );
}

export default MobEncounter;
