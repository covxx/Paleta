import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Avatar,
  LinearProgress,
} from '@mui/material';
import {
  People as PeopleIcon,
  Inventory as InventoryIcon,
  Print as PrintIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import axios from 'axios';

const StatCard = ({ title, value, icon, color, subtitle, progress }) => (
  <Card sx={{ height: '100%' }}>
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

const Dashboard = () => {
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
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3, fontWeight: 600 }}>
        Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={stats?.total_users || 0}
            icon={<PeopleIcon />}
            color="primary.main"
            subtitle="Active admin users"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Items"
            value={stats?.total_items || 0}
            icon={<InventoryIcon />}
            color="success.main"
            subtitle="Items in inventory"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Printers"
            value={stats?.active_printers || 0}
            icon={<PrintIcon />}
            color="warning.main"
            subtitle="Connected printers"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Orders Today"
            value={stats?.orders_today || 0}
            icon={<TrendingUpIcon />}
            color="info.main"
            subtitle="Orders processed"
          />
        </Grid>
        
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
        
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Box sx={{ mt: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Database</Typography>
                  <Typography variant="body2" color="success.main">Online</Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">QuickBooks</Typography>
                  <Typography variant="body2" color={stats?.qb_connected ? 'success.main' : 'error.main'}>
                    {stats?.qb_connected ? 'Connected' : 'Disconnected'}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Print Service</Typography>
                  <Typography variant="body2" color="success.main">Running</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
