import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
import ReactApexChart from 'react-apexcharts';

const ProgressionChart = ({ player }) => {
    if (!player) return null;

    // Calculate XP for current and next level
    const currentLevel = player.level;
    const currentXP = player.experience;
    const xpForNextLevel = player.get_xp_for_level ? player.get_xp_for_level(currentLevel + 1) : (currentLevel + 1) * 100;
    const xpProgress = (currentXP / xpForNextLevel) * 100;

    const options = {
        chart: {
            type: 'area',
            height: 200,
            sparkline: {
                enabled: false
            },
            toolbar: {
                show: false
            },
            background: 'transparent'
        },
        dataLabels: {
            enabled: false
        },
        stroke: {
            curve: 'smooth',
            width: 2
        },
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.7,
                opacityTo: 0.2,
                stops: [0, 90, 100]
            }
        },
        xaxis: {
            categories: ['Niveau actuel', 'Progression', 'Prochain niveau'],
            labels: {
                style: {
                    colors: '#888',
                    fontSize: '10px',
                    fontFamily: 'monospace'
                }
            },
            axisBorder: {
                color: '#333'
            },
            axisTicks: {
                color: '#333'
            }
        },
        yaxis: {
            show: true,
            labels: {
                style: {
                    colors: '#666',
                    fontSize: '10px',
                    fontFamily: 'monospace'
                },
                formatter: function (val) {
                    return Math.round(val) + ' XP';
                }
            }
        },
        grid: {
            borderColor: '#333',
            strokeDashArray: 4
        },
        colors: ['#4caf50'],
        tooltip: {
            theme: 'dark',
            style: {
                fontSize: '12px',
                fontFamily: 'monospace'
            },
            y: {
                formatter: function (val) {
                    return val + ' XP';
                }
            }
        }
    };

    const series = [{
        name: 'Expérience',
        data: [0, currentXP, xpForNextLevel]
    }];

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
                📈 PROGRESSION
            </Typography>

            <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2" sx={{ color: '#888', fontFamily: 'monospace' }}>
                        Niveau {currentLevel}
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#4caf50', fontFamily: 'monospace', fontWeight: 'bold' }}>
                        {xpProgress.toFixed(1)}%
                    </Typography>
                </Box>
                <Box sx={{
                    width: '100%',
                    height: 8,
                    bgcolor: '#222',
                    borderRadius: 1,
                    overflow: 'hidden'
                }}>
                    <Box sx={{
                        width: `${xpProgress}%`,
                        height: '100%',
                        bgcolor: '#4caf50',
                        transition: 'width 0.3s ease'
                    }} />
                </Box>
                <Typography variant="caption" sx={{ color: '#666', fontFamily: 'monospace', display: 'block', mt: 0.5 }}>
                    {currentXP} / {xpForNextLevel} XP
                </Typography>
            </Box>

            <ReactApexChart
                options={options}
                series={series}
                type="area"
                height={200}
            />
        </Paper>
    );
};

export default ProgressionChart;
