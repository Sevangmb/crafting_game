import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Grid,
  Alert,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  SwapHoriz as TradeIcon,
  Send as SentIcon,
  Inbox as ReceivedIcon,
  History as HistoryIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { tradingAPI } from '../../services/api';
import { useInventory } from '../../hooks';
import CreateTradeDialog from '../trading/CreateTradeDialog';

const TradingTab = () => {
  const { flatInventory } = useInventory();
  const [currentTab, setCurrentTab] = useState(0);
  const [receivedTrades, setReceivedTrades] = useState([]);
  const [sentTrades, setSentTrades] = useState([]);
  const [tradeHistory, setTradeHistory] = useState([]);
  const [tradeStats, setTradeStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [selectedTrade, setSelectedTrade] = useState(null);

  useEffect(() => {
    loadTrades();
    loadTradeStats();
  }, [currentTab]);

  const loadTrades = async () => {
    setLoading(true);
    setError('');
    try {
      if (currentTab === 0) {
        const response = await tradingAPI.getReceived();
        setReceivedTrades(response.data);
      } else if (currentTab === 1) {
        const response = await tradingAPI.getSent();
        setSentTrades(response.data);
      } else if (currentTab === 2) {
        const response = await tradingAPI.getHistory();
        setTradeHistory(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du chargement des échanges');
    } finally {
      setLoading(false);
    }
  };

  const loadTradeStats = async () => {
    try {
      const response = await tradingAPI.getStats();
      setTradeStats(response.data);
    } catch (err) {
      console.error('Erreur chargement stats:', err);
    }
  };

  const handleAcceptTrade = async (tradeId) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await tradingAPI.accept(tradeId);
      setSuccess(response.data.message || 'Échange accepté avec succès!');
      setSelectedTrade(null);
      loadTrades();
      loadTradeStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de l\'acceptation');
    } finally {
      setLoading(false);
    }
  };

  const handleRejectTrade = async (tradeId) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await tradingAPI.reject(tradeId);
      setSuccess(response.data.message || 'Échange refusé');
      setSelectedTrade(null);
      loadTrades();
      loadTradeStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du refus');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelTrade = async (tradeId) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await tradingAPI.cancel(tradeId);
      setSuccess(response.data.message || 'Échange annulé');
      setSelectedTrade(null);
      loadTrades();
      loadTradeStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de l\'annulation');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTrade = async (tradeData) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const response = await tradingAPI.createOffer(
        parseInt(tradeData.toPlayerId),
        tradeData.offeredItems,
        parseInt(tradeData.offeredMoney) || 0,
        tradeData.requestedItems,
        parseInt(tradeData.requestedMoney) || 0,
        tradeData.message,
        tradeData.durationHours
      );
      setSuccess(response.data.message || 'Offre créée avec succès!');
      setCreateDialogOpen(false);
      loadTrades();
      loadTradeStats();
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erreur lors de la création';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'accepted':
      case 'completed': return 'success';
      case 'rejected':
      case 'cancelled': return 'error';
      case 'expired': return 'default';
      default: return 'default';
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      pending: 'En attente',
      accepted: 'Accepté',
      completed: 'Complété',
      rejected: 'Refusé',
      cancelled: 'Annulé',
      expired: 'Expiré',
    };
    return labels[status] || status;
  };

  const renderTradeCard = (trade, showActions = false, isSent = false) => {
    return (
      <Grid item xs={12} key={trade.id}>
        <Card>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6">
                {isSent ? `Vers: ${trade.to_player_name}` : `De: ${trade.from_player_name}`}
              </Typography>
              <Chip
                label={getStatusLabel(trade.status)}
                color={getStatusColor(trade.status)}
                size="small"
              />
            </Box>

            <Grid container spacing={2}>
              <Grid item xs={12} md={5}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle2" gutterBottom color="primary">
                    Offert
                  </Typography>
                  {trade.offered_items_details && trade.offered_items_details.length > 0 ? (
                    <List dense>
                      {trade.offered_items_details.map((item, idx) => (
                        <ListItem key={idx}>
                          <ListItemText
                            primary={`${item.icon} ${item.name}`}
                            secondary={`Quantité: ${item.quantity}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Aucun item
                    </Typography>
                  )}
                  {trade.offered_money > 0 && (
                    <Chip label={`${trade.offered_money} 💰`} color="success" size="small" />
                  )}
                </Paper>
              </Grid>

              <Grid item xs={12} md={2} display="flex" alignItems="center" justifyContent="center">
                <TradeIcon fontSize="large" color="action" />
              </Grid>

              <Grid item xs={12} md={5}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle2" gutterBottom color="secondary">
                    Demandé
                  </Typography>
                  {trade.requested_items_details && trade.requested_items_details.length > 0 ? (
                    <List dense>
                      {trade.requested_items_details.map((item, idx) => (
                        <ListItem key={idx}>
                          <ListItemText
                            primary={`${item.icon} ${item.name}`}
                            secondary={`Quantité: ${item.quantity}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Aucun item
                    </Typography>
                  )}
                  {trade.requested_money > 0 && (
                    <Chip label={`${trade.requested_money} 💰`} color="warning" size="small" />
                  )}
                </Paper>
              </Grid>
            </Grid>

            {trade.message && (
              <Box mt={2}>
                <Typography variant="body2" color="text.secondary">
                  Message: "{trade.message}"
                </Typography>
              </Box>
            )}

            <Box mt={2} display="flex" gap={1}>
              <Typography variant="caption" color="text.secondary">
                Créé: {new Date(trade.created_at).toLocaleString()}
              </Typography>
              {trade.expires_at && (
                <Typography variant="caption" color="text.secondary">
                  | Expire: {new Date(trade.expires_at).toLocaleString()}
                </Typography>
              )}
            </Box>
          </CardContent>

          {showActions && trade.status === 'pending' && (
            <CardActions>
              {!isSent && (
                <>
                  <Button
                    variant="contained"
                    color="success"
                    onClick={() => handleAcceptTrade(trade.id)}
                    disabled={loading}
                  >
                    Accepter
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => handleRejectTrade(trade.id)}
                    disabled={loading}
                  >
                    Refuser
                  </Button>
                </>
              )}
              {isSent && (
                <Button
                  variant="outlined"
                  color="error"
                  onClick={() => handleCancelTrade(trade.id)}
                  disabled={loading}
                >
                  Annuler
                </Button>
              )}
              <Button
                variant="text"
                onClick={() => setSelectedTrade(trade)}
              >
                Détails
              </Button>
            </CardActions>
          )}
        </Card>
      </Grid>
    );
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Stats Header */}
      {tradeStats && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={2}>
              <Typography variant="h6" color="warning.main">{tradeStats.pending_received}</Typography>
              <Typography variant="caption">Reçus en attente</Typography>
            </Grid>
            <Grid item xs={2}>
              <Typography variant="h6" color="info.main">{tradeStats.pending_sent}</Typography>
              <Typography variant="caption">Envoyés en attente</Typography>
            </Grid>
            <Grid item xs={2}>
              <Typography variant="h6" color="success.main">{tradeStats.total_completed}</Typography>
              <Typography variant="caption">Complétés</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="h6" color="primary">{tradeStats.total_sent}</Typography>
              <Typography variant="caption">Total envoyés</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="h6" color="secondary.main">{tradeStats.total_received}</Typography>
              <Typography variant="caption">Total reçus</Typography>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* Alerts */}
      {error && (
        <Alert severity="error" onClose={() => setError('')} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess('')} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* Action Buttons */}
      <Box mb={2} display="flex" justifyContent="flex-end">
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Créer une offre
        </Button>
      </Box>

      {/* Tabs */}
      <Paper sx={{ mb: 2 }}>
        <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)} centered>
          <Tab label="Reçus" icon={<ReceivedIcon />} iconPosition="start" />
          <Tab label="Envoyés" icon={<SentIcon />} iconPosition="start" />
          <Tab label="Historique" icon={<HistoryIcon />} iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Trade List */}
      <Grid container spacing={2}>
        {currentTab === 0 && receivedTrades.map(trade => renderTradeCard(trade, true, false))}
        {currentTab === 1 && sentTrades.map(trade => renderTradeCard(trade, true, true))}
        {currentTab === 2 && tradeHistory.map(trade => renderTradeCard(trade, false, false))}
      </Grid>

      {/* Empty states */}
      {currentTab === 0 && receivedTrades.length === 0 && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            Aucune offre reçue
          </Typography>
        </Paper>
      )}
      {currentTab === 1 && sentTrades.length === 0 && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            Aucune offre envoyée
          </Typography>
        </Paper>
      )}

      {/* Create Trade Dialog - New Improved Version */}
      <CreateTradeDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        inventory={flatInventory}
        onSubmit={handleCreateTrade}
        loading={loading}
      />
    </Box>
  );
};

export default TradingTab;
