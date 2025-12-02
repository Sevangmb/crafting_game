import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    Box,
    Typography,
    LinearProgress,
    Paper,
    Chip,
    Alert,
    Stack,
    Divider
} from '@mui/material';
import {
    Warning as WarningIcon,
    Favorite as HeartIcon,
    Shield as ShieldIcon,
    Bolt as AttackIcon,
    DirectionsRun as FleeIcon,
    EmojiEvents as VictoryIcon,
    Skull as DefeatIcon
} from '@mui/icons-material';
import { encounterAPI } from '../../services/api';
import { useGameStore } from '../../stores/useGameStore';
import logger from '../../utils/logger';

const EncounterDialog = ({ encounter, open, onClose, onPlayerUpdate }) => {
    const [combatLog, setCombatLog] = useState([]);
    const [enemyHealth, setEnemyHealth] = useState(encounter?.enemy?.health || 0);
    const [playerHealth, setPlayerHealth] = useState(null);
    const [loading, setLoading] = useState(false);
    const [victory, setVictory] = useState(false);
    const [defeated, setDefeated] = useState(false);
    const [loot, setLoot] = useState(null);
    const showNotification = useGameStore((state) => state.showNotification);

    useEffect(() => {
        if (encounter) {
            setEnemyHealth(encounter.enemy.current_health || encounter.enemy.health);
            setCombatLog([]);
            setVictory(false);
            setDefeated(false);
            setLoot(null);

            // Add initial message
            if (encounter.attacked_first) {
                setCombatLog([`⚠️ ${encounter.enemy.name} vous attaque en premier!`]);
            } else {
                setCombatLog([`⚔️ Vous rencontrez ${encounter.enemy.name}!`]);
            }
        }
    }, [encounter]);

    const handleAttack = async () => {
        setLoading(true);
        try {
            const response = await encounterAPI.attack();

            if (response.data.victory) {
                setVictory(true);
                setLoot(response.data.loot);
                setCombatLog(response.data.combat_log);
                setEnemyHealth(0);
                showNotification('Victoire! Vous avez vaincu l\'ennemi!', 'success');
                if (onPlayerUpdate) {
                    onPlayerUpdate();
                }
            } else if (response.data.defeated) {
                setDefeated(true);
                setCombatLog(response.data.combat_log);
                showNotification('Vous avez été vaincu...', 'error');
                if (onPlayerUpdate) {
                    onPlayerUpdate();
                }
            } else {
                setCombatLog(response.data.combat_log);
                setEnemyHealth(response.data.enemy_health);
                setPlayerHealth(response.data.player_health);
            }
        } catch (error) {
            logger.error('Failed to attack:', error);
            showNotification(error.response?.data?.error || 'Échec de l\'attaque', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleFlee = async () => {
        setLoading(true);
        try {
            const response = await encounterAPI.flee();

            if (response.data.success) {
                showNotification(response.data.message, 'success');
                if (onPlayerUpdate) {
                    onPlayerUpdate();
                }
                onClose();
            } else if (response.data.defeated) {
                setDefeated(true);
                setCombatLog([response.data.message]);
                showNotification('Fuite échouée et vous avez été vaincu!', 'error');
                if (onPlayerUpdate) {
                    onPlayerUpdate();
                }
            } else {
                setCombatLog([response.data.message]);
                setPlayerHealth(response.data.player_health);
                showNotification('Fuite échouée!', 'warning');
            }
        } catch (error) {
            logger.error('Failed to flee:', error);
            showNotification(error.response?.data?.error || 'Échec de la fuite', 'error');
        } finally {
            setLoading(false);
        }
    };

    const handleClose = () => {
        if (victory || defeated) {
            if (onPlayerUpdate) {
                onPlayerUpdate();
            }
        }
        onClose();
    };

    if (!encounter) return null;

    const { enemy } = encounter;
    const enemyHealthPercent = (enemyHealth / enemy.health) * 100;

    const getAggressionColor = (level) => {
        switch (level) {
            case 'passive': return 'success';
            case 'defensive': return 'info';
            case 'neutral': return 'default';
            case 'aggressive': return 'warning';
            case 'very_aggressive': return 'error';
            default: return 'default';
        }
    };

    const getAggressionLabel = (level) => {
        switch (level) {
            case 'passive': return 'Passif';
            case 'defensive': return 'Défensif';
            case 'neutral': return 'Neutre';
            case 'aggressive': return 'Agressif';
            case 'very_aggressive': return 'Très Agressif';
            default: return level;
        }
    };

    return (
        <Dialog
            open={open}
            onClose={handleClose}
            maxWidth="md"
            fullWidth
            PaperProps={{
                sx: {
                    bgcolor: 'background.paper',
                    backgroundImage: 'none'
                }
            }}
        >
            <DialogTitle sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                bgcolor: 'error.dark',
                color: 'white'
            }}>
                <WarningIcon />
                <Typography variant="h6">
                    Rencontre Ennemie!
                </Typography>
            </DialogTitle>

            <DialogContent sx={{ pt: 2 }}>
                {/* Enemy Info */}
                <Paper elevation={3} sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <Typography variant="h4">{enemy.icon}</Typography>
                        <Box sx={{ flex: 1 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                                <Typography variant="h6">{enemy.name}</Typography>
                                <Chip
                                    label={`Niveau ${enemy.level}`}
                                    size="small"
                                    color="primary"
                                />
                                <Chip
                                    label={getAggressionLabel(enemy.aggression_level)}
                                    size="small"
                                    color={getAggressionColor(enemy.aggression_level)}
                                />
                            </Box>
                            <Typography variant="body2" color="text.secondary">
                                {enemy.description}
                            </Typography>
                        </Box>
                    </Box>

                    <Divider sx={{ my: 1 }} />

                    {/* Enemy Stats */}
                    <Stack direction="row" spacing={2} sx={{ mb: 1 }}>
                        <Chip
                            icon={<AttackIcon />}
                            label={`Attaque: ${enemy.attack}`}
                            size="small"
                            variant="outlined"
                        />
                        <Chip
                            icon={<ShieldIcon />}
                            label={`Défense: ${enemy.defense}`}
                            size="small"
                            variant="outlined"
                        />
                    </Stack>

                    {/* Enemy Health Bar */}
                    <Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                            <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <HeartIcon fontSize="small" color="error" />
                                Santé de l'ennemi
                            </Typography>
                            <Typography variant="caption">
                                {enemyHealth} / {enemy.health}
                            </Typography>
                        </Box>
                        <LinearProgress
                            variant="determinate"
                            value={enemyHealthPercent}
                            sx={{
                                height: 10,
                                borderRadius: 1,
                                bgcolor: 'grey.800',
                                '& .MuiLinearProgress-bar': {
                                    bgcolor: enemyHealthPercent > 50 ? 'error.main' :
                                            enemyHealthPercent > 25 ? 'warning.main' : 'error.dark'
                                }
                            }}
                        />
                    </Box>
                </Paper>

                {/* Combat Log */}
                <Paper elevation={3} sx={{ p: 2, bgcolor: 'background.default', minHeight: 120 }}>
                    <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                        📜 Journal de Combat
                    </Typography>
                    <Stack spacing={0.5}>
                        {combatLog.map((log, index) => (
                            <Typography
                                key={index}
                                variant="body2"
                                sx={{
                                    color: log.includes('💀') ? 'error.main' :
                                           log.includes('inflige') && log.includes('Vous') ? 'success.main' :
                                           log.includes('inflige') ? 'error.main' : 'text.primary'
                                }}
                            >
                                {log}
                            </Typography>
                        ))}
                    </Stack>
                </Paper>

                {/* Victory/Defeat Messages */}
                {victory && loot && (
                    <Alert severity="success" icon={<VictoryIcon />} sx={{ mt: 2 }}>
                        <Typography variant="h6" sx={{ mb: 1 }}>Victoire!</Typography>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                            💰 Argent: {loot.money}₡ | ⭐ XP: +{loot.xp}
                        </Typography>
                        {loot.items && loot.items.length > 0 && (
                            <>
                                <Typography variant="body2" sx={{ mb: 0.5 }}>
                                    🎁 Butin:
                                </Typography>
                                <Stack direction="row" spacing={0.5} flexWrap="wrap">
                                    {loot.items.map((item, index) => (
                                        <Chip
                                            key={index}
                                            label={`${item.icon} ${item.material_name} x${item.quantity}`}
                                            size="small"
                                            color="success"
                                            variant="outlined"
                                        />
                                    ))}
                                </Stack>
                            </>
                        )}
                    </Alert>
                )}

                {defeated && (
                    <Alert severity="error" icon={<DefeatIcon />} sx={{ mt: 2 }}>
                        <Typography variant="h6">Défaite...</Typography>
                        <Typography variant="body2">
                            Vous avez été vaincu. Reposez-vous et revenez plus fort!
                        </Typography>
                    </Alert>
                )}
            </DialogContent>

            <DialogActions sx={{ p: 2, gap: 1 }}>
                {!victory && !defeated ? (
                    <>
                        <Button
                            variant="outlined"
                            color="warning"
                            startIcon={<FleeIcon />}
                            onClick={handleFlee}
                            disabled={loading}
                        >
                            Fuir
                        </Button>
                        <Button
                            variant="contained"
                            color="error"
                            startIcon={<AttackIcon />}
                            onClick={handleAttack}
                            disabled={loading}
                        >
                            Attaquer
                        </Button>
                    </>
                ) : (
                    <Button
                        variant="contained"
                        onClick={handleClose}
                    >
                        Fermer
                    </Button>
                )}
            </DialogActions>
        </Dialog>
    );
};

export default EncounterDialog;
