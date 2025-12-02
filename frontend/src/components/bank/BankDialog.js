import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  TextField,
  Box,
  Alert,
  Tabs,
  Tab,
  Grid,
  Paper,
  Divider,
} from '@mui/material';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import MoneyIcon from '@mui/icons-material/Money';
import { bankAPI } from '../../services/api';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} style={{ paddingTop: 16 }}>
      {value === index && children}
    </div>
  );
}

export default function BankDialog({ open, onClose, onTransactionComplete, player }) {
  const [banks, setBanks] = useState([]);
  const [selectedBank, setSelectedBank] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [depositAmount, setDepositAmount] = useState('');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      loadBanks();
      setError('');
      setSuccess('');
      setDepositAmount('');
      setWithdrawAmount('');
    }
  }, [open]);

  const loadBanks = async () => {
    try {
      const response = await bankAPI.getCurrentBanks();
      setBanks(response.data.banks || []);
      if (response.data.banks && response.data.banks.length > 0) {
        setSelectedBank(response.data.banks[0]);
      }
    } catch (err) {
      setError('Erreur lors du chargement des banques');
      console.error(err);
    }
  };

  const handleDeposit = async () => {
    setError('');
    setSuccess('');

    const amount = parseInt(depositAmount);
    if (isNaN(amount) || amount <= 0) {
      setError('Montant invalide');
      return;
    }

    if (amount > player.money) {
      setError('Argent liquide insuffisant');
      return;
    }

    setLoading(true);
    try {
      const response = await bankAPI.deposit(selectedBank.id, amount);
      setSuccess(response.data.message);
      setDepositAmount('');
      if (onTransactionComplete) {
        onTransactionComplete();
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du dépôt');
    } finally {
      setLoading(false);
    }
  };

  const handleWithdraw = async () => {
    setError('');
    setSuccess('');

    const amount = parseInt(withdrawAmount);
    if (isNaN(amount) || amount <= 0) {
      setError('Montant invalide');
      return;
    }

    if (amount > player.credit_card_balance) {
      setError('Solde de carte insuffisant');
      return;
    }

    setLoading(true);
    try {
      const response = await bankAPI.withdraw(selectedBank.id, amount);
      setSuccess(response.data.message);
      setWithdrawAmount('');
      if (onTransactionComplete) {
        onTransactionComplete();
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du retrait');
    } finally {
      setLoading(false);
    }
  };

  if (!selectedBank) {
    return (
      <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <AccountBalanceIcon sx={{ mr: 1 }} />
            Banque
          </Box>
        </DialogTitle>
        <DialogContent>
          <Alert severity="info">Aucune banque disponible à cet emplacement</Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Fermer</Button>
        </DialogActions>
      </Dialog>
    );
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center">
          <AccountBalanceIcon sx={{ mr: 1 }} />
          {selectedBank.icon} {selectedBank.name}
        </Box>
        <Typography variant="body2" color="text.secondary">
          {selectedBank.description}
        </Typography>
      </DialogTitle>

      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={6}>
            <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
              <Box display="flex" alignItems="center" justifyContent="center" mb={1}>
                <MoneyIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Liquide</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {player.money}₡
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={6}>
            <Paper elevation={2} sx={{ p: 2, textAlign: 'center' }}>
              <Box display="flex" alignItems="center" justifyContent="center" mb={1}>
                <CreditCardIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Carte</Typography>
              </Box>
              <Typography variant="h4" color="secondary">
                {player.credit_card_balance}₡
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        <Divider sx={{ mb: 2 }} />

        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 2 }}>
          <Tab label="Dépôt" />
          <Tab label="Retrait" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Déposez votre argent liquide sur votre carte de crédit.
            {selectedBank.deposit_fee_percent > 0 && (
              <strong> Frais: {selectedBank.deposit_fee_percent}%</strong>
            )}
          </Typography>
          <Box display="flex" alignItems="center" gap={2}>
            <TextField
              label="Montant à déposer"
              type="number"
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              fullWidth
              disabled={loading}
              inputProps={{ min: 1, max: player.money }}
            />
            <Button
              variant="contained"
              onClick={handleDeposit}
              disabled={loading || !depositAmount}
              sx={{ minWidth: 120 }}
            >
              Déposer
            </Button>
          </Box>
          <Box display="flex" gap={1} mt={1}>
            <Button size="small" onClick={() => setDepositAmount(Math.floor(player.money * 0.25))}>25%</Button>
            <Button size="small" onClick={() => setDepositAmount(Math.floor(player.money * 0.5))}>50%</Button>
            <Button size="small" onClick={() => setDepositAmount(Math.floor(player.money * 0.75))}>75%</Button>
            <Button size="small" onClick={() => setDepositAmount(player.money)}>Tout</Button>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Retirez de l'argent de votre carte de crédit.
            {selectedBank.withdrawal_fee_percent > 0 && (
              <strong> Frais: {selectedBank.withdrawal_fee_percent}%</strong>
            )}
          </Typography>
          <Box display="flex" alignItems="center" gap={2}>
            <TextField
              label="Montant à retirer"
              type="number"
              value={withdrawAmount}
              onChange={(e) => setWithdrawAmount(e.target.value)}
              fullWidth
              disabled={loading}
              inputProps={{ min: 1, max: player.credit_card_balance }}
            />
            <Button
              variant="contained"
              onClick={handleWithdraw}
              disabled={loading || !withdrawAmount}
              sx={{ minWidth: 120 }}
            >
              Retirer
            </Button>
          </Box>
          <Box display="flex" gap={1} mt={1}>
            <Button size="small" onClick={() => setWithdrawAmount(Math.floor(player.credit_card_balance * 0.25))}>25%</Button>
            <Button size="small" onClick={() => setWithdrawAmount(Math.floor(player.credit_card_balance * 0.5))}>50%</Button>
            <Button size="small" onClick={() => setWithdrawAmount(Math.floor(player.credit_card_balance * 0.75))}>75%</Button>
            <Button size="small" onClick={() => setWithdrawAmount(player.credit_card_balance)}>Tout</Button>
          </Box>
        </TabPanel>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Fermer</Button>
      </DialogActions>
    </Dialog>
  );
}
