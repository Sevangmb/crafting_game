import React from 'react';
import { Box, Typography, Paper, LinearProgress, Divider, List, ListItem, ListItemText, Chip } from '@mui/material';

function SkillsTab({ craftingLevel, craftingXp, talents, tree }) {
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
                🎓 Compétences
                <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 400 }}>
                    Développez vos talents et compétences
                </Typography>
            </Typography>
            <Paper elevation={1} sx={{ borderRadius: 1, overflow: 'hidden' }}>
                <Box sx={{ p: 3 }}>
                    <Box sx={{ mb: 2 }}>
                        <Typography variant="h6">Artisanat</Typography>
                        <Typography variant="body2" sx={{ mb: 0.5 }}>Niveau {craftingLevel}</Typography>
                        <LinearProgress variant="determinate" value={Math.min(100, Math.round((craftingXp.xp / craftingXp.xp_to_next) * 100))} />
                        <Typography variant="caption" color="text.secondary">
                            {craftingXp.xp} / {craftingXp.xp_to_next} XP
                        </Typography>
                    </Box>

                    <Divider sx={{ my: 2 }} />

                    <Typography variant="subtitle1" sx={{ mb: 1 }}>Talents</Typography>
                    <List dense>
                        {tree.map((node) => {
                            const unlocked = talents.some((t) => t.talent_node?.code === node.code);
                            return (
                                <ListItem key={node.id} sx={{ px: 0 }}>
                                    <ListItemText
                                        primary={node.name}
                                        secondary={`${node.description} • Palier ${node.tier} • XP requis: ${node.xp_required}`}
                                    />
                                    <Chip label={unlocked ? 'Débloqué' : 'Verrouillé'} color={unlocked ? 'success' : 'default'} size="small" />
                                </ListItem>
                            );
                        })}
                    </List>
                </Box>
            </Paper>
        </Box>
    );
}

export default SkillsTab;
