import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
import ReactApexChart from 'react-apexcharts';

const SurvivalGauges = ({ player }) => {
    if (!player) return null;

    const gauges = [
        {
            name: 'Santé',
            value: player.health,
            max: player.max_health,
            color: '#f44336',
            icon: '❤️'
        },
        {
            name: 'Énergie',
            value: player.energy,
            max: player.max_energy,
            color: '#ffc107',
            icon: '⚡'
        },
        {
            name: 'Faim',
            value: player.hunger,
            max: player.max_hunger,
            color: '#ff9800',
            icon: '🍖'
        },
        {
            name: 'Soif',
            value: player.thirst,
            max: player.max_thirst,
            color: '#2196f3',
            icon: '💧'
        }
    ];

    return (
        <Paper sx={{
            bgcolor: '#1a1a1a',
            p: 3,
            border: '1px solid #333',
            borderRadius: 2
        }}>
            <Typography variant="h6" sx={{
                mb: 3,
                fontFamily: 'monospace',
                color: '#ff9800',
                borderBottom: '1px solid #333',
                pb: 1
            }}>
                💪 SURVIE
            </Typography>

            <Box sx={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: 3
            }}>
                {gauges.map((gauge) => {
                    const percentage = (gauge.value / gauge.max) * 100;

                    const options = {
                        chart: {
                            type: 'radialBar',
                            sparkline: {
                                enabled: true
                            }
                        },
                        plotOptions: {
                            radialBar: {
                                startAngle: -90,
                                endAngle: 90,
                                track: {
                                    background: '#222',
                                    strokeWidth: '97%',
                                    margin: 5,
                                },
                                dataLabels: {
                                    name: {
                                        show: false
                                    },
                                    value: {
                                        offsetY: -10,
                                        fontSize: '20px',
                                        fontFamily: 'monospace',
                                        color: '#fff',
                                        formatter: function (val) {
                                            return Math.round(val) + '%';
                                        }
                                    }
                                }
                            }
                        },
                        fill: {
                            type: 'solid',
                            colors: [gauge.color]
                        },
                        stroke: {
                            lineCap: 'round'
                        }
                    };

                    const series = [percentage];

                    return (
                        <Box key={gauge.name} sx={{ textAlign: 'center' }}>
                            <Typography variant="body2" sx={{
                                mb: 1,
                                fontFamily: 'monospace',
                                color: '#888',
                                fontSize: '0.9rem'
                            }}>
                                {gauge.icon} {gauge.name}
                            </Typography>
                            <ReactApexChart
                                options={options}
                                series={series}
                                type="radialBar"
                                height={150}
                            />
                            <Typography variant="caption" sx={{
                                color: '#666',
                                fontFamily: 'monospace',
                                display: 'block',
                                mt: -1
                            }}>
                                {gauge.value} / {gauge.max}
                            </Typography>
                        </Box>
                    );
                })}
            </Box>
        </Paper>
    );
};

export default SurvivalGauges;
