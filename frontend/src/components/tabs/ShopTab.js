import React, { useState, useEffect } from 'react';
import {
    Box,
    Typography,
    Paper,
    Grid,
    Card,
    CardContent,
    Button,
    Chip,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Alert,
    Tabs,
    Tab,
    CircularProgress,
} from '@mui/material';
import { shopAPI } from '../../services/api';
import { useGameStore, selectPlayer } from '../../stores/useGameStore';
import MaterialIcon from '../common/MaterialIcon';

const ShopItemCard = ({ item, onBuy, playerMoney, playerLevel }) => {
    const [quantity, setQuantity] = useState(1);
    const [buyDialogOpen, setBuyDialogOpen] = useState(false);

    const canAfford = playerMoney >= item.effective_buy_price * quantity;
    const canBuy = item.available && playerLevel >= item.required_level && canAfford;
    const totalCost = item.effective_buy_price * quantity;

    const handleBuy = () => {
        onBuy(item.id, quantity);
        setBuyDialogOpen(false);
        setQuantity(1);
    };

    return (
        <>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <MaterialIcon icon={item.material.icon} size={48} />
                        <Box sx={{ flex: 1 }}>
                            <Typography variant="h6" sx={{ fontSize: '1rem', fontWeight: 600 }}>
                                {item.material.name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                                {item.material.description}
                            </Typography>
                        </Box>
                    </Box>

                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                        <Chip
                            label={item.material.rarity}
                            size="small"
                            sx={{ textTransform: 'capitalize', fontSize: '0.75rem' }}
                        />
                        {item.stock !== -1 && (
                            <Chip
                                label={`Stock: ${item.stock}`}
                                size="small"
                                color={item.stock > 0 ? 'success' : 'error'}
                                sx={{ fontSize: '0.75rem' }}
                            />
                        )}
                        {item.required_level > 1 && (
                            <Chip
                                label={`Niveau ${item.required_level}`}
                                size="small"
                                color={playerLevel >= item.required_level ? 'default' : 'warning'}
                                sx={{ fontSize: '0.75rem' }}
                            />
                        )}
                    </Box>

                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                        <Typography variant="h5" color="primary" sx={{ fontWeight: 700 }}>
                            {item.effective_buy_price} 💎
                        </Typography>
                        {item.effective_sell_price > 0 && (
                            <Typography variant="caption" color="text.secondary">
                                Revente: {item.effective_sell_price} 💎
                            </Typography>
                        )}
                    </Box>

                    <Button
                        variant="contained"
                        fullWidth
                        disabled={!canBuy}
                        onClick={() => setBuyDialogOpen(true)}
                    >
                        {!item.available ? 'Indisponible' :
                            playerLevel < item.required_level ? `Niveau ${item.required_level} requis` :
                                'Acheter'}
                    </Button>
                </CardContent>
            </Card>

            <Dialog open={buyDialogOpen} onClose={() => setBuyDialogOpen(false)}>
                <DialogTitle>Acheter {item.material.name}</DialogTitle>
                <DialogContent>
                    <Box sx={{ pt: 2 }}>
                        <TextField
                            label="Quantité"
                            type="number"
                            value={quantity}
                            onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                            fullWidth
                            inputProps={{ min: 1, max: item.stock !== -1 ? item.stock : 999 }}
                            sx={{ mb: 2 }}
                        />
                        <Typography variant="body1" sx={{ mb: 1 }}>
                            Coût total: <strong>{totalCost} 💎</strong>
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Solde actuel: {playerMoney} 💎
                        </Typography>
                        {!canAfford && (
                            <Alert severity="error" sx={{ mt: 2 }}>
                                Argent insuffisant
                            </Alert>
                        )}
                    </Box>
                </DialogContent>
                <DialogActions>
                    <Button onClick={() => setBuyDialogOpen(false)}>Annuler</Button>
                    <Button onClick={handleBuy} variant="contained" disabled={!canAfford}>
                        Confirmer
                    </Button>
                </DialogActions>
            </Dialog>
        </>
    );
};

const ShopTab = () => {
    const player = useGameStore(selectPlayer);
    const [shops, setShops] = useState([]);
    const [selectedShop, setSelectedShop] = useState(null);
    const [shopItems, setShopItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState('');

    useEffect(() => {
        loadShops();
    }, []);

    const loadShops = async () => {
        try {
            setLoading(true);
            const response = await shopAPI.getAll();
            setShops(response.data);
            if (response.data.length > 0) {
                selectShop(response.data[0]);
            }
        } catch (err) {
            setError('Erreur lors du chargement des magasins');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const selectShop = async (shop) => {
        try {
            setSelectedShop(shop);
            const response = await shopAPI.getItems(shop.id);
            setShopItems(response.data);
        } catch (err) {
            setError('Erreur lors du chargement des articles');
            console.error(err);
        }
    };

    const handleBuy = async (itemId, quantity) => {
        try {
            const response = await shopAPI.buyItem(selectedShop.id, itemId, quantity);
            setSuccessMessage(response.data.message);

            // Refresh shop items and player data
            selectShop(selectedShop);
            useGameStore.getState().fetchPlayerData();

            setTimeout(() => setSuccessMessage(''), 3000);
        } catch (err) {
            setError(err.response?.data?.error || 'Erreur lors de l\'achat');
            setTimeout(() => setError(null), 5000);
        }
    };

    if (loading) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
                <CircularProgress />
            </Box>
        );
    }

    if (shops.length === 0) {
        return (
            <Box sx={{ maxWidth: '1200px', mx: 'auto', textAlign: 'center', py: 8 }}>
                <Typography variant="h6" color="text.secondary">
                    Aucun magasin disponible pour le moment
                </Typography>
            </Box>
        );
    }

    return (
        <Box sx={{ maxWidth: '1200px', mx: 'auto' }}>
            <Typography variant="h4" gutterBottom sx={{ fontWeight: 700, color: 'primary.main', mb: 3 }}>
                🏪 Magasins
            </Typography>

            {successMessage && (
                <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMessage('')}>
                    {successMessage}
                </Alert>
            )}

            {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                    {error}
                </Alert>
            )}

            <Paper elevation={1} sx={{ mb: 3, p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6">
                        💰 Solde: <strong>{(player?.money || 0).toLocaleString()} 💎</strong>
                    </Typography>
                </Box>
            </Paper>

            <Tabs
                value={selectedShop?.id || 0}
                onChange={(e, newValue) => {
                    const shop = shops.find(s => s.id === newValue);
                    if (shop) selectShop(shop);
                }}
                sx={{ mb: 3 }}
            >
                {shops.map((shop) => (
                    <Tab
                        key={shop.id}
                        label={`${shop.icon} ${shop.name}`}
                        value={shop.id}
                    />
                ))}
            </Tabs>

            {selectedShop && (
                <Box>
                    <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                        {selectedShop.description}
                    </Typography>

                    <Grid container spacing={2}>
                        {shopItems.map((item) => (
                            <Grid item xs={12} sm={6} md={4} key={item.id}>
                                <ShopItemCard
                                    item={item}
                                    onBuy={handleBuy}
                                    playerMoney={player?.money || 0}
                                    playerLevel={player?.level || 1}
                                />
                            </Grid>
                        ))}
                    </Grid>

                    {shopItems.length === 0 && (
                        <Box sx={{ textAlign: 'center', py: 4 }}>
                            <Typography variant="body1" color="text.secondary">
                                Aucun article disponible dans ce magasin
                            </Typography>
                        </Box>
                    )}
                </Box>
            )}
        </Box>
    );
};

export default ShopTab;
