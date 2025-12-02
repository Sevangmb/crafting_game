import React, { useState, useMemo } from 'react';
import { Box, Tabs, Tab, Menu, MenuItem, ListItemIcon, ListItemText, Divider } from '@mui/material';
import {
    Inventory2,
    Build,
    Person,
    Map,
    Dashboard as DashboardIcon,
    School,
    AccountTree,
    Home,
    EmojiEvents,
    Storefront,
    Assignment as QuestIcon,
    SwapHoriz as TradeIcon,
    Leaderboard as LeaderboardIcon,
    SportsEsports,
    Business,
    Category
} from '@mui/icons-material';

const MENU_STRUCTURE = [
    {
        id: 'game',
        label: 'Jeu',
        icon: <SportsEsports sx={{ fontSize: '1.2rem' }} />,
        items: [
            { label: 'Carte', icon: <Map fontSize="small" />, index: 3 },
            { label: 'Inventaire', icon: <Inventory2 fontSize="small" />, index: 0 },
            { label: 'Personnage', icon: <Person fontSize="small" />, index: 2 },
        ]
    },
    {
        id: 'craft',
        label: 'Construction',
        icon: <Build sx={{ fontSize: '1.2rem' }} />,
        items: [
            { label: 'Fabrication', icon: <Build fontSize="small" />, index: 1 },
            { label: 'Bâtiments', icon: <Home fontSize="small" />, index: 4 },
            { label: 'Recettes', icon: <AccountTree fontSize="small" />, index: 7 },
        ]
    },
    {
        id: 'social',
        label: 'Social',
        icon: <Business sx={{ fontSize: '1.2rem' }} />,
        items: [
            { label: 'Magasin', icon: <Storefront fontSize="small" />, index: 9 },
            { label: 'Échanges', icon: <TradeIcon fontSize="small" />, index: 11 },
            { label: 'Classements', icon: <LeaderboardIcon fontSize="small" />, index: 12 },
        ]
    },
    {
        id: 'progression',
        label: 'Progression',
        icon: <EmojiEvents sx={{ fontSize: '1.2rem' }} />,
        items: [
            { label: 'Compétences', icon: <School fontSize="small" />, index: 6 },
            { label: 'Quêtes', icon: <QuestIcon fontSize="small" />, index: 10 },
            { label: 'Succès', icon: <EmojiEvents fontSize="small" />, index: 8 },
            { label: 'Statistiques', icon: <DashboardIcon fontSize="small" />, index: 5 },
        ]
    }
];

function NavigationTabs({ currentTab, onTabChange }) {
    const [anchorEl, setAnchorEl] = useState(null);
    const [activeMenuId, setActiveMenuId] = useState(null);

    // Calculate which parent tab should be active based on the current content index
    const activeGroupIndex = useMemo(() => {
        return MENU_STRUCTURE.findIndex(group =>
            group.items.some(item => item.index === currentTab)
        );
    }, [currentTab]);

    const handleMenuOpen = (event, menuId) => {
        setAnchorEl(event.currentTarget);
        setActiveMenuId(menuId);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setActiveMenuId(null);
    };

    const handleMenuItemClick = (tabIndex) => {
        onTabChange(tabIndex);
        handleMenuClose();
    };

    return (
        <Box sx={{
            borderBottom: 1,
            borderColor: 'divider',
            bgcolor: 'background.paper',
            px: 2,
            py: 0.5
        }}>
            <Tabs
                value={activeGroupIndex !== -1 ? activeGroupIndex : false}
                variant="scrollable"
                scrollButtons="auto"
                sx={{
                    minHeight: 48,
                    '& .MuiTab-root': {
                        minHeight: 48,
                        textTransform: 'none',
                        fontSize: '0.9rem',
                        fontWeight: 500,
                        borderRadius: 2,
                        mx: 0.5,
                        minWidth: 100,
                        '&.Mui-selected': {
                            bgcolor: 'primary.main',
                            color: 'primary.contrastText',
                            boxShadow: 2
                        }
                    },
                    '& .MuiTabs-indicator': {
                        display: 'none'
                    }
                }}
            >
                {MENU_STRUCTURE.map((group) => (
                    <Tab
                        key={group.id}
                        icon={group.icon}
                        label={group.label}
                        iconPosition="start"
                        onClick={(e) => handleMenuOpen(e, group.id)}
                        sx={{ position: 'relative' }}
                    />
                ))}
            </Tabs>

            {MENU_STRUCTURE.map((group) => (
                <Menu
                    key={group.id}
                    anchorEl={anchorEl}
                    open={activeMenuId === group.id}
                    onClose={handleMenuClose}
                    sx={{
                        '& .MuiPaper-root': {
                            minWidth: 200,
                            mt: 1
                        }
                    }}
                >
                    {group.items.map((item) => (
                        <MenuItem
                            key={item.index}
                            onClick={() => handleMenuItemClick(item.index)}
                            selected={currentTab === item.index}
                        >
                            <ListItemIcon>{item.icon}</ListItemIcon>
                            <ListItemText>{item.label}</ListItemText>
                        </MenuItem>
                    ))}
                </Menu>
            ))}
        </Box>
    );
}

export default NavigationTabs;
