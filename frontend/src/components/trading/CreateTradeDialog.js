import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  TextField,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Paper,
  Grid,
  Chip,
  Alert,
} from '@mui/material';
import {
  SwapHoriz as TradeIcon,
  Person as PersonIcon,
  Inventory as InventoryIcon,
  Message as MessageIcon,
} from '@mui/icons-material';
import ItemSelector from './ItemSelector';

const CreateTradeDialog = ({ open, onClose, inventory, onSubmit, loading }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [tradeData, setTradeData] = useState({
    toPlayerId: '',
    offeredItems: [],
    offeredMoney: 0,
    requestedItems: [],
    requestedMoney: 0,
    message: '',
    durationHours: 24,
  });
  const [error, setError] = useState('');

  const steps = [
    'Destinataire',
    'Vous offrez',
    'Vous demandez',
    'Confirmation'
  ];

  const handleNext = () => {
    // Validation
    if (activeStep === 0 && !tradeData.toPlayerId) {
      setError('Veuillez entrer l\'ID du joueur');
      return;
    }
    if (activeStep === 1 && tradeData.offeredItems.length === 0 && tradeData.offeredMoney === 0) {
      setError('Vous devez offrir au moins quelque chose');
      return;
    }
    if (activeStep === 2 && tradeData.requestedItems.length === 0 && tradeData.requestedMoney === 0) {
      setError('Vous devez demander au moins quelque chose');
      return;
    }

    setError('');
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setError('');
    setActiveStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    try {
      await onSubmit(tradeData);
      handleClose();
    } catch (err) {
      setError(err.message || 'Erreur lors de la création');
    }
  };

  const handleClose = () => {
    setActiveStep(0);
    setTradeData({
      toPlayerId: '',
      offeredItems: [],
      offeredMoney: 0,
      requestedItems: [],
      requestedMoney: 0,
      message: '',
      durationHours: 24,
    });
    setError('');
    onClose();
  };

  const getItemDetails = (items) => {
    return items.map(item => {
      const inventoryItem = inventory.find(inv => inv.material?.id === item.material_id);
      return {
        ...item,
        name: inventoryItem?.material?.name || 'Item',
        icon: inventoryItem?.material?.icon || '📦',
      };
    });
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Avec qui voulez-vous échanger?
            </Typography>
            <TextField
              fullWidth
              label="ID du joueur"
              type="number"
              value={tradeData.toPlayerId}
              onChange={(e) => setTradeData({ ...tradeData, toPlayerId: e.target.value })}
              placeholder="Ex: 2"
              helperText="Entrez l'ID du joueur avec qui vous voulez échanger"
              sx={{ mt: 2 }}
            />
          </Box>
        );

      case 1:
        return (
          <Box>
            <ItemSelector
              inventory={inventory}
              selectedItems={tradeData.offeredItems}
              onItemsChange={(items) => setTradeData({ ...tradeData, offeredItems: items })}
              title="Items que vous offrez"
            />

            <Box mt={3}>
              <TextField
                fullWidth
                label="Argent offert"
                type="number"
                value={tradeData.offeredMoney}
                onChange={(e) => setTradeData({ ...tradeData, offeredMoney: parseInt(e.target.value) || 0 })}
                InputProps={{
                  startAdornment: <Typography sx={{ mr: 1 }}>💰</Typography>,
                }}
                helperText="Montant d'argent à offrir (optionnel)"
              />
            </Box>
          </Box>
        );

      case 2:
        return (
          <Box>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>Note:</strong> Les items demandés doivent être dans l'inventaire du destinataire.
                Cette fonctionnalité sera améliorée pour permettre la sélection depuis leur inventaire.
              </Typography>
            </Alert>

            <TextField
              fullWidth
              label="Argent demandé"
              type="number"
              value={tradeData.requestedMoney}
              onChange={(e) => setTradeData({ ...tradeData, requestedMoney: parseInt(e.target.value) || 0 })}
              InputProps={{
                startAdornment: <Typography sx={{ mr: 1 }}>💰</Typography>,
              }}
              helperText="Montant d'argent à recevoir"
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Message (optionnel)"
              multiline
              rows={3}
              value={tradeData.message}
              onChange={(e) => setTradeData({ ...tradeData, message: e.target.value })}
              placeholder="Ajoutez un message pour expliquer l'échange..."
              helperText="Un message personnel peut faciliter l'échange"
            />
          </Box>
        );

      case 3:
        const offeredDetails = getItemDetails(tradeData.offeredItems);
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Résumé de votre offre
            </Typography>

            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={5}>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'success.50' }}>
                  <Typography variant="subtitle2" color="success.main" gutterBottom>
                    ✓ Vous offrez
                  </Typography>
                  {offeredDetails.length > 0 && (
                    <Box mb={1}>
                      {offeredDetails.map((item, idx) => (
                        <Chip
                          key={idx}
                          label={`${item.icon} ${item.name} (${item.quantity})`}
                          size="small"
                          sx={{ mr: 0.5, mb: 0.5 }}
                        />
                      ))}
                    </Box>
                  )}
                  {tradeData.offeredMoney > 0 && (
                    <Chip
                      label={`💰 ${tradeData.offeredMoney}`}
                      color="success"
                      size="small"
                    />
                  )}
                  {offeredDetails.length === 0 && tradeData.offeredMoney === 0 && (
                    <Typography variant="body2" color="text.secondary">
                      Rien
                    </Typography>
                  )}
                </Paper>
              </Grid>

              <Grid item xs={12} md={2} display="flex" alignItems="center" justifyContent="center">
                <TradeIcon fontSize="large" color="primary" />
              </Grid>

              <Grid item xs={12} md={5}>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'warning.50' }}>
                  <Typography variant="subtitle2" color="warning.main" gutterBottom>
                    ← Vous demandez
                  </Typography>
                  {tradeData.requestedMoney > 0 && (
                    <Chip
                      label={`💰 ${tradeData.requestedMoney}`}
                      color="warning"
                      size="small"
                    />
                  )}
                  {tradeData.requestedMoney === 0 && (
                    <Typography variant="body2" color="text.secondary">
                      Rien
                    </Typography>
                  )}
                </Paper>
              </Grid>
            </Grid>

            {tradeData.message && (
              <Box mt={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Message:
                </Typography>
                <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'background.default' }}>
                  <Typography variant="body2" fontStyle="italic">
                    "{tradeData.message}"
                  </Typography>
                </Paper>
              </Box>
            )}

            <Alert severity="info" sx={{ mt: 2 }}>
              L'offre expirera dans {tradeData.durationHours} heures
            </Alert>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <TradeIcon />
          Créer une offre d'échange
        </Box>
      </DialogTitle>

      <DialogContent>
        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {steps.map((label, index) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" onClose={() => setError('')} sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ minHeight: 400 }}>
          {renderStepContent(activeStep)}
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={handleClose} disabled={loading}>
          Annuler
        </Button>
        <Box flex={1} />
        <Button
          onClick={handleBack}
          disabled={activeStep === 0 || loading}
        >
          Retour
        </Button>
        {activeStep < steps.length - 1 ? (
          <Button
            variant="contained"
            onClick={handleNext}
            disabled={loading}
          >
            Suivant
          </Button>
        ) : (
          <Button
            variant="contained"
            onClick={handleSubmit}
            disabled={loading}
            color="success"
          >
            Créer l'offre
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default CreateTradeDialog;
