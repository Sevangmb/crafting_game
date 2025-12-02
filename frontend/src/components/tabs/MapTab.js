import React from 'react';
import { Box, Paper } from '@mui/material';
import GameMap from '../map/GameMap';

const MapTab = React.memo(function MapTab({ player, onPlayerUpdate, onGather, onCellUpdate }) {
    return (
        <Box sx={{ height: 'calc(100vh - 250px)' }}>
            {player ? (
                <GameMap
                    player={player}
                    onPlayerUpdate={onPlayerUpdate}
                    onGather={onGather}
                    onCellUpdate={onCellUpdate}
                />
            ) : (
                <Paper sx={{
                    height: '100%',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    bgcolor: 'background.paper'
                }}>
                    Chargement...
                </Paper>
            )}
        </Box>
    );
});

export default MapTab;
