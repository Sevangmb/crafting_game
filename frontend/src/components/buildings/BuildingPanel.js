import React, { useState, useEffect } from 'react';
import {
    Paper,
    Typography,
    Box,
    Button,
    Grid,
    Card,
    CardContent,
    CardActions,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    List,
    ListItem,
    ListItemText,
    CircularProgress,
    Divider,
    LinearProgress
} from '@mui/material';
import { buildingAPI } from '../../services/api';
import { useGameStore } from '../../stores/useGameStore';
import logger from '../../utils/logger';

// Local hook to encapsulate building data loading and actions
const useBuildingsPanel = (currentCell, onRefresh) => {
    const [availableTypes, setAvailableTypes] = useState([]);
    const [myBuildings, setMyBuildings] = useState([]);
    const [bonuses, setBonuses] = useState(null);
    const [loading, setLoading] = useState(false); // initial/global loading
    const [actionLoading, setActionLoading] = useState(false); // construct / complete actions
    const [selectedBuilding, setSelectedBuilding] = useState(null);
    const [openDialog, setOpenDialog] = useState(false);

    const showNotification = useGameStore((state) => state.showNotification);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [typesRes, buildingsRes, bonusesRes] = await Promise.all([
                buildingAPI.getAvailable(),
                buildingAPI.getMyBuildings(),
                buildingAPI.getBonuses(),
            ]);
            setAvailableTypes(typesRes.data);
            setMyBuildings(buildingsRes.data);
            setBonuses(bonusesRes.data);
        } catch (error) {
            logger.error('Failed to fetch building data:', error);
            showNotification('Erreur lors du chargement des bâtiments', 'error');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleOpenDialog = (buildingType) => {
        setSelectedBuilding(buildingType);
        setOpenDialog(true);
    };

    const handleCloseDialog = () => {
        setOpenDialog(false);
        setSelectedBuilding(null);
    };

    const handleConstruct = async () => {
        if (!selectedBuilding || !currentCell) return;

        setActionLoading(true);
        try {
            const response = await buildingAPI.construct(selectedBuilding.id, currentCell.id);
            showNotification(response.data.message, 'success');
            handleCloseDialog();
            await fetchData();
            if (onRefresh) onRefresh();
        } catch (error) {
            logger.error('Failed to construct building:', error);
            showNotification(error.response?.data?.error || 'Échec de la construction', 'error');
        } finally {
            setActionLoading(false);
        }
    };

    const handleCompleteConstruction = async (buildingId) => {
        setActionLoading(true);
        try {
            const response = await buildingAPI.complete(buildingId);
            showNotification(response.data.message, 'success');
            await fetchData();
            if (onRefresh) onRefresh();
        } catch (error) {
            logger.error('Failed to complete construction:', error);
            showNotification(error.response?.data?.error || 'Échec de la finalisation', 'error');
        } finally {
            setActionLoading(false);
        }
    };

    return {
        availableTypes,
        myBuildings,
        bonuses,
        loading,
        actionLoading,
        selectedBuilding,
        openDialog,
        handleOpenDialog,
        handleCloseDialog,
        handleConstruct,
        handleCompleteConstruction,
    };
};

const BuildingPanel = ({ currentCell, player, onRefresh }) => {
    const {
        availableTypes,
        myBuildings,
        bonuses,
        loading,
        actionLoading,
        selectedBuilding,
        openDialog,
        handleOpenDialog,
        handleCloseDialog,
        handleConstruct,
        handleCompleteConstruction,
    } = useBuildingsPanel(currentCell, onRefresh);

    const getCategoryColor = (category) => {
        const colors = {
            housing: '#4CAF50',
            production: '#FF9800',
            storage: '#2196F3',
            defense: '#F44336',
            decoration: '#9C27B0',
        };
        return colors[category] || '#757575';
    };

    // Check if player already has a building on current cell
    const hasBuildingOnCurrentCell = currentCell?.buildings?.some(
        b => b.owner === player?.user?.username && ['under_construction', 'completed'].includes(b.status)
    );

    if (loading && availableTypes.length === 0) {
        return (
            <Paper sx={{ p: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
                <CircularProgress />
            </Paper>
        );
    }

    return (
        <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
                🏗️ Construction
            </Typography>

            {/* Player bonuses */}
            {bonuses && (
                <Box sx={{ mb: 2, p: 2, bgcolor: 'action.hover', borderRadius: 1 }}>
                    <Typography variant="subtitle2" gutterBottom>
                        Bonus Actifs
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {bonuses.energy_regeneration > 0 && (
                            <Chip size="small" label={`⚡ +${bonuses.energy_regeneration}/h`} color="success" />
                        )}
                        {bonuses.storage > 0 && (
                            <Chip size="small" label={`📦 +${bonuses.storage} stockage`} color="info" />
                        )}
                        {bonuses.defense > 0 && (
                            <Chip size="small" label={`🛡️ +${bonuses.defense} défense`} color="error" />
                        )}
                        {bonuses.production > 0 && (
                            <Chip size="small" label={`⚙️ +${(bonuses.production * 100).toFixed(0)}% production`} color="warning" />
                        )}
                        {bonuses.energy_regeneration === 0 && bonuses.storage === 0 && bonuses.defense === 0 && bonuses.production === 0 && (
                            <Typography variant="body2" color="text.secondary">
                                Aucun bonus actif
                            </Typography>
                        )}
                    </Box>
                </Box>
            )}

            <Divider sx={{ my: 2 }} />

            {/* Buildings on current cell */}
            {currentCell?.buildings && currentCell.buildings.length > 0 && (
                <Box sx={{ mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                        Bâtiments sur cette case
                    </Typography>
                    <List dense>
                        {currentCell.buildings.map((building) => (
                            <ListItem
                                key={building.id ?? `${building.building_type?.id || 'bt'}-${building.owner || 'owner'}`}
                                sx={{
                                    border: 1,
                                    borderColor: 'divider',
                                    borderRadius: 1,
                                    mb: 1,
                                    bgcolor: building.owner === player?.user?.username ? 'action.selected' : 'background.paper'
                                }}
                            >
                                <ListItemText
                                    primary={
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Typography variant="body1">
                                                {building.building_type.icon} {building.building_type.name}
                                            </Typography>
                                            <Chip
                                                size="small"
                                                label={building.owner}
                                                color={building.owner === player?.user?.username ? 'primary' : 'default'}
                                            />
                                            <Chip
                                                size="small"
                                                label={building.status === 'completed' ? 'Terminé' : 'En construction'}
                                                color={building.status === 'completed' ? 'success' : 'warning'}
                                            />
                                        </Box>
                                    }
                                    secondary={
                                        building.status === 'under_construction' && (
                                            <Box sx={{ mt: 1 }}>
                                                <LinearProgress variant="determinate" value={building.construction_progress} />
                                                <Typography variant="caption">
                                                    Progression: {building.construction_progress}%
                                                </Typography>
                                            </Box>
                                        )
                                    }
                                />
                            </ListItem>
                        ))}
                    </List>
                    <Divider sx={{ my: 2 }} />
                </Box>
            )}

            {/* Available building types */}
            <Typography variant="subtitle1" gutterBottom>
                Bâtiments Disponibles
            </Typography>

            {hasBuildingOnCurrentCell && (
                <Box sx={{ mb: 2, p: 1, bgcolor: 'warning.light', borderRadius: 1 }}>
                    <Typography variant="body2" color="warning.dark">
                        ⚠️ Vous avez déjà un bâtiment sur cette case
                    </Typography>
                </Box>
            )}

            <Grid container spacing={2}>
                {availableTypes.map((buildingType) => (
                    <Grid item xs={12} sm={6} md={4} key={buildingType.id}>
                        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                            <CardContent sx={{ flexGrow: 1 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                    <Typography variant="h5">
                                        {buildingType.icon}
                                    </Typography>
                                    <Chip
                                        label={buildingType.category}
                                        size="small"
                                        sx={{
                                            bgcolor: getCategoryColor(buildingType.category),
                                            color: 'white'
                                        }}
                                    />
                                </Box>
                                <Typography variant="h6" gutterBottom>
                                    {buildingType.name}
                                </Typography>
                                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                                    {buildingType.description}
                                </Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                    {buildingType.energy_regeneration_bonus > 0 && (
                                        <Chip size="small" label={`⚡ +${buildingType.energy_regeneration_bonus}/h`} />
                                    )}
                                    {buildingType.storage_bonus > 0 && (
                                        <Chip size="small" label={`📦 +${buildingType.storage_bonus}`} />
                                    )}
                                    {buildingType.defense_bonus > 0 && (
                                        <Chip size="small" label={`🛡️ +${buildingType.defense_bonus}`} />
                                    )}
                                    {buildingType.production_bonus > 0 && (
                                        <Chip size="small" label={`⚙️ +${(buildingType.production_bonus * 100).toFixed(0)}%`} />
                                    )}
                                </Box>
                            </CardContent>
                            <CardActions>
                                <Button
                                    size="small"
                                    variant="contained"
                                    fullWidth
                                    onClick={() => handleOpenDialog(buildingType)}
                                    disabled={loading || hasBuildingOnCurrentCell}
                                >
                                    Construire
                                </Button>
                            </CardActions>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {/* Construction dialog */}
            <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
                <DialogTitle>
                    {selectedBuilding?.icon} Construire {selectedBuilding?.name}
                </DialogTitle>
                <DialogContent>
                    <Typography variant="body2" paragraph>
                        {selectedBuilding?.description}
                    </Typography>

                    <Typography variant="subtitle2" gutterBottom>
                        Matériaux requis:
                    </Typography>
                    <List dense>
                        {selectedBuilding?.materials?.map((mat, index) => (
                            <ListItem key={index}>
                                <ListItemText
                                    primary={`${mat.material_icon} ${mat.material_name} x${mat.quantity}`}
                                />
                            </ListItem>
                        ))}
                    </List>

                    <Box sx={{ mt: 2, p: 1, bgcolor: 'info.light', borderRadius: 1 }}>
                        <Typography variant="body2">
                            ⏱️ Temps de construction: {selectedBuilding?.construction_time}s
                        </Typography>
                        <Typography variant="body2">
                            📊 Niveau requis: {selectedBuilding?.required_level}
                        </Typography>
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCloseDialog}>Annuler</Button>
                    <Button
                        onClick={handleConstruct}
                        variant="contained"
                        disabled={loading}
                    >
                        {loading ? 'Construction...' : 'Confirmer'}
                    </Button>
                </DialogActions>
            </Dialog>

            {/* My buildings list */}
            {myBuildings.length > 0 && (
                <Box sx={{ mt: 3 }}>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="subtitle1" gutterBottom>
                        Mes Bâtiments ({myBuildings.length})
                    </Typography>
                    <List>
                        {myBuildings.map((building, index) => (
                            <ListItem
                                key={index}
                                sx={{ border: 1, borderColor: 'divider', borderRadius: 1, mb: 1 }}
                            >
                                <ListItemText
                                    primary={
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            <Typography>
                                                {building.building_type.icon} {building.building_type.name}
                                            </Typography>
                                            <Chip size="small" label={`(${building.cell.grid_x}, ${building.cell.grid_y})`} />
                                            <Chip
                                                size="small"
                                                label={building.status === 'completed' ? 'Terminé' : 'En construction'}
                                                color={building.status === 'completed' ? 'success' : 'warning'}
                                            />
                                        </Box>
                                    }
                                    secondary={
                                        building.status === 'under_construction' && (
                                            <Box sx={{ mt: 1 }}>
                                                <LinearProgress variant="determinate" value={building.construction_progress} />
                                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                                                    <Typography variant="caption">
                                                        {building.construction_progress}%
                                                    </Typography>
                                                    <Button
                                                        size="small"
                                                        variant="outlined"
                                                        onClick={() => handleCompleteConstruction(building.id)}
                                                        disabled={actionLoading}
                                                    >
                                                        Finir maintenant
                                                    </Button>
                                                </Box>
                                            </Box>
                                        )
                                    }
                                />
                            </ListItem>
                        ))}
                    </List>
                </Box>
            )}
        </Paper>
    );
};

export default BuildingPanel;
