import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  LinearProgress,
  Button,
  Chip,
  Divider
} from '@mui/material';
import {
  People as PeopleIcon,
  Inventory as InventoryIcon,
  Print as PrintIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  LocalShipping as ShippingIcon,
  ShoppingCart as ShoppingCartIcon,
  Label as LabelIcon,
  AccountBalance as QuickBooksIcon,
  Dashboard as DashboardIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const StatCard = ({ title, value, icon, color, subtitle, progress, onClick }) => (
  <Card sx={{ height: '100%', cursor: onClick ? 'pointer' : 'default' }} onClick={onClick}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Avatar sx={{ bgcolor: color, mr: 2 }}>
          {icon}
        </Avatar>
        <Box>
          <Typography color="textSecondary" gutterBottom variant="h6">
            {title}
          </Typography>
          <Typography variant="h4" component="div">
            {value}
          </Typography>
        </Box>
      </Box>
      {subtitle && (
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      )}
      {progress !== undefined && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            {progress}% complete
          </Typography>
        </Box>
      )}
    </CardContent>
  </Card>
);

const QuickActionCard = ({ title, description, icon, color, onClick }) => (
  <Card sx={{ height: '100%', cursor: 'pointer' }} onClick={onClick}>
    <CardContent sx={{ textAlign: 'center', p: 3 }}>
      <Avatar sx={{ bgcolor: color, width: 56, height: 56, mx: 'auto', mb: 2 }}>
        {icon}
      </Avatar>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {description}
      </Typography>
    </CardContent>
  </Card>
);

const Dashboard = () => {
  const navigate = useNavigate();

  // Fetch dashboard statistics
  const { data: stats, isLoading } = useQuery(
    'dashboard-stats',
    async () => {
      const response = await axios.get('/api/dashboard/stats');
      return response.data;
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  // Fetch additional stats
  const { data: items = [] } = useQuery(
    'items',
    () => axios.get('/api/items').then(res => res.data)
  );

  const { data: lots = [] } = useQuery(
    'lots',
    () => axios.get('/api/lots').then(res => res.data)
  );

  const { data: vendors = [] } = useQuery(
    'vendors',
    () => axios.get('/api/vendors').then(res => res.data)
  );

  const { data: orders = [] } = useQuery(
    'orders',
    () => axios.get('/api/orders').then(res => res.data)
  );

  const { data: customers = [] } = useQuery(
    'customers',
    () => axios.get('/api/customers').then(res => res.data)
  );

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
        Dashboard
      </Typography>
      
      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Items"
            value={items.length}
            icon={<InventoryIcon />}
            color="primary.main"
            subtitle="Items in inventory"
            onClick={() => navigate('/admin/items')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total LOTs"
            value={lots.length}
            icon={<LabelIcon />}
            color="success.main"
            subtitle="Active lots"
            onClick={() => navigate('/admin/lots')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Vendors"
            value={vendors.length}
            icon={<ShippingIcon />}
            color="warning.main"
            subtitle="Active vendors"
            onClick={() => navigate('/admin/vendors')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Orders"
            value={orders.length}
            icon={<ShoppingCartIcon />}
            color="info.main"
            subtitle="Total orders"
            onClick={() => navigate('/orders')}
          />
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        Quick Actions
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <QuickActionCard
            title="Receiving"
            description="Receive new inventory"
            icon={<ShippingIcon />}
            color="primary.main"
            onClick={() => navigate('/receiving')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <QuickActionCard
            title="New Order"
            description="Create new order"
            icon={<ShoppingCartIcon />}
            color="success.main"
            onClick={() => navigate('/orders/new')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <QuickActionCard
            title="Label Designer"
            description="Design custom labels"
            icon={<LabelIcon />}
            color="warning.main"
            onClick={() => navigate('/label-designer')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <QuickActionCard
            title="QuickBooks"
            description="Import & sync data"
            icon={<QuickBooksIcon />}
            color="info.main"
            onClick={() => navigate('/quickbooks-import')}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Recent Activity */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <Box sx={{ mt: 2 }}>
                {stats?.recent_activity?.map((activity, index) => (
                  <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar sx={{ width: 32, height: 32, mr: 2, bgcolor: 'primary.main' }}>
                      <ScheduleIcon />
                    </Avatar>
                    <Box>
                      <Typography variant="body2">
                        {activity.description}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {activity.timestamp}
                      </Typography>
                    </Box>
                  </Box>
                )) || (
                  <Typography variant="body2" color="text.secondary">
                    No recent activity
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        {/* System Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2">Database</Typography>
                  <Chip label="Online" color="success" size="small" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2">QuickBooks</Typography>
                  <Chip 
                    label={stats?.qb_connected ? 'Connected' : 'Disconnected'} 
                    color={stats?.qb_connected ? 'success' : 'error'} 
                    size="small" 
                  />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2">Print Service</Typography>
                  <Chip label="Running" color="success" size="small" />
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="body2">Active Users</Typography>
                  <Chip label={stats?.total_users || 0} color="info" size="small" />
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Navigation Cards */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Main Application
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<ShippingIcon />}
                    onClick={() => navigate('/receiving')}
                  >
                    Receiving
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<ShoppingCartIcon />}
                    onClick={() => navigate('/orders')}
                  >
                    Orders
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<PeopleIcon />}
                    onClick={() => navigate('/customers')}
                  >
                    Customers
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<LabelIcon />}
                    onClick={() => navigate('/label-designer')}
                  >
                    Label Designer
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Admin Panel */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Admin Panel
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<InventoryIcon />}
                    onClick={() => navigate('/admin/items')}
                  >
                    Items
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<LabelIcon />}
                    onClick={() => navigate('/admin/lots')}
                  >
                    LOTs
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<ShippingIcon />}
                    onClick={() => navigate('/admin/vendors')}
                  >
                    Vendors
                  </Button>
                </Grid>
                <Grid item xs={6}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<PrintIcon />}
                    onClick={() => navigate('/admin/printers')}
                  >
                    Printers
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;