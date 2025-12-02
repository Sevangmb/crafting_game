import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  LinearProgress,
  Divider,
  Card,
  CardContent,
} from '@mui/material';
import axios from 'axios';

const ScumHealthPanel = () => {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHealthData();
    const interval = setInterval(loadHealthData, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadHealthData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/api/character/health-display/', {
        headers: { Authorization: `Token ${token}` }
      });
      setHealthData(response.data);
      setLoading(false);
    } catch (err) {
      console.error('[ScumHealthPanel] Error:', err);
      setLoading(false);
    }
  };

  if (loading || !healthData) {
    return null;
  }

  const getVitaminColor = (level) => {
    if (level < 30) return '#ff4444';
    if (level < 60) return '#ffaa00';
    if (level < 80) return '#ffdd00';
    return '#44ff44';
  };

  const getMineralColor = (level) => {
    if (level < 30) return '#ff4444';
    if (level < 60) return '#ffaa00';
    if (level < 80) return '#ffdd00';
    return '#44ff44';
  };

  return (
    <Box sx={{
      bgcolor: 'rgba(0, 0, 0, 0.85)',
      color: '#fff',
      p: 2,
      borderRadius: 2,
      fontFamily: 'monospace',
    }}>
      <Grid container spacing={2}>
        {/* Left Panel - ICU & Body Monitor */}
        <Grid item xs={12} md={4}>
          {/* BCU ICU MONITOR */}
          <Paper sx={{
            bgcolor: 'rgba(20, 20, 20, 0.95)',
            p: 2,
            mb: 2,
            border: '1px solid rgba(255, 255, 255, 0.2)',
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="caption" sx={{ color: '#aaa', fontFamily: 'monospace' }}>
                BCU ICU MONITOR
              </Typography>
              <Box sx={{ fontSize: '0.7rem', color: '#888' }}>📝</Box>
            </Box>
            <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', mb: 2 }} />

            {/* Heart Rate */}
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ color: '#ff6b6b', fontSize: '1.2rem' }}>💓</Box>
                  <Typography variant="h4" sx={{ fontFamily: 'monospace', color: '#ff6b6b' }}>
                    {healthData.vital_signs?.heart_rate || 75}
                  </Typography>
                </Box>
                <Typography variant="caption" sx={{ color: '#888' }}>
                  {healthData.vital_signs?.blood_volume?.toFixed(1) || '5.0'}/{healthData.vital_signs?.blood_volume?.toFixed(1) || '5.0'}
                </Typography>
              </Box>
              <Box sx={{ height: 40, bgcolor: 'rgba(0, 0, 0, 0.5)', mt: 1, borderRadius: 1, overflow: 'hidden' }}>
                {/* Simple heartbeat visualization */}
                <svg width="100%" height="100%" viewBox="0 0 200 40" preserveAspectRatio="none">
                  <polyline
                    points="0,20 40,20 45,5 50,35 55,20 200,20"
                    fill="none"
                    stroke="#ff6b6b"
                    strokeWidth="1"
                  />
                </svg>
              </Box>
            </Box>

            {/* Blood Volume & Oxygen */}
            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Box sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                  <Box sx={{ color: '#4488ff', fontSize: '0.9rem' }}>🩸</Box>
                  <Typography variant="h5" sx={{ fontFamily: 'monospace', color: '#4488ff' }}>
                    {Math.round((healthData.vital_signs?.blood_volume || 5) / 5 * 100)}
                  </Typography>
                </Box>
                <Typography variant="caption" sx={{ color: '#666' }}>BLOOD VOL</Typography>
              </Box>
              <Box sx={{ flex: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                  <Box sx={{ color: '#44ff44', fontSize: '0.9rem' }}>💚</Box>
                  <Typography variant="h5" sx={{ fontFamily: 'monospace', color: '#44ff44' }}>
                    {Math.round(healthData.vital_signs?.oxygen_level || 98)}
                  </Typography>
                </Box>
                <Typography variant="caption" sx={{ color: '#666' }}>OXYGEN</Typography>
              </Box>
            </Box>

            {/* Temperature */}
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                <Box sx={{ color: '#ffaa44', fontSize: '0.9rem' }}>🌡️</Box>
                <Typography variant="caption" sx={{ color: '#888' }}>TEMP</Typography>
                <Typography variant="body2" sx={{ fontFamily: 'monospace', color: '#ffaa44', ml: 'auto' }}>
                  {healthData.vital_signs?.body_temperature?.toFixed(1) || '36.5'}°C
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={50}
                sx={{
                  height: 6,
                  bgcolor: 'rgba(255, 170, 68, 0.2)',
                  '& .MuiLinearProgress-bar': { bgcolor: '#ffaa44' }
                }}
              />
            </Box>

            {/* Stats Grid */}
            <Box sx={{ mt: 2, display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 1 }}>
              {[
                { label: 'STR', value: 74 },
                { label: 'COM', value: 74 },
                { label: 'DEX', value: 304 },
                { label: 'INT', value: '2.96 BCu' },
              ].map((stat, idx) => (
                <Box key={idx} sx={{ bgcolor: 'rgba(0, 0, 0, 0.5)', p: 0.5, textAlign: 'center' }}>
                  <Typography variant="caption" sx={{ color: '#666', fontSize: '0.65rem' }}>
                    {stat.label}
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#fff', fontSize: '0.7rem', display: 'block' }}>
                    {stat.value}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>

          {/* BCU BODY MONITOR */}
          <Paper sx={{
            bgcolor: 'rgba(20, 20, 20, 0.95)',
            p: 2,
            border: '1px solid rgba(255, 255, 255, 0.2)',
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="caption" sx={{ color: '#aaa', fontFamily: 'monospace' }}>
                BCU BODY MONITOR
              </Typography>
              <Box sx={{ fontSize: '0.7rem', color: '#888' }}>📝</Box>
            </Box>
            <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', mb: 2 }} />

            <Grid container spacing={1}>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#888' }}>AGE</Typography>
                <Typography variant="body2" sx={{ color: '#fff' }}>30 years</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#888' }}>TEETH NUMBER</Typography>
                <Typography variant="body2" sx={{ color: '#fff' }}>32/32</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#888' }}>LIFETIME</Typography>
                <Typography variant="body2" sx={{ color: '#fff' }}>0.540h</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#888' }}>TEMPERATURE</Typography>
                <Typography variant="body2" sx={{ color: '#fff' }}>
                  {healthData.vital_signs?.body_temperature?.toFixed(1) || '36.5'}°C
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#888' }}>WEIGHT</Typography>
                <Typography variant="body2" sx={{ color: '#fff' }}>
                  {healthData.metabolism?.body_weight?.current?.toFixed(1) || '88.5'}kg
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#888' }}>TEMP. DEVIATION</Typography>
                <Typography variant="body2" sx={{ color: '#fff' }}>-0.2°C</Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#888' }}>BMI</Typography>
                <Typography variant="body2" sx={{ color: '#fff' }}>
                  {healthData.metabolism?.bmi?.toFixed(1) || '19.1'}kg
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#888' }}>BLOOD VOLUME</Typography>
                <Typography variant="body2" sx={{ color: '#fff' }}>
                  {healthData.vital_signs?.blood_volume?.toFixed(1) || '5.0'}l
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#888' }}>STORAGE FAT</Typography>
                <Typography variant="body2" sx={{ color: '#fff' }}>
                  {healthData.metabolism?.body_fat?.current?.toFixed(1) || '8.8'}kg
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="caption" sx={{ color: '#888' }}>MIN. BLOOD VOL</Typography>
                <Typography variant="body2" sx={{ color: '#fff' }}>3.8l</Typography>
              </Grid>
              <Grid item xs={12}>
                <Typography variant="caption" sx={{ color: '#888' }}>SICKNESSES</Typography>
                <Typography variant="body2" sx={{ color: healthData.active_diseases_count > 0 ? '#ff4444' : '#44ff44' }}>
                  {healthData.active_diseases_count > 0 ? `${healthData.active_diseases_count} active` : '0'}
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Right Panel - Nutrition & Digestion */}
        <Grid item xs={12} md={4}>
          {/* BCU NUTRITION MONITOR */}
          <Paper sx={{
            bgcolor: 'rgba(20, 20, 20, 0.95)',
            p: 2,
            border: '1px solid rgba(255, 255, 255, 0.2)',
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="caption" sx={{ color: '#aaa', fontFamily: 'monospace' }}>
                BCU NUTRITION MONITOR
              </Typography>
              <Box sx={{ fontSize: '0.7rem', color: '#888' }}>📝</Box>
            </Box>
            <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', mb: 2 }} />

            {/* Calorie & Water Bars */}
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <Box sx={{ flex: 1, textAlign: 'center' }}>
                  <Box sx={{ fontSize: '2rem', mb: 0.5 }}>🍎</Box>
                  <Box sx={{
                    border: '2px solid rgba(255, 255, 255, 0.3)',
                    borderRadius: 1,
                    p: 1,
                    minHeight: 80,
                    position: 'relative',
                    overflow: 'hidden',
                  }}>
                    <Box sx={{
                      position: 'absolute',
                      bottom: 0,
                      left: 0,
                      right: 0,
                      height: `${healthData.metabolism?.calories?.percentage || 70}%`,
                      background: 'linear-gradient(to top, #44ff44, #88ff88)',
                      transition: 'height 0.3s',
                    }} />
                    <Typography variant="caption" sx={{ position: 'relative', zIndex: 1, color: '#fff', fontWeight: 'bold' }}>
                      {Math.round(healthData.metabolism?.calories?.current || 1183)}kcal
                    </Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: '#888' }}>INTAKE</Typography>
                </Box>

                <Box sx={{ flex: 1, textAlign: 'center' }}>
                  <Box sx={{ fontSize: '2rem', mb: 0.5 }}>🔥</Box>
                  <Box sx={{
                    border: '2px solid rgba(255, 255, 255, 0.3)',
                    borderRadius: 1,
                    p: 1,
                    minHeight: 80,
                    position: 'relative',
                    overflow: 'hidden',
                  }}>
                    <Box sx={{
                      position: 'absolute',
                      bottom: 0,
                      left: 0,
                      right: 0,
                      height: `${healthData.metabolism?.water?.percentage || 90}%`,
                      background: 'linear-gradient(to top, #4488ff, #88ccff)',
                      transition: 'height 0.3s',
                    }} />
                    <Typography variant="caption" sx={{ position: 'relative', zIndex: 1, color: '#fff', fontWeight: 'bold' }}>
                      {Math.round(healthData.metabolism?.water?.current || 3033)}ml
                    </Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: '#888' }}>WATER</Typography>
                </Box>
              </Box>

              {/* Macronutrients */}
              <Box sx={{ display: 'flex', justifyContent: 'space-around', mb: 2 }}>
                <Box sx={{ textAlign: 'center' }}>
                  <Box sx={{
                    width: 50,
                    height: 50,
                    borderRadius: '50%',
                    border: '3px solid #ff8844',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                  }}>
                    <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#ff8844' }}>
                      {Math.round(healthData.metabolism?.proteins?.percentage || 40)}%
                    </Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: '#888', fontSize: '0.65rem' }}>
                    PROTEIN
                  </Typography>
                </Box>

                <Box sx={{ textAlign: 'center' }}>
                  <Box sx={{
                    width: 50,
                    height: 50,
                    borderRadius: '50%',
                    border: '3px solid #ffdd44',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#ffdd44' }}>
                      {Math.round(healthData.metabolism?.carbohydrates?.percentage || 28)}%
                    </Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: '#888', fontSize: '0.65rem' }}>
                    CARBS
                  </Typography>
                </Box>

                <Box sx={{ textAlign: 'center' }}>
                  <Box sx={{
                    width: 50,
                    height: 50,
                    borderRadius: '50%',
                    border: '3px solid #44ff88',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#44ff88' }}>
                      {Math.round(healthData.metabolism?.fats?.percentage || 38)}%
                    </Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: '#888', fontSize: '0.65rem' }}>
                    FAT
                  </Typography>
                </Box>
              </Box>

              {/* Detailed Stats */}
              <Box sx={{ bgcolor: 'rgba(0, 0, 0, 0.5)', p: 1, borderRadius: 1 }}>
                <Grid container spacing={0.5}>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#888' }}>CALORIE BALANCE</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#fff', textAlign: 'right' }}>
                      {Math.round(healthData.metabolism?.calories?.current || 240)}kcal
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#888' }}>WATER BALANCE</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#fff', textAlign: 'right' }}>
                      {Math.round(healthData.metabolism?.water?.current || 1368)}ml
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#888' }}>CALORIE INTAKE</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#fff', textAlign: 'right' }}>
                      {Math.round(healthData.metabolism?.calories?.current || 3775)}kcal
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#888' }}>WATER INTAKE</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#fff', textAlign: 'right' }}>
                      {Math.round(healthData.metabolism?.water?.current || 2262)}ml
                    </Typography>
                  </Grid>
                </Grid>
              </Box>
            </Box>

            {/* Vitamins */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" sx={{ color: '#aaa', mb: 1, display: 'block' }}>
                VITAMINS
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 0.5 }}>
                {healthData.metabolism?.vitamins && healthData.metabolism.vitamins.slice(0, 12).map((vitamin, idx) => (
                  <Box
                    key={idx}
                    sx={{
                      width: 35,
                      height: 35,
                      borderRadius: '50%',
                      border: `2px solid ${getVitaminColor(vitamin.level)}`,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: 'rgba(0, 0, 0, 0.5)',
                    }}
                  >
                    <Typography variant="caption" sx={{ fontSize: '0.6rem', color: '#888' }}>
                      {vitamin.name.replace('Vitamine ', '')}
                    </Typography>
                    <Typography variant="caption" sx={{ fontSize: '0.55rem', color: getVitaminColor(vitamin.level), fontWeight: 'bold' }}>
                      {Math.round(vitamin.level)}%
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>

            {/* Minerals */}
            <Box>
              <Typography variant="caption" sx={{ color: '#aaa', mb: 1, display: 'block' }}>
                MINERALS
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 0.5 }}>
                {healthData.metabolism?.minerals && healthData.metabolism.minerals.slice(0, 12).map((mineral, idx) => (
                  <Box
                    key={idx}
                    sx={{
                      width: 35,
                      height: 35,
                      borderRadius: '50%',
                      border: `2px solid ${getMineralColor(mineral.level)}`,
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'center',
                      bgcolor: 'rgba(0, 0, 0, 0.5)',
                    }}
                  >
                    <Typography variant="caption" sx={{ fontSize: '0.55rem', color: '#888' }}>
                      {mineral.name.slice(0, 3)}
                    </Typography>
                    <Typography variant="caption" sx={{ fontSize: '0.55rem', color: getMineralColor(mineral.level), fontWeight: 'bold' }}>
                      {Math.round(mineral.level)}%
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          </Paper>

          {/* BCU DIGESTION MONITOR */}
          <Paper sx={{
            bgcolor: 'rgba(20, 20, 20, 0.95)',
            p: 2,
            mt: 2,
            border: '1px solid rgba(255, 255, 255, 0.2)',
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
              <Typography variant="caption" sx={{ color: '#aaa', fontFamily: 'monospace' }}>
                BCU DIGESTION MONITOR
              </Typography>
              <Box sx={{ fontSize: '0.7rem', color: '#888' }}>📝</Box>
            </Box>
            <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.1)', mb: 2 }} />

            <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
              {[
                { label: 'STOMACH', value: healthData.metabolism?.stomach_fullness || 0, unit: 'VOLUME' },
                { label: 'INTESTINE', value: healthData.metabolism?.intestine_fullness || 31, unit: 'VOLUME' },
                { label: 'COLON', value: healthData.metabolism?.bowel_fullness || 48, unit: 'VOLUME' },
                { label: 'BLADDER', value: healthData.metabolism?.bladder_fullness || 48, unit: 'VOLUME' },
              ].map((item, idx) => (
                <Box key={idx} sx={{ textAlign: 'center' }}>
                  <Typography variant="caption" sx={{ color: '#888', fontSize: '0.65rem' }}>
                    {item.value.toFixed(0)}%
                  </Typography>
                  <Box sx={{
                    width: 60,
                    height: 60,
                    borderRadius: '50%',
                    border: '3px solid rgba(255, 255, 255, 0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    mx: 'auto',
                    my: 1,
                  }}>
                    <Box sx={{
                      position: 'absolute',
                      bottom: 0,
                      left: 0,
                      right: 0,
                      height: `${item.value}%`,
                      bgcolor: '#4488ff',
                      borderRadius: '0 0 50% 50%',
                    }} />
                    <Typography variant="caption" sx={{ position: 'relative', zIndex: 1, color: '#fff', fontWeight: 'bold' }}>
                      {item.label}
                    </Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: '#666', fontSize: '0.6rem' }}>
                    {item.unit}
                  </Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ScumHealthPanel;
