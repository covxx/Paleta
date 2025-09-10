import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Print as PrintIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

const Receiving = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedLot, setSelectedLot] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const queryClient = useQueryClient();

  // Form state
  const [formData, setFormData] = useState({
    item_id: '',
    vendor_id: '',
    quantity: '',
    unit_price: '',
    receiving_date: new Date().toISOString().split('T')[0],
    notes: ''
  });

  // Fetch lots
  const { data: lots = [], isLoading } = useQuery(
    'lots',
    () => axios.get('/api/lots').then(res => res.data),
    {
      onError: (error) => {
        toast.error('Failed to load lots');
      }
    }
  );

  // Fetch items
  const { data: items = [] } = useQuery(
    'items',
    () => axios.get('/api/items').then(res => res.data)
  );

  // Fetch vendors
  const { data: vendors = [] } = useQuery(
    'vendors',
    () => axios.get('/api/vendors').then(res => res.data)
  );

  // Create lot mutation
  const createLotMutation = useMutation(
    (lotData) => axios.post('/api/lots', lotData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('lots');
        toast.success('Lot created successfully');
        setOpenDialog(false);
        setFormData({
          item_id: '',
          vendor_id: '',
          quantity: '',
          unit_price: '',
          receiving_date: new Date().toISOString().split('T')[0],
          notes: ''
        });
      },
      onError: (error) => {
        toast.error('Failed to create lot');
      }
    }
  );

  // Print label mutation
  const printLabelMutation = useMutation(
    (lotCode) => axios.post(`/api/lots/${lotCode}/print`),
    {
      onSuccess: () => {
        toast.success('Label printed successfully');
      },
      onError: (error) => {
        toast.error('Failed to print label');
      }
    }
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    createLotMutation.mutate(formData);
  };

  const handlePrintLabel = (lotCode) => {
    printLabelMutation.mutate(lotCode);
  };

  const filteredLots = lots.filter(lot => {
    const matchesSearch = lot.lot_code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         lot.item?.name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || lot.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Receiving
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          New Lot
        </Button>
      </Box>

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Search lots"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="all">All</MenuItem>
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="expired">Expired</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Lots Table */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Lot Code</TableCell>
                  <TableCell>Item</TableCell>
                  <TableCell>Vendor</TableCell>
                  <TableCell>Quantity</TableCell>
                  <TableCell>Unit Price</TableCell>
                  <TableCell>Receiving Date</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredLots.map((lot) => (
                  <TableRow key={lot.lot_code}>
                    <TableCell>{lot.lot_code}</TableCell>
                    <TableCell>{lot.item?.name || 'N/A'}</TableCell>
                    <TableCell>{lot.vendor?.name || 'N/A'}</TableCell>
                    <TableCell>{lot.quantity}</TableCell>
                    <TableCell>${lot.unit_price}</TableCell>
                    <TableCell>{new Date(lot.receiving_date).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <Chip
                        label={lot.status}
                        color={lot.status === 'active' ? 'success' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handlePrintLabel(lot.lot_code)}
                        disabled={printLabelMutation.isLoading}
                      >
                        <PrintIcon />
                      </IconButton>
                      <IconButton size="small">
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small" color="error">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Create Lot Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Lot</DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Item</InputLabel>
                  <Select
                    value={formData.item_id}
                    onChange={(e) => setFormData({ ...formData, item_id: e.target.value })}
                  >
                    {items.map((item) => (
                      <MenuItem key={item.id} value={item.id}>
                        {item.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>Vendor</InputLabel>
                  <Select
                    value={formData.vendor_id}
                    onChange={(e) => setFormData({ ...formData, vendor_id: e.target.value })}
                  >
                    {vendors.map((vendor) => (
                      <MenuItem key={vendor.id} value={vendor.id}>
                        {vendor.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Quantity"
                  type="number"
                  required
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Unit Price"
                  type="number"
                  step="0.01"
                  required
                  value={formData.unit_price}
                  onChange={(e) => setFormData({ ...formData, unit_price: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Receiving Date"
                  type="date"
                  required
                  value={formData.receiving_date}
                  onChange={(e) => setFormData({ ...formData, receiving_date: e.target.value })}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Notes"
                  multiline
                  rows={3}
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createLotMutation.isLoading}
            >
              {createLotMutation.isLoading ? 'Creating...' : 'Create Lot'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default Receiving;
