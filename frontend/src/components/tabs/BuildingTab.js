import React from 'react';
import { Box } from '@mui/material';
import BuildingPanel from '../buildings/BuildingPanel';
import { useGameStore, selectPlayer, selectCurrentCell } from '../../stores/useGameStore';

const BuildingTab = ({ onRefresh }) => {
    const player = useGameStore(selectPlayer);
    const currentCell = useGameStore(selectCurrentCell);

    return (
        <Box sx={{ p: 2 }}>
            <BuildingPanel
                currentCell={currentCell}
                player={player}
                onRefresh={onRefresh}
            />
        </Box>
    );
};

export default BuildingTab;
