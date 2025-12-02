import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Paper, Typography, Box, Chip } from '@mui/material';

const RecipeNode = ({ data }) => {
  return (
    <Paper
      elevation={4}
      sx={{
        padding: 2,
        minWidth: 180,
        border: '3px solid #ff9800',
        backgroundColor: '#fff3e0',
      }}
    >
      <Handle type="target" position={Position.Left} />
      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="h4" sx={{ mb: 1 }}>
          {data.icon}
        </Typography>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
          {data.name}
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          {data.description}
        </Typography>
        {data.requiredWorkstation && (
          <Chip
            icon={<span>{data.requiredWorkstation.icon}</span>}
            label={data.requiredWorkstation.name}
            size="small"
            color="warning"
            sx={{ mt: 1 }}
          />
        )}
      </Box>
      <Handle type="source" position={Position.Right} />
    </Paper>
  );
};

export default RecipeNode;
