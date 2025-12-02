import React, { useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Paper,
  Divider,
} from '@mui/material';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
  ResponsiveContainer,
} from 'recharts';
import { useInventory, useRecipes } from '../../hooks';
import { useGameStore, selectPlayer } from '../../stores/useGameStore';
import { RARITY_COLORS } from '../../utils/gameLogic';

// Couleurs variées pour les charts
const CHART_COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1'];

const Dashboard = () => {
  const player = useGameStore(selectPlayer);
  const { inventory, flatInventory, stats: invStats, foodItems, materialItems } = useInventory();
  const { stats: craftStats, craftableRecipes } = useRecipes();

  // Stats d'inventaire détaillées (utiliser invStats comme base)
  const inventoryStatsDetailed = useMemo(() => {
    const list = Array.isArray(flatInventory) ? flatInventory : [];
    const total = list.length;
    const totalQuantity = list.reduce((sum, item) => sum + item.quantity, 0);
    const foodCount = list.filter((i) => i.material.is_food).length;

    // Compter par rareté
    const rarityData = list.reduce((acc, item) => {
      const rarity = item.material.rarity;
      const existing = acc.find((r) => r.name === rarity);
      if (existing) {
        existing.count += 1;
        existing.quantity += item.quantity;
      } else {
        acc.push({
          name: rarity,
          count: 1,
          quantity: item.quantity,
        });
      }
      return acc;
    }, []);

    // Top 5 des items par quantité
    const topItems = [...list]
      .sort((a, b) => b.quantity - a.quantity)
      .slice(0, 5)
      .map((item) => ({
        name: item.material.name,
        quantity: item.quantity,
        icon: item.material.icon,
      }));

    return {
      total,
      totalQuantity,
      foodCount,
      materialCount: total - foodCount,
      rarityData,
      topItems,
    };
  }, [flatInventory]);

  // Utiliser directement craftStats du hook useRecipes

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        📊 Tableau de bord
      </Typography>

      {/* Stats principales */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <CardContent>
              <Typography color="white" variant="h6">
                Niveau
              </Typography>
              <Typography color="white" variant="h3" sx={{ fontWeight: 'bold' }}>
                {player?.level || 0}
              </Typography>
              <Typography color="white" variant="body2">
                XP: {player?.experience || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <CardContent>
              <Typography color="white" variant="h6">
                Énergie
              </Typography>
              <Typography color="white" variant="h3" sx={{ fontWeight: 'bold' }}>
                {player?.energy || 0}
              </Typography>
              <Typography color="white" variant="body2">
                / {player?.max_energy || 100}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <CardContent>
              <Typography color="white" variant="h6">
                Objets
              </Typography>
              <Typography color="white" variant="h3" sx={{ fontWeight: 'bold' }}>
                {inventoryStatsDetailed.total}
              </Typography>
              <Typography color="white" variant="body2">
                Qté totale: {inventoryStatsDetailed.totalQuantity}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' }}>
            <CardContent>
              <Typography color="white" variant="h6">
                Crafts
              </Typography>
              <Typography color="white" variant="h3" sx={{ fontWeight: 'bold' }}>
                {craftStats.totalCrafts}
              </Typography>
              <Typography color="white" variant="body2">
                Recettes utilisées
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        {/* Distribution par rareté */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Distribution par rareté
              </Typography>
              {inventoryStatsDetailed.rarityData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={inventoryStatsDetailed.rarityData}
                      dataKey="count"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      label={(entry) => `${entry.name}: ${entry.count}`}
                    >
                      {inventoryStatsDetailed.rarityData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={RARITY_COLORS[entry.name] || CHART_COLORS[index % CHART_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  Aucune donnée disponible
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Top 5 des items */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top 5 des items (quantité)
              </Typography>
              {inventoryStatsDetailed.topItems.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={inventoryStatsDetailed.topItems}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="quantity" fill="#8884d8">
                      {inventoryStatsDetailed.topItems.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  Aucune donnée disponible
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Top recettes craftées */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recettes les plus craftées
              </Typography>
              {craftStats.topRecipes.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={craftStats.topRecipes} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={150} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                  Aucune recette craftée pour le moment
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Liste détaillée */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Inventaire par type
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Paper sx={{ p: 2, flex: 1, minWidth: 120, textAlign: 'center', bgcolor: 'success.light' }}>
                  <Typography variant="h4">{inventoryStatsDetailed.foodCount}</Typography>
                  <Typography variant="body2">🍎 Nourriture</Typography>
                </Paper>
                <Paper sx={{ p: 2, flex: 1, minWidth: 120, textAlign: 'center', bgcolor: 'info.light' }}>
                  <Typography variant="h4">{inventoryStatsDetailed.materialCount}</Typography>
                  <Typography variant="body2">⚒️ Matériaux</Typography>
                </Paper>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Stats joueur */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Profil du joueur
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Paper sx={{ p: 2, display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>Position</Typography>
                  <Typography sx={{ fontWeight: 'bold' }}>
                    ({player?.grid_x || 0}, {player?.grid_y || 0})
                  </Typography>
                </Paper>
                <Paper sx={{ p: 2, display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>Énergie</Typography>
                  <Typography sx={{ fontWeight: 'bold' }}>
                    {player?.energy || 0} / {player?.max_energy || 100}
                  </Typography>
                </Paper>
                <Paper sx={{ p: 2, display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>Niveau</Typography>
                  <Typography sx={{ fontWeight: 'bold' }}>{player?.level || 0}</Typography>
                </Paper>
                <Paper sx={{ p: 2, display: 'flex', justifyContent: 'space-between' }}>
                  <Typography>Expérience</Typography>
                  <Typography sx={{ fontWeight: 'bold' }}>{player?.experience || 0} XP</Typography>
                </Paper>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
