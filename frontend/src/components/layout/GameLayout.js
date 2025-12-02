import React from 'react';
import { Box, Container } from '@mui/material';
import TopBar from './TopBar';
import NavigationTabs from './NavigationTabs';
import SurvivalAlerts from '../survival/SurvivalAlerts';

function GameLayout({
    children,
    player,
    currentTab,
    onTabChange,
    onOpenAdmin,
    onRestart,
    onLogout
}) {
    return (
        <Box sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            minHeight: '100vh',
            bgcolor: 'background.default'
        }}>
            <TopBar
                player={player}
                onOpenAdmin={onOpenAdmin}
                onRestart={onRestart}
                onLogout={onLogout}
            />

            <NavigationTabs
                currentTab={currentTab}
                onTabChange={onTabChange}
            />



            <Box sx={{
                flex: 1,
                overflow: 'auto',
                bgcolor: 'background.default',
                p: 2
            }}>
                <Container maxWidth="xl" disableGutters>
                    <SurvivalAlerts player={player} />
                    {children}
                </Container>
            </Box>
        </Box>
    );
}

export default GameLayout;
