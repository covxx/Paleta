import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const VendorManagement = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        Vendor Management
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Vendor management functionality will be implemented here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default VendorManagement;
