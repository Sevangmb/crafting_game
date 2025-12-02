import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Tooltip } from '@mui/material';
import axios from 'axios';

const TimeDisplay = () => {
    const [timeInfo, setTimeInfo] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchTime = async () => {
        try {
            const response = await axios.get('/api/time/');
            setTimeInfo(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch time:', error);
        }
    };

    useEffect(() => {
        // Initial fetch
        fetchTime();

        // Update every 30 seconds
        const interval = setInterval(fetchTime, 30000);

        return () => clearInterval(interval);
    }, []);

    if (loading || !timeInfo) {
        return null;
    }

    return (
        <Tooltip
            title={
                <Box>
                    <Typography variant="caption" display="block">
                        {timeInfo.date}
                    </Typography>
                    <Typography variant="caption" display="block">
                        Lever: {timeInfo.sunrise} | Coucher: {timeInfo.sunset}
                    </Typography>
                </Box>
            }
            arrow
        >
            <Paper
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    px: 2,
                    py: 0.5,
                    bgcolor: '#1a1a1a',
                    border: '1px solid #333',
                    borderRadius: 1,
                    cursor: 'pointer',
                    '&:hover': {
                        bgcolor: '#252525',
                        borderColor: '#444',
                    }
                }}
            >
                <Typography
                    variant="h6"
                    sx={{
                        fontSize: '1.5rem',
                        lineHeight: 1,
                    }}
                >
                    {timeInfo.time_of_day_icon}
                </Typography>
                <Box>
                    <Typography
                        variant="body2"
                        sx={{
                            fontFamily: 'monospace',
                            fontWeight: 'bold',
                            color: '#ff9800',
                            lineHeight: 1.2,
                        }}
                    >
                        {timeInfo.current_time}
                    </Typography>
                    <Typography
                        variant="caption"
                        sx={{
                            color: '#888',
                            fontSize: '0.65rem',
                            lineHeight: 1,
                        }}
                    >
                        {timeInfo.time_of_day_label}
                    </Typography>
                </Box>
            </Paper>
        </Tooltip>
    );
};

export default TimeDisplay;
