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
  IconButton,
  Alert,
  Divider,
  Chip
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

const OrderEntry = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Form state
  const [formData, setFormData] = useState({
    customer_id: '',
    order_number: '',
    notes: ''
  });

  // Order items state
  const [orderItems, setOrderItems] = useState([]);
  const [newItem, setNewItem] = useState({
    item_id: '',
    quantity: '',
    unit_price: ''
  });

  // Fetch customers
  const { data: customers = [] } = useQuery(
    'customers',
    () => axios.get('/api/customers').then(res => res.data)
  );

  // Fetch items
  const { data: items = [] } = useQuery(
    'items',
    () => axios.get('/api/items').then(res => res.data)
  );

  // Create order mutation
  const createOrderMutation = useMutation(
    (orderData) => axios.post('/api/orders', orderData),
    {
      onSuccess: (response) => {
        queryClient.invalidateQueries('orders');
        toast.success('Order created successfully');
        navigate(`/orders/${response.data.id}/fill`);
      },
      onError: (error) => {
        toast.error('Failed to create order');
      }
    }
  );

  const handleInputChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleAddItem = () => {
    if (!newItem.item_id || !newItem.quantity || !newItem.unit_price) {
      toast.error('Please fill in all item fields');
      return;
    }

    const selectedItem = items.find(item => item.id === parseInt(newItem.item_id));
    const itemTotal = parseFloat(newItem.quantity) * parseFloat(newItem.unit_price);

    setOrderItems([...orderItems, {
      ...newItem,
      item_name: selectedItem?.name || '',
      total: itemTotal
    }]);

    setNewItem({
      item_id: '',
      quantity: '',
      unit_price: ''
    });
  };

  const handleRemoveItem = (index) => {
    setOrderItems(orderItems.filter((_, i) => i !== index));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!formData.customer_id) {
      toast.error('Please select a customer');
      return;
    }

    if (orderItems.length === 0) {
      toast.error('Please add at least one item');
      return;
    }

    const orderData = {
      ...formData,
      items: orderItems.map(item => ({
        item_id: parseInt(item.item_id),
        quantity: parseFloat(item.quantity),
        unit_price: parseFloat(item.unit_price)
      }))
    };

    createOrderMutation.mutate(orderData);
  };

  const calculateTotal = () => {
    return orderItems.reduce((sum, item) => sum + item.total, 0);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          New Order
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<CancelIcon />}
            onClick={() => navigate('/orders')}
            sx={{ mr: 2 }}
          >
            Cancel
          </Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={handleSubmit}
            disabled={createOrderMutation.isLoading}
          >
            {createOrderMutation.isLoading ? 'Creating...' : 'Create Order'}
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Order Information */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Order Information
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth required>
                    <InputLabel>Customer</InputLabel>
                    <Select
                      value={formData.customer_id}
                      onChange={(e) => handleInputChange('customer_id', e.target.value)}
                    >
                      {customers.map((customer) => (
                        <MenuItem key={customer.id} value={customer.id}>
                          {customer.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Order Number"
                    value={formData.order_number}
                    onChange={(e) => handleInputChange('order_number', e.target.value)}
                    placeholder="Auto-generated if empty"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Notes"
                    multiline
                    rows={3}
                    value={formData.notes}
                    onChange={(e) => handleInputChange('notes', e.target.value)}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Add Items */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Add Items
              </Typography>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} md={4}>
                  <FormControl fullWidth>
                    <InputLabel>Item</InputLabel>
                    <Select
                      value={newItem.item_id}
                      onChange={(e) => setNewItem({ ...newItem, item_id: e.target.value })}
                    >
                      {items.map((item) => (
                        <MenuItem key={item.id} value={item.id}>
                          {item.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={2}>
                  <TextField
                    fullWidth
                    label="Quantity"
                    type="number"
                    value={newItem.quantity}
                    onChange={(e) => setNewItem({ ...newItem, quantity: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <TextField
                    fullWidth
                    label="Unit Price"
                    type="number"
                    step="0.01"
                    value={newItem.unit_price}
                    onChange={(e) => setNewItem({ ...newItem, unit_price: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12} md={2}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={handleAddItem}
                  >
                    Add
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>

          {/* Order Items Table */}
          {orderItems.length > 0 && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Order Items
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Item</TableCell>
                        <TableCell>Quantity</TableCell>
                        <TableCell>Unit Price</TableCell>
                        <TableCell>Total</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {orderItems.map((item, index) => (
                        <TableRow key={index}>
                          <TableCell>{item.item_name}</TableCell>
                          <TableCell>{item.quantity}</TableCell>
                          <TableCell>${item.unit_price}</TableCell>
                          <TableCell>${item.total.toFixed(2)}</TableCell>
                          <TableCell>
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => handleRemoveItem(index)}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                <Divider sx={{ my: 2 }} />
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="h6">
                    Total: ${calculateTotal().toFixed(2)}
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default OrderEntry;
