import React from 'react';
import {
    Card,
    CardContent,
    Typography,
    Box,
    Chip,
    Button,
    Tooltip,
    IconButton,
    ListItem,
    ListItemAvatar,
    Avatar,
    ListItemText,
    ListItemSecondaryAction,
    LinearProgress
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import { Build, FitnessCenter } from '@mui/icons-material';
import { getRarityColor } from '../../utils/gameLogic';
import MaterialIcon from '../common/MaterialIcon';

const InventoryItem = ({ item, onConsume, onDrop, onEquip, viewMode = 'grid' }) => {
    const isConsumable = item.material.is_food === true;
    const isEquipment = item.material.is_equipment === true;
    const rarityColor = getRarityColor(item.material.rarity);

    // Durability calculations
    const hasDurability = item.durability_max > 0;
    const durabilityPercent = hasDurability ? (item.durability_current / item.durability_max) * 100 : 0;
    const getDurabilityColor = (percent) => {
        if (percent > 50) return 'success';
        if (percent > 20) return 'warning';
        return 'error';
    };

    // Weight calculation
    const totalWeight = item.material.weight * item.quantity;

    if (viewMode === 'list') {
        return (
            <ListItem
                sx={{
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    mb: 1,
                    bgcolor: 'background.paper',
                    '&:hover': { bgcolor: 'action.hover' }
                }}
            >
                <ListItemAvatar>
                    <Avatar sx={{ bgcolor: rarityColor, color: '#fff' }}>
                        <MaterialIcon icon={item.material.icon} size={24} />
                    </Avatar>
                </ListItemAvatar>
                <ListItemText
                    primaryTypographyProps={{ component: 'div' }}
                    secondaryTypographyProps={{ component: 'div' }}
                    primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                            <Typography variant="subtitle1">{item.material.name}</Typography>
                            <Chip
                                label={`x${item.quantity}`}
                                size="small"
                                color="primary"
                                variant="outlined"
                            />
                            {item.quality > 1 && (
                                <Chip
                                    label={`Qualité: ${item.quality}`}
                                    size="small"
                                    color="secondary"
                                    variant="outlined"
                                />
                            )}
                            {totalWeight > 0 && (
                                <Chip
                                    icon={<FitnessCenter sx={{ fontSize: 16 }} />}
                                    label={`${totalWeight.toFixed(1)}kg`}
                                    size="small"
                                    variant="outlined"
                                />
                            )}
                        </Box>
                    }
                    secondary={
                        <Box>
                            <Typography variant="body2" color="text.secondary">{item.material.description}</Typography>
                            {hasDurability && (
                                <Box sx={{ mt: 1 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                        <Typography variant="caption" color="text.secondary">
                                            <Build sx={{ fontSize: 12, verticalAlign: 'middle', mr: 0.5 }} />
                                            Durabilité: {item.durability_current}/{item.durability_max}
                                        </Typography>
                                        <Typography variant="caption" fontWeight="bold">
                                            {durabilityPercent.toFixed(0)}%
                                        </Typography>
                                    </Box>
                                    <LinearProgress
                                        variant="determinate"
                                        value={durabilityPercent}
                                        color={getDurabilityColor(durabilityPercent)}
                                        sx={{ height: 4, borderRadius: 1 }}
                                    />
                                </Box>
                            )}
                        </Box>
                    }
                />
                <ListItemSecondaryAction sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Chip
                        label={item.material.rarity}
                        size="small"
                        sx={{
                            bgcolor: getRarityColor(item.material.rarity, 0.1),
                            color: rarityColor,
                            textTransform: 'capitalize',
                            display: { xs: 'none', sm: 'flex' }
                        }}
                    />
                    {isConsumable && (
                        <Button
                            variant="contained"
                            size="small"
                            color="success"
                            onClick={() => onConsume(item.id)}
                        >
                            Utiliser
                        </Button>
                    )}
                    <Tooltip title="Détails">
                        <IconButton size="small">
                            <InfoIcon />
                        </IconButton>
                    </Tooltip>
                </ListItemSecondaryAction>
            </ListItem>
        );
    }

    // Grid View
    return (
        <Card
            sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4
                },
                border: 1,
                borderColor: 'divider'
            }}
        >
            <Box
                sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    width: '100%',
                    height: 4,
                    bgcolor: rarityColor
                }}
            />
            <CardContent sx={{ flexGrow: 1, p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                    <Avatar
                        variant="rounded"
                        sx={{
                            bgcolor: getRarityColor(item.material.rarity, 0.1),
                            color: rarityColor,
                            width: 48,
                            height: 48,
                            fontSize: '1.5rem'
                        }}
                    >
                        <MaterialIcon icon={item.material.icon} size={32} />
                    </Avatar>
                    <Chip
                        label={`x${item.quantity}`}
                        color="primary"
                        size="small"
                        sx={{ fontWeight: 'bold' }}
                    />
                </Box>

                <Typography variant="h6" gutterBottom component="div" sx={{ fontSize: '1rem', fontWeight: 600 }}>
                    {item.material.name}
                </Typography>

                <Typography variant="body2" color="text.secondary" sx={{
                    mb: 2,
                    height: 40,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical'
                }}>
                    {item.material.description}
                </Typography>

                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                    <Chip
                        label={item.material.rarity}
                        size="small"
                        sx={{
                            bgcolor: getRarityColor(item.material.rarity, 0.1),
                            color: rarityColor,
                            textTransform: 'capitalize',
                            fontSize: '0.7rem',
                            height: 20
                        }}
                    />
                    {item.material.is_food && (
                        <Chip
                            label={`+${item.material.energy_restore} énergie`}
                            size="small"
                            variant="outlined"
                            color="success"
                            sx={{ fontSize: '0.7rem', height: 20 }}
                        />
                    )}
                    {item.quality > 1 && (
                        <Chip
                            label={`Q${item.quality}`}
                            size="small"
                            color="secondary"
                            variant="outlined"
                            sx={{ fontSize: '0.7rem', height: 20 }}
                        />
                    )}
                    {totalWeight > 0 && (
                        <Chip
                            icon={<FitnessCenter sx={{ fontSize: '0.8rem !important' }} />}
                            label={`${totalWeight.toFixed(1)}kg`}
                            size="small"
                            variant="outlined"
                            sx={{ fontSize: '0.7rem', height: 20 }}
                        />
                    )}
                </Box>

                {/* Durability Bar */}
                {hasDurability && (
                    <Box sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                <Build sx={{ fontSize: 14 }} /> Durabilité
                            </Typography>
                            <Typography variant="caption" fontWeight="bold">
                                {item.durability_current}/{item.durability_max}
                            </Typography>
                        </Box>
                        <LinearProgress
                            variant="determinate"
                            value={durabilityPercent}
                            color={getDurabilityColor(durabilityPercent)}
                            sx={{ height: 6, borderRadius: 1 }}
                        />
                    </Box>
                )}

                <Box sx={{ display: 'flex', gap: 1, mt: 'auto', flexWrap: 'wrap' }}>
                    {isConsumable && (
                        <Button
                            variant="contained"
                            color="success"
                            size="small"
                            fullWidth
                            onClick={() => onConsume(item.id)}
                        >
                            Utiliser
                        </Button>
                    )}
                    {isEquipment && onEquip && (
                        <Button
                            variant="contained"
                            color="primary"
                            size="small"
                            fullWidth={!isConsumable}
                            onClick={() => onEquip(item.material.id, item.material.equipment_slot)}
                        >
                            ⚔️ Équiper
                        </Button>
                    )}
                    {onDrop && (
                        <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            fullWidth={!isConsumable && !isEquipment}
                            onClick={() => onDrop(item.id, item.material.name, item.quantity)}
                        >
                            Déposer
                        </Button>
                    )}
                </Box>
            </CardContent>
        </Card>
    );
};

export default InventoryItem;
