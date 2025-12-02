import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  LinearProgress,
  Avatar,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  Badge,
  Paper
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { achievementsAPI } from '../../services/api';
import LockIcon from '@mui/icons-material/Lock';
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RefreshIcon from '@mui/icons-material/Refresh';

// Styled components pour les achievements
const AchievementCard = styled(Card)(({ theme, completed, hidden }) => ({
  position: 'relative',
  cursor: 'pointer',
  transition: 'all 0.3s ease',
  border: completed ? '2px solid #4caf50' : '1px solid #e0e0e0',
  background: completed
    ? 'linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%)'
    : hidden
      ? 'linear-gradient(135deg, #f5f5f5 0%, #fafafa 100%)'
      : 'white',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[4],
  },
}));

const AchievementIcon = styled(Avatar)(({ completed }) => ({
  width: 60,
  height: 60,
  backgroundColor: completed ? '#4caf50' : '#9e9e9e',
  fontSize: '2rem',
}));

const categoryIcons = {
  exploration: '🗺️',
  gathering: '🌾',
  crafting: '🔨',
  combat: '⚔️',
  progression: '⭐',
  collection: '🧺',
};

const categoryNames = {
  exploration: 'Exploration',
  gathering: 'Récolte',
  crafting: 'Craft',
  combat: 'Combat',
  progression: 'Progression',
  collection: 'Collection',
};

const AchievementsTab = () => {
  const [achievements, setAchievements] = useState([]);
  const [progress, setProgress] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [recentAchievements, setRecentAchievements] = useState([]);

  useEffect(() => {
    loadAchievements();
    loadProgress();
    loadRecent();
  }, []);

  const loadAchievements = async () => {
    try {
      const response = await achievementsAPI.getAll();
      setAchievements(response.data.results || response.data);
    } catch (error) {
      console.error('Erreur chargement achievements:', error);
    }
  };

  const loadProgress = async () => {
    try {
      const response = await achievementsAPI.getProgress();
      setProgress(response.data.progress || []);
      setStats(response.data.stats || {});
    } catch (error) {
      console.error('Erreur chargement progression:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRecent = async () => {
    try {
      const response = await achievementsAPI.getRecent();
      setRecentAchievements(response.data.recent || []);
    } catch (error) {
      console.error('Erreur chargement récents:', error);
    }
  };

  const refreshData = async () => {
    setLoading(true);
    await Promise.all([loadAchievements(), loadProgress(), loadRecent()]);
  };

  const getProgressForAchievement = (achievementId) => {
    const prog = progress.find(p => p.achievement === achievementId);
    return prog || { progress: 0, completed: false };
  };

  const filteredAchievements = selectedCategory === 'all'
    ? achievements
    : achievements.filter(a => a.category === selectedCategory);

  const categories = ['all', ...Object.keys(categoryNames)];

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Chargement des achievements...
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header avec statistiques */}
      <Box sx={{ mb: 3 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.light', color: 'white' }}>
              <Typography variant="h4">{stats.total_completed || 0}</Typography>
              <Typography variant="body2">Complétés</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.light', color: 'white' }}>
              <Typography variant="h4">{stats.total_available || 0}</Typography>
              <Typography variant="body2">Disponibles</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.light', color: 'white' }}>
              <Typography variant="h4">
                {stats.total_available ? Math.round((stats.total_completed / stats.total_available) * 100) : 0}%
              </Typography>
              <Typography variant="body2">Progression</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'info.light', color: 'white' }}>
              <Typography variant="h4">{stats.total_xp_earned || 0}</Typography>
              <Typography variant="body2">XP gagné</Typography>
            </Paper>
          </Grid>
        </Grid>
      </Box>

      {/* Achievements récents */}
      {recentAchievements.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
            <EmojiEventsIcon sx={{ mr: 1 }} />
            Derniers achievements débloqués
          </Typography>
          <Grid container spacing={2}>
            {recentAchievements.slice(0, 4).map((achievement) => (
              <Grid item xs={12} sm={6} md={3} key={achievement.id}>
                <AchievementCard completed>
                  <CardContent sx={{ textAlign: 'center', p: 2 }}>
                    <AchievementIcon completed>
                      {achievement.icon}
                    </AchievementIcon>
                    <Typography variant="h6" sx={{ mt: 1, fontSize: '0.9rem' }}>
                      {achievement.name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      +{achievement.reward_xp} XP
                    </Typography>
                  </CardContent>
                </AchievementCard>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Filtres par catégorie */}
      <Box sx={{ mb: 3 }}>
        <Tabs
          value={selectedCategory}
          onChange={(e, value) => setSelectedCategory(value)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {categories.map(category => (
            <Tab
              key={category}
              label={category === 'all' ? 'Tous' : categoryNames[category]}
              value={category}
              icon={category === 'all' ? undefined : categoryIcons[category]}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Box>

      {/* Bouton refresh */}
      <Box sx={{ mb: 3, textAlign: 'right' }}>
        <Tooltip title="Actualiser">
          <IconButton onClick={refreshData} disabled={loading}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Grille des achievements */}
      <Grid container spacing={3}>
        {filteredAchievements.map((achievement) => {
          const progressInfo = getProgressForAchievement(achievement.id);
          const isCompleted = progressInfo.completed;
          const isHidden = achievement.hidden && !isCompleted;
          const progressPercent = achievement.requirement_value
            ? (progressInfo.progress / achievement.requirement_value) * 100
            : 0;

          return (
            <Grid item xs={12} sm={6} md={4} lg={3} key={achievement.id}>
              <AchievementCard completed={isCompleted} hidden={isHidden}>
                {isCompleted && (
                  <Badge
                    color="success"
                    badgeContent={<CheckCircleIcon fontSize="small" />}
                    sx={{ position: 'absolute', top: 8, right: 8, zIndex: 1 }}
                  />
                )}
                {isHidden && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      bottom: 0,
                      bgcolor: 'rgba(0,0,0,0.7)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      zIndex: 2,
                      borderRadius: 1,
                    }}
                  >
                    <LockIcon sx={{ fontSize: 48, color: 'white' }} />
                  </Box>
                )}

                <CardContent sx={{ textAlign: 'center', p: 2 }}>
                  <AchievementIcon completed={isCompleted}>
                    {isHidden ? '?' : achievement.icon}
                  </AchievementIcon>

                  <Typography variant="h6" sx={{ mt: 1, fontSize: '0.95rem' }}>
                    {isHidden ? 'Achievement caché' : achievement.name}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {achievement.category && (
                      <Chip
                        size="small"
                        label={categoryNames[achievement.category]}
                        icon={<span>{categoryIcons[achievement.category]}</span>}
                        sx={{ mr: 1, mb: 1 }}
                      />
                    )}
                    +{achievement.reward_xp} XP
                  </Typography>

                  {!isHidden && (
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 32 }}>
                      {achievement.description}
                    </Typography>
                  )}

                  {!isCompleted && !isHidden && achievement.requirement_value && (
                    <Box sx={{ mt: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="caption">
                          {progressInfo.progress}/{achievement.requirement_value}
                        </Typography>
                        <Typography variant="caption">
                          {Math.round(progressPercent)}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(progressPercent, 100)}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Box>
                  )}
                </CardContent>
              </AchievementCard>
            </Grid>
          );
        })}
      </Grid>
    </Box>
  );
};

export default AchievementsTab;