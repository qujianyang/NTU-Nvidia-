import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { message } from 'antd';
import { gsap } from 'gsap';

// Create context
const AuthContext = createContext();

// Constants
const TOKEN_KEY = 'session_token';
const USER_KEY = 'user_data';

// Axios configuration
axios.defaults.baseURL = import.meta.env.VITE_API_URL || '';
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Auth Provider Component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Token management utilities
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

  const removeStoredToken = () => {
    localStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  };

  // Setup axios interceptors
  useEffect(() => {
    // Request interceptor to add token
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        const token = getStoredToken();
        if (token) {
          config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle 401s
    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          removeStoredToken();
          setUser(null);
          setIsAuthenticated(false);

          // Animate logout with GSAP
          gsap.to('.premium-app', {
            opacity: 0,
            duration: 0.3,
            onComplete: () => {
              window.location.href = '/login';
              gsap.to('.premium-app', { opacity: 1, duration: 0.3 });
            }
          });

          message.error('Session expired. Please login again.');
        }
        return Promise.reject(error);
      }
    );

    // Cleanup
    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, []);

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = getStoredToken();
      const storedUser = localStorage.getItem(USER_KEY);

      if (token && storedUser) {
        try {
          // Verify token with backend
          const response = await axios.get('/api/verify-session');
          if (response.data.valid) {
            setUser(JSON.parse(storedUser));
            setIsAuthenticated(true);
          } else {
            removeStoredToken();
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          removeStoredToken();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  // Authentication functions
  const login = async (email, password, remember = false) => {
    try {
      const response = await axios.post('/api/login', { email, password });
      const { user: userData, session_token } = response.data;

      // Store token and user data
      setStoredToken(session_token, remember);
      localStorage.setItem(USER_KEY, JSON.stringify(userData));

      // Update state
      setUser(userData);
      setIsAuthenticated(true);

      // Success animation
      gsap.fromTo('.premium-app',
        { scale: 0.98, opacity: 0.8 },
        { scale: 1, opacity: 1, duration: 0.5, ease: 'power2.out' }
      );

      message.success(`Welcome back, ${userData.username}!`);
      return { success: true };
    } catch (error) {
      message.error(error.response?.data?.error || 'Login failed');
      return { success: false, error: error.response?.data?.error };
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await axios.post('/api/register', {
        username,
        email,
        password
      });

      const { user: userData, session_token } = response.data;

      // Auto login after registration
      setStoredToken(session_token, false);
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
      setUser(userData);
      setIsAuthenticated(true);

      // Welcome animation
      gsap.timeline()
        .fromTo('.premium-app',
          { rotationY: -5, opacity: 0 },
          { rotationY: 0, opacity: 1, duration: 0.8, ease: 'power3.out' }
        );

      message.success('Registration successful! Welcome to NVIDIA Learning Universe!');
      return { success: true };
    } catch (error) {
      message.error(error.response?.data?.error || 'Registration failed');
      return { success: false, error: error.response?.data?.error };
    }
  };

  const logout = async () => {
    try {
      const token = getStoredToken();
      if (token) {
        await axios.post('/api/logout');
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local data regardless
      removeStoredToken();
      setUser(null);
      setIsAuthenticated(false);

      // Logout animation
      gsap.to('.premium-app', {
        scale: 0.95,
        opacity: 0.5,
        duration: 0.3,
        onComplete: () => {
          window.location.href = '/';
          gsap.set('.premium-app', { scale: 1, opacity: 1 });
        }
      });

      message.info('You have been logged out');
    }
  };

  // Session management functions
  const getUserSessions = async () => {
    try {
      const response = await axios.get('/api/user-sessions');
      return response.data.sessions;
    } catch (error) {
      message.error('Failed to fetch sessions');
      return [];
    }
  };

  const revokeSession = async (tokenToRevoke) => {
    try {
      await axios.post('/api/revoke-session', { token: tokenToRevoke });
      message.success('Session revoked successfully');

      // If revoking current session, logout
      if (tokenToRevoke === getStoredToken()) {
        await logout();
      }
      return true;
    } catch (error) {
      message.error('Failed to revoke session');
      return false;
    }
  };

  const logoutAllDevices = async () => {
    try {
      await axios.post('/api/logout-all');
      message.success('Logged out from all devices');
      await logout();
      return true;
    } catch (error) {
      message.error('Failed to logout from all devices');
      return false;
    }
  };

  // Progress tracking functions
  const getUserProgress = async () => {
    try {
      const response = await axios.get('/api/user-progress');
      return response.data.progress;
    } catch (error) {
      console.error('Failed to fetch progress:', error);
      return [];
    }
  };

  const updateCourseProgress = async (courseId, progress, completed = false) => {
    try {
      const response = await axios.post('/api/update-progress', {
        course_id: courseId,
        progress,
        completed
      });

      if (completed) {
        // Celebration animation for course completion
        gsap.timeline()
          .to('.course-card', { scale: 1.05, duration: 0.2 })
          .to('.course-card', { scale: 1, duration: 0.2 });

        message.success('🎉 Course completed! Great job!');
      }

      return response.data;
    } catch (error) {
      message.error('Failed to update progress');
      return null;
    }
  };

  // Chat history functions
  const getChatHistory = async (limit = 50) => {
    try {
      const response = await axios.get(`/api/chat-history?limit=${limit}`);
      return response.data.history;
    } catch (error) {
      console.error('Failed to fetch chat history:', error);
      return [];
    }
  };

  const saveChatMessage = async (question, answer) => {
    try {
      await axios.post('/api/save-chat', { question, answer });
    } catch (error) {
      console.error('Failed to save chat message:', error);
    }
  };

  // Context value
  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    getUserSessions,
    revokeSession,
    logoutAllDevices,
    getUserProgress,
    updateCourseProgress,
    getChatHistory,
    saveChatMessage,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;