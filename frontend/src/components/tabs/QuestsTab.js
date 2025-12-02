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
  LinearProgress,
  Grid,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  CheckCircle as CompletedIcon,
  HourglassEmpty as ActiveIcon,
  Star as AvailableIcon,
  EmojiEvents as RewardIcon,
  Timeline as ProgressIcon,
} from '@mui/icons-material';
import { questsAPI } from '../../services/api';

const QuestsTab = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [availableQuests, setAvailableQuests] = useState([]);
  const [activeQuests, setActiveQuests] = useState([]);
  const [completedQuests, setCompletedQuests] = useState([]);
  const [questStats, setQuestStats] = useState(null);
  const [selectedQuest, setSelectedQuest] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    loadQuests();
    loadQuestStats();
  }, [currentTab]);

  const loadQuests = async () => {
    setLoading(true);
    setError('');
    try {
      if (currentTab === 0) {
        const response = await questsAPI.getAvailable();
        setAvailableQuests(response.data);
      } else if (currentTab === 1) {
        const response = await questsAPI.getActive();
        setActiveQuests(response.data);
      } else if (currentTab === 2) {
        const response = await questsAPI.getCompleted();
        setCompletedQuests(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du chargement des quêtes');
    } finally {
      setLoading(false);
    }
  };

  const loadQuestStats = async () => {
    try {
      const response = await questsAPI.getStats();
      setQuestStats(response.data);
    } catch (err) {
      console.error('Erreur chargement stats:', err);
    }
  };

  const handleAcceptQuest = async (questId) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await questsAPI.accept(questId);
      setSuccess('Quête acceptée avec succès!');
      setSelectedQuest(null);
      loadQuests();
      loadQuestStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de l\'acceptation');
    } finally {
      setLoading(false);
    }
  };

  const handleAbandonQuest = async (questId) => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await questsAPI.abandon(questId);
      setSuccess('Quête abandonnée');
      setSelectedQuest(null);
      loadQuests();
      loadQuestStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de l\'abandon');
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      case 'epic': return 'secondary';
      default: return 'default';
    }
  };

  const getTypeIcon = (type) => {
    const icons = {
      gather: '⛏️',
      craft: '🔨',
      explore: '🗺️',
      defeat: '⚔️',
      delivery: '📦',
      talk: '💬',
    };
    return icons[type] || '📜';
  };

  const renderQuestCard = (quest, isActive = false, isCompleted = false) => {
    const progress = quest.progress || {};
    const requirements = quest.quest?.requirements || quest.requirements || {};

    // Calculate total progress percentage
    let totalProgress = 0;
    let totalRequirements = 0;
    Object.entries(requirements).forEach(([type, items]) => {
      if (Array.isArray(items)) {
        items.forEach((item) => {
          totalRequirements++;
          const currentProgress = progress[type]?.find(p =>
            p.material_id === item.material_id || p.target === item.target
          );
          if (currentProgress && currentProgress.current >= item.quantity) {
            totalProgress++;
          }
        });
      }
    });
    const progressPercentage = totalRequirements > 0 ? (totalProgress / totalRequirements) * 100 : 0;

    const questData = quest.quest || quest;

    return (
      <Grid item xs={12} md={6} key={quest.id}>
        <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          <CardContent sx={{ flexGrow: 1 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="h6" component="div">
                {getTypeIcon(questData.quest_type)} {questData.name}
              </Typography>
              <Chip
                label={questData.difficulty_display || questData.difficulty}
                color={getDifficultyColor(questData.difficulty)}
                size="small"
              />
            </Box>

            <Typography variant="body2" color="text.secondary" gutterBottom>
              {questData.description}
            </Typography>

            {questData.story_text && (
              <Typography variant="body2" color="text.secondary" fontStyle="italic" mb={1}>
                "{questData.story_text}"
              </Typography>
            )}

            {isActive && (
              <Box mt={2}>
                <Box display="flex" alignItems="center" mb={1}>
                  <ProgressIcon fontSize="small" sx={{ mr: 1 }} />
                  <Typography variant="body2">
                    Progression: {progressPercentage.toFixed(0)}%
                  </Typography>
                </Box>
                <LinearProgress variant="determinate" value={progressPercentage} />
              </Box>
            )}

            <Box mt={2}>
              <Typography variant="body2" fontWeight="bold" gutterBottom>
                <RewardIcon fontSize="small" sx={{ mr: 0.5, verticalAlign: 'middle' }} />
                Récompenses:
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap">
                {questData.reward_xp > 0 && (
                  <Chip label={`${questData.reward_xp} XP`} size="small" color="primary" />
                )}
                {questData.reward_money > 0 && (
                  <Chip label={`${questData.reward_money} 💰`} size="small" color="success" />
                )}
                {questData.reward_items && questData.reward_items.length > 0 && (
                  <Chip label={`${questData.reward_items.length} items`} size="small" />
                )}
              </Box>
            </Box>

            {isCompleted && quest.completed_at && (
              <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                Complétée le {new Date(quest.completed_at).toLocaleDateString()}
              </Typography>
            )}
          </CardContent>

          <CardActions>
            {!isActive && !isCompleted && (
              <Button
                size="small"
                variant="contained"
                onClick={() => setSelectedQuest(quest)}
                startIcon={<AvailableIcon />}
              >
                Voir détails
              </Button>
            )}
            {isActive && (
              <>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => setSelectedQuest(quest)}
                >
                  Détails
                </Button>
                <Button
                  size="small"
                  color="error"
                  onClick={() => handleAbandonQuest(quest.id)}
                  disabled={loading}
                >
                  Abandonner
                </Button>
              </>
            )}
            {isCompleted && quest.times_completed > 1 && (
              <Chip
                label={`Complétée ${quest.times_completed}×`}
                size="small"
                color="success"
              />
            )}
          </CardActions>
        </Card>
      </Grid>
    );
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* Stats Header */}
      {questStats && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={3}>
              <Typography variant="h6" color="primary">{questStats.total_active}</Typography>
              <Typography variant="caption">Actives</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="h6" color="success.main">{questStats.total_completed}</Typography>
              <Typography variant="caption">Complétées</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="h6" color="warning.main">{questStats.total_xp_earned}</Typography>
              <Typography variant="caption">XP totale</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="h6" color="info.main">{questStats.total_money_earned}</Typography>
              <Typography variant="caption">Argent total</Typography>
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

      {/* Tabs */}
      <Paper sx={{ mb: 2 }}>
        <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)} centered>
          <Tab label="Disponibles" icon={<AvailableIcon />} iconPosition="start" />
          <Tab label="En cours" icon={<ActiveIcon />} iconPosition="start" />
          <Tab label="Complétées" icon={<CompletedIcon />} iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Quest List */}
      <Grid container spacing={2}>
        {currentTab === 0 && availableQuests.map(quest => renderQuestCard(quest))}
        {currentTab === 1 && activeQuests.map(quest => renderQuestCard(quest, true))}
        {currentTab === 2 && completedQuests.map(quest => renderQuestCard(quest, false, true))}
      </Grid>

      {/* Empty state */}
      {currentTab === 0 && availableQuests.length === 0 && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            Aucune quête disponible pour le moment
          </Typography>
        </Paper>
      )}
      {currentTab === 1 && activeQuests.length === 0 && !loading && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography color="text.secondary">
            Vous n'avez aucune quête active. Allez dans l'onglet "Disponibles" pour en accepter!
          </Typography>
        </Paper>
      )}

      {/* Quest Details Dialog */}
      {selectedQuest && (
        <Dialog
          open={Boolean(selectedQuest)}
          onClose={() => setSelectedQuest(null)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>
            {getTypeIcon((selectedQuest.quest || selectedQuest).quest_type)}{' '}
            {(selectedQuest.quest || selectedQuest).name}
          </DialogTitle>
          <DialogContent>
            <Box mb={2}>
              <Chip
                label={(selectedQuest.quest || selectedQuest).difficulty_display || (selectedQuest.quest || selectedQuest).difficulty}
                color={getDifficultyColor((selectedQuest.quest || selectedQuest).difficulty)}
                size="small"
              />
              <Chip
                label={`Niveau requis: ${(selectedQuest.quest || selectedQuest).required_level}`}
                size="small"
                sx={{ ml: 1 }}
              />
            </Box>

            <Typography variant="body1" paragraph>
              {(selectedQuest.quest || selectedQuest).description}
            </Typography>

            {(selectedQuest.quest || selectedQuest).story_text && (
              <Paper sx={{ p: 2, mb: 2, bgcolor: 'background.default' }}>
                <Typography variant="body2" fontStyle="italic">
                  "{(selectedQuest.quest || selectedQuest).story_text}"
                </Typography>
              </Paper>
            )}

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom>
              Objectifs
            </Typography>
            <List dense>
              {Object.entries((selectedQuest.quest || selectedQuest).requirements || {}).map(([type, items]) => (
                Array.isArray(items) && items.map((item, idx) => (
                  <ListItem key={`${type}-${idx}`}>
                    <ListItemText
                      primary={`${type === 'gather' ? 'Récolter' : type === 'craft' ? 'Fabriquer' : 'Objectif'}: ${item.quantity} ${item.material_id ? `(ID: ${item.material_id})` : ''}`}
                    />
                  </ListItem>
                ))
              ))}
            </List>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom>
              Récompenses
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {(selectedQuest.quest || selectedQuest).reward_xp > 0 && (
                <Chip label={`${(selectedQuest.quest || selectedQuest).reward_xp} XP`} color="primary" />
              )}
              {(selectedQuest.quest || selectedQuest).reward_money > 0 && (
                <Chip label={`${(selectedQuest.quest || selectedQuest).reward_money} 💰`} color="success" />
              )}
              {(selectedQuest.quest || selectedQuest).reward_items && (selectedQuest.quest || selectedQuest).reward_items.length > 0 && (
                (selectedQuest.quest || selectedQuest).reward_items.map((item, idx) => (
                  <Chip key={idx} label={`${item.quantity}× Item ID ${item.material_id}`} />
                ))
              )}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSelectedQuest(null)}>
              Fermer
            </Button>
            {currentTab === 0 && (
              <Button
                variant="contained"
                onClick={() => handleAcceptQuest(selectedQuest.id)}
                disabled={loading}
              >
                Accepter la quête
              </Button>
            )}
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};

export default QuestsTab;
