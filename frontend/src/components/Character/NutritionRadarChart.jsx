import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const NutritionRadarChart = ({ nutritionData }) => {
    if (!nutritionData) return null;

    // Prepare vitamins data
    const vitaminsData = Object.entries(nutritionData.vitamins || {}).map(([key, value]) => ({
        nutrient: `Vit. ${key.toUpperCase()}`,
        value: value,
        fullMark: 100
    }));

    // Prepare minerals data
    const mineralsData = Object.entries(nutritionData.minerals || {}).map(([key, value]) => ({
        nutrient: key.charAt(0).toUpperCase() + key.slice(1),
        value: value,
        fullMark: 100
    }));

    const getColor = (value) => {
        if (value >= 80) return '#4caf50';
        if (value >= 60) return '#8bc34a';
        if (value >= 40) return '#ff9800';
        return '#f44336';
    };

    return (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3 }}>
            {/* Vitamins Radar */}
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
                    💊 VITAMINES
                </Typography>

                <Box sx={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <RadarChart data={vitaminsData}>
                            <PolarGrid stroke="#333" />
                            <PolarAngleAxis
                                dataKey="nutrient"
                                tick={{ fill: '#888', fontSize: 11, fontFamily: 'monospace' }}
                            />
                            <PolarRadiusAxis
                                angle={90}
                                domain={[0, 100]}
                                tick={{ fill: '#666', fontSize: 9 }}
                            />
                            <Radar
                                name="Vitamines"
                                dataKey="value"
                                stroke="#9c27b0"
                                fill="#9c27b0"
                                fillOpacity={0.6}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1a1a1a',
                                    border: '1px solid #333',
                                    borderRadius: 4,
                                    fontFamily: 'monospace'
                                }}
                                labelStyle={{ color: '#9c27b0' }}
                                formatter={(value) => [`${value}%`, 'Niveau']}
                            />
                        </RadarChart>
                    </ResponsiveContainer>
                </Box>

                <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {vitaminsData.map((vit) => (
                        <Box key={vit.nutrient} sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.5,
                            px: 1,
                            py: 0.5,
                            bgcolor: '#222',
                            borderRadius: 1,
                            border: `1px solid ${getColor(vit.value)}`
                        }}>
                            <Box sx={{
                                width: 8,
                                height: 8,
                                bgcolor: getColor(vit.value),
                                borderRadius: '50%'
                            }} />
                            <Typography variant="caption" sx={{ color: '#888', fontFamily: 'monospace', fontSize: '0.7rem' }}>
                                {vit.nutrient}: {vit.value}%
                            </Typography>
                        </Box>
                    ))}
                </Box>
            </Paper>

            {/* Minerals Radar */}
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
                    ⚗️ MINÉRAUX
                </Typography>

                <Box sx={{ width: '100%', height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <RadarChart data={mineralsData}>
                            <PolarGrid stroke="#333" />
                            <PolarAngleAxis
                                dataKey="nutrient"
                                tick={{ fill: '#888', fontSize: 11, fontFamily: 'monospace' }}
                            />
                            <PolarRadiusAxis
                                angle={90}
                                domain={[0, 100]}
                                tick={{ fill: '#666', fontSize: 9 }}
                            />
                            <Radar
                                name="Minéraux"
                                dataKey="value"
                                stroke="#00bcd4"
                                fill="#00bcd4"
                                fillOpacity={0.6}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#1a1a1a',
                                    border: '1px solid #333',
                                    borderRadius: 4,
                                    fontFamily: 'monospace'
                                }}
                                labelStyle={{ color: '#00bcd4' }}
                                formatter={(value) => [`${value}%`, 'Niveau']}
                            />
                        </RadarChart>
                    </ResponsiveContainer>
                </Box>

                <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {mineralsData.map((min) => (
                        <Box key={min.nutrient} sx={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 0.5,
                            px: 1,
                            py: 0.5,
                            bgcolor: '#222',
                            borderRadius: 1,
                            border: `1px solid ${getColor(min.value)}`
                        }}>
                            <Box sx={{
                                width: 8,
                                height: 8,
                                bgcolor: getColor(min.value),
                                borderRadius: '50%'
                            }} />
                            <Typography variant="caption" sx={{ color: '#888', fontFamily: 'monospace', fontSize: '0.7rem' }}>
                                {min.nutrient}: {min.value}%
                            </Typography>
                        </Box>
                    ))}
                </Box>
            </Paper>
        </Box>
    );
};

export default NutritionRadarChart;
