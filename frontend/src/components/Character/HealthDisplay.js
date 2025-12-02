import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  LinearProgress,
  Chip,
  Divider,
  Tooltip,
  Alert,
  Card,
  CardContent,
} from '@mui/material';
import {
  Favorite,
  Warning,
  CheckCircle,
  Error,
  LocalHospital,
  Restaurant,
  Opacity,
  FitnessCenter,
} from '@mui/icons-material';
import axios from 'axios';

const HealthDisplay = ({ playerId }) => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadHealthData();
    // Refresh every 30 seconds
    const interval = setInterval(loadHealthData, 30000);
    return () => clearInterval(interval);
  }, [playerId]);

  const loadHealthData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/character/health-display/', {
        headers: { Authorization: `Token ${token}` }
      });
      setHealthData(response.data);
      setError(null);
    } catch (err) {
      console.error('Error loading health data:', err);
      setError('Erreur lors du chargement des données de santé');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" p={4}>
        <Typography>Chargement des données de santé...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!healthData) {
    return null;
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

  const getSeverityColor = (severity) => {
    const colors = {
      emergency: 'error',
      critical: 'error',
      warning: 'warning',
      info: 'info',
    };
    return colors[severity] || 'default';
  };

  const renderNutritionBar = (bar) => {
    const percentage = bar.percentage || 0;
    const color = getColorByName(bar.color);

    return (
      <Box mb={2} key={bar.name}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
          <Box display="flex" alignItems="center" gap={0.5}>
            <Typography variant="body2" fontWeight={500}>
              {bar.icon} {bar.name}
            </Typography>
            {bar.warning_level !== 'none' && (
              <Warning fontSize="small" color={bar.warning_level === 'critical' ? 'error' : 'warning'} />
            )}
          </Box>
          <Typography variant="body2" color="text.secondary">
            {bar.current.toFixed(1)}{bar.unit} / {bar.max.toFixed(1)}{bar.unit}
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={Math.min(100, percentage)}
          sx={{
            height: 10,
            borderRadius: 1,
            bgcolor: 'rgba(0,0,0,0.1)',
            '& .MuiLinearProgress-bar': {
              bgcolor: color,
            }
          }}
        />
      </Box>
    );
  };

  const renderVitaminMineral = (item) => {
    const color = getColorByName(item.color);
    return (
      <Box key={item.name} mb={1}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.3}>
          <Typography variant="caption">{item.name}</Typography>
          <Chip
            label={`${item.level.toFixed(0)}%`}
            size="small"
            sx={{
              bgcolor: color,
              color: 'white',
              height: 20,
              fontSize: '0.7rem',
            }}
          />
        </Box>
        <LinearProgress
          variant="determinate"
          value={Math.min(100, item.level)}
          sx={{
            height: 4,
            borderRadius: 0.5,
            '& .MuiLinearProgress-bar': {
              bgcolor: color,
            }
          }}
        />
      </Box>
    );
  };

  return (
    <Box>
      {/* Overall Health Status */}
      <Paper elevation={2} sx={{ p: 2, mb: 2, bgcolor: healthData.is_critical ? '#ffebee' : 'background.paper' }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            <Favorite sx={{ fontSize: 40, color: healthData.is_critical ? '#f44336' : '#4caf50' }} />
            <Box>
              <Typography variant="h6" fontWeight={600}>
                État de Santé Global
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {healthData.health_status}
              </Typography>
            </Box>
          </Box>
          <Chip
            label={`${healthData.overall_health_percentage.toFixed(0)}%`}
            size="large"
            sx={{
              fontSize: '1.5rem',
              fontWeight: 'bold',
              height: 50,
              bgcolor: getColorByName(
                healthData.overall_health_percentage >= 80 ? 'green' :
                healthData.overall_health_percentage >= 50 ? 'yellow' :
                healthData.overall_health_percentage >= 30 ? 'orange' : 'red'
              ),
              color: 'white',
            }}
          />
        </Box>
      </Paper>

      {/* Health Alerts */}
      {healthData.alerts && healthData.alerts.length > 0 && (
        <Box mb={2}>
          {healthData.alerts.map((alert, index) => (
            <Alert
              key={index}
              severity={getSeverityColor(alert.severity)}
              icon={alert.icon}
              sx={{ mb: 1 }}
            >
              <Typography variant="body2" fontWeight={500}>
                {alert.message}
              </Typography>
              {alert.action_required && (
                <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                  → {alert.action_required}
                </Typography>
              )}
            </Alert>
          ))}
        </Box>
      )}

      <Grid container spacing={2}>
        {/* Body Parts - Left Column */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              🧍 Parties du Corps
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {/* Summary */}
            <Box display="flex" gap={1} mb={2} flexWrap="wrap">
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
              {healthData.bleeding_parts_count === 0 &&
               healthData.fractured_parts_count === 0 &&
               healthData.infected_parts_count === 0 && (
                <Chip
                  label="✅ Aucune blessure"
                  size="small"
                  color="success"
                />
              )}
            </Box>

            {/* Body parts list */}
            {healthData.body_parts && healthData.body_parts.map((part) => (
              <Card
                key={part.name}
                variant="outlined"
                sx={{
                  mb: 1.5,
                  borderLeft: `4px solid ${getColorByName(part.color_code)}`,
                  bgcolor: part.health_percentage < 50 ? 'rgba(255, 0, 0, 0.05)' : 'transparent',
                }}
              >
                <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                    <Typography variant="body2" fontWeight={600}>
                      {part.name}
                    </Typography>
                    <Chip
                      label={`${part.health_percentage.toFixed(0)}%`}
                      size="small"
                      sx={{
                        bgcolor: getColorByName(part.color_code),
                        color: 'white',
                      }}
                    />
                  </Box>

                  <LinearProgress
                    variant="determinate"
                    value={part.health_percentage}
                    sx={{
                      height: 6,
                      borderRadius: 0.5,
                      mb: 1,
                      '& .MuiLinearProgress-bar': {
                        bgcolor: getColorByName(part.color_code),
                      }
                    }}
                  />

                  <Box display="flex" gap={0.5} flexWrap="wrap">
                    {part.is_bleeding && (
                      <Chip label={`🩸 ${part.bleeding_severity}`} size="small" color="error" sx={{ height: 20 }} />
                    )}
                    {part.is_fractured && (
                      <Chip label="🦴 Fracture" size="small" color="warning" sx={{ height: 20 }} />
                    )}
                    {part.is_infected && (
                      <Chip label="🦠 Infecté" size="small" color="error" sx={{ height: 20 }} />
                    )}
                    {part.is_bandaged && (
                      <Chip label="🩹 Bandé" size="small" color="info" sx={{ height: 20 }} />
                    )}
                    {part.is_splinted && (
                      <Chip label="🔧 Attelle" size="small" color="info" sx={{ height: 20 }} />
                    )}
                    {part.pain_level > 0 && (
                      <Chip label={`💥 Douleur ${part.pain_level.toFixed(0)}`} size="small" sx={{ height: 20 }} />
                    )}
                  </Box>

                  {part.status_text && (
                    <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                      {part.status_text}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            ))}
          </Paper>
        </Grid>

        {/* Vital Signs & Metabolism - Right Column */}
        <Grid item xs={12} md={6}>
          {/* Vital Signs */}
          <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              ❤️ Signes Vitaux
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {healthData.vital_signs && (
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                    <Typography variant="caption" color="text.secondary">🌡️ Température</Typography>
                    <Typography variant="h6" fontWeight={600} color={getColorByName(healthData.vital_signs.temperature_color)}>
                      {healthData.vital_signs.body_temperature.toFixed(1)}°C
                    </Typography>
                    <Typography variant="caption">{healthData.vital_signs.temperature_status}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                    <Typography variant="caption" color="text.secondary">💓 Fréquence</Typography>
                    <Typography variant="h6" fontWeight={600} color={getColorByName(healthData.vital_signs.heart_rate_color)}>
                      {healthData.vital_signs.heart_rate} BPM
                    </Typography>
                    <Typography variant="caption">{healthData.vital_signs.heart_rate_status}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                    <Typography variant="caption" color="text.secondary">🩸 Volume Sang</Typography>
                    <Typography variant="h6" fontWeight={600} color={getColorByName(healthData.vital_signs.blood_color)}>
                      {healthData.vital_signs.blood_volume.toFixed(1)}L
                    </Typography>
                    <Typography variant="caption">{healthData.vital_signs.blood_status}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                    <Typography variant="caption" color="text.secondary">🫁 Oxygène</Typography>
                    <Typography variant="h6" fontWeight={600} color={getColorByName(healthData.vital_signs.oxygen_color)}>
                      {healthData.vital_signs.oxygen_level.toFixed(0)}%
                    </Typography>
                    <Typography variant="caption">{healthData.vital_signs.oxygen_status}</Typography>
                  </Box>
                </Grid>
              </Grid>
            )}

            {healthData.vital_signs && (
              <Box mt={2}>
                <Typography variant="body2" fontWeight={500} mb={1}>⚡ Endurance</Typography>
                <LinearProgress
                  variant="determinate"
                  value={(healthData.vital_signs.stamina / healthData.vital_signs.stamina_max) * 100}
                  sx={{ height: 8, borderRadius: 1 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {healthData.vital_signs.stamina.toFixed(0)} / {healthData.vital_signs.stamina_max.toFixed(0)}
                </Typography>
              </Box>
            )}
          </Paper>

          {/* Metabolism */}
          <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              🔥 Métabolisme
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {healthData.metabolism && (
              <>
                {/* Energy bars */}
                {renderNutritionBar(healthData.metabolism.calories)}
                {renderNutritionBar(healthData.metabolism.water)}

                {/* Body composition */}
                <Box mt={2} mb={2}>
                  <Typography variant="body2" fontWeight={500} mb={1}>
                    🏋️ Composition Corporelle
                  </Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={4}>
                      <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                        <Typography variant="caption" color="text.secondary">Poids</Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {healthData.metabolism.body_weight.current.toFixed(1)}kg
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4}>
                      <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                        <Typography variant="caption" color="text.secondary">Muscle</Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {healthData.metabolism.muscle_mass.current.toFixed(1)}kg
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={4}>
                      <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                        <Typography variant="caption" color="text.secondary">Graisse</Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {healthData.metabolism.body_fat.current.toFixed(1)}kg
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                  <Box mt={1} display="flex" justifyContent="center" gap={2}>
                    <Chip label={`IMC: ${healthData.metabolism.bmi.toFixed(1)}`} size="small" />
                    <Chip label={healthData.metabolism.bmi_category} size="small" color="primary" />
                    <Chip label={healthData.metabolism.fitness_level} size="small" color="success" />
                  </Box>
                </Box>

                {/* Macronutrients */}
                <Divider sx={{ my: 2 }} />
                <Typography variant="body2" fontWeight={500} mb={1}>
                  🍖 Macronutriments
                </Typography>
                {renderNutritionBar(healthData.metabolism.proteins)}
                {renderNutritionBar(healthData.metabolism.carbohydrates)}
                {renderNutritionBar(healthData.metabolism.fats)}
              </>
            )}
          </Paper>

          {/* Digestion Status */}
          <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              🍽️ Digestion
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {healthData.metabolism && (
              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                    <Typography variant="caption" color="text.secondary">Estomac</Typography>
                    <LinearProgress
                      variant="determinate"
                      value={healthData.metabolism.stomach_fullness}
                      sx={{ height: 6, borderRadius: 1, my: 0.5 }}
                    />
                    <Typography variant="caption">{healthData.metabolism.stomach_fullness.toFixed(0)}%</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                    <Typography variant="caption" color="text.secondary">Intestins</Typography>
                    <LinearProgress
                      variant="determinate"
                      value={healthData.metabolism.intestine_fullness}
                      sx={{ height: 6, borderRadius: 1, my: 0.5 }}
                    />
                    <Typography variant="caption">{healthData.metabolism.intestine_fullness.toFixed(0)}%</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                    <Typography variant="caption" color="text.secondary">Vessie</Typography>
                    <LinearProgress
                      variant="determinate"
                      value={healthData.metabolism.bladder_fullness}
                      sx={{ height: 6, borderRadius={1, my: 0.5 }}
                    />
                    <Typography variant="caption">{healthData.metabolism.bladder_fullness.toFixed(0)}%</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box textAlign="center" p={1} borderRadius={1} bgcolor="grey.100">
                    <Typography variant="caption" color="text.secondary">Intestin</Typography>
                    <LinearProgress
                      variant="determinate"
                      value={healthData.metabolism.bowel_fullness}
                      sx={{ height: 6, borderRadius: 1, my: 0.5 }}
                    />
                    <Typography variant="caption">{healthData.metabolism.bowel_fullness.toFixed(0)}%</Typography>
                  </Box>
                </Grid>
              </Grid>
            )}

            {healthData.digesting_foods && healthData.digesting_foods.length > 0 && (
              <Box mt={2}>
                <Typography variant="body2" fontWeight={500} mb={1}>
                  En cours de digestion ({healthData.digesting_foods.length})
                </Typography>
                {healthData.digesting_foods.slice(0, 3).map((food, index) => (
                  <Chip
                    key={index}
                    label={`${food.food_name} (${food.quantity_grams}g)`}
                    size="small"
                    sx={{ mr: 0.5, mb: 0.5 }}
                  />
                ))}
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Vitamins */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              💊 Vitamines
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {healthData.metabolism && healthData.metabolism.vitamins && healthData.metabolism.vitamins.map(renderVitaminMineral)}
          </Paper>
        </Grid>

        {/* Minerals */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              ⚗️ Minéraux
            </Typography>
            <Divider sx={{ mb: 2 }} />
            {healthData.metabolism && healthData.metabolism.minerals && healthData.metabolism.minerals.map(renderVitaminMineral)}
          </Paper>
        </Grid>

        {/* Performance Modifiers */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom fontWeight={600}>
              ⚡ Modificateurs de Performance
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box display="flex" flexDirection="column" gap={1}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="body2">🔋 Régénération d'énergie</Typography>
                <Chip
                  label={`x${healthData.energy_regen_modifier.toFixed(2)}`}
                  size="small"
                  color={healthData.energy_regen_modifier >= 1 ? 'success' : 'error'}
                />
              </Box>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="body2">⚡ Endurance</Typography>
                <Chip
                  label={`x${healthData.stamina_modifier.toFixed(2)}`}
                  size="small"
                  color={healthData.stamina_modifier >= 1 ? 'success' : 'error'}
                />
              </Box>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="body2">💪 Force</Typography>
                <Chip
                  label={`x${healthData.strength_modifier.toFixed(2)}`}
                  size="small"
                  color={healthData.strength_modifier >= 1 ? 'success' : 'error'}
                />
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Recommendations */}
        {healthData.recommendations && healthData.recommendations.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                💡 Recommandations
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Box display="flex" flexDirection="column" gap={1}>
                {healthData.recommendations.map((rec, index) => (
                  <Alert key={index} severity="info" sx={{ py: 0.5 }}>
                    <Typography variant="body2">{rec}</Typography>
                  </Alert>
                ))}
              </Box>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default HealthDisplay;
