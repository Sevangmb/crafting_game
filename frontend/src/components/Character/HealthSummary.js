import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Chip,
  Grid,
  Divider,
  Alert,
  IconButton,
  Collapse,
} from '@mui/material';
import {
  ExpandMore,
  ExpandLess,
  Favorite,
  Warning,
  CheckCircle,
} from '@mui/icons-material';
import axios from 'axios';

const HealthSummary = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    loadHealthData();
    const interval = setInterval(loadHealthData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadHealthData = async () => {
    console.log('[HealthSummary] Loading health data...');
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/character/health-display/', {
        headers: { Authorization: `Token ${token}` }
      });
      console.log('[HealthSummary] Health data loaded successfully:', response.data);
      setHealthData(response.data);
      setLoading(false);
    } catch (err) {
      console.error('[HealthSummary] Error loading health data:', err);
      // Don't show anything if the API fails - silently fail
      setLoading(false);
      setHealthData(null);
    }
  };

  if (loading) {
    return (
      <Paper elevation={1} sx={{ p: 2.5, mb: 2 }}>
        <Typography variant="body2" color="text.secondary" align="center">
          Chargement des données de santé...
        </Typography>
      </Paper>
    );
  }

  if (!healthData) {
    return (
      <Paper elevation={1} sx={{ p: 2.5, mb: 2 }}>
        <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
          ❤️ Santé SCUM
        </Typography>
        <Alert severity="info">
          <Typography variant="body2">
            Le système de santé détaillé sera disponible après votre prochaine action dans le jeu.
          </Typography>
        </Alert>
      </Paper>
    );
  }

  const getColorByName = (colorName) => {
    const colors = {
      green: '#4caf50',
      yellow: '#ffeb3b',
      orange: '#ff9800',
      red: '#f44336',
    };
    return colors[colorName] || '#9e9e9e';
  };

  const healthPercentage = healthData.overall_health_percentage || 0;
  const healthColor = healthPercentage >= 80 ? 'green' :
                      healthPercentage >= 50 ? 'yellow' :
                      healthPercentage >= 30 ? 'orange' : 'red';

  const criticalAlerts = healthData.alerts?.filter(a => a.severity === 'critical' || a.severity === 'emergency') || [];
  const hasInjuries = healthData.bleeding_parts_count > 0 || healthData.fractured_parts_count > 0 || healthData.infected_parts_count > 0;

  return (
    <Paper elevation={1} sx={{ p: 2.5, mb: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          ❤️ Santé SCUM
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <Chip
            label={`${healthPercentage.toFixed(0)}%`}
            size="medium"
            sx={{
              bgcolor: getColorByName(healthColor),
              color: 'white',
              fontWeight: 'bold',
            }}
          />
          <IconButton
            size="small"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>
      </Box>

      {/* Critical Alerts */}
      {criticalAlerts.length > 0 && (
        <Box mb={2}>
          {criticalAlerts.map((alert, index) => (
            <Alert key={index} severity="error" sx={{ mb: 1, py: 0.5 }}>
              <Typography variant="body2" fontWeight={500}>
                {alert.icon} {alert.message}
              </Typography>
            </Alert>
          ))}
        </Box>
      )}

      {/* Quick Status */}
      <Grid container spacing={1.5} mb={2}>
        <Grid item xs={6}>
          <Box p={1} borderRadius={1} bgcolor="grey.100">
            <Typography variant="caption" color="text.secondary">🌡️ Temp.</Typography>
            <Typography variant="body2" fontWeight={600}>
              {healthData.vital_signs?.body_temperature?.toFixed(1) || 37.0}°C
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6}>
          <Box p={1} borderRadius={1} bgcolor="grey.100">
            <Typography variant="caption" color="text.secondary">💓 Pouls</Typography>
            <Typography variant="body2" fontWeight={600}>
              {healthData.vital_signs?.heart_rate || 75} BPM
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6}>
          <Box p={1} borderRadius={1} bgcolor="grey.100">
            <Typography variant="caption" color="text.secondary">🔥 Calories</Typography>
            <Typography variant="body2" fontWeight={600}>
              {healthData.metabolism?.calories?.current?.toFixed(0) || 2000} kcal
            </Typography>
          </Box>
        </Grid>
        <Grid item xs={6}>
          <Box p={1} borderRadius={1} bgcolor="grey.100">
            <Typography variant="caption" color="text.secondary">💧 Eau</Typography>
            <Typography variant="body2" fontWeight={600}>
              {healthData.metabolism?.water?.percentage?.toFixed(0) || 100}%
            </Typography>
          </Box>
        </Grid>
      </Grid>

      {/* Injury Summary */}
      {hasInjuries && (
        <Box mb={2}>
          <Typography variant="body2" fontWeight={500} mb={1}>
            ⚠️ Blessures actives:
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {healthData.bleeding_parts_count > 0 && (
              <Chip
                label={`🩸 ${healthData.bleeding_parts_count} Saignement(s)`}
                size="small"
                color="error"
              />
            )}
            {healthData.fractured_parts_count > 0 && (
              <Chip
                label={`🦴 ${healthData.fractured_parts_count} Fracture(s)`}
                size="small"
                color="warning"
              />
            )}
            {healthData.infected_parts_count > 0 && (
              <Chip
                label={`🦠 ${healthData.infected_parts_count} Infection(s)`}
                size="small"
                color="error"
              />
            )}
          </Box>
        </Box>
      )}

      {/* Expandable Details */}
      <Collapse in={expanded}>
        <Divider sx={{ my: 2 }} />

        {/* Body Composition */}
        <Typography variant="body2" fontWeight={500} mb={1}>
          🏋️ Composition Corporelle
        </Typography>
        <Grid container spacing={1} mb={2}>
          <Grid item xs={4}>
            <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.50">
              <Typography variant="caption" color="text.secondary">Poids</Typography>
              <Typography variant="body2" fontWeight={600}>
                {healthData.metabolism?.body_weight?.current?.toFixed(1) || 70}kg
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.50">
              <Typography variant="caption" color="text.secondary">Muscle</Typography>
              <Typography variant="body2" fontWeight={600}>
                {healthData.metabolism?.muscle_mass?.current?.toFixed(1) || 30}kg
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.50">
              <Typography variant="caption" color="text.secondary">Graisse</Typography>
              <Typography variant="body2" fontWeight={600}>
                {healthData.metabolism?.body_fat?.current?.toFixed(1) || 15}kg
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Macronutrients */}
        <Typography variant="body2" fontWeight={500} mb={1}>
          🍖 Macronutriments
        </Typography>
        <Box mb={1}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.3}>
            <Typography variant="caption">Protéines</Typography>
            <Typography variant="caption">
              {healthData.metabolism?.proteins?.current?.toFixed(0) || 0}g
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={healthData.metabolism?.proteins?.percentage || 0}
            sx={{
              height: 6,
              borderRadius: 0.5,
              '& .MuiLinearProgress-bar': {
                bgcolor: getColorByName(healthData.metabolism?.proteins?.color || 'green'),
              }
            }}
          />
        </Box>
        <Box mb={1}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.3}>
            <Typography variant="caption">Glucides</Typography>
            <Typography variant="caption">
              {healthData.metabolism?.carbohydrates?.current?.toFixed(0) || 0}g
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={healthData.metabolism?.carbohydrates?.percentage || 0}
            sx={{
              height: 6,
              borderRadius: 0.5,
              '& .MuiLinearProgress-bar': {
                bgcolor: getColorByName(healthData.metabolism?.carbohydrates?.color || 'green'),
              }
            }}
          />
        </Box>
        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.3}>
            <Typography variant="caption">Lipides</Typography>
            <Typography variant="caption">
              {healthData.metabolism?.fats?.current?.toFixed(0) || 0}g
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={healthData.metabolism?.fats?.percentage || 0}
            sx={{
              height: 6,
              borderRadius: 0.5,
              '& .MuiLinearProgress-bar': {
                bgcolor: getColorByName(healthData.metabolism?.fats?.color || 'green'),
              }
            }}
          />
        </Box>

        {/* Performance Modifiers */}
        <Typography variant="body2" fontWeight={500} mb={1}>
          ⚡ Modificateurs
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          <Chip
            label={`🔋 Énergie x${healthData.energy_regen_modifier?.toFixed(2) || 1.0}`}
            size="small"
            color={healthData.energy_regen_modifier >= 1 ? 'success' : 'error'}
          />
          <Chip
            label={`💪 Force x${healthData.strength_modifier?.toFixed(2) || 1.0}`}
            size="small"
            color={healthData.strength_modifier >= 1 ? 'success' : 'error'}
          />
          <Chip
            label={`⚡ Endurance x${healthData.stamina_modifier?.toFixed(2) || 1.0}`}
            size="small"
            color={healthData.stamina_modifier >= 1 ? 'success' : 'error'}
          />
        </Box>

        {/* Recommendations */}
        {healthData.recommendations && healthData.recommendations.length > 0 && (
          <Box mt={2}>
            <Typography variant="body2" fontWeight={500} mb={1}>
              💡 Recommandations
            </Typography>
            {healthData.recommendations.slice(0, 3).map((rec, index) => (
              <Alert key={index} severity="info" sx={{ mb: 0.5, py: 0.3 }}>
                <Typography variant="caption">{rec}</Typography>
              </Alert>
            ))}
          </Box>
        )}
      </Collapse>
    </Paper>
  );
};

export default HealthSummary;
