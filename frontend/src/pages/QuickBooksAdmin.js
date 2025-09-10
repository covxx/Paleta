import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const QuickBooksAdmin = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
        QuickBooks Integration
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          QuickBooks integration functionality will be implemented here.
        </Typography>
      </Paper>
    </Box>
  );
};

export default QuickBooksAdmin;
