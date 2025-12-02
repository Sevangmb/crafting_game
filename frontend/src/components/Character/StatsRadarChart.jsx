import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

const StatsRadarChart = ({ player }) => {
    if (!player) return null;

    const data = [
        {
            stat: 'Force',
            value: player.strength,
            fullMark: 100,
        },
        {
            stat: 'Agilité',
            value: player.agility,
            fullMark: 100,
        },
        {
            stat: 'Intelligence',
            value: player.intelligence,
            fullMark: 100,
        },
        {
            stat: 'Chance',
            value: player.luck,
            fullMark: 100,
        },
    ];

    return (
        <Paper sx={{
            bgcolor: '#1a1a1a',
            p: 3,
            border: '1px solid #333',
            borderRadius: 2
        }}>
            <Typography variant="h6" sx={{
                mb: 2,
                fontFamily: 'monospace',
                color: '#ff9800',
                borderBottom: '1px solid #333',
                pb: 1
            }}>
                📊 ATTRIBUTS
            </Typography>

            <Box sx={{ width: '100%', height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={data}>
                        <PolarGrid stroke="#333" />
                        <PolarAngleAxis
                            dataKey="stat"
                            tick={{ fill: '#888', fontSize: 12, fontFamily: 'monospace' }}
                        />
                        <PolarRadiusAxis
                            angle={90}
                            domain={[0, 100]}
                            tick={{ fill: '#666', fontSize: 10 }}
                        />
                        <Radar
                            name="Stats"
                            dataKey="value"
                            stroke="#ff9800"
                            fill="#ff9800"
                            fillOpacity={0.6}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1a1a1a',
                                border: '1px solid #333',
                                borderRadius: 4,
                                fontFamily: 'monospace'
                            }}
                            labelStyle={{ color: '#ff9800' }}
                        />
                    </RadarChart>
                </ResponsiveContainer>
            </Box>

            <Box sx={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: 1,
                mt: 2
            }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 12, height: 12, bgcolor: '#f44336', borderRadius: '50%' }} />
                    <Typography variant="caption" sx={{ color: '#888', fontFamily: 'monospace' }}>
                        Force: {player.strength}
                    </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 12, height: 12, bgcolor: '#4caf50', borderRadius: '50%' }} />
                    <Typography variant="caption" sx={{ color: '#888', fontFamily: 'monospace' }}>
                        Agilité: {player.agility}
                    </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 12, height: 12, bgcolor: '#2196f3', borderRadius: '50%' }} />
                    <Typography variant="caption" sx={{ color: '#888', fontFamily: 'monospace' }}>
                        Intelligence: {player.intelligence}
                    </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 12, height: 12, bgcolor: '#ff9800', borderRadius: '50%' }} />
                    <Typography variant="caption" sx={{ color: '#888', fontFamily: 'monospace' }}>
                        Chance: {player.luck}
                    </Typography>
                </Box>
            </Box>
        </Paper>
    );
};

export default StatsRadarChart;
