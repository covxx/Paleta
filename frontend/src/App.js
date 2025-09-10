import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';

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

// Hooks
import { useAuth, AuthProvider } from './hooks/useAuth';

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
    <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
      <Routes>
        {/* Public Routes */}
        <Route 
          path="/admin/login" 
          element={
            isAuthenticated ? <Navigate to="/admin" replace /> : <LoginPage />
          } 
        />
        
        {/* Protected Routes */}
        <Route 
          path="/admin/*" 
          element={
            isAuthenticated ? (
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/users" element={<UserManagement />} />
                  <Route path="/items" element={<ItemManagement />} />
                  <Route path="/lots" element={<LotManagement />} />
                  <Route path="/vendors" element={<VendorManagement />} />
                  <Route path="/printers" element={<PrinterManagement />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/quickbooks" element={<QuickBooksAdmin />} />
                </Routes>
              </Layout>
            ) : (
              <Navigate to="/admin/login" replace />
            )
          } 
        />
        
        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/admin" replace />} />
        <Route path="*" element={<Navigate to="/admin" replace />} />
      </Routes>
    </Box>
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
