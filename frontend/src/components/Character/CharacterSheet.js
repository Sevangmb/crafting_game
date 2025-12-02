import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Paper,
  Typography,
  Box,
  Avatar,
  Divider,
  LinearProgress,
  Chip,
  Tooltip,
  IconButton,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Person as PersonIcon,
  FitnessCenter as StrengthIcon,
  Speed as AgilityIcon,
  Psychology as IntelligenceIcon,
  Casino as LuckIcon,
  Close as CloseIcon,
  RemoveCircleOutline as UnequipIcon,
  Favorite as HealthIcon,
  Restaurant as NutritionIcon,
  LocalHospital as MedicalIcon,
} from '@mui/icons-material';
import { equipmentAPI } from '../../services/api';
import axios from 'axios';
import HealthDisplay from './HealthDisplay';
import ScumHealthPanel from './ScumHealthPanel';

const EQUIPMENT_SLOTS = [
  { key: 'head', label: 'Tête', icon: '🎩', position: { row: 1, col: 2 } },
  { key: 'chest', label: 'Torse', icon: '👔', position: { row: 2, col: 2 } },
  { key: 'hands', label: 'Mains', icon: '🧤', position: { row: 3, col: 2 } },
  { key: 'legs', label: 'Jambes', icon: '👖', position: { row: 4, col: 2 } },
  { key: 'feet', label: 'Pieds', icon: '👟', position: { row: 5, col: 2 } },
  { key: 'backpack', label: 'Sac à dos', icon: '🎒', position: { row: 2, col: 3 } },
  { key: 'main_hand', label: 'Main principale', icon: '⚔️', position: { row: 3, col: 1 } },
  { key: 'off_hand', label: 'Main secondaire', icon: '🛡️', position: { row: 3, col: 3 } },
  { key: 'accessory', label: 'Accessoire', icon: '💍', position: { row: 4, col: 3 } },
];

export default function CharacterSheet({ open, onClose, player, onUpdate }) {
  const [equipment, setEquipment] = useState({});
  const [loading, setLoading] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [nutritionData, setNutritionData] = useState(null);
  const [loadingNutrition, setLoadingNutrition] = useState(false);

  useEffect(() => {
    if (open && player) {
      loadEquipment();
      if (currentTab === 1) {
        loadNutritionData();
      }
    }
  }, [open, player, currentTab]);

  const loadEquipment = async () => {
    try {
      const response = await equipmentAPI.getAll();
      const equipmentMap = {};
      response.data.forEach(item => {
        equipmentMap[item.slot] = item;
      });
      setEquipment(equipmentMap);
    } catch (error) {
      console.error('Error loading equipment:', error);
    }
  };

  const loadNutritionData = async () => {
    setLoadingNutrition(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`http://localhost:8000/api/players/${player.id}/nutrition/`, {
        headers: { Authorization: `Token ${token}` }
      });
      setNutritionData(response.data);
    } catch (error) {
      console.error('Error loading nutrition data:', error);
    } finally {
      setLoadingNutrition(false);
    }
  };

  const handleUnequip = async (slot) => {
    setLoading(true);
    try {
      await equipmentAPI.unequip(slot);
      await loadEquipment();
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Error unequipping:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!player) return null;

  const getStatBar = (current, max, color) => {
    const percentage = (current / max) * 100;
    return (
      <Box sx={{ width: '100%' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="caption">{current}/{max}</Typography>
          <Typography variant="caption">{percentage.toFixed(0)}%</Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={percentage}
          sx={{
            height: 8,
            borderRadius: 1,
            backgroundColor: 'rgba(0,0,0,0.1)',
            '& .MuiLinearProgress-bar': {
              backgroundColor: color
            }
          }}
        />
      </Box>
    );
  };

  const renderEquipmentSlot = (slotConfig) => {
    const equipped = equipment[slotConfig.key];

    return (
      <Paper
        key={slotConfig.key}
        elevation={equipped ? 3 : 1}
        sx={{
          p: 1.5,
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: equipped ? 'action.selected' : 'background.paper',
          border: equipped ? '2px solid' : '1px dashed',
          borderColor: equipped ? 'primary.main' : 'divider',
          position: 'relative',
          transition: 'all 0.2s',
          '&:hover': equipped ? {
            boxShadow: 4,
          } : {},
        }}
      >
        {equipped && (
          <IconButton
            size="small"
            sx={{
              position: 'absolute',
              top: 2,
              right: 2,
              padding: 0.5,
            }}
            onClick={() => handleUnequip(slotConfig.key)}
            disabled={loading}
          >
            <UnequipIcon fontSize="small" />
          </IconButton>
        )}

        <Typography variant="caption" sx={{ fontSize: '1.5rem', mb: 0.5 }}>
          {slotConfig.icon}
        </Typography>

        <Typography variant="caption" sx={{ fontWeight: 600, fontSize: '0.7rem', textAlign: 'center' }}>
          {slotConfig.label}
        </Typography>

        {equipped ? (
          <>
            <Typography variant="caption" sx={{ mt: 0.5, fontSize: '0.75rem', textAlign: 'center' }}>
              {equipped.material.icon} {equipped.material.name}
            </Typography>
            {equipped.material.defense > 0 && (
              <Chip label={`🛡️ ${equipped.material.defense}`} size="small" sx={{ mt: 0.5, height: 18 }} />
            )}
            {equipped.material.attack > 0 && (
              <Chip label={`⚔️ ${equipped.material.attack}`} size="small" sx={{ mt: 0.5, height: 18 }} />
            )}
          </>
        ) : (
          <Typography variant="caption" color="text.disabled" sx={{ mt: 0.5, fontSize: '0.65rem' }}>
            Vide
          </Typography>
        )}
      </Paper>
    );
  };

  const getNutritionColor = (value) => {
    if (value >= 80) return '#4caf50';
    if (value >= 60) return '#8bc34a';
    if (value >= 40) return '#ff9800';
    return '#f44336';
  };

  const renderNutritionTab = () => {
    if (loadingNutrition) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" p={4}>
          <Typography>Chargement des données nutritionnelles...</Typography>
        </Box>
      );
    }

    if (!nutritionData) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" p={4}>
          <Typography>Aucune donnée nutritionnelle disponible</Typography>
        </Box>
      );
    }

    return (
      <Grid container spacing={3}>
        {/* Overall Status */}
        <Grid item xs={12}>
          <Paper elevation={2} sx={{ p: 2, bgcolor: 'background.default' }}>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="h6">Score Nutritionnel Global</Typography>
                <Typography variant="body2" color="text.secondary">
                  Statut: {nutritionData.status}
                </Typography>
              </Box>
              <Chip
                label={`${nutritionData.overall_score}%`}
                size="large"
                sx={{
                  fontSize: '1.2rem',
                  fontWeight: 'bold',
                  bgcolor: getNutritionColor(nutritionData.overall_score),
                  color: 'white'
                }}
              />
            </Box>
            {nutritionData.is_malnourished && (
              <Box mt={1}>
                <Chip label="⚠️ Malnutrition" color="error" size="small" />
              </Box>
            )}
            {nutritionData.food_poisoning && (
              <Box mt={1}>
                <Chip label="☠️ Intoxication alimentaire" color="error" size="small" />
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Macronutrients */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>🍖 Macronutriments</Typography>
            <Divider sx={{ mb: 2 }} />

            <Box mb={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Protéines</Typography>
                <Chip label={`${nutritionData.macronutrients.proteins}g`} size="small" />
              </Box>
              <LinearProgress
                variant="determinate"
                value={Math.min(100, (nutritionData.macronutrients.proteins / 80) * 100)}
                sx={{ height: 8, borderRadius: 1 }}
              />
            </Box>

            <Box mb={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Glucides</Typography>
                <Chip label={`${nutritionData.macronutrients.carbs}g`} size="small" />
              </Box>
              <LinearProgress
                variant="determinate"
                value={Math.min(100, (nutritionData.macronutrients.carbs / 250) * 100)}
                sx={{ height: 8, borderRadius: 1 }}
              />
            </Box>

            <Box mb={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">Lipides</Typography>
                <Chip label={`${nutritionData.macronutrients.fats}g`} size="small" />
              </Box>
              <LinearProgress
                variant="determinate"
                value={Math.min(100, (nutritionData.macronutrients.fats / 70) * 100)}
                sx={{ height: 8, borderRadius: 1 }}
              />
            </Box>
          </Paper>
        </Grid>

        {/* Vitamins */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>💊 Vitamines</Typography>
            <Divider sx={{ mb: 2 }} />

            {Object.entries(nutritionData.vitamins).map(([key, value]) => (
              <Box key={key} mb={1.5}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                  <Typography variant="body2">Vitamine {key.toUpperCase()}</Typography>
                  <Chip
                    label={`${value}%`}
                    size="small"
                    sx={{
                      bgcolor: getNutritionColor(value),
                      color: 'white'
                    }}
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={Math.min(100, value)}
                  sx={{
                    height: 6,
                    borderRadius: 1,
                    '& .MuiLinearProgress-bar': {
                      bgcolor: getNutritionColor(value)
                    }
                  }}
                />
              </Box>
            ))}
          </Paper>
        </Grid>

        {/* Minerals */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>⚗️ Minéraux</Typography>
            <Divider sx={{ mb: 2 }} />

            {Object.entries(nutritionData.minerals).map(([key, value]) => (
              <Box key={key} mb={1.5}>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                  <Typography variant="body2">{key.charAt(0).toUpperCase() + key.slice(1)}</Typography>
                  <Chip
                    label={`${value}%`}
                    size="small"
                    sx={{
                      bgcolor: getNutritionColor(value),
                      color: 'white'
                    }}
                  />
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={Math.min(100, value)}
                  sx={{
                    height: 6,
                    borderRadius: 1,
                    '& .MuiLinearProgress-bar': {
                      bgcolor: getNutritionColor(value)
                    }
                  }}
                />
              </Box>
            ))}
          </Paper>
        </Grid>

        {/* Health Effects */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>❤️ Effets sur la Santé</Typography>
            <Divider sx={{ mb: 2 }} />

            <Box display="flex" flexDirection="column" gap={1.5}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="body2">🛡️ Système immunitaire</Typography>
                <Chip label={`${nutritionData.health_effects.immune_system}%`} size="small" color="primary" />
              </Box>

              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="body2">⚡ Régénération endurance</Typography>
                <Chip label={`x${nutritionData.health_effects.stamina_regen}`} size="small" color="success" />
              </Box>

              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="body2">💚 Vitesse de guérison</Typography>
                <Chip label={`x${nutritionData.health_effects.healing_rate}`} size="small" color="error" />
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Body Composition */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>🏋️ Composition Corporelle</Typography>
            <Divider sx={{ mb: 2 }} />

            <Box display="flex" flexDirection="column" gap={1.5}>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="body2">% Graisse corporelle</Typography>
                <Chip label={`${nutritionData.body.fat_percentage}%`} size="small" />
              </Box>

              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="body2">💪 Masse musculaire</Typography>
                <Chip label={`${nutritionData.body.muscle_mass} kg`} size="small" color="primary" />
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Digestion */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>🍽️ Digestion en cours</Typography>
            <Divider sx={{ mb: 2 }} />

            {nutritionData.digesting_count > 0 ? (
              <Box>
                <Typography variant="body2">
                  {nutritionData.digesting_count} aliment(s) en cours de digestion
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Les nutriments sont absorbés progressivement
                </Typography>
              </Box>
            ) : (
              <Typography variant="body2" color="text.secondary">
                Aucune nourriture en cours de digestion
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Toxicity */}
        {nutritionData.toxin_level > 0 && (
          <Grid item xs={12} md={6}>
            <Paper elevation={2} sx={{ p: 2, bgcolor: '#ffebee' }}>
              <Typography variant="h6" gutterBottom color="error">☠️ Toxicité</Typography>
              <Divider sx={{ mb: 2 }} />

              <Box>
                <Typography variant="body2">
                  Niveau de toxines: {nutritionData.toxin_level}
                </Typography>
                {nutritionData.food_poisoning && (
                  <Typography variant="caption" color="error">
                    ⚠️ Vous souffrez d'intoxication alimentaire!
                  </Typography>
                )}
              </Box>
            </Paper>
          </Grid>
        )}
      </Grid>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="xl"
      fullWidth
      PaperProps={{
        sx: {
          minHeight: '90vh',
          background: 'linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%)',
        }
      }}
    >
      <DialogTitle sx={{
        background: 'linear-gradient(90deg, #3a3a52 0%, #2d2d44 100%)',
        borderBottom: '2px solid rgba(255, 255, 255, 0.1)',
        pb: 2
      }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            <Avatar
              sx={{
                width: 56,
                height: 56,
                bgcolor: 'primary.main',
                fontSize: '1.5rem',
                border: '3px solid rgba(255, 255, 255, 0.2)'
              }}
            >
              {player.user.username[0].toUpperCase()}
            </Avatar>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'white' }}>
                {player.user.username}
              </Typography>
              <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                <Chip
                  label={`Niveau ${player.level}`}
                  size="small"
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'white',
                    fontWeight: 'bold'
                  }}
                />
                <Chip
                  label={`${player.money}₡`}
                  size="small"
                  sx={{
                    bgcolor: 'warning.main',
                    color: 'white',
                    fontWeight: 'bold'
                  }}
                />
              </Box>
            </Box>
          </Box>
          <IconButton
            onClick={onClose}
            size="large"
            sx={{
              color: 'white',
              '&:hover': { bgcolor: 'rgba(255, 255, 255, 0.1)' }
            }}
          >
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0, bgcolor: 'transparent' }}>
        <Tabs
          value={currentTab}
          onChange={(e, newValue) => setCurrentTab(newValue)}
          sx={{
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            bgcolor: 'rgba(0, 0, 0, 0.2)',
            px: 2,
            '& .MuiTab-root': {
              color: 'rgba(255, 255, 255, 0.6)',
              fontWeight: 'bold',
              fontSize: '0.95rem',
              minHeight: 64,
              transition: 'all 0.3s',
              '&:hover': {
                color: 'rgba(255, 255, 255, 0.9)',
                bgcolor: 'rgba(255, 255, 255, 0.05)'
              },
              '&.Mui-selected': {
                color: 'white',
                bgcolor: 'rgba(255, 255, 255, 0.1)'
              }
            },
            '& .MuiTabs-indicator': {
              height: 3,
              background: 'linear-gradient(90deg, #4CAF50 0%, #2196F3 100%)'
            }
          }}
        >
          <Tab
            label="Équipement & Stats"
            icon={<PersonIcon />}
            iconPosition="start"
          />
          <Tab
            label="Nutrition"
            icon={<NutritionIcon />}
            iconPosition="start"
          />
          <Tab
            label="Santé Détaillée (SCUM)"
            icon={<MedicalIcon />}
            iconPosition="start"
          />
        </Tabs>

        <Box sx={{ p: 3 }}>

        {currentTab === 0 && (
        <Grid container spacing={3}>
          {/* Left Panel: Character Info */}
          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{
              p: 2,
              height: '100%',
              background: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 2
            }}>
              <Box display="flex" flexDirection="column" alignItems="center" mb={2}>
                <Avatar sx={{
                  width: 80,
                  height: 80,
                  mb: 1,
                  bgcolor: 'primary.main',
                  fontSize: '2rem',
                  border: '3px solid rgba(255, 255, 255, 0.2)'
                }}>
                  {player.user.username[0].toUpperCase()}
                </Avatar>
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                  {player.user.username}
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  Niveau {player.level}
                </Typography>
              </Box>

              <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

              {/* Stats */}
              <Box mb={2}>
                <Typography variant="subtitle2" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
                  ❤️ Santé
                </Typography>
                {getStatBar(player.health, player.max_health, '#f44336')}
              </Box>

              <Box mb={2}>
                <Typography variant="subtitle2" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
                  ⚡ Énergie
                </Typography>
                {getStatBar(player.energy, player.max_energy, '#ffc107')}
              </Box>

              <Box mb={2}>
                <Typography variant="subtitle2" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
                  🍖 Faim
                </Typography>
                {getStatBar(player.hunger, player.max_hunger, '#ff9800')}
              </Box>

              <Box mb={2}>
                <Typography variant="subtitle2" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
                  💧 Soif
                </Typography>
                {getStatBar(player.thirst, player.max_thirst, '#2196f3')}
              </Box>

              <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

              {/* Attributes */}
              <Typography variant="subtitle2" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
                Attributs
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box display="flex" alignItems="center">
                    <StrengthIcon fontSize="small" sx={{ mr: 1, color: 'rgba(255, 255, 255, 0.7)' }} />
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>Force</Typography>
                  </Box>
                  <Chip label={player.strength} size="small" />
                </Box>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box display="flex" alignItems="center">
                    <AgilityIcon fontSize="small" sx={{ mr: 1, color: 'rgba(255, 255, 255, 0.7)' }} />
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>Agilité</Typography>
                  </Box>
                  <Chip label={player.agility} size="small" />
                </Box>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box display="flex" alignItems="center">
                    <IntelligenceIcon fontSize="small" sx={{ mr: 1, color: 'rgba(255, 255, 255, 0.7)' }} />
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>Intelligence</Typography>
                  </Box>
                  <Chip label={player.intelligence} size="small" />
                </Box>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box display="flex" alignItems="center">
                    <LuckIcon fontSize="small" sx={{ mr: 1, color: 'rgba(255, 255, 255, 0.7)' }} />
                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>Chance</Typography>
                  </Box>
                  <Chip label={player.luck} size="small" />
                </Box>
              </Box>

              <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

              {/* Combat Stats */}
              <Typography variant="subtitle2" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
                Combat
              </Typography>
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>⚔️ Attaque totale</Typography>
                  <Chip label={player.total_attack} size="small" color="error" />
                </Box>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>🛡️ Défense totale</Typography>
                  <Chip label={player.total_defense} size="small" color="primary" />
                </Box>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>⚡ Bonus vitesse</Typography>
                  <Chip label={`${player.total_speed_bonus}%`} size="small" color="success" />
                </Box>
              </Box>

              <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

              {/* Money */}
              <Box display="flex" flexDirection="column" gap={1}>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>💵 Argent liquide</Typography>
                  <Chip label={`${player.money}₡`} size="small" color="warning" />
                </Box>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>💳 Carte de crédit</Typography>
                  <Chip label={`${player.credit_card_balance}₡`} size="small" color="info" />
                </Box>
              </Box>

              <Divider sx={{ my: 2, borderColor: 'rgba(255, 255, 255, 0.1)' }} />

              {/* Carry Weight */}
              <Box>
                <Typography variant="subtitle2" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
                  🎒 Capacité de transport
                </Typography>
                {getStatBar(player.current_carry_weight, player.effective_carry_capacity, '#9c27b0')}
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {player.current_carry_weight.toFixed(1)} / {player.effective_carry_capacity.toFixed(1)} kg
                </Typography>
              </Box>
            </Paper>
          </Grid>

          {/* Right Panel: Equipment */}
          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{
              p: 2,
              background: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 2
            }}>
              <Typography variant="h6" gutterBottom sx={{ color: 'white', fontWeight: 'bold' }}>
                ⚔️ Équipement
              </Typography>

              <Grid container spacing={1.5} sx={{ mt: 1 }}>
                {/* Create a 5x3 grid for equipment */}
                {[...Array(5)].map((_, rowIndex) => (
                  <React.Fragment key={rowIndex}>
                    {[...Array(3)].map((_, colIndex) => {
                      const slot = EQUIPMENT_SLOTS.find(
                        s => s.position.row === rowIndex + 1 && s.position.col === colIndex + 1
                      );

                      return (
                        <Grid item xs={4} key={`${rowIndex}-${colIndex}`}>
                          {slot ? renderEquipmentSlot(slot) : <Box sx={{ height: '100%' }} />}
                        </Grid>
                      );
                    })}
                  </React.Fragment>
                ))}
              </Grid>

              <Divider sx={{ my: 2 }} />

              <Typography variant="caption" color="text.secondary">
                💡 Astuce: Allez dans l'onglet Inventaire pour équiper des objets
              </Typography>
            </Paper>
          </Grid>
        </Grid>
        )}

        {currentTab === 1 && renderNutritionTab()}

        {currentTab === 2 && (
          <ScumHealthPanel />
        )}
        </Box>
      </DialogContent>

      <DialogActions sx={{
        background: 'linear-gradient(90deg, #3a3a52 0%, #2d2d44 100%)',
        borderTop: '2px solid rgba(255, 255, 255, 0.1)',
        p: 2
      }}>
        <Button
          onClick={onClose}
          variant="contained"
          sx={{
            background: 'linear-gradient(90deg, #4CAF50 0%, #2196F3 100%)',
            color: 'white',
            fontWeight: 'bold',
            px: 4,
            '&:hover': {
              background: 'linear-gradient(90deg, #45a049 0%, #1976D2 100%)'
            }
          }}
        >
          Fermer
        </Button>
      </DialogActions>
    </Dialog>
  );
}
