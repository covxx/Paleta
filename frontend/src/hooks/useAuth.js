import { useState, useEffect, createContext, useContext } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import axios from 'axios';
import toast from 'react-hot-toast';

// Create Auth Context
const AuthContext = createContext();

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();

  // Check authentication status
  const { data: authStatus } = useQuery(
    'auth-status',
    async () => {
      const response = await axios.get('/api/auth/status');
      return response.data;
    },
    {
      retry: false,
      onSuccess: (data) => {
        setIsAuthenticated(data.authenticated);
        setIsLoading(false);
      },
      onError: () => {
        setIsAuthenticated(false);
        setIsLoading(false);
      },
    }
  );

  // Login mutation
  const loginMutation = useMutation(
    async (credentials) => {
      const response = await axios.post('/api/auth/login', credentials);
      return response.data;
    },
    {
      onSuccess: (data) => {
        setIsAuthenticated(true);
        toast.success('Login successful!');
        queryClient.invalidateQueries('auth-status');
      },
      onError: (error) => {
        const message = error.response?.data?.error || 'Login failed';
        toast.error(message);
      },
    }
  );

  // Logout mutation
  const logoutMutation = useMutation(
    async () => {
      const response = await axios.post('/api/auth/logout');
      return response.data;
    },
    {
      onSuccess: () => {
        setIsAuthenticated(false);
        toast.success('Logged out successfully');
        queryClient.clear();
      },
      onError: (error) => {
        toast.error('Logout failed');
      },
    }
  );

  const login = (credentials) => {
    loginMutation.mutate(credentials);
  };

  const logout = () => {
    logoutMutation.mutate();
  };

  const value = {
    isAuthenticated,
    isLoading,
    login,
    logout,
    isLoggingIn: loginMutation.isLoading,
    isLoggingOut: logoutMutation.isLoading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
