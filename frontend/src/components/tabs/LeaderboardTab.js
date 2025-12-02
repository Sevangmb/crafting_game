import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Avatar,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  TrendingUp as LevelIcon,
  AttachMoney as WealthIcon,
  LocalFlorist as GathererIcon,
  Build as CrafterIcon,
  Explore as ExplorerIcon,
  SportsMma as CombatantIcon,
  Assignment as QuestsIcon,
} from '@mui/icons-material';
import { leaderboardAPI } from '../../services/api';

const LeaderboardTab = () => {
  const [currentCategory, setCurrentCategory] = useState('level');
  const [leaderboard, setLeaderboard] = useState([]);
  const [myRanks, setMyRanks] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const categories = [
    { value: 'level', label: 'Niveau', icon: <LevelIcon />, color: '#9c27b0' },
    { value: 'wealth', label: 'Richesse', icon: <WealthIcon />, color: '#4caf50' },
    { value: 'gatherer', label: 'Récolteur', icon: <GathererIcon />, color: '#8bc34a' },
    { value: 'crafter', label: 'Artisan', icon: <CrafterIcon />, color: '#ff9800' },
    { value: 'explorer', label: 'Explorateur', icon: <ExplorerIcon />, color: '#2196f3' },
    { value: 'combatant', label: 'Combattant', icon: <CombatantIcon />, color: '#f44336' },
    { value: 'quests', label: 'Quêtes', icon: <QuestsIcon />, color: '#00bcd4' },
  ];

  useEffect(() => {
    loadLeaderboard();
    loadMyRanks();
  }, [currentCategory]);

  const loadLeaderboard = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await leaderboardAPI.getAll(currentCategory, 100);
      setLeaderboard(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors du chargement du classement');
    } finally {
      setLoading(false);
    }
  };

  const loadMyRanks = async () => {
    try {
      const response = await leaderboardAPI.getMyRanks();
      setMyRanks(response.data);
    } catch (err) {
      console.error('Erreur chargement rangs:', err);
    }
  };

  const getMedalIcon = (rank) => {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return `#${rank}`;
  };

  const getCategoryIcon = (category) => {
    const cat = categories.find(c => c.value === category);
    return cat ? cat.icon : <TrophyIcon />;
  };

  const getCategoryColor = (category) => {
    const cat = categories.find(c => c.value === category);
    return cat ? cat.color : '#757575';
  };

  const formatScore = (score, category) => {
    if (category === 'level') {
      const level = Math.floor(score / 1000000);
      const xp = score % 1000000;
      return `Niv ${level} (${xp} XP)`;
    }
    if (category === 'wealth') {
      return `${score.toLocaleString()} 💰`;
    }
    return score.toLocaleString();
  };

  return (
    <Box sx={{ width: '100%', p: 2 }}>
      {/* My Ranks Summary */}
      {myRanks && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="h6" gutterBottom>
            Mes Classements
          </Typography>
          <Grid container spacing={1}>
            {categories.map(cat => {
              const myRank = myRanks[cat.value];
              return (
                <Grid item xs={12} sm={6} md={3} key={cat.value}>
                  <Card
                    sx={{
                      bgcolor: currentCategory === cat.value ? `${cat.color}20` : 'background.paper',
                      borderLeft: `4px solid ${cat.color}`,
                      cursor: 'pointer',
                    }}
                    onClick={() => setCurrentCategory(cat.value)}
                  >
                    <CardContent sx={{ py: 1.5 }}>
                      <Box display="flex" alignItems="center" gap={1}>
                        {React.cloneElement(cat.icon, { sx: { color: cat.color } })}
                        <Box flexGrow={1}>
                          <Typography variant="caption" color="text.secondary">
                            {cat.label}
                          </Typography>
                          {myRank ? (
                            <>
                              <Typography variant="h6">
                                {getMedalIcon(myRank.rank)}
                              </Typography>
                              <Typography variant="caption">
                                Score: {myRank.score.toLocaleString()}
                              </Typography>
                            </>
                          ) : (
                            <Typography variant="body2" color="text.secondary">
                              Non classé
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              );
            })}
          </Grid>
        </Paper>
      )}

      {/* Error Alert */}
      {error && (
        <Alert severity="error" onClose={() => setError('')} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Category Tabs */}
      <Paper sx={{ mb: 2 }}>
        <Tabs
          value={currentCategory}
          onChange={(e, v) => setCurrentCategory(v)}
          variant="scrollable"
          scrollButtons="auto"
        >
          {categories.map(cat => (
            <Tab
              key={cat.value}
              value={cat.value}
              label={cat.label}
              icon={cat.icon}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Paper>

      {/* Loading */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Leaderboard Table */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell width="80px">Rang</TableCell>
                <TableCell>Joueur</TableCell>
                <TableCell align="right">Score</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {leaderboard.map((entry) => {
                const isTopThree = entry.rank <= 3;
                const isMe = myRanks && myRanks[currentCategory]?.rank === entry.rank;

                return (
                  <TableRow
                    key={entry.id}
                    sx={{
                      bgcolor: isMe ? 'action.selected' : 'inherit',
                      '&:hover': {
                        bgcolor: 'action.hover',
                      },
                    }}
                  >
                    <TableCell>
                      <Typography
                        variant="h6"
                        sx={{
                          fontSize: isTopThree ? '1.5rem' : '1rem',
                          fontWeight: isTopThree ? 'bold' : 'normal',
                        }}
                      >
                        {getMedalIcon(entry.rank)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Avatar
                          sx={{
                            bgcolor: getCategoryColor(currentCategory),
                            width: isTopThree ? 40 : 32,
                            height: isTopThree ? 40 : 32,
                          }}
                        >
                          {entry.player_name[0].toUpperCase()}
                        </Avatar>
                        <Box>
                          <Typography variant="body1" fontWeight={isMe ? 'bold' : 'normal'}>
                            {entry.player_name}
                            {isMe && (
                              <Chip
                                label="Vous"
                                size="small"
                                color="primary"
                                sx={{ ml: 1 }}
                              />
                            )}
                          </Typography>
                          {entry.metadata && (
                            <Typography variant="caption" color="text.secondary">
                              {JSON.stringify(entry.metadata).substring(0, 50)}...
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Typography
                        variant={isTopThree ? 'h6' : 'body1'}
                        fontWeight={isTopThree ? 'bold' : 'normal'}
                        color={isTopThree ? getCategoryColor(currentCategory) : 'text.primary'}
                      >
                        {formatScore(entry.score, currentCategory)}
                      </Typography>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Empty State */}
        {!loading && leaderboard.length === 0 && (
          <Box p={4} textAlign="center">
            <Typography color="text.secondary">
              Aucune entrée dans ce classement pour le moment
            </Typography>
          </Box>
        )}
      </Paper>

      {/* Footer Info */}
      <Paper sx={{ p: 2, mt: 2 }}>
        <Typography variant="caption" color="text.secondary">
          Les classements sont mis à jour périodiquement. Seuls les 100 premiers joueurs sont affichés.
        </Typography>
      </Paper>
    </Box>
  );
};

export default LeaderboardTab;
