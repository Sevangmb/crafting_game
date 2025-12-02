import React from 'react';
import { Box } from '@mui/material';
import CraftingPanel from '../crafting/CraftingPanel';

const CraftingTab = React.memo(function CraftingTab({ inventory, onCraft }) {
    return (
        <Box sx={{ height: 'calc(100vh - 250px)' }}>
            <CraftingPanel inventory={inventory} onCraft={onCraft} />
        </Box>
    );
});

export default CraftingTab;
