import React from 'react';
import { Box, Typography, LinearProgress, Grid, Paper, Divider } from '@mui/material';
import { FitnessCenter, Speed, Lightbulb, Favorite } from '@mui/icons-material';
import Chart from 'react-apexcharts';
import StatsRadarChart from './StatsRadarChart';
import ProgressionChart from './ProgressionChart';

const MonitorHeader = ({ title }) => (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5, borderBottom: '1px solid #444', pb: 0.5 }}>
        <Typography variant="caption" sx={{ color: '#fff', fontFamily: 'monospace', fontWeight: 'bold', fontSize: '0.75rem', letterSpacing: 1 }}>
            {title}
        </Typography>
        <Box sx={{ width: 0, height: 0, borderTop: '6px solid transparent', borderBottom: '6px solid transparent', borderRight: '6px solid #fff' }} />
    </Box>
);

const StatBar = ({ label, value, max = 5, color = '#fff' }) => (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1, borderRight: '1px solid #333', px: 1 }}>
        <Typography variant="caption" sx={{ color: '#888', fontWeight: 'bold', fontSize: '0.7rem' }}>{label}</Typography>
        <Typography variant="h6" sx={{ color: '#fff', fontWeight: 'bold', lineHeight: 1, my: 0.5 }}>{value.toFixed(2)}</Typography>
        <Box sx={{ width: '100%', height: 4, bgcolor: '#333', mt: 0.5 }}>
            <Box sx={{ width: `${(value / max) * 100}%`, height: '100%', bgcolor: color }} />
        </Box>
    </Box>
);

const PerformanceRow = ({ label, value, unit = '', barValue = 0, barColor = '#fff' }) => (
    <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5, fontSize: '0.7rem' }}>
        <Typography sx={{ color: '#ccc', flex: 1, fontSize: 'inherit', fontFamily: 'monospace' }}>{label}</Typography>
        <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            {barValue > 0 && (
                <Box sx={{ flex: 1, height: 6, bgcolor: '#333' }}>
                    <Box sx={{ width: `${barValue}%`, height: '100%', bgcolor: barColor }} />
                </Box>
            )}
            <Typography sx={{ color: '#fff', fontSize: 'inherit', fontFamily: 'monospace', minWidth: 60, textAlign: 'right' }}>
                {value}{unit}
            </Typography>
        </Box>
    </Box>
);

const AttributesPanel = ({ player }) => {
    if (!player) return null;

    const graphOptions = {
        chart: {
            type: 'area',
            sparkline: { enabled: true },
            animations: { enabled: false }
        },
        stroke: { curve: 'straight', width: 1, colors: ['#44ff44'] },
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.3,
                opacityTo: 0.0,
                stops: [0, 100]
            }
        },
        tooltip: { enabled: false },
        colors: ['#44ff44']
    };

    const graphSeries = [{
        data: [30, 40, 35, 50, 49, 60, 70, 91, 125]
    }];

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 2 }}>
            {/* Stats Radar Chart and Progression Chart */}
            <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                    <StatsRadarChart player={player} />
                </Grid>
                <Grid item xs={12} md={6}>
                    <ProgressionChart player={player} />
                </Grid>
            </Grid>

            {/* Original Performance Monitor */}
            <Paper sx={{ bgcolor: '#111', p: 1, border: '1px solid #333', borderRadius: 0 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <StatBar label="STR" value={player.strength || 3.0} color="#ff4444" />
                    <StatBar label="CON" value={player.constitution || 3.0} color="#ffaa00" />
                    <StatBar label="DEX" value={player.agility || 3.0} color="#44ff44" />
                    <StatBar label="INT" value={player.intelligence || 3.0} color="#4488ff" />
                </Box>

                {/* Graph Area */}
                <Box sx={{ mt: 1, height: 60, bgcolor: '#000', border: '1px solid #222', position: 'relative' }}>
                    <Typography variant="caption" sx={{ position: 'absolute', top: 2, left: 2, color: '#666', fontSize: '0.6rem', zIndex: 1 }}>Zoom 7d 30d</Typography>
                    <Chart options={graphOptions} series={graphSeries} type="area" height="100%" width="100%" />
                </Box>

                {/* Skill Progress Bars (Mini) */}
                <Box sx={{ mt: 1 }}>
                    <PerformanceRow label="Boxing" value="3/10,000" barValue={10} barColor="#888" />
                    <PerformanceRow label="Rifles" value="0/100,000" barValue={0} barColor="#888" />
                    <PerformanceRow label="Melee Weapons" value="1,856/100,000" barValue={25} barColor="#888" />
                    <PerformanceRow label="Handgun" value="321,761/1,000,000" barValue={32} barColor="#fff" />
                </Box>
            </Paper>

            {/* BCU PERFORMANCE MONITOR */}
            <Paper sx={{ bgcolor: '#111', p: 1, border: '1px solid #333', borderRadius: 0 }}>
                <MonitorHeader title="MONITEUR PERFORMANCE BCU" />

                <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                        <PerformanceRow label="VITESSE MARCHE" value="5.5" unit=" km/h" barValue={30} barColor="#fff" />
                        <PerformanceRow label="VITESSE JOGGING" value="11.4" unit=" km/h" barValue={60} barColor="#fff" />
                        <PerformanceRow label="VITESSE COURSE" value="20.3" unit=" km/h" barValue={90} barColor="#fff" />
                        <Divider sx={{ borderColor: '#333', my: 0.5 }} />
                        <PerformanceRow label="POIDS ÉQUIPEMENT" value="24" unit="/41kg" barValue={58} barColor="#fff" />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <PerformanceRow label="ENDURANCE" value="100" unit="%" barValue={100} barColor="#fff" />
                        <PerformanceRow label="MSR" value="0" unit="%" barValue={0} barColor="#fff" />
                        <PerformanceRow label="CHARGE" value="100" unit="%" barValue={100} barColor="#fff" />
                    </Grid>
                </Grid>

                <Box sx={{ mt: 2 }}>
                    <MonitorHeader title="STATS PERFORMANCE" />
                    <Grid container spacing={2}>
                        <Grid item xs={6}>
                            <PerformanceRow label="VITESSE SOIN" value="100" unit="%" barValue={100} barColor="#fff" />
                            <PerformanceRow label="VITESSE REPAS" value="100" unit="%" barValue={100} barColor="#fff" />
                        </Grid>
                        <Grid item xs={6}>
                            <PerformanceRow label="BONUS DÉGÂTS MÊLÉE" value="52" unit="%" barValue={52} barColor="#fff" />
                            <PerformanceRow label="GAIN FORCE" value="100" unit="%" barValue={100} barColor="#fff" />
                        </Grid>
                    </Grid>
                </Box>
            </Paper>
        </Box>
    );
};

export default AttributesPanel;
