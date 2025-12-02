import React from 'react';
import { Paper, Typography, Box, Button } from '@mui/material';
import { Store, AccountBalance } from '@mui/icons-material';

function MapPOI({ pois, banks, onPOIClick, onBankClick }) {
    if ((!pois || pois.length === 0) && (!banks || banks.length === 0)) return null;

    return (
        <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Store /> Lieux d'Intérêt
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {banks && banks.map((bank, index) => (
                    <Button
                        key={`bank-${bank.id}-${index}`}
                        variant="outlined"
                        color="secondary"
                        onClick={() => onBankClick(bank)}
                        startIcon={<AccountBalance />}
                        sx={{
                            textTransform: 'none',
                            justifyContent: 'flex-start',
                            minWidth: 200,
                            '&:hover': {
                                bgcolor: 'secondary.light',
                                color: 'white',
                            }
                        }}
                    >
                        {bank.icon} {bank.name}
                    </Button>
                ))}
                {pois && pois.map((poi, index) => (
                    <Button
                        key={`${poi.osm_id}-${index}`}
                        variant="outlined"
                        color="primary"
                        onClick={() => onPOIClick(poi)}
                        startIcon={<span style={{ fontSize: '1.5rem' }}>{poi.icon}</span>}
                        sx={{
                            textTransform: 'none',
                            justifyContent: 'flex-start',
                            minWidth: 200,
                            '&:hover': {
                                bgcolor: 'primary.light',
                                color: 'white',
                            }
                        }}
                    >
                        {poi.name}
                    </Button>
                ))}
            </Box>
        </Paper>
    );
}

export default MapPOI;
