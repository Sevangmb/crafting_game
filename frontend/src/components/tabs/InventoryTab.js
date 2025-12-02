import React from 'react';
import { Box } from '@mui/material';
import Inventory from '../inventory/Inventory';

const InventoryTab = React.memo(function InventoryTab({ groupedInventory, onConsume }) {
    return (
        <Box sx={{ height: 'calc(100vh - 250px)' }}>
            <Inventory inventory={groupedInventory} onConsume={onConsume} />
        </Box>
    );
});

export default InventoryTab;
