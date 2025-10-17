import React, { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Spin, message, ConfigProvider } from 'antd';
import { BookOutlined, PartitionOutlined, RobotOutlined } from '@ant-design/icons';
import CourseCatalog from './components/CourseCatalog';
import LearningPathTree from './components/LearningPathTree';
import ChatWidget from './components/ChatWidget';
import axios from 'axios';
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

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#76b900',
          borderRadius: 8,
        },
      }}
    >
      <Layout className="app-layout">
        <Header className="app-header">
          <div className="header-content">
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
    </ConfigProvider>
  );
}

export default App
