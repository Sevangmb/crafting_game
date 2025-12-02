import React, { useState, useEffect } from 'react';
import {
    Box,
    Grid,
    Paper,
    Typography,
    Divider,
} from '@mui/material';
import axios from 'axios';
import Chart from 'react-apexcharts';
import NutritionRadarChart from './NutritionRadarChart';

const MonitorHeader = ({ title }) => (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5, borderBottom: '1px solid #444', pb: 0.5 }}>
        <Typography variant="caption" sx={{ color: '#fff', fontFamily: 'monospace', fontWeight: 'bold', fontSize: '0.75rem', letterSpacing: 1 }}>
            {title}
        </Typography>
        <Box sx={{ width: 0, height: 0, borderTop: '6px solid transparent', borderBottom: '6px solid transparent', borderRight: '6px solid #fff' }} />
    </Box>
);

const CircularGauge = ({ value, label, color = '#44ff44', size = 70 }) => {
    const options = {
        chart: {
            type: 'radialBar',
            sparkline: { enabled: true }
        },
        plotOptions: {
            radialBar: {
                hollow: { size: '60%' },
                track: { background: '#333' },
                dataLabels: {
                    show: true,
                    name: { show: false },
                    value: {
                        color: color,
                        fontSize: '14px',
                        fontWeight: 'bold',
                        offsetY: 5,
                        show: true,
                        formatter: (val) => `${Math.round(val)}%`
                    }
                }
            }
        },
        fill: { colors: [color] },
        stroke: { lineCap: 'round' }
    };

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Box sx={{ width: size, height: size }}>
                <Chart options={options} series={[value]} type="radialBar" width="100%" height="100%" />
            </Box>
            <Typography variant="caption" sx={{ color: '#888', fontSize: '0.6rem', mt: -1, textTransform: 'uppercase' }}>
                {label}
            </Typography>
        </Box>
    );
};

const MetabolismPanel = () => {
    const [healthData, setHealthData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [ecgData, setEcgData] = useState(Array(50).fill(0));

    useEffect(() => {
        loadHealthData();
        const interval = setInterval(loadHealthData, 10000);

        // Simulate ECG data updates
        const ecgInterval = setInterval(() => {
            setEcgData(prev => {
                const newData = [...prev.slice(1), Math.random() * 10 + (Math.random() > 0.9 ? 50 : 0)]; // Random spikes
                return newData;
            });
        }, 100);

        return () => {
            clearInterval(interval);
            clearInterval(ecgInterval);
        };
    }, []);

    const loadHealthData = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get('http://localhost:8000/api/character/health-display/', {
                headers: { Authorization: `Token ${token}` }
            });
            setHealthData(response.data);
            setLoading(false);
        } catch (err) {
            console.error('[MetabolismPanel] Error:', err);
            setLoading(false);
        }
    };

    if (loading || !healthData) {
        return (
            <Box sx={{ p: 4, textAlign: 'center', color: '#888' }}>
                <Typography>Chargement des données métaboliques...</Typography>
            </Box>
        );
    }

    const getNutrientColor = (percentage) => {
        if (percentage > 120) return '#ff4444'; // Too high
        if (percentage < 50) return '#ffaa00'; // Low
        return '#44ff44'; // Good
    };

    const ecgOptions = {
        chart: {
            type: 'line',
            animations: { enabled: false },
            toolbar: { show: false },
            sparkline: { enabled: true }
        },
        stroke: { curve: 'smooth', width: 2, colors: ['#ff9800'] },
        tooltip: { enabled: false },
        grid: { show: false },
        xaxis: { labels: { show: false } },
        yaxis: { show: false, min: 0, max: 100 }
    };

    return (
        <Box sx={{
            bgcolor: '#0a0a0a',
            color: '#fff',
            p: 1,
            fontFamily: 'monospace',
            minHeight: '100%'
        }}>
            <Grid container spacing={1}>
                {/* Left Column: ICU & Body */}
                <Grid item xs={12} md={4}>
                    {/* BCU ICU MONITOR */}
                    <Paper sx={{ bgcolor: '#111', p: 1, mb: 1, border: '1px solid #333', borderRadius: 0 }}>
                        <MonitorHeader title="MONITEUR ICU BCU" />

                        {/* ECG Graph */}
                        <Box sx={{ mb: 1, bgcolor: '#000', height: 80, position: 'relative', border: '1px solid #222', overflow: 'hidden' }}>
                            <Chart options={ecgOptions} series={[{ data: ecgData }]} type="line" height="100%" width="100%" />
                            <Box sx={{ position: 'absolute', right: 5, top: 5, textAlign: 'right' }}>
                                <Typography variant="caption" sx={{ color: '#ff9800', display: 'block', fontSize: '0.6rem' }}>BPM</Typography>
                                <Typography variant="h5" sx={{ color: '#ff9800', lineHeight: 1, fontWeight: 'bold' }}>
                                    {healthData.vital_signs?.heart_rate || 65}
                                </Typography>
                            </Box>
                        </Box>

                        {/* Other Vitals */}
                        <Box sx={{ display: 'grid', gap: 0.5 }}>
                            {/* Blood Pressure */}
                            <Box sx={{ bgcolor: '#000', p: 0.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: '3px solid #ff9800' }}>
                                <Typography variant="caption" sx={{ color: '#888' }}>PRESSION ARTÉRIELLE</Typography>
                                <Typography variant="body2" sx={{ color: '#ff9800', fontWeight: 'bold' }}>115/73</Typography>
                            </Box>
                            {/* Oxygen */}
                            <Box sx={{ bgcolor: '#000', p: 0.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: '3px solid #2196f3' }}>
                                <Typography variant="caption" sx={{ color: '#888' }}>OXYGÈNE (SpO2)</Typography>
                                <Typography variant="body2" sx={{ color: '#2196f3', fontWeight: 'bold' }}>
                                    {Math.round(healthData.vital_signs?.oxygen_level || 98)}%
                                </Typography>
                            </Box>
                            {/* Temp */}
                            <Box sx={{ bgcolor: '#000', p: 0.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderLeft: '3px solid #ffeb3b' }}>
                                <Typography variant="caption" sx={{ color: '#888' }}>TEMPÉRATURE</Typography>
                                <Typography variant="body2" sx={{ color: '#ffeb3b', fontWeight: 'bold' }}>
                                    {healthData.vital_signs?.body_temperature?.toFixed(1) || '36.5'}°C
                                </Typography>
                            </Box>
                        </Box>
                    </Paper>

                    {/* BCU BODY MONITOR */}
                    <Paper sx={{ bgcolor: '#111', p: 1, border: '1px solid #333', borderRadius: 0 }}>
                        <MonitorHeader title="MONITEUR CORPOREL BCU" />
                        <Grid container spacing={0.5}>
                            <Grid item xs={6}><Typography variant="caption" sx={{ color: '#888' }}>ÂGE</Typography></Grid>
                            <Grid item xs={6}><Typography variant="caption" sx={{ color: '#fff', float: 'right' }}>30 ans</Typography></Grid>

                            <Grid item xs={6}><Typography variant="caption" sx={{ color: '#888' }}>POIDS</Typography></Grid>
                            <Grid item xs={6}><Typography variant="caption" sx={{ color: '#fff', float: 'right' }}>{healthData.metabolism?.body_weight?.current?.toFixed(1)} kg</Typography></Grid>

                            <Grid item xs={6}><Typography variant="caption" sx={{ color: '#888' }}>GRAISSE</Typography></Grid>
                            <Grid item xs={6}><Typography variant="caption" sx={{ color: '#fff', float: 'right' }}>10.0%</Typography></Grid>

                            <Grid item xs={6}><Typography variant="caption" sx={{ color: '#888' }}>VOL. SANG</Typography></Grid>
                            <Grid item xs={6}><Typography variant="caption" sx={{ color: '#fff', float: 'right' }}>{healthData.vital_signs?.blood_volume?.toFixed(1)} l</Typography></Grid>
                        </Grid>

                        <Box sx={{ mt: 1, borderTop: '1px solid #333', pt: 0.5 }}>
                            <Typography variant="caption" sx={{ color: '#888', display: 'block' }}>MALADIES</Typography>
                            {healthData.active_diseases_count === 0 ? (
                                <Typography variant="caption" sx={{ color: '#4caf50' }}>AUCUNE</Typography>
                            ) : (
                                <Typography variant="caption" sx={{ color: '#f44336' }}>{healthData.active_diseases_count} ACTIVES</Typography>
                            )}
                        </Box>
                    </Paper>
                </Grid>

                {/* Center Column: Nutrition */}
                <Grid item xs={12} md={4}>
                    <Paper sx={{ bgcolor: '#111', p: 1, height: '100%', border: '1px solid #333', borderRadius: 0 }}>
                        <MonitorHeader title="MONITEUR NUTRITION BCU" />

                        {/* Calorie Bars */}
                        <Box sx={{ display: 'flex', gap: 0.5, mb: 2, bgcolor: '#000', p: 1 }}>
                            <Box sx={{ flex: 1 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                    <Typography variant="caption" sx={{ color: '#888' }}>APPORT</Typography>
                                    <Typography variant="caption" sx={{ color: '#fff' }}>{Math.round(healthData.metabolism?.calories?.current)} kcal</Typography>
                                </Box>
                                <Box sx={{ height: 10, bgcolor: '#333', width: '100%' }}>
                                    <Box sx={{ height: '100%', width: `${Math.min(100, healthData.metabolism?.calories?.percentage)}%`, bgcolor: '#4caf50' }} />
                                </Box>
                            </Box>
                            <Box sx={{ flex: 1 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                                    <Typography variant="caption" sx={{ color: '#888' }}>USAGE</Typography>
                                    <Typography variant="caption" sx={{ color: '#fff' }}>2500 kcal</Typography>
                                </Box>
                                <Box sx={{ height: 10, bgcolor: '#333', width: '100%' }}>
                                    <Box sx={{ height: '100%', width: '60%', bgcolor: '#f44336' }} />
                                </Box>
                            </Box>
                        </Box>

                        {/* Macros Circles */}
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 1, mb: 2 }}>
                            <CircularGauge label="PROTÉINES" value={healthData.metabolism?.proteins?.percentage || 0} color="#ff9800" />
                            <CircularGauge label="GLUCIDES" value={healthData.metabolism?.carbohydrates?.percentage || 0} color="#ffeb3b" />
                            <CircularGauge label="LIPIDES" value={healthData.metabolism?.fats?.percentage || 0} color="#4caf50" />
                            <CircularGauge label="EAU" value={healthData.metabolism?.water?.percentage || 0} color="#2196f3" />
                        </Box>

                        {/* Vitamins & Minerals - Enhanced with Radar Chart */}
                        <Box sx={{ mt: 2 }}>
                            <Typography variant="caption" sx={{ color: '#888', mb: 1, display: 'block' }}>VITAMINES & MINÉRAUX</Typography>
                            {healthData.metabolism?.vitamins && healthData.metabolism?.vitamins.length > 0 ? (
                                <NutritionRadarChart nutritionData={{
                                    vitamins: healthData.metabolism.vitamins.reduce((acc, v) => {
                                        const key = v.name.replace('Vitamine ', '').toLowerCase();
                                        acc[key] = v.level;
                                        return acc;
                                    }, {}),
                                    minerals: healthData.metabolism?.minerals?.reduce((acc, m) => {
                                        acc[m.name.toLowerCase()] = m.level;
                                        return acc;
                                    }, {}) || {}
                                }} />
                            ) : (
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                    {healthData.metabolism?.vitamins?.slice(0, 8).map((v, i) => (
                                        <Box key={i} sx={{
                                            width: 24, height: 24,
                                            borderRadius: '50%',
                                            border: `1px solid ${getNutrientColor(v.level)}`,
                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                            bgcolor: '#000'
                                        }}>
                                            <Typography variant="caption" sx={{ fontSize: '0.5rem', color: getNutrientColor(v.level) }}>
                                                {v.name.replace('Vitamine ', '').substring(0, 2)}
                                            </Typography>
                                        </Box>
                                    ))}
                                </Box>
                            )}
                        </Box>
                    </Paper>
                </Grid>

                {/* Right Column: Digestion */}
                <Grid item xs={12} md={4}>
                    <Paper sx={{ bgcolor: '#111', p: 1, height: '100%', border: '1px solid #333', borderRadius: 0 }}>
                        <MonitorHeader title="MONITEUR DIGESTION BCU" />

                        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2, mt: 2 }}>
                            <Box sx={{ textAlign: 'center' }}>
                                <CircularGauge
                                    label="ESTOMAC"
                                    value={healthData.metabolism?.stomach_fullness || 0}
                                    color="#2196f3"
                                    size={80}
                                />
                                <Typography variant="caption" sx={{ display: 'block', color: '#666', fontSize: '0.6rem' }}>VOLUME</Typography>
                            </Box>
                            <Box sx={{ textAlign: 'center' }}>
                                <CircularGauge
                                    label="INTESTIN"
                                    value={healthData.metabolism?.intestine_fullness || 0}
                                    color="#2196f3"
                                    size={80}
                                />
                                <Typography variant="caption" sx={{ display: 'block', color: '#666', fontSize: '0.6rem' }}>VOLUME</Typography>
                            </Box>
                            <Box sx={{ textAlign: 'center' }}>
                                <CircularGauge
                                    label="CÔLON"
                                    value={healthData.metabolism?.bowel_fullness || 0}
                                    color="#ff9800"
                                    size={80}
                                />
                                <Typography variant="caption" sx={{ display: 'block', color: '#666', fontSize: '0.6rem' }}>VOLUME</Typography>
                            </Box>
                            <Box sx={{ textAlign: 'center' }}>
                                <CircularGauge
                                    label="VESSIE"
                                    value={healthData.metabolism?.bladder_fullness || 0}
                                    color="#ffeb3b"
                                    size={80}
                                />
                                <Typography variant="caption" sx={{ display: 'block', color: '#666', fontSize: '0.6rem' }}>VOLUME</Typography>
                            </Box>
                        </Box>
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};

export default MetabolismPanel;
