import React, { useState, useEffect } from 'react';
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
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Divider
} from '@mui/material';
import {
  Print as PrintIcon,
  Save as SaveIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useNavigate, useParams } from 'react-router-dom';

const OrderFill = () => {
  const navigate = useNavigate();
  const { orderId } = useParams();
  const queryClient = useQueryClient();

  const [selectedLots, setSelectedLots] = useState({});
  const [fillQuantities, setFillQuantities] = useState({});

  // Fetch order details
  const { data: order, isLoading: orderLoading } = useQuery(
    ['order', orderId],
    () => axios.get(`/api/orders/${orderId}`).then(res => res.data),
    {
      enabled: !!orderId,
      onError: (error) => {
        toast.error('Failed to load order');
      }
    }
  );

  // Fetch available lots for each item
  const { data: availableLots = [] } = useQuery(
    ['orderLots', orderId],
    () => axios.get(`/api/orders/${orderId}/lots-available`).then(res => res.data),
    {
      enabled: !!orderId,
      onError: (error) => {
        toast.error('Failed to load available lots');
      }
    }
  );

  // Fill order mutation
  const fillOrderMutation = useMutation(
    (fillData) => axios.post(`/api/orders/${orderId}/fill`, fillData),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('orders');
        toast.success('Order filled successfully');
        navigate('/orders');
      },
      onError: (error) => {
        toast.error('Failed to fill order');
      }
    }
  );

  const handleLotSelection = (itemId, lotCode) => {
    setSelectedLots({ ...selectedLots, [itemId]: lotCode });
  };

  const handleQuantityChange = (itemId, quantity) => {
    setFillQuantities({ ...fillQuantities, [itemId]: quantity });
  };

  const handleFillOrder = () => {
    const fillData = Object.keys(selectedLots).map(itemId => ({
      item_id: parseInt(itemId),
      lot_code: selectedLots[itemId],
      quantity: parseFloat(fillQuantities[itemId] || 0)
    })).filter(item => item.quantity > 0);

    if (fillData.length === 0) {
      toast.error('Please select lots and quantities for at least one item');
      return;
    }

    fillOrderMutation.mutate({ items: fillData });
  };

  const getAvailableLotsForItem = (itemId) => {
    return availableLots.filter(lot => lot.item_id === itemId);
  };

  const getItemLots = (itemId) => {
    return getAvailableLotsForItem(itemId);
  };

  if (orderLoading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography>Loading order...</Typography>
      </Box>
    );
  }

  if (!order) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">Order not found</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/orders')}
            sx={{ mr: 2 }}
          >
            Back to Orders
          </Button>
          <Typography variant="h4" component="h1">
            Fill Order #{order.order_number}
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleFillOrder}
          disabled={fillOrderMutation.isLoading}
        >
          {fillOrderMutation.isLoading ? 'Filling...' : 'Fill Order'}
        </Button>
      </Box>

      {/* Order Information */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2">Customer</Typography>
              <Typography>{order.customer?.name || 'N/A'}</Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2">Order Date</Typography>
              <Typography>{new Date(order.created_at).toLocaleDateString()}</Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2">Status</Typography>
              <Chip label={order.status} color="primary" size="small" />
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography variant="subtitle2">Total</Typography>
              <Typography>${order.total_amount || 0}</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Order Items */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Order Items
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Item</TableCell>
                  <TableCell>Ordered Qty</TableCell>
                  <TableCell>Unit Price</TableCell>
                  <TableCell>Available Lots</TableCell>
                  <TableCell>Select Lot</TableCell>
                  <TableCell>Fill Quantity</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {order.items?.map((item) => {
                  const availableLots = getItemLots(item.item_id);
                  const selectedLot = selectedLots[item.item_id];
                  const fillQuantity = fillQuantities[item.item_id] || '';

                  return (
                    <TableRow key={item.item_id}>
                      <TableCell>{item.item?.name || 'N/A'}</TableCell>
                      <TableCell>{item.quantity}</TableCell>
                      <TableCell>${item.unit_price}</TableCell>
                      <TableCell>
                        {availableLots.length > 0 ? (
                          <Box>
                            {availableLots.map((lot) => (
                              <Chip
                                key={lot.lot_code}
                                label={`${lot.lot_code} (${lot.available_quantity})`}
                                size="small"
                                sx={{ mr: 1, mb: 1 }}
                                color={lot.available_quantity > 0 ? 'success' : 'error'}
                              />
                            ))}
                          </Box>
                        ) : (
                          <Typography color="error" variant="body2">
                            No available lots
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <FormControl size="small" sx={{ minWidth: 150 }}>
                          <InputLabel>Select Lot</InputLabel>
                          <Select
                            value={selectedLot || ''}
                            onChange={(e) => handleLotSelection(item.item_id, e.target.value)}
                          >
                            {availableLots.map((lot) => (
                              <MenuItem key={lot.lot_code} value={lot.lot_code}>
                                {lot.lot_code} ({lot.available_quantity} available)
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </TableCell>
                      <TableCell>
                        <TextField
                          size="small"
                          type="number"
                          value={fillQuantity}
                          onChange={(e) => handleQuantityChange(item.item_id, e.target.value)}
                          disabled={!selectedLot}
                          sx={{ width: 100 }}
                          inputProps={{ min: 0, max: availableLots.find(lot => lot.lot_code === selectedLot)?.available_quantity || 0 }}
                        />
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Fill Summary */}
      {Object.keys(selectedLots).length > 0 && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Fill Summary
            </Typography>
            <Grid container spacing={2}>
              {Object.keys(selectedLots).map((itemId) => {
                const item = order.items?.find(i => i.item_id === parseInt(itemId));
                const lot = availableLots.find(l => l.lot_code === selectedLots[itemId]);
                const quantity = fillQuantities[itemId] || 0;

                return (
                  <Grid item xs={12} md={4} key={itemId}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle2">{item?.item?.name}</Typography>
                        <Typography variant="body2">Lot: {selectedLots[itemId]}</Typography>
                        <Typography variant="body2">Quantity: {quantity}</Typography>
                        {lot && (
                          <Typography variant="body2" color="text.secondary">
                            Available: {lot.available_quantity}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default OrderFill;
