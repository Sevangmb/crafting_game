import React, { useState, useEffect } from 'react';
import {
    Paper, Typography, Box, Grid, Button, Card, CardContent,
    CardActions, Chip, CircularProgress, Alert
} from '@mui/material';
import { DirectionsBike, ShoppingCart, Sailing, Speed, FitnessCenter, Bolt } from '@mui/icons-material';
import api from '../../services/api';

function VehiclePanel({ onVehicleChange }) {
    const [vehicles, setVehicles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [actionLoading, setActionLoading] = useState(false);

    const fetchVehicles = async () => {
        try {
            setLoading(true);
            const response = await api.get('/vehicles/');
            setVehicles(response.data);
            setError(null);
        } catch (err) {
            console.error('Error fetching vehicles:', err);
            setError('Impossible de charger les véhicules');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchVehicles();
    }, []);

    const handleEquip = async (vehicleId) => {
        try {
            setActionLoading(true);
            await api.post(`/vehicles/${vehicleId}/equip/`);
            await fetchVehicles();
            if (onVehicleChange) onVehicleChange();
        } catch (err) {
            console.error('Error equipping vehicle:', err);
            setError('Erreur lors de l\'équipement du véhicule');
        } finally {
            setActionLoading(false);
        }
    };

    const handleUnequip = async () => {
        try {
            setActionLoading(true);
            await api.post('/vehicles/unequip/');
            await fetchVehicles();
            if (onVehicleChange) onVehicleChange();
        } catch (err) {
            console.error('Error unequipping vehicle:', err);
            setError('Erreur lors du déséquipement');
        } finally {
            setActionLoading(false);
        }
    };

    const getVehicleIcon = (icon) => {
        switch (icon) {
            case '🚲': return <DirectionsBike />;
            case '🛒': return <ShoppingCart />;
            case '🛶': return <Sailing />;
            default: return <DirectionsBike />;
        }
    };

    if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}><CircularProgress /></Box>;

    return (
        <Paper sx={{ p: 2, mt: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <DirectionsBike sx={{ mr: 1 }} />
                Mes Véhicules
            </Typography>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            {vehicles.length === 0 ? (
                <Typography color="text.secondary" align="center" sx={{ py: 3 }}>
                    Vous ne possédez aucun véhicule. Fabriquez-en un dans l'atelier !
                </Typography>
            ) : (
                <Grid container spacing={2}>
                    {vehicles.map((v) => (
                        <Grid item xs={12} sm={6} md={4} key={v.id}>
                            <Card variant="outlined" sx={{
                                borderColor: v.is_equipped ? 'primary.main' : 'divider',
                                bgcolor: v.is_equipped ? 'rgba(25, 118, 210, 0.05)' : 'background.paper'
                            }}>
                                <CardContent>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                                            <Box sx={{ mr: 1, fontSize: '1.5rem' }}>{v.icon}</Box>
                                            <Typography variant="h6">{v.name}</Typography>
                                        </Box>
                                        {v.is_equipped && <Chip label="Équipé" color="primary" size="small" />}
                                    </Box>

                                    <Typography variant="body2" color="text.secondary" paragraph>
                                        {v.description}
                                    </Typography>

                                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                        <Chip
                                            icon={<FitnessCenter sx={{ fontSize: 16 }} />}
                                            label={`+${v.carry_bonus}kg`}
                                            size="small"
                                            color="success"
                                            variant="outlined"
                                        />
                                        <Chip
                                            icon={<Speed sx={{ fontSize: 16 }} />}
                                            label={`${v.speed_bonus > 0 ? '+' : ''}${v.speed_bonus}% Vitesse`}
                                            size="small"
                                            color={v.speed_bonus >= 0 ? "info" : "warning"}
                                            variant="outlined"
                                        />
                                        {v.energy_efficiency > 0 && (
                                            <Chip
                                                icon={<Bolt sx={{ fontSize: 16 }} />}
                                                label={`-${v.energy_efficiency}% Fatigue`}
                                                size="small"
                                                color="secondary"
                                                variant="outlined"
                                            />
                                        )}
                                    </Box>
                                </CardContent>
                                <CardActions>
                                    {v.is_equipped ? (
                                        <Button
                                            size="small"
                                            color="warning"
                                            onClick={handleUnequip}
                                            disabled={actionLoading}
                                            fullWidth
                                        >
                                            Déséquiper
                                        </Button>
                                    ) : (
                                        <Button
                                            size="small"
                                            variant="contained"
                                            onClick={() => handleEquip(v.id)}
                                            disabled={actionLoading}
                                            fullWidth
                                        >
                                            Utiliser
                                        </Button>
                                    )}
                                </CardActions>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            )}
        </Paper>
    );
}

export default VehiclePanel;
