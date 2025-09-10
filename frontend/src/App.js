import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, ThemeProvider, createTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';

// Components
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import UserManagement from './pages/UserManagement';
import ItemManagement from './pages/ItemManagement';
import LotManagement from './pages/LotManagement';
import VendorManagement from './pages/VendorManagement';
import PrinterManagement from './pages/PrinterManagement';
import Analytics from './pages/Analytics';
import QuickBooksAdmin from './pages/QuickBooksAdmin';

// Main Application Pages
import Receiving from './pages/Receiving';
import Orders from './pages/Orders';
import OrderEntry from './pages/OrderEntry';
import OrderFill from './pages/OrderFill';
import Customers from './pages/Customers';
import LabelDesigner from './pages/LabelDesigner';
import QuickBooksImport from './pages/QuickBooksImport';

// Hooks
import { useAuth, AuthProvider } from './hooks/useAuth';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box 
        display="flex" 
        justifyContent="center" 
        alignItems="center" 
        minHeight="100vh"
      >
        <div>Loading...</div>
      </Box>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
        <Routes>
          {/* Public Routes */}
          <Route 
            path="/login" 
            element={
              isAuthenticated ? <Navigate to="/" replace /> : <LoginPage />
            } 
          />
          
          {/* Main Application Routes */}
          <Route 
            path="/*" 
            element={
              <Layout>
                <Routes>
                  {/* Dashboard */}
                  <Route path="/" element={<Dashboard />} />
                  
                  {/* Main Application Pages */}
                  <Route path="/receiving" element={<Receiving />} />
                  <Route path="/orders" element={<Orders />} />
                  <Route path="/orders/new" element={<OrderEntry />} />
                  <Route path="/orders/:orderId/fill" element={<OrderFill />} />
                  <Route path="/customers" element={<Customers />} />
                  <Route path="/label-designer" element={<LabelDesigner />} />
                  <Route path="/quickbooks-import" element={<QuickBooksImport />} />
                  
                  {/* Admin Routes */}
                  <Route path="/admin" element={<Dashboard />} />
                  <Route path="/admin/users" element={<UserManagement />} />
                  <Route path="/admin/items" element={<ItemManagement />} />
                  <Route path="/admin/lots" element={<LotManagement />} />
                  <Route path="/admin/vendors" element={<VendorManagement />} />
                  <Route path="/admin/printers" element={<PrinterManagement />} />
                  <Route path="/admin/analytics" element={<Analytics />} />
                  <Route path="/admin/quickbooks" element={<QuickBooksAdmin />} />
                  
                  {/* Legacy admin login redirect */}
                  <Route path="/admin/login" element={<Navigate to="/login" replace />} />
                  
                  {/* Catch all */}
                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </Layout>
            } 
          />
        </Routes>
      </Box>
    </ThemeProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;