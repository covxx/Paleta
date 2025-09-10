import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Chip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Sync as SyncIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

const Customers = () => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const queryClient = useQueryClient();

  // Form state
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zip_code: '',
    quickbooks_id: ''
  });

  // Fetch customers
  const { data: customers = [], isLoading } = useQuery(
    'customers',
    () => axios.get('/api/customers').then(res => res.data),
    {
      onError: (error) => {
        toast.error('Failed to load customers');
      }
    }
  );

  // Create customer mutation
  const createCustomerMutation = useMutation(
    (customerData) => axios.post('/api/customers', customerData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('customers');
        toast.success('Customer created successfully');
        setOpenDialog(false);
        resetForm();
      },
      onError: (error) => {
        toast.error('Failed to create customer');
      }
    }
  );

  // Update customer mutation
  const updateCustomerMutation = useMutation(
    ({ customerId, customerData }) => axios.put(`/api/customers/${customerId}`, customerData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('customers');
        toast.success('Customer updated successfully');
        setOpenDialog(false);
        setSelectedCustomer(null);
        resetForm();
      },
      onError: (error) => {
        toast.error('Failed to update customer');
      }
    }
  );

  // Delete customer mutation
  const deleteCustomerMutation = useMutation(
    (customerId) => axios.delete(`/api/customers/${customerId}`),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('customers');
        toast.success('Customer deleted successfully');
      },
      onError: (error) => {
        toast.error('Failed to delete customer');
      }
    }
  );

  // Sync with QuickBooks mutation
  const syncQuickBooksMutation = useMutation(
    () => axios.post('/api/quickbooks/sync/customers'),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('customers');
        toast.success('Customers synced with QuickBooks');
      },
      onError: (error) => {
        toast.error('Failed to sync customers');
      }
    }
  );

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      address: '',
      city: '',
      state: '',
      zip_code: '',
      quickbooks_id: ''
    });
  };

  const handleEdit = (customer) => {
    setSelectedCustomer(customer);
    setFormData({
      name: customer.name || '',
      email: customer.email || '',
      phone: customer.phone || '',
      address: customer.address || '',
      city: customer.city || '',
      state: customer.state || '',
      zip_code: customer.zip_code || '',
      quickbooks_id: customer.quickbooks_id || ''
    });
    setOpenDialog(true);
  };

  const handleDelete = (customerId) => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      deleteCustomerMutation.mutate(customerId);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (selectedCustomer) {
      updateCustomerMutation.mutate({
        customerId: selectedCustomer.id,
        customerData: formData
      });
    } else {
      createCustomerMutation.mutate(formData);
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedCustomer(null);
    resetForm();
  };

  const filteredCustomers = customers.filter(customer =>
    customer.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Customers
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<SyncIcon />}
            onClick={() => syncQuickBooksMutation.mutate()}
            disabled={syncQuickBooksMutation.isLoading}
            sx={{ mr: 2 }}
          >
            Sync QuickBooks
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenDialog(true)}
          >
            New Customer
          </Button>
        </Box>
      </Box>

      {/* Search */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            label="Search customers"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
          />
        </CardContent>
      </Card>

      {/* Customers Table */}
      <Card>
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>City</TableCell>
                  <TableCell>State</TableCell>
                  <TableCell>QuickBooks</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredCustomers.map((customer) => (
                  <TableRow key={customer.id}>
                    <TableCell>{customer.name}</TableCell>
                    <TableCell>{customer.email || 'N/A'}</TableCell>
                    <TableCell>{customer.phone || 'N/A'}</TableCell>
                    <TableCell>{customer.city || 'N/A'}</TableCell>
                    <TableCell>{customer.state || 'N/A'}</TableCell>
                    <TableCell>
                      {customer.quickbooks_id ? (
                        <Chip label="Synced" color="success" size="small" />
                      ) : (
                        <Chip label="Not Synced" color="default" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleEdit(customer)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDelete(customer.id)}
                      >
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

      {/* Customer Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedCustomer ? 'Edit Customer' : 'New Customer'}
        </DialogTitle>
        <form onSubmit={handleSubmit}>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Name"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Phone"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="QuickBooks ID"
                  value={formData.quickbooks_id}
                  onChange={(e) => setFormData({ ...formData, quickbooks_id: e.target.value })}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Address"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="City"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="State"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="ZIP Code"
                  value={formData.zip_code}
                  onChange={(e) => setFormData({ ...formData, zip_code: e.target.value })}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Cancel</Button>
            <Button
              type="submit"
              variant="contained"
              disabled={createCustomerMutation.isLoading || updateCustomerMutation.isLoading}
            >
              {selectedCustomer ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
};

export default Customers;
