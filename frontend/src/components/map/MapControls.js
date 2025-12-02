import React from 'react';
import { Box, Typography, Button, ButtonGroup } from '@mui/material';
import { ArrowUpward, ArrowDownward, ArrowBack, ArrowForward } from '@mui/icons-material';

function MapControls({
    loading,
    onMove,
    onGather,
    onFish,
    onHunt,
    onScavenge,
    currentCell,
    huntLoading
}) {
    return (
        <React.Fragment>
            {/* Movement Controls */}
            <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom color="text.secondary">
                    Déplacement
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.75 }}>
                    <Button
                        variant="outlined"
                        onClick={() => onMove('north')}
                        disabled={loading}
                        startIcon={<ArrowUpward />}
                        size="small"
                    >
                        Nord
                    </Button>
                    <ButtonGroup disabled={loading} size="small">
                        <Button onClick={() => onMove('west')} startIcon={<ArrowBack />}>Ouest</Button>
                        <Button onClick={() => onMove('south')} startIcon={<ArrowDownward />}>Sud</Button>
                        <Button onClick={() => onMove('east')} startIcon={<ArrowForward />}>Est</Button>
                    </ButtonGroup>
                </Box>
            </Box>

            {/* Action Controls */}
            <Box>
                <Typography variant="subtitle2" gutterBottom color="text.secondary">
                    Actions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
                    {/* Primary action */}
                    <Button
                        variant="contained"
                        color="primary"
                        fullWidth
                        disabled={loading || !currentCell?.materials?.length}
                        onClick={onGather}
                        startIcon={<span>🌾</span>}
                        size="small"
                    >
                        Cueillir / Récolter
                    </Button>

                    {/* Secondary actions, more sobres */}
                    <Button
                        variant="outlined"
                        color="info"
                        fullWidth
                        disabled={loading || currentCell?.biome !== 'water'}
                        onClick={onFish}
                        startIcon={<span>🎣</span>}
                        size="small"
                    >
                        Pêcher
                    </Button>

                    <Button
                        variant="outlined"
                        color="warning"
                        fullWidth
                        disabled={huntLoading || loading}
                        onClick={onHunt}
                        startIcon={<span>🏹</span>}
                        size="small"
                    >
                        {huntLoading ? 'Recherche...' : 'Chasser'}
                    </Button>

                    <Button
                        variant="outlined"
                        color="secondary"
                        fullWidth
                        disabled={loading || currentCell?.biome !== 'urban'}
                        onClick={onScavenge}
                        startIcon={<span>🏙️</span>}
                        size="small"
                    >
                        Fouiller (Zone urbaine)
                    </Button>
                </Box>
            </Box>
        </React.Fragment>
    );
}

export default MapControls;
