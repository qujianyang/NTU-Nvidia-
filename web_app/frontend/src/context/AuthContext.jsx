import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { message } from 'antd';
import { useNavigate } from 'react-router-dom';

// Create the context
const AuthContext = createContext(null);

// Configure axios defaults for all requests
axios.defaults.withCredentials = true;  // Always send cookies
axios.defaults.baseURL = '';  // Use relative URLs for proxy

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

  // Check if user is already logged in on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await axios.get('/api/check-auth');
      if (response.data.authenticated) {
        setUser(response.data.user);
        setIsAuthenticated(true);
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = (userData) => {
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = async () => {
    try {
      await axios.post('/api/logout');
      setUser(null);
      setIsAuthenticated(false);
      message.success('Logged out successfully');
    } catch (error) {
      console.error('Logout failed:', error);
      message.error('Logout failed');
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

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    checkAuth,
    updateUserProgress,
    getUserProgress,
    getChatHistory
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