import React, { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer, Rectangle, useMap } from 'react-leaflet';
import { Box, Paper, Typography, CircularProgress } from '@mui/material';
import { mapAPI, combatAPI, poiAPI, inventoryAPI, bankAPI } from '../../services/api';
import { useGameStore } from '../../stores/useGameStore';
import { useInventory, useMapActions, useWorldState } from '../../hooks';
import { getBiomeColor, getBiomeName } from '../../utils/gameLogic';
import CombatInterface from '../combat/CombatInterface';
import MobEncounter from '../combat/MobEncounter';
import POIDialog from '../poi/POIDialog';
import BankDialog from '../bank/BankDialog';
import logger from '../../utils/logger';
import 'leaflet/dist/leaflet.css';

// Sub-components
import MapControls from './MapControls';
import MapPOI from './MapPOI';
import MapDroppedItems from './MapDroppedItems';
import MapMaterials from './MapMaterials';
import MapEvents from './MapEvents';

const GRID_SIZE = 0.001; // Approximately 100m

function MapUpdater({ center }) {
    const map = useMap();
    useEffect(() => {
        const [lat, lng] = center || [];
        if (Number.isFinite(lat) && Number.isFinite(lng)) {
            map.setView(center, 16);
        }
    }, [center, map]);
    return null;
}

function GameMap({ player, onPlayerUpdate, onGather, onCellUpdate }) {
    const [currentCell, setCurrentCell] = useState(null);
    const [encounterMob, setEncounterMob] = useState(null);
    const [showEncounter, setShowEncounter] = useState(false);
    const [showCombat, setShowCombat] = useState(false);
    const [huntLoading, setHuntLoading] = useState(false);
    const [pois, setPois] = useState([]);
    const [selectedPOI, setSelectedPOI] = useState(null);
    const [showPOIDialog, setShowPOIDialog] = useState(false);
    const [banks, setBanks] = useState([]);
    const [showBankDialog, setShowBankDialog] = useState(false);
    const [location, setLocation] = useState({ city: '', country: '' });
    const showNotification = useGameStore((state) => state.showNotification);
    const { flatInventory } = useInventory();
    const { worldState } = useWorldState(60000);

    const fetchCurrentCell = useCallback(async () => {
        try {
            const response = await mapAPI.getCurrentCell();
            setCurrentCell(response.data);
            if (onCellUpdate) {
                onCellUpdate(response.data);
            }
            // Fetch POIs and banks for current cell
            fetchPOIs();
            fetchBanks();
            return true;
        } catch (error) {
            logger.error('Failed to fetch current cell:', error);
            if (error.response?.status === 401) {
                showNotification('Veuillez vous connecter pour charger la carte.', 'error');
                return false;
            }
            if (error.response?.status === 500) {
                await new Promise(resolve => setTimeout(resolve, 5000));
            }
            return false;
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [onCellUpdate, showNotification]);

    const fetchPOIs = useCallback(async () => {
        try {
            const response = await poiAPI.getCurrentPOIs();
            setPois(response.data.pois || []);
            logger.debug('GameMap', 'POIs loaded:', response.data.pois?.length || 0);
        } catch (error) {
            logger.error('Failed to fetch POIs:', error);
            setPois([]);
        }
    }, []);

    const fetchBanks = useCallback(async () => {
        try {
            const response = await bankAPI.getCurrentBanks();
            setBanks(response.data.banks || []);
            logger.debug('GameMap', 'Banks loaded:', response.data.banks?.length || 0);
        } catch (error) {
            logger.error('Failed to fetch banks:', error);
            setBanks([]);
        }
    }, []);

    const fetchLocation = useCallback(async (lat, lng) => {
        try {
            // Use OpenStreetMap Nominatim for reverse geocoding
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&accept-language=fr`
            );
            const data = await response.json();

            if (data.address) {
                const city = data.address.city ||
                            data.address.town ||
                            data.address.village ||
                            data.address.municipality ||
                            'Localité inconnue';
                const country = data.address.country || 'Pays inconnu';

                setLocation({ city, country });
                logger.debug('GameMap', 'Location fetched:', { city, country });
            }
        } catch (error) {
            logger.error('Failed to fetch location:', error);
            setLocation({ city: 'Localité inconnue', country: 'Pays inconnu' });
        }
    }, []);

    const handlePOIClick = (poi) => {
        setSelectedPOI(poi);
        setShowPOIDialog(true);
    };

    const handlePOIDialogClose = () => {
        setShowPOIDialog(false);
        setSelectedPOI(null);
    };

    const handlePurchaseComplete = (updatedPlayerData) => {
        // Update player data in parent
        if (onPlayerUpdate) {
            onPlayerUpdate();
        }
        showNotification('Achat effectué avec succès!', 'success');
    };

    const handleBankClick = () => {
        setShowBankDialog(true);
    };

    const handleBankDialogClose = () => {
        setShowBankDialog(false);
    };

    const handleBankTransactionComplete = () => {
        // Update player data after transaction
        if (onPlayerUpdate) {
            onPlayerUpdate();
        }
    };

    // Use the new hook for map actions
    const { move, gather, loading } = useMapActions(onPlayerUpdate, onCellUpdate, onGather);

    useEffect(() => {
        let isMounted = true;
        let retryCount = 0;
        const maxRetries = 3;

        const loadCell = async () => {
            if (!player) return;

            let success = false;
            while (!success && retryCount < maxRetries && isMounted) {
                success = await fetchCurrentCell();
                if (!success) {
                    retryCount++;
                    logger.warn(`Tentative ${retryCount} échouée, nouvelle tentative...`);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            }

            if (!success && isMounted) {
                showNotification('Impossible de charger la cellule actuelle', 'error');
            }
        };

        loadCell();

        return () => {
            isMounted = false;
        };
    // Only trigger when grid coordinates change, not on every player update
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [player?.grid_x, player?.grid_y, fetchCurrentCell, showNotification]);

    // Fetch location when player coordinates change
    useEffect(() => {
        if (player?.current_y && player?.current_x) {
            fetchLocation(player.current_y, player.current_x);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [player?.current_y, player?.current_x]);

    const handleMove = (direction) => {
        // Just move - the useEffect will handle fetching the new cell when grid coordinates change
        move(player.id, direction, player.energy);
    };

    const handleGatherMaterial = (materialId) => {
        if (!currentCell) return;
        gather(currentCell.id, materialId, fetchCurrentCell);
    };

    const handleGatherAll = async () => {
        if (!currentCell?.materials?.length) return;

        for (const material of currentCell.materials) {
            if (material.quantity <= 0) continue;
            await gather(currentCell.id, material.material.id);
            // Petite pause entre chaque récolte
            await new Promise(resolve => setTimeout(resolve, 500));
        }
        await fetchCurrentCell();
    };

    const handlePickup = async (droppedId) => {
        try {
            const response = await inventoryAPI.pickup(droppedId);
            showNotification(response.data.message, 'success');
            await fetchCurrentCell();
            if (onPlayerUpdate) onPlayerUpdate();
        } catch (error) {
            logger.error('Failed to pickup item:', error);
            showNotification(error.response?.data?.error || 'Impossible de ramasser', 'error');
        }
    };

    const handleHunt = async () => {
        setHuntLoading(true);
        try {
            const response = await combatAPI.searchForMob();
            if (response.data.found) {
                setEncounterMob(response.data.mob);
                setShowEncounter(true);
                showNotification(response.data.message, 'info');
            } else {
                showNotification(response.data.message, 'warning');
            }
        } catch (error) {
            logger.error('Failed to search for mob:', error);
            showNotification(error.response?.data?.error || 'Erreur lors de la recherche', 'error');
        } finally {
            setHuntLoading(false);
        }
    };

    const handleFish = async () => {
        // Find fish material in current cell
        const fishMaterial = currentCell.materials?.find(m =>
            m.material.name.toLowerCase().includes('poisson')
        );
        if (fishMaterial) {
            handleGatherMaterial(fishMaterial.material.id);
        } else {
            showNotification('Aucun poisson à pêcher ici', 'warning');
        }
    };

    const handleScavenge = async () => {
        try {
            const response = await mapAPI.scavenge();
            if (response.data.result === 'success') {
                let msg = response.data.message;
                if (response.data.loot && response.data.loot.length > 0) {
                    const items = response.data.loot.map(i => `${i.quantity}x ${i.name}`).join(', ');
                    msg += ` Trouvé: ${items}`;
                }
                showNotification(msg, 'success');

                // Reload data - onGather callback will trigger player update in parent
                if (onGather) onGather();
            } else {
                showNotification(response.data.message, 'info');
            }
        } catch (error) {
            logger.error('Scavenge failed:', error);
            showNotification(error.response?.data?.error || 'Erreur lors de la fouille', 'error');
        }
    };

    const handleStartCombat = () => {
        setShowEncounter(false);
        setShowCombat(true);
    };

    const handleFlee = () => {
        setShowEncounter(false);
        setEncounterMob(null);
        showNotification('Vous avez fui sans combattre', 'info');
    };

    const handleCombatClose = () => {
        setShowCombat(false);
        setEncounterMob(null);
        fetchCurrentCell();
        if (onPlayerUpdate) {
            // Refresh player data
            onPlayerUpdate();
        }
    };

    const handleVictory = (combatState) => {
        // Combat interface will handle showing loot
        if (onGather) onGather(); // Refresh inventory
    };

    // Debug logging for troubleshooting
    logger.debug('GameMap', 'Render state:', { player: !!player, currentCell: !!currentCell, loading });

    if (!player) {
        return (
            <Paper sx={{ p: 2, height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography>Chargement du joueur...</Typography>
            </Paper>
        );
    }

    if (!currentCell) {
        return (
            <Paper sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <CircularProgress sx={{ mb: 2 }} />
                <Typography>Chargement de la carte...</Typography>
            </Paper>
        );
    }

    const hasValidCoords = Number.isFinite(player.current_y) && Number.isFinite(player.current_x);

    // Use player coordinates when valid, otherwise fall back to default center (Valence)
    const fallbackLat = 44.933;
    const fallbackLng = 4.893;
    const centerLat = hasValidCoords ? player.current_y : fallbackLat;
    const centerLng = hasValidCoords ? player.current_x : fallbackLng;

    const center = [centerLat, centerLng];
    const gridBounds = [
        [centerLat - GRID_SIZE / 2, centerLng - GRID_SIZE / 2],
        [centerLat + GRID_SIZE / 2, centerLng + GRID_SIZE / 2],
    ];

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 1 }}>
            {/* Map section */}
            <Paper sx={{ p: 1.5, flex: '0 0 auto', display: 'flex', flexDirection: 'column', gap: 0.75 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body1" sx={{ fontWeight: 600, fontSize: '0.95rem' }}>
                        📍 ({player.grid_x}, {player.grid_y})
                    </Typography>
                    <Box sx={{
                        bgcolor: getBiomeColor(currentCell.biome),
                        color: 'white',
                        px: 1.5,
                        py: 0.25,
                        borderRadius: 0.5,
                        fontWeight: 600,
                        fontSize: '0.8rem',
                    }}>
                        {getBiomeName(currentCell.biome)}
                    </Box>
                </Box>

                {worldState && (
                    <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap', fontSize: 12, color: 'text.secondary' }}>
                        <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>⏱️ {worldState.time_of_day}</Typography>
                        <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>🍂 {worldState.season}</Typography>
                        <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>☁️ {worldState.weather}</Typography>
                        <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>🌡️ {worldState.temperature}°C</Typography>
                        {location.city && location.country && (
                            <Typography variant="caption" sx={{ fontSize: '0.75rem' }}>📍 {location.city}, {location.country}</Typography>
                        )}
                    </Box>
                )}

                <Box sx={{ flex: 1, position: 'relative', borderRadius: 1, overflow: 'hidden', minHeight: '300px' }}>
                    <MapContainer
                        center={center}
                        zoom={17}
                        style={{ height: '100%', width: '100%' }}
                        zoomControl={true}
                    >
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        <Rectangle
                            bounds={gridBounds}
                            pathOptions={{
                                color: getBiomeColor(currentCell.biome),
                                weight: 4,
                                fillOpacity: 0.35,
                                fillColor: getBiomeColor(currentCell.biome),
                            }}
                        />
                        <MapUpdater center={center} />
                    </MapContainer>

                    {/* Events Overlay */}
                    <MapEvents
                        playerGridX={player.grid_x}
                        playerGridY={player.grid_y}
                    />
                </Box>
            </Paper>

            {/* Bottom layout: controls / POI / dropped items on the left, materials on the right */}
            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', md: '1.1fr 1.2fr' },
                    gap: 1,
                }}
            >
                {/* Left column: controls + POI + dropped items */}
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Paper sx={{ p: 1.5 }}>
                        <Typography variant="subtitle2" sx={{ mb: 1, fontSize: '0.85rem', fontWeight: 600 }}>
                            🎮 Contrôles
                        </Typography>
                        <MapControls
                            loading={loading}
                            onMove={handleMove}
                            onGather={() => {
                                if (currentCell.materials?.length) {
                                    handleGatherMaterial(currentCell.materials[0].material.id);
                                }
                            }}
                            onFish={handleFish}
                            onHunt={handleHunt}
                            onScavenge={handleScavenge}
                            currentCell={currentCell}
                            huntLoading={huntLoading}
                        />
                    </Paper>

                    <MapPOI pois={pois} banks={banks} onPOIClick={handlePOIClick} onBankClick={handleBankClick} />

                    <MapDroppedItems
                        droppedItems={currentCell.dropped_items}
                        onPickup={handlePickup}
                        loading={loading}
                    />
                </Box>

                {/* Right column: materials */}
                <Box>
                    <MapMaterials
                        materials={currentCell.materials}
                        onGather={handleGatherMaterial}
                        onGatherAll={handleGatherAll}
                        loading={loading}
                        flatInventory={flatInventory}
                    />
                </Box>
            </Box>

            {/* Combat Dialogs */}
            <MobEncounter
                open={showEncounter}
                mob={encounterMob}
                onFight={handleStartCombat}
                onFlee={handleFlee}
                onClose={handleFlee}
            />

            <CombatInterface
                open={showCombat}
                initialMob={encounterMob}
                onClose={handleCombatClose}
                onVictory={handleVictory}
            />

            {/* POI Dialog */}
            <POIDialog
                open={showPOIDialog}
                onClose={handlePOIDialogClose}
                poi={selectedPOI}
                onPurchaseComplete={handlePurchaseComplete}
            />

            {/* Bank Dialog */}
            <BankDialog
                open={showBankDialog}
                onClose={handleBankDialogClose}
                onTransactionComplete={handleBankTransactionComplete}
                player={player}
            />
        </Box >
    );
}

export default GameMap;
