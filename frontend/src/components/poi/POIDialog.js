import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    List,
    ListItem,
    ListItemText,
    ListItemAvatar,
    Avatar,
    Typography,
    Box,
    Chip,
    TextField,
    CircularProgress,
    Alert,
    IconButton,
    Divider,
    Tabs,
    Tab
} from '@mui/material';
import { Close, ShoppingCart, Restaurant, Sell, AttachMoney, TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';
import { poiAPI } from '../../services/api';
import { useGameLogic } from '../../hooks/useGameLogic';

const POIDialog = ({ open, onClose, poi, onPurchaseComplete }) => {
    const [tabIndex, setTabIndex] = useState(0);
    const [menu, setMenu] = useState(null);
    const [loading, setLoading] = useState(true);
    const [processing, setProcessing] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [quantities, setQuantities] = useState({});
    const [sellPrices, setSellPrices] = useState({});

    // Get player inventory from store using flatInventory to handle both array and object cases
    const { flatInventory } = useGameLogic();

    useEffect(() => {
        if (open && poi) {
            loadMenu();
            loadSellPrices();
            setTabIndex(0); // Reset to buy tab
        }
    }, [open, poi]);

    const loadMenu = async () => {
        setLoading(true);
        setError(null);
        setSuccess(null);
        try {
            const response = await poiAPI.getMenu(poi.type);
            setMenu(response.data);
        } catch (err) {
            console.error('Failed to load POI menu:', err);
            setError('Impossible de charger le menu');
        } finally {
            setLoading(false);
        }
    };

    const loadSellPrices = async () => {
        // Load real sell prices for all sellable items in inventory
        const sellableItems = getFilteredInventory();
        const prices = {};

        for (const item of sellableItems) {
            try {
                const response = await poiAPI.getSellPrice(poi.type, item.material.id);
                if (response.data.accepted) {
                    prices[item.material.id] = response.data.sell_price;
                }
            } catch (err) {
                console.error(`Failed to load sell price for ${item.material.name}:`, err);
            }
        }

        setSellPrices(prices);
    };

    const handleQuantityChange = (materialId, value) => {
        const qty = Math.max(1, parseInt(value) || 1);
        setQuantities(prev => ({ ...prev, [materialId]: qty }));
    };

    const handlePurchase = async (item) => {
        setProcessing(true);
        setError(null);
        setSuccess(null);

        const quantity = quantities[item.material_id] || 1;

        try {
            const response = await poiAPI.purchase(poi.type, item.material_id, quantity);

            if (response.data.success) {
                setSuccess(response.data.message);
                setQuantities(prev => ({ ...prev, [item.material_id]: 1 }));

                if (onPurchaseComplete && response.data.player) {
                    onPurchaseComplete(response.data.player);
                }

                setTimeout(() => setSuccess(null), 3000);
            } else {
                setError(response.data.error || 'Échec de l\'achat');
            }
        } catch (err) {
            console.error('Purchase failed:', err);
            setError(err.response?.data?.error || 'Erreur lors de l\'achat');
        } finally {
            setProcessing(false);
        }
    };

    const handleSell = async (item) => {
        setProcessing(true);
        setError(null);
        setSuccess(null);

        const quantity = quantities[item.id] || 1;

        try {
            const response = await poiAPI.sell(poi.type, item.material.id, quantity);

            if (response.data.success) {
                setSuccess(response.data.message);
                setQuantities(prev => ({ ...prev, [item.id]: 1 }));

                if (onPurchaseComplete && response.data.player) {
                    onPurchaseComplete(response.data.player);
                }

                // Reload sell prices after selling
                loadSellPrices();

                setTimeout(() => setSuccess(null), 3000);
            } else {
                setError(response.data.error || 'Échec de la vente');
            }
        } catch (err) {
            console.error('Sell failed:', err);
            setError(err.response?.data?.error || 'Erreur lors de la vente');
        } finally {
            setProcessing(false);
        }
    };

    const handleSellAll = async () => {
        setProcessing(true);
        setError(null);
        setSuccess(null);

        const sellableItems = getFilteredInventory();
        let totalEarned = 0;
        let successCount = 0;
        let errors = [];

        for (const item of sellableItems) {
            try {
                const response = await poiAPI.sell(poi.type, item.material.id, item.quantity);
                if (response.data.success) {
                    successCount++;
                    // Extract money earned from message (hacky but works)
                    const match = response.data.message.match(/(\d+)₡/);
                    if (match) {
                        totalEarned += parseInt(match[1]);
                    }
                } else {
                    errors.push(`${item.material.name}: ${response.data.error}`);
                }
            } catch (err) {
                errors.push(`${item.material.name}: ${err.response?.data?.error || 'Erreur'}`);
            }
        }

        if (successCount > 0) {
            setSuccess(`✅ Vendu ${successCount} types d'items pour ${totalEarned}₡!`);

            // Refresh player data
            if (onPurchaseComplete) {
                try {
                    const playerResponse = await poiAPI.getMenu(poi.type);
                    // Trigger parent refresh
                    loadSellPrices();
                } catch (err) {
                    console.error('Failed to refresh after sell all:', err);
                }
            }
        }

        if (errors.length > 0) {
            setError(`Certains items n'ont pas pu être vendus: ${errors.join(', ')}`);
        }

        setProcessing(false);
        setTimeout(() => {
            setSuccess(null);
            setError(null);
        }, 5000);
    };

    const getPriceIndicator = (priceChange) => {
        if (!priceChange || Math.abs(priceChange) < 1) {
            return { icon: <TrendingFlat />, color: 'default', text: 'Prix stable' };
        } else if (priceChange > 0) {
            return { icon: <TrendingUp />, color: 'error', text: `+${priceChange.toFixed(0)}%` };
        } else {
            return { icon: <TrendingDown />, color: 'success', text: `${priceChange.toFixed(0)}%` };
        }
    };

    const canSellItem = (item) => {
        const acceptedCategories = {
            'restaurant': ['nourriture'],
            'fast_food': ['nourriture'],
            'cafe': ['nourriture'],
            'supermarket': ['nourriture', 'divers'],
            'hardware': ['bois', 'minerais', 'divers'],
            'pharmacy': ['divers'],
            'clothes': ['equipement'],
            'fuel': ['divers']
        };

        const accepted = acceptedCategories[poi.type] || [];
        return accepted.includes(item.material.category);
    };

    const getFilteredInventory = () => {
        // flatInventory is always an array, so we can safely filter it
        return flatInventory.filter(item => canSellItem(item));
    };

    const getPOIIcon = (type) => {
        const icons = {
            'restaurant': '🍽️',
            'fast_food': '🍔',
            'cafe': '☕',
            'supermarket': '🛒',
            'clothes': '👕',
            'hardware': '🔧',
            'pharmacy': '⚕️',
            'fuel': '⛽',
        };
        return icons[type] || '📍';
    };

    const getPOIName = (type) => {
        const names = {
            'restaurant': 'Restaurant',
            'fast_food': 'Fast Food',
            'cafe': 'Café',
            'supermarket': 'Supermarché',
            'clothes': 'Magasin de vêtements',
            'hardware': 'Quincaillerie',
            'pharmacy': 'Pharmacie',
            'fuel': 'Station-service'
        };
        return names[type] || type;
    };

    if (!poi) return null;

    const sellableItems = getFilteredInventory();

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="md"
            fullWidth
            PaperProps={{
                sx: { minHeight: '60vh' }
            }}
        >
            <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h4">{getPOIIcon(poi.type)}</Typography>
                    <Box>
                        <Typography variant="h6">{poi.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                            {getPOIName(poi.type)}
                        </Typography>
                    </Box>
                </Box>
                <IconButton onClick={onClose} size="small">
                    <Close />
                </IconButton>
            </DialogTitle>

            <Divider />

            {/* Tabs for Buy/Sell */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                <Tabs value={tabIndex} onChange={(e, newValue) => setTabIndex(newValue)}>
                    <Tab icon={<ShoppingCart />} label="Acheter" iconPosition="start" />
                    <Tab
                        icon={<Sell />}
                        label={`Vendre ${sellableItems.length > 0 ? `(${sellableItems.length})` : ''}`}
                        iconPosition="start"
                    />
                </Tabs>
            </Box>

            <DialogContent>
                {loading && (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                        <CircularProgress />
                    </Box>
                )}

                {error && (
                    <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}

                {success && (
                    <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
                        {success}
                    </Alert>
                )}

                {/* BUY TAB */}
                {tabIndex === 0 && menu && !loading && (
                    <>
                        <Typography variant="body2" color="text.secondary" gutterBottom sx={{ mb: 2 }}>
                            Monnaie: <Chip label="Argent (₡)" size="small" color="success" icon={<AttachMoney />} />
                        </Typography>

                        <List>
                            {menu.menu.length === 0 ? (
                                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                                    Aucun article disponible
                                </Typography>
                            ) : (
                                menu.menu.map((item) => (
                                    <ListItem
                                        key={item.material_id}
                                        sx={{
                                            border: 1,
                                            borderColor: 'divider',
                                            borderRadius: 1,
                                            mb: 1,
                                            flexDirection: 'column',
                                            alignItems: 'stretch',
                                            bgcolor: 'background.paper',
                                        }}
                                    >
                                        <Box sx={{ display: 'flex', width: '100%', alignItems: 'center', mb: 1 }}>
                                            <ListItemAvatar>
                                                <Avatar sx={{ bgcolor: 'primary.light' }}>
                                                    {item.material_icon}
                                                </Avatar>
                                            </ListItemAvatar>
                                            <ListItemText
                                                primary={
                                                    <Typography variant="subtitle1" fontWeight="bold">
                                                        {item.material_name}
                                                    </Typography>
                                                }
                                                secondary={item.material_description}
                                            />
                                            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 0.5 }}>
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                    <Chip
                                                        label={`${item.price}₡`}
                                                        color="success"
                                                        sx={{ fontWeight: 'bold', minWidth: 80 }}
                                                    />
                                                    {item.price_change && Math.abs(item.price_change) >= 1 && (
                                                        <Chip
                                                            icon={getPriceIndicator(item.price_change).icon}
                                                            label={getPriceIndicator(item.price_change).text}
                                                            size="small"
                                                            color={getPriceIndicator(item.price_change).color}
                                                            variant="outlined"
                                                        />
                                                    )}
                                                </Box>
                                                {item.base_price && item.price !== item.base_price && (
                                                    <Typography variant="caption" color="text.secondary" sx={{ textDecoration: 'line-through' }}>
                                                        Prix normal: {item.base_price}₡
                                                    </Typography>
                                                )}
                                            </Box>
                                        </Box>

                                        <Box sx={{ display: 'flex', gap: 1, mb: 1, flexWrap: 'wrap' }}>
                                            {item.hunger_restore > 0 && (
                                                <Chip
                                                    icon={<Restaurant sx={{ fontSize: 16 }} />}
                                                    label={`+${item.hunger_restore} Faim`}
                                                    size="small"
                                                    variant="outlined"
                                                    color="success"
                                                />
                                            )}
                                            {item.thirst_restore > 0 && (
                                                <Chip
                                                    label={`+${item.thirst_restore} Soif`}
                                                    size="small"
                                                    variant="outlined"
                                                    color="info"
                                                />
                                            )}
                                            {item.energy_restore > 0 && (
                                                <Chip
                                                    label={`+${item.energy_restore} Énergie`}
                                                    size="small"
                                                    variant="outlined"
                                                    color="warning"
                                                />
                                            )}
                                        </Box>

                                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                                            <TextField
                                                type="number"
                                                size="small"
                                                label="Quantité"
                                                value={quantities[item.material_id] || 1}
                                                onChange={(e) => handleQuantityChange(item.material_id, e.target.value)}
                                                inputProps={{ min: 1, max: 99 }}
                                                sx={{ width: 100 }}
                                            />
                                            <Typography variant="caption" color="text.secondary">
                                                Total: {(quantities[item.material_id] || 1) * item.price}₡
                                            </Typography>
                                            <Button
                                                variant="contained"
                                                color="primary"
                                                onClick={() => handlePurchase(item)}
                                                disabled={processing}
                                                startIcon={<ShoppingCart />}
                                                sx={{ ml: 'auto' }}
                                            >
                                                Acheter
                                            </Button>
                                        </Box>
                                    </ListItem>
                                ))
                            )}
                        </List>
                    </>
                )}

                {/* SELL TAB */}
                {tabIndex === 1 && !loading && (
                    <>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                            <Typography variant="body2" color="text.secondary">
                                Vendez vos items pour gagner de l'argent. Ce magasin accepte: {' '}
                                <strong>
                                    {poi.type === 'restaurant' || poi.type === 'fast_food' || poi.type === 'cafe' ? 'Nourriture' : ''}
                                    {poi.type === 'supermarket' ? 'Nourriture, Divers' : ''}
                                    {poi.type === 'hardware' ? 'Bois, Minerais, Divers' : ''}
                                    {poi.type === 'pharmacy' ? 'Médicaments, Divers' : ''}
                                    {poi.type === 'clothes' ? 'Équipement' : ''}
                                    {poi.type === 'fuel' ? 'Divers' : ''}
                                </strong>
                            </Typography>
                            {sellableItems.length > 0 && (
                                <Button
                                    variant="outlined"
                                    color="secondary"
                                    onClick={handleSellAll}
                                    disabled={processing}
                                    startIcon={<AttachMoney />}
                                    size="small"
                                >
                                    Vendre Tout
                                </Button>
                            )}
                        </Box>

                        <List>
                            {sellableItems.length === 0 ? (
                                <Alert severity="info" sx={{ mt: 2 }}>
                                    Vous n'avez aucun item que ce magasin accepte d'acheter.
                                </Alert>
                            ) : (
                                sellableItems.map((item) => (
                                    <ListItem
                                        key={item.id}
                                        sx={{
                                            border: 1,
                                            borderColor: 'divider',
                                            borderRadius: 1,
                                            mb: 1,
                                            flexDirection: 'column',
                                            alignItems: 'stretch',
                                            bgcolor: 'background.paper',
                                        }}
                                    >
                                        <Box sx={{ display: 'flex', width: '100%', alignItems: 'center', mb: 1 }}>
                                            <ListItemAvatar>
                                                <Avatar sx={{ bgcolor: 'secondary.light' }}>
                                                    {item.material.icon}
                                                </Avatar>
                                            </ListItemAvatar>
                                            <ListItemText
                                                primary={
                                                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                        <Typography variant="subtitle1" fontWeight="bold">
                                                            {item.material.name}
                                                        </Typography>
                                                        <Chip
                                                            label={`x${item.quantity}`}
                                                            size="small"
                                                            color="primary"
                                                            variant="outlined"
                                                        />
                                                    </Box>
                                                }
                                                secondary={item.material.description}
                                            />
                                            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                                                <Chip
                                                    label={sellPrices[item.material.id] ? `${sellPrices[item.material.id]}₡` : 'Chargement...'}
                                                    color="warning"
                                                    sx={{ fontWeight: 'bold', minWidth: 80 }}
                                                />
                                                <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                                                    par unité
                                                </Typography>
                                            </Box>
                                        </Box>

                                        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                                            <TextField
                                                type="number"
                                                size="small"
                                                label="Quantité"
                                                value={quantities[item.id] || 1}
                                                onChange={(e) => handleQuantityChange(item.id, e.target.value)}
                                                inputProps={{ min: 1, max: item.quantity }}
                                                sx={{ width: 100 }}
                                            />
                                            <Typography variant="caption" color="text.secondary">
                                                Disponible: {item.quantity}
                                            </Typography>
                                            {sellPrices[item.material.id] && (
                                                <Typography variant="caption" color="success.main" sx={{ fontWeight: 'bold' }}>
                                                    Total: {(quantities[item.id] || 1) * sellPrices[item.material.id]}₡
                                                </Typography>
                                            )}
                                            <Button
                                                variant="contained"
                                                color="secondary"
                                                onClick={() => handleSell(item)}
                                                disabled={processing || !sellPrices[item.material.id]}
                                                startIcon={<Sell />}
                                                sx={{ ml: 'auto' }}
                                            >
                                                Vendre
                                            </Button>
                                        </Box>
                                    </ListItem>
                                ))
                            )}
                        </List>
                    </>
                )}
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose} color="inherit">
                    Fermer
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default POIDialog;
