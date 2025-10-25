import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import { Layout, Menu, Typography, Spin, message, ConfigProvider } from 'antd';
import { BookOutlined, PartitionOutlined, RobotOutlined, UserOutlined, LoginOutlined, LogoutOutlined, DashboardOutlined } from '@ant-design/icons';
import CourseCatalog from './components/CourseCatalog';
import PremiumCourseCatalog from './components/PremiumCourseCatalog';
import LearningPathTree from './components/LearningPathTree';
import ChatWidget from './components/ChatWidget';
import WebGLBackground from './components/WebGLBackground';
import MagneticButton, { CustomCursor } from './components/MagneticButton';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ROUTES } from './constants/routes';
import axios from 'axios';
import { gsap } from 'gsap';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;

// Main App Content Component (separated for routing)
function AppContent() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('catalog');
  const [chatOpen, setChatOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await axios.get('/api/courses');

      // Ensure prerequisites and leads_to are arrays (safety check)
      const coursesWithArrays = response.data.map(course => ({
        ...course,
        prerequisites: Array.isArray(course.prerequisites)
          ? course.prerequisites
          : typeof course.prerequisites === 'string'
            ? (() => { try { return JSON.parse(course.prerequisites); } catch { return []; }})()
            : [],
        leads_to: Array.isArray(course.leads_to)
          ? course.leads_to
          : typeof course.leads_to === 'string'
            ? (() => { try { return JSON.parse(course.leads_to); } catch { return []; }})()
            : []
      }));

      setCourses(coursesWithArrays);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching courses:', error);
      message.error('Failed to load courses');
      setLoading(false);
    }
  };

  const menuItems = [
    {
      key: 'catalog',
      icon: <BookOutlined />,
      label: 'Course Catalog',
    },
    {
      key: 'tree',
      icon: <PartitionOutlined />,
      label: 'Learning Paths',
    },
  ];

  // Add entrance animation
  useEffect(() => {
    // Animate header on load
    gsap.fromTo('.premium-header',
      { opacity: 0, y: -50 },
      { opacity: 1, y: 0, duration: 1, delay: 0.5, ease: 'power3.out' }
    );
  }, []);

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#76b900',
          borderRadius: 8,
        },
      }}
    >
      {/* WebGL Background */}
      <WebGLBackground intensity={0.8} />

      {/* Custom Cursor */}
      <CustomCursor />

      <div className="premium-app">
        {/* Premium Header */}
        <header className="premium-header">
          <div className="header-inner">
            <div className="logo-section">
              <span className="logo-text">NVIDIA</span>
              <span className="logo-subtitle">Learning Universe</span>
            </div>

            <nav className="premium-nav">
              <MagneticButton
                variant={activeView === 'catalog' ? 'primary' : 'ghost'}
                onClick={() => setActiveView('catalog')}
              >
                Catalog
              </MagneticButton>
              <MagneticButton
                variant={activeView === 'tree' ? 'primary' : 'ghost'}
                onClick={() => setActiveView('tree')}
              >
                Paths
              </MagneticButton>

              {/* Auth Navigation */}
              <div style={{ marginLeft: 'auto', display: 'flex', gap: '1rem', alignItems: 'center' }}>
                {isAuthenticated ? (
                  <>
                    <span style={{ color: 'rgba(255,255,255,0.8)', marginRight: '1rem' }}>
                      Welcome, {user?.username}!
                    </span>
                    <MagneticButton
                      variant="ghost"
                      onClick={() => navigate(ROUTES.DASHBOARD)}
                      icon={<DashboardOutlined />}
                    >
                      Dashboard
                    </MagneticButton>
                    <MagneticButton
                      variant="ghost"
                      onClick={logout}
                      icon={<LogoutOutlined />}
                    >
                      Logout
                    </MagneticButton>
                  </>
                ) : (
                  <>
                    <MagneticButton
                      variant="ghost"
                      onClick={() => navigate(ROUTES.LOGIN)}
                      icon={<LoginOutlined />}
                    >
                      Login
                    </MagneticButton>
                    <MagneticButton
                      variant="primary"
                      onClick={() => navigate(ROUTES.REGISTER)}
                    >
                      Sign Up
                    </MagneticButton>
                  </>
                )}
              </div>
            </nav>
          </div>
        </header>

        {/* Premium Content */}
        <main className="premium-content">
          {loading ? (
            <div className="premium-loading">
              <div className="loading-orb" />
              <p className="loading-text">Initializing Learning Universe...</p>
            </div>
          ) : (
            <>
              {activeView === 'catalog' && <PremiumCourseCatalog courses={courses} />}
              {activeView === 'tree' && <LearningPathTree courses={courses} />}
            </>
          )}
        </main>

        {/* Floating Chat Button with Magnetic Effect */}
        <MagneticButton
          variant="primary"
          size="large"
          onClick={() => setChatOpen(true)}
          magnetStrength={0.5}
          style={{
            position: 'fixed',
            bottom: '2rem',
            right: '2rem',
            borderRadius: '50%',
            width: '60px',
            height: '60px',
            zIndex: 1000,
          }}
        >
          <RobotOutlined style={{ fontSize: '24px' }} />
        </MagneticButton>

        {/* Chat Widget */}
        <ChatWidget
          open={chatOpen}
          onClose={() => setChatOpen(false)}
        />
      </div>
    </ConfigProvider>
  );
}

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
  }

  return children;
};

// Main App Component with Router
function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Auth routes */}
          <Route path={ROUTES.LOGIN} element={<LoginPage />} />
          <Route path={ROUTES.REGISTER} element={<RegisterPage />} />

          {/* Protected routes */}
          <Route
            path={ROUTES.DASHBOARD}
            element={
              <ProtectedRoute>
                <div style={{ color: 'white', padding: '2rem', textAlign: 'center' }}>
                  <h1>User Dashboard - Coming Soon!</h1>
                </div>
              </ProtectedRoute>
            }
          />

          {/* Main application route */}
          <Route path="/*" element={<AppContent />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
