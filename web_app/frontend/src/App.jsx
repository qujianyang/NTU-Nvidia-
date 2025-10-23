import React, { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Spin, message, ConfigProvider, Button, Avatar, Dropdown, Space } from 'antd';
import { BookOutlined, PartitionOutlined, RobotOutlined, UserOutlined, LogoutOutlined, LoginOutlined } from '@ant-design/icons';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import CourseCatalog from './components/CourseCatalog';
import LearningPathTree from './components/LearningPathTree';
import ChatWidget from './components/ChatWidget';
import LoginPage from './components/LoginPage';
import RegisterPage from './components/RegisterPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import axios from 'axios';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;

// Main App Component (uses auth context)
function MainApp() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('catalog');
  const [chatOpen, setChatOpen] = useState(false);
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

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

  return (
    <Layout className="app-layout">
        <Header className="app-header">
          <div className="header-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Title level={2} style={{ color: 'white', margin: 0 }}>
              🎓 NVIDIA Learning Path Explorer
            </Title>
            <Menu
              theme="dark"
              mode="horizontal"
              selectedKeys={[activeView]}
              items={menuItems}
              onClick={(e) => setActiveView(e.key)}
              style={{ flex: 1, minWidth: 0, justifyContent: 'center' }}
            />

            {/* User Menu */}
            <div>
              {isAuthenticated ? (
                <Dropdown
                  menu={{
                    items: [
                      {
                        key: 'profile',
                        label: (
                          <Space>
                            <UserOutlined />
                            {user?.full_name || user?.email}
                          </Space>
                        ),
                      },
                      {
                        type: 'divider',
                      },
                      {
                        key: 'logout',
                        label: (
                          <Space>
                            <LogoutOutlined />
                            Logout
                          </Space>
                        ),
                        onClick: async () => {
                          await logout();
                          navigate('/login');
                        }
                      },
                    ],
                  }}
                  placement="bottomRight"
                >
                  <Avatar
                    style={{ backgroundColor: '#76b900', cursor: 'pointer' }}
                    icon={<UserOutlined />}
                  />
                </Dropdown>
              ) : (
                <Button
                  type="primary"
                  icon={<LoginOutlined />}
                  onClick={() => navigate('/login')}
                  style={{ background: '#76b900' }}
                >
                  Login
                </Button>
              )}
            </div>
          </div>
        </Header>

        <Content className="app-content">
          {loading ? (
            <div className="loading-container">
              <Spin size="large" tip="Loading courses..." />
            </div>
          ) : (
            <>
              {activeView === 'catalog' && <CourseCatalog courses={courses} />}
              {activeView === 'tree' && <LearningPathTree courses={courses} />}
            </>
          )}
        </Content>

        {/* Floating Chat Button */}
        <div
          className="floating-chat-button"
          onClick={() => setChatOpen(true)}
        >
          <RobotOutlined style={{ fontSize: '24px' }} />
        </div>

        {/* Chat Widget */}
        <ChatWidget
          open={chatOpen}
          onClose={() => setChatOpen(false)}
        />
      </Layout>
  );
}

// Root App Component with Router and Auth Provider
function App() {
  const [authUser, setAuthUser] = useState(null);

  const handleLogin = (user) => {
    setAuthUser(user);
  };

  return (
    <Router>
      <AuthProvider>
        <ConfigProvider
          theme={{
            token: {
              colorPrimary: '#76b900',
              borderRadius: 8,
            },
          }}
        >
          <Routes>
            <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
            <Route path="/register" element={<RegisterPage onLogin={handleLogin} />} />
            <Route path="/" element={<MainApp />} />
          </Routes>
        </ConfigProvider>
      </AuthProvider>
    </Router>
  );
}

export default App
