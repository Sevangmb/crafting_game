import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import Dashboard from '../Dashboard/Dashboard';

function DashboardTab() {
    return (
        <Box sx={{ maxWidth: '1200px', mx: 'auto' }}>
            <Typography variant="h4" gutterBottom sx={{
                fontWeight: 700,
                color: 'primary.main',
                mb: 3,
                display: 'flex',
                alignItems: 'center',
                gap: 2
            }}>
                📊 Tableau de Bord
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 400 }}>
                    Suivez votre progression et vos statistiques
                </Typography>
            </Typography>
            <Paper elevation={1} sx={{ borderRadius: 1, overflow: 'hidden' }}>
                <Dashboard />
            </Paper>
        </Box>
    );
}

export default DashboardTab;
