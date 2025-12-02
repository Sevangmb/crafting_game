import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper } from '@mui/material';
import RecipeGraphTabs from '../crafting/RecipeGraphTabs';
import { recipesAPI } from '../../services/api';

function RecipeGraphTab() {
    const [recipes, setRecipes] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const res = await recipesAPI.getAll();
                setRecipes(res.data || []);
            } catch (e) {
                setRecipes([]);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, []);

    return (
        <Box sx={{ maxWidth: '1200px', mx: 'auto' }}>
            <Typography variant="h4" gutterBottom sx={{
                fontWeight: 700,
                color: 'primary.main',
                mb: 3,
                display: 'flex',
                alignItems: 'center',
                gap: 2
            }}>
                🔗 Graphe des Recettes
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 400 }}>
                    Visualisez les dépendances entre les crafts
                </Typography>
            </Typography>
            <Paper elevation={1} sx={{ borderRadius: 3, overflow: 'hidden' }}>
                {loading ? (
                    <Box sx={{ p: 3, textAlign: 'center' }}>Chargement...</Box>
                ) : (
                    <RecipeGraphTabs recipes={recipes} />
                )}
            </Paper>
        </Box>
    );
}

export default RecipeGraphTab;
