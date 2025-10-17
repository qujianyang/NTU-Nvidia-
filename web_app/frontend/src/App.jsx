import React, { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Spin, message, ConfigProvider } from 'antd';
import { BookOutlined, PartitionOutlined, RobotOutlined } from '@ant-design/icons';
import CourseCatalog from './components/CourseCatalog';
import PremiumCourseCatalog from './components/PremiumCourseCatalog';
import LearningPathTree from './components/LearningPathTree';
import ChatWidget from './components/ChatWidget';
import WebGLBackground from './components/WebGLBackground';
import MagneticButton, { CustomCursor } from './components/MagneticButton';
import axios from 'axios';
import { gsap } from 'gsap';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;

function App() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('catalog');
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await axios.get('/api/courses');
      setCourses(response.data);
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

export default App
