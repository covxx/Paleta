import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Sync as SyncIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Download as DownloadIcon,
  Upload as UploadIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

const QuickBooksImport = () => {
  const [importType, setImportType] = useState('customers');
  const [importResults, setImportResults] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const queryClient = useQueryClient();

  // Fetch QuickBooks connection status
  const { data: qbStatus } = useQuery(
    'quickbooks-status',
    () => axios.get('/api/quickbooks/sync/status').then(res => res.data),
    {
      refetchInterval: 5000,
      onError: (error) => {
        console.error('Failed to fetch QuickBooks status:', error);
      }
    }
  );

  // Fetch sync statistics
  const { data: syncStats } = useQuery(
    'quickbooks-stats',
    () => axios.get('/api/quickbooks/sync/statistics').then(res => res.data)
  );

  // Fetch sync log
  const { data: syncLog = [] } = useQuery(
    'quickbooks-log',
    () => axios.get('/api/quickbooks/sync/log').then(res => res.data)
  );

  // Connect to QuickBooks mutation
  const connectQBMutation = useMutation(
    () => axios.get('/api/quickbooks/connect'),
    {
      onSuccess: (response) => {
        if (response.data.auth_url) {
          window.open(response.data.auth_url, '_blank');
          toast.success('QuickBooks authorization opened in new window');
        }
      },
      onError: (error) => {
        toast.error('Failed to connect to QuickBooks');
      }
    }
  );

  // Disconnect from QuickBooks mutation
  const disconnectQBMutation = useMutation(
    () => axios.post('/api/quickbooks/disconnect'),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('quickbooks-status');
        toast.success('Disconnected from QuickBooks');
      },
      onError: (error) => {
        toast.error('Failed to disconnect from QuickBooks');
      }
    }
  );

  // Import customers mutation
  const importCustomersMutation = useMutation(
    () => axios.post('/api/quickbooks/import/customers'),
    {
      onSuccess: (response) => {
        setImportResults(response.data);
        setShowResults(true);
        queryClient.invalidateQueries('customers');
        queryClient.invalidateQueries('quickbooks-stats');
        toast.success('Customers imported successfully');
      },
      onError: (error) => {
        toast.error('Failed to import customers');
      }
    }
  );

  // Import items mutation
  const importItemsMutation = useMutation(
    () => axios.post('/api/quickbooks/import/items'),
    {
      onSuccess: (response) => {
        setImportResults(response.data);
        setShowResults(true);
        queryClient.invalidateQueries('items');
        queryClient.invalidateQueries('quickbooks-stats');
        toast.success('Items imported successfully');
      },
      onError: (error) => {
        toast.error('Failed to import items');
      }
    }
  );

  // Sync customers mutation
  const syncCustomersMutation = useMutation(
    () => axios.post('/api/quickbooks/sync/customers'),
    {
      onSuccess: (response) => {
        setImportResults(response.data);
        setShowResults(true);
        queryClient.invalidateQueries('customers');
        queryClient.invalidateQueries('quickbooks-stats');
        toast.success('Customers synced successfully');
      },
      onError: (error) => {
        toast.error('Failed to sync customers');
      }
    }
  );

  // Sync items mutation
  const syncItemsMutation = useMutation(
    () => axios.post('/api/quickbooks/sync/items'),
    {
      onSuccess: (response) => {
        setImportResults(response.data);
        setShowResults(true);
        queryClient.invalidateQueries('items');
        queryClient.invalidateQueries('quickbooks-stats');
        toast.success('Items synced successfully');
      },
      onError: (error) => {
        toast.error('Failed to sync items');
      }
    }
  );

  const handleImport = () => {
    if (importType === 'customers') {
      importCustomersMutation.mutate();
    } else if (importType === 'items') {
      importItemsMutation.mutate();
    }
  };

  const handleSync = () => {
    if (importType === 'customers') {
      syncCustomersMutation.mutate();
    } else if (importType === 'items') {
      syncItemsMutation.mutate();
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircleIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'info';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        QuickBooks Import
      </Typography>

      {/* Connection Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            QuickBooks Connection
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Chip
                  label={qbStatus?.connected ? 'Connected' : 'Disconnected'}
                  color={qbStatus?.connected ? 'success' : 'error'}
                  icon={qbStatus?.connected ? <CheckCircleIcon /> : <ErrorIcon />}
                />
                {qbStatus?.connected && (
                  <Typography variant="body2" color="text.secondary">
                    Last sync: {new Date(qbStatus.last_sync).toLocaleString()}
                  </Typography>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                {!qbStatus?.connected ? (
                  <Button
                    variant="contained"
                    startIcon={<SyncIcon />}
                    onClick={() => connectQBMutation.mutate()}
                    disabled={connectQBMutation.isLoading}
                  >
                    Connect to QuickBooks
                  </Button>
                ) : (
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => disconnectQBMutation.mutate()}
                    disabled={disconnectQBMutation.isLoading}
                  >
                    Disconnect
                  </Button>
                )}
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Sync Statistics */}
      {syncStats && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Sync Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {syncStats.total_customers || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Customers
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {syncStats.total_items || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Items
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {syncStats.total_orders || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Orders
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {syncStats.last_sync_count || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Last Sync
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Import Actions */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Import & Sync
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <Typography variant="subtitle2" gutterBottom>
                Select Data Type
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant={importType === 'customers' ? 'contained' : 'outlined'}
                  onClick={() => setImportType('customers')}
                  size="small"
                >
                  Customers
                </Button>
                <Button
                  variant={importType === 'items' ? 'contained' : 'outlined'}
                  onClick={() => setImportType('items')}
                  size="small"
                >
                  Items
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12} md={8}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleImport}
                  disabled={!qbStatus?.connected || importCustomersMutation.isLoading || importItemsMutation.isLoading}
                >
                  Import from QuickBooks
                </Button>
                <Button
                  variant="contained"
                  startIcon={<UploadIcon />}
                  onClick={handleSync}
                  disabled={!qbStatus?.connected || syncCustomersMutation.isLoading || syncItemsMutation.isLoading}
                >
                  Sync with QuickBooks
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Sync Log */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Sync Activity
          </Typography>
          <List>
            {syncLog.slice(0, 10).map((log, index) => (
              <React.Fragment key={index}>
                <ListItem>
                  <ListItemIcon>
                    {getStatusIcon(log.status)}
                  </ListItemIcon>
                  <ListItemText
                    primary={log.message}
                    secondary={`${new Date(log.timestamp).toLocaleString()} - ${log.type}`}
                  />
                </ListItem>
                {index < syncLog.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </CardContent>
      </Card>

      {/* Import Results Dialog */}
      <Dialog open={showResults} onClose={() => setShowResults(false)} maxWidth="md" fullWidth>
        <DialogTitle>Import Results</DialogTitle>
        <DialogContent>
          {importResults && (
            <Box>
              <Alert severity={getStatusColor(importResults.status)} sx={{ mb: 2 }}>
                {importResults.message}
              </Alert>
              {importResults.details && (
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Item</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Message</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {importResults.details.map((detail, index) => (
                        <TableRow key={index}>
                          <TableCell>{detail.name || detail.id}</TableCell>
                          <TableCell>
                            <Chip
                              label={detail.status}
                              color={getStatusColor(detail.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{detail.message}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowResults(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default QuickBooksImport;
