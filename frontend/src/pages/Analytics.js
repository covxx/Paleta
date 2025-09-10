import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Analytics = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Analytics
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Analytics and reporting functionality will be implemented here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Analytics;
