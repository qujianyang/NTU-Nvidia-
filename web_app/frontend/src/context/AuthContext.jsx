import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { message } from 'antd';
import { useNavigate } from 'react-router-dom';

// Create the context
const AuthContext = createContext(null);

// Configure axios defaults for all requests
axios.defaults.withCredentials = true;  // Always send cookies
axios.defaults.baseURL = '';  // Use relative URLs for proxy

// Token management utilities
const TOKEN_KEY = 'session_token';
const USER_KEY = 'user_data';

const getStoredToken = () => {
  return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY);
};

const setStoredToken = (token, remember = false) => {
  if (remember) {
    localStorage.setItem(TOKEN_KEY, token);
    sessionStorage.removeItem(TOKEN_KEY);
  } else {
    sessionStorage.setItem(TOKEN_KEY, token);
    localStorage.removeItem(TOKEN_KEY);
  }
};

const clearStoredToken = () => {
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  sessionStorage.removeItem(USER_KEY);
};

// Configure axios interceptor to add token to all requests
axios.interceptors.request.use(
  (config) => {
    const token = getStoredToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Configure response interceptor to handle token expiry
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && error.response?.data?.error?.includes('token')) {
      // Token expired or invalid
      clearStoredToken();
      window.location.href = '/login';
      message.error('Session expired. Please login again.');
    }
    return Promise.reject(error);
  }
);

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth Provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionToken, setSessionToken] = useState(null);

  // Check if user is already logged in on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // First check if we have a stored token
      const storedToken = getStoredToken();
      if (storedToken) {
        setSessionToken(storedToken);
      }

      const response = await axios.get('/api/check-auth');
      if (response.data.authenticated) {
        setUser(response.data.user);
        setIsAuthenticated(true);

        // Store token if returned from server
        if (response.data.session_token) {
          setSessionToken(response.data.session_token);
        }
      } else {
        setUser(null);
        setIsAuthenticated(false);
        clearStoredToken();
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
      setIsAuthenticated(false);
      clearStoredToken();
    } finally {
      setLoading(false);
    }
  };

  const login = (userData, token, remember = false) => {
    setUser(userData);
    setIsAuthenticated(true);
    setSessionToken(token);

    // Store token based on remember me preference
    if (token) {
      setStoredToken(token, remember);
    }

    // Also store user data
    const storage = remember ? localStorage : sessionStorage;
    storage.setItem(USER_KEY, JSON.stringify(userData));
  };

  const logout = async () => {
    try {
      await axios.post('/api/logout');
      setUser(null);
      setIsAuthenticated(false);
      setSessionToken(null);
      clearStoredToken();
      message.success('Logged out successfully');
    } catch (error) {
      console.error('Logout failed:', error);
      message.error('Logout failed');
      // Clear local state even if server logout fails
      setUser(null);
      setIsAuthenticated(false);
      setSessionToken(null);
      clearStoredToken();
    }
  };

  const updateUserProgress = async (courseId, courseTitle, completionPercentage, notes = null) => {
    if (!isAuthenticated) return false;

    try {
      const response = await axios.post('/api/user/progress', {
        course_id: courseId,
        course_title: courseTitle,
        completion_percentage: completionPercentage,
        notes: notes
      });

      return response.data.success;
    } catch (error) {
      console.error('Failed to update progress:', error);
      return false;
    }
  };

  const getUserProgress = async () => {
    if (!isAuthenticated) return [];

    try {
      const response = await axios.get('/api/user/progress');
      return response.data.progress;
    } catch (error) {
      console.error('Failed to get progress:', error);
      return [];
    }
  };

  const getChatHistory = async (limit = 50) => {
    if (!isAuthenticated) return [];

    try {
      const response = await axios.get(`/api/user/chat-history?limit=${limit}`);
      return response.data.history;
    } catch (error) {
      console.error('Failed to get chat history:', error);
      return [];
    }
  };

  // New session management functions
  const getUserSessions = async () => {
    if (!isAuthenticated || !sessionToken) return [];

    try {
      const response = await axios.get('/api/user/sessions');
      return response.data.sessions;
    } catch (error) {
      console.error('Failed to get sessions:', error);
      if (error.response?.status === 401) {
        // Token invalid, trigger logout
        await logout();
      }
      return [];
    }
  };

  const revokeSession = async (sessionTokenToRevoke) => {
    if (!isAuthenticated || !sessionToken) return false;

    try {
      const response = await axios.delete(`/api/user/sessions/${sessionTokenToRevoke}`);
      if (response.data.success) {
        message.success('Session revoked successfully');
        return true;
      }
    } catch (error) {
      console.error('Failed to revoke session:', error);
      message.error('Failed to revoke session');
    }
    return false;
  };

  const logoutAllDevices = async () => {
    if (!isAuthenticated || !sessionToken) return false;

    try {
      const response = await axios.delete('/api/user/sessions/all');
      if (response.data.success) {
        message.success('Logged out from all other devices');
        return true;
      }
    } catch (error) {
      console.error('Failed to logout all devices:', error);
      message.error('Failed to logout from all devices');
    }
    return false;
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    sessionToken,
    login,
    logout,
    checkAuth,
    updateUserProgress,
    getUserProgress,
    getChatHistory,
    // Session management
    getUserSessions,
    revokeSession,
    logoutAllDevices
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Protected Route component
export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate('/login');
    }
  }, [loading, isAuthenticated, navigate]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? children : null;
};