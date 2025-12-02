import React, { useState } from 'react';
import { Box, Typography, Tabs, Tab, Paper, Grid } from '@mui/material';
import { useGameStore, selectPlayer } from '../../stores/useGameStore';
import EquipmentPanel from '../Character/EquipmentPanel';
import MetabolismPanel from '../Character/MetabolismPanel';
import AttributesPanel from '../Character/AttributesPanel';
import SurvivalGauges from '../Character/SurvivalGauges';
import {
  AccessibilityNew,
  MonitorHeart,
  Face,
  DirectionsRun
} from '@mui/icons-material';

const CharacterTab = () => {
  const player = useGameStore(selectPlayer);
  const [tabIndex, setTabIndex] = useState(0);

  if (!player) {
    return (
      <Box sx={{ maxWidth: '1200px', mx: 'auto', textAlign: 'center', py: 8 }}>
        <Typography variant="h6" color="text.secondary">Chargement des données...</Typography>
      </Box>
    );
  }

  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };

  return (
    <Box sx={{ maxWidth: '1600px', mx: 'auto', p: 2 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: '#ff9800', fontFamily: 'monospace', letterSpacing: 2 }}>
          FICHE PERSONNAGE
        </Typography>
        <Typography variant="h6" sx={{ color: '#888', fontFamily: 'monospace' }}>
          {player.user.username} | NIVEAU {player.level}
        </Typography>
      </Box>

      {/* Tabs */}
      <Paper sx={{ bgcolor: '#1a1a1a', borderRadius: 0, mb: 3, border: '1px solid #333' }}>
        <Tabs
          value={tabIndex}
          onChange={handleTabChange}
          sx={{
            '& .MuiTab-root': {
              color: '#888',
              fontFamily: 'monospace',
              fontWeight: 'bold',
              fontSize: '1rem',
              '&.Mui-selected': {
                color: '#ff9800',
              }
            },
            '& .MuiTabs-indicator': {
              backgroundColor: '#ff9800',
              height: 3
            }
          }}
        >
          <Tab icon={<AccessibilityNew />} iconPosition="start" label="APERÇU" />
          <Tab icon={<MonitorHeart />} iconPosition="start" label="MÉTABOLISME" />
          <Tab icon={<Face />} iconPosition="start" label="APPARENCE" />
        </Tabs>
      </Paper>

      {/* Content */}
      <Box sx={{ minHeight: 600 }}>
        {/* Tab 0: Aperçu (Overview) */}
        {tabIndex === 0 && (
          <Grid container spacing={3}>
            {/* Left: Attributes & Performance */}
            <Grid item xs={12} md={7}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <SurvivalGauges player={player} />
                <AttributesPanel player={player} />
              </Box>
            </Grid>

            {/* Right: Equipment & Quick Stats */}
            <Grid item xs={12} md={5}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {/* Equipment */}
                <Paper sx={{
                  bgcolor: '#1a1a1a',
                  p: 3,
                  border: '1px solid #333',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center'
                }}>
                  <Typography variant="h6" sx={{ mb: 3, fontFamily: 'monospace', color: '#ff9800', width: '100%', borderBottom: '1px solid #333', pb: 1 }}>
                    ÉQUIPEMENT
                  </Typography>

                  {/* Silhouette Placeholder */}
                  <Box sx={{
                    width: 150,
                    height: 300,
                    bgcolor: '#111',
                    mb: 3,
                    borderRadius: 4,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    border: '2px dashed #333'
                  }}>
                    <DirectionsRun sx={{ fontSize: 80, color: '#333' }} />
                  </Box>

                  <EquipmentPanel player={player} />
                </Paper>

                {/* Quick Stats (Money, XP) */}
                <Paper sx={{ bgcolor: '#1a1a1a', p: 3, border: '1px solid #333' }}>
                  <Typography variant="h6" sx={{ mb: 2, fontFamily: 'monospace', color: '#ff9800', width: '100%', borderBottom: '1px solid #333', pb: 1 }}>
                    FINANCES & PROGRESSION
                  </Typography>
                  <Box sx={{ display: 'grid', gap: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #222', pb: 1 }}>
                      <Typography sx={{ color: '#888', fontFamily: 'monospace' }}>EXPÉRIENCE</Typography>
                      <Typography sx={{ color: '#fff', fontFamily: 'monospace' }}>{player.experience} XP</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #222', pb: 1 }}>
                      <Typography sx={{ color: '#888', fontFamily: 'monospace' }}>ARGENT (LIQUIDE)</Typography>
                      <Typography sx={{ color: '#4caf50', fontFamily: 'monospace' }}>{player.money} ₡</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #222', pb: 1 }}>
                      <Typography sx={{ color: '#888', fontFamily: 'monospace' }}>BANQUE</Typography>
                      <Typography sx={{ color: '#2196f3', fontFamily: 'monospace' }}>{player.credit_card_balance || 0} ₡</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #222', pb: 1 }}>
                      <Typography sx={{ color: '#888', fontFamily: 'monospace' }}>POIDS PORTÉ</Typography>
                      <Typography sx={{ color: '#fff', fontFamily: 'monospace' }}>
                        {player.current_carry_weight?.toFixed(1) || 0} / {player.max_carry_weight} kg
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              </Box>
            </Grid>
          </Grid>
        )}

        {/* Tab 1: Métabolisme */}
        {tabIndex === 1 && (
          <MetabolismPanel />
        )}

        {/* Tab 2: Apparence (Placeholder) */}
        {tabIndex === 2 && (
          <Box sx={{ textAlign: 'center', py: 10, color: '#888' }}>
            <Face sx={{ fontSize: 60, mb: 2, opacity: 0.5 }} />
            <Typography variant="h5" sx={{ fontFamily: 'monospace' }}>
              PERSONNALISATION DE L'APPARENCE
            </Typography>
            <Typography variant="body2" sx={{ fontFamily: 'monospace', mt: 1 }}>
              Bientôt disponible...
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
};

export default CharacterTab;

