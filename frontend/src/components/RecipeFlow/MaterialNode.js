import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Paper, Typography, Box, Chip } from '@mui/material';
import { getRarityColor } from '../../utils/gameLogic';

const MaterialNode = ({ data }) => {

  return (
    <Paper
      elevation={3}
      sx={{
        padding: 2,
        minWidth: 150,
        border: `2px solid ${getRarityColor(data.rarity)}`,
        backgroundColor: 'background.paper',
      }}
    >
      <Handle type="target" position={Position.Left} />
      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="h4" sx={{ mb: 1 }}>
          {data.icon}
        </Typography>
        <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
          {data.name}
        </Typography>
        {data.quantity && (
          <Chip
            label={`x${data.quantity}`}
            size="small"
            color="primary"
            sx={{ mt: 1 }}
          />
        )}
        <Chip
          label={data.rarity}
          size="small"
          sx={{
            mt: 1,
            backgroundColor: getRarityColor(data.rarity),
            color: 'white',
          }}
        />
      </Box>
      <Handle type="source" position={Position.Right} />
    </Paper>
  );
};

export default MaterialNode;
