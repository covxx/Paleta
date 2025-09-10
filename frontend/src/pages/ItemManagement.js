import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const ItemManagement = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Item Management
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Item management functionality will be implemented here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default ItemManagement;
