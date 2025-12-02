import React from 'react';
import { Paper, Typography, Box, LinearProgress, Chip, Grid } from '@mui/material';
import {
  Person,
  Bolt,
  Star,
  TrendingUp,
  Restaurant,
  WaterDrop,
  Science,
  FitnessCenter,
  Favorite
} from '@mui/icons-material';
import { usePlayerStats } from '../hooks';

function PlayerStats() {
  const stats = usePlayerStats();

  if (!stats) return null;

  const {
    player,
    energyPercent,
    healthPercent,
    hungerPercent,
    thirstPercent,
    radiationPercent,
    weightPercent,
    xpPercent,
    xpForNextLevel,
    energyColor,
    healthColor,
    hungerColor,
    thirstColor,
    radiationColor,
    weightColor
  } = stats;

  return (
    <Paper sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Person sx={{ mr: 1, color: 'primary.main' }} />
        <Typography variant="h6">
          {player.user?.username || 'Joueur'}
        </Typography>
        <Chip
          label={`Niveau ${player.level}`}
          color="primary"
          size="small"
          sx={{ ml: 2 }}
          icon={<Star />}
        />
      </Box>

      <Grid container spacing={2}>
        {/* Energy */}
        <Grid item xs={12} sm={6} md={4}>
          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Bolt sx={{ fontSize: 18, mr: 0.5, color: 'warning.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Énergie
                </Typography>
              </Box>
              <Typography variant="body2" fontWeight="bold">
                {player.energy} / {player.max_energy}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={energyPercent}
              sx={{
                height: 8,
                borderRadius: 1,
                backgroundColor: 'rgba(255, 152, 0, 0.2)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: energyColor,
                }
              }}
            />
          </Box>
        </Grid>

        {/* Health */}
        <Grid item xs={12} sm={6} md={4}>
          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Favorite sx={{ fontSize: 18, mr: 0.5, color: 'error.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Santé
                </Typography>
              </Box>
              <Typography variant="body2" fontWeight="bold">
                {player.health} / {player.max_health}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={healthPercent}
              sx={{
                height: 8,
                borderRadius: 1,
                backgroundColor: 'rgba(244, 67, 54, 0.2)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: healthColor,
                }
              }}
            />
          </Box>
        </Grid>

        {/* Experience */}
        <Grid item xs={12} sm={6} md={4}>
          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <TrendingUp sx={{ fontSize: 18, mr: 0.5, color: 'success.main' }} />
                <Typography variant="body2" color="text.secondary">
                  Expérience
                </Typography>
              </Box>
              <Typography variant="body2" fontWeight="bold">
                {player.experience} / {xpForNextLevel}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={xpPercent}
              sx={{
                height: 8,
                borderRadius: 1,
                backgroundColor: 'rgba(76, 175, 80, 0.2)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: 'success.main',
                }
              }}
            />
          </Box>
        </Grid>

        {/* Hunger */}
        <Grid item xs={12} sm={6} md={4}>
          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Restaurant sx={{ fontSize: 18, mr: 0.5, color: '#FF9800' }} />
                <Typography variant="body2" color="text.secondary">
                  Faim
                </Typography>
              </Box>
              <Typography variant="body2" fontWeight="bold">
                {player.hunger} / {player.max_hunger}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={hungerPercent}
              sx={{
                height: 8,
                borderRadius: 1,
                backgroundColor: 'rgba(255, 152, 0, 0.2)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: hungerColor,
                }
              }}
            />
          </Box>
        </Grid>

        {/* Thirst */}
        <Grid item xs={12} sm={6} md={4}>
          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <WaterDrop sx={{ fontSize: 18, mr: 0.5, color: '#2196F3' }} />
                <Typography variant="body2" color="text.secondary">
                  Soif
                </Typography>
              </Box>
              <Typography variant="body2" fontWeight="bold">
                {player.thirst} / {player.max_thirst}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={thirstPercent}
              sx={{
                height: 8,
                borderRadius: 1,
                backgroundColor: 'rgba(33, 150, 243, 0.2)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: thirstColor,
                }
              }}
            />
          </Box>
        </Grid>

        {/* Radiation */}
        <Grid item xs={12} sm={6} md={4}>
          <Box sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Science sx={{ fontSize: 18, mr: 0.5, color: '#9C27B0' }} />
                <Typography variant="body2" color="text.secondary">
                  Radiation
                </Typography>
              </Box>
              <Typography variant="body2" fontWeight="bold">
                {player.radiation} / 100
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={radiationPercent}
              sx={{
                height: 8,
                borderRadius: 1,
                backgroundColor: 'rgba(156, 39, 176, 0.2)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: radiationColor,
                }
              }}
            />
          </Box>
        </Grid>
      </Grid>

      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 2 }}>
        <Chip
          label={`Position: (${player.grid_x}, ${player.grid_y})`}
          size="small"
          variant="outlined"
        />
        <Chip
          icon={<FitnessCenter sx={{ fontSize: 16 }} />}
          label={`Poids: ${player.current_carry_weight?.toFixed(1) || 0}kg / ${player.effective_carry_capacity?.toFixed(1) || 50}kg`}
          size="small"
          variant="outlined"
          color={weightColor}
        />
      </Box>

      {/* Survival Warnings */}
      {player.survival_warnings && player.survival_warnings.length > 0 && (
        <Box sx={{ mt: 2 }}>
          {player.survival_warnings.map((warning, idx) => (
            <Typography
              key={idx}
              variant="caption"
              color={warning.type === 'critical' ? 'error' : 'warning.main'}
              sx={{ display: 'block' }}
            >
              {warning.message}
            </Typography>
          ))}
        </Box>
      )}
    </Paper>
  );
}

export default PlayerStats;
