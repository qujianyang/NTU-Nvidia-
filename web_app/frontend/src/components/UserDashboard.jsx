import React, { useState, useEffect } from 'react';
import {
  Card,
  Progress,
  List,
  Typography,
  Button,
  Spin,
  Row,
  Col,
  Statistic,
  Timeline,
  Empty,
  Tag,
  Space,
  Modal,
  Input,
  message,
  Table,
  Popconfirm,
  Badge
} from 'antd';
import {
  BookOutlined,
  ClockCircleOutlined,
  TrophyOutlined,
  HistoryOutlined,
  UserOutlined,
  EditOutlined,
  CheckCircleOutlined,
  DesktopOutlined,
  MobileOutlined,
  DeleteOutlined,
  SafetyOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const UserDashboard = () => {
  const {
    user,
    getUserProgress,
    getChatHistory,
    updateUserProgress,
    isAuthenticated,
    sessionToken,
    getUserSessions,
    revokeSession,
    logoutAllDevices
  } = useAuth();
  const [courseProgress, setCourseProgress] = useState([]);
  const [chatHistory, setChatHistory] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [stats, setStats] = useState({
    totalCourses: 0,
    completedCourses: 0,
    averageProgress: 0,
    totalQuestions: 0
  });
  const [editingNotes, setEditingNotes] = useState(null);
  const [noteText, setNoteText] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      loadDashboardData();
      loadSessions();
    }
  }, [isAuthenticated]);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      // Load progress and chat history in parallel
      const [progress, history] = await Promise.all([
        getUserProgress(),
        getChatHistory(20) // Get last 20 conversations
      ]);

      setCourseProgress(progress || []);
      setChatHistory(history || []);

      // Calculate statistics
      calculateStats(progress || [], history || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      message.error('Failed to load your data');
    } finally {
      setLoading(false);
    }
  };

  const loadSessions = async () => {
    setSessionsLoading(true);
    try {
      const userSessions = await getUserSessions();
      setSessions(userSessions || []);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setSessionsLoading(false);
    }
  };

  const handleRevokeSession = async (tokenToRevoke) => {
    const success = await revokeSession(tokenToRevoke);
    if (success) {
      loadSessions(); // Reload sessions
    }
  };

  const handleLogoutAllDevices = async () => {
    const success = await logoutAllDevices();
    if (success) {
      loadSessions(); // Reload sessions
    }
  };

  const calculateStats = (progress, history) => {
    const totalCourses = progress.length;
    const completedCourses = progress.filter(p => p.completion_percentage >= 100).length;
    const averageProgress = totalCourses > 0
      ? progress.reduce((sum, p) => sum + p.completion_percentage, 0) / totalCourses
      : 0;
    const totalQuestions = history.length;

    setStats({
      totalCourses,
      completedCourses,
      averageProgress: Math.round(averageProgress),
      totalQuestions
    });
  };

  const handleUpdateProgress = async (courseId, courseTitle, newPercentage) => {
    try {
      const success = await updateUserProgress(courseId, courseTitle, newPercentage);
      if (success) {
        message.success('Progress updated!');
        loadDashboardData(); // Reload data
      } else {
        message.error('Failed to update progress');
      }
    } catch (error) {
      message.error('Failed to update progress');
    }
  };

  const handleSaveNotes = async (courseId, courseTitle, currentPercentage) => {
    try {
      const success = await updateUserProgress(courseId, courseTitle, currentPercentage, noteText);
      if (success) {
        message.success('Notes saved!');
        setEditingNotes(null);
        setNoteText('');
        loadDashboardData();
      }
    } catch (error) {
      message.error('Failed to save notes');
    }
  };

  const getProgressColor = (percentage) => {
    if (percentage >= 80) return '#52c41a';
    if (percentage >= 50) return '#1890ff';
    if (percentage >= 20) return '#faad14';
    return '#f5222d';
  };

  const getProgressStatus = (percentage) => {
    if (percentage >= 100) return 'Completed';
    if (percentage >= 80) return 'Almost Done';
    if (percentage >= 50) return 'In Progress';
    if (percentage >= 20) return 'Started';
    return 'Just Beginning';
  };

  if (!isAuthenticated) {
    return (
      <Card>
        <Empty description="Please log in to view your dashboard" />
      </Card>
    );
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" tip="Loading your dashboard..." />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      style={{ padding: '20px' }}
    >
      {/* User Welcome Card */}
      <Card
        style={{ marginBottom: '20px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
        bodyStyle={{ color: 'white' }}
      >
        <Row align="middle">
          <Col span={2}>
            <UserOutlined style={{ fontSize: '48px', color: 'white' }} />
          </Col>
          <Col span={22}>
            <Title level={2} style={{ color: 'white', margin: 0 }}>
              Welcome back, {user?.full_name || 'Learner'}!
            </Title>
            <Text style={{ color: 'rgba(255,255,255,0.9)' }}>
              {user?.role_department && `Department: ${user.role_department} | `}
              {user?.experience_level && `Level: ${user.experience_level} | `}
              {user?.email}
            </Text>
            {user?.learning_goals && (
              <Paragraph style={{ color: 'rgba(255,255,255,0.9)', marginTop: '10px' }}>
                Learning Goals: {user.learning_goals}
              </Paragraph>
            )}
          </Col>
        </Row>
      </Card>

      {/* Statistics Cards */}
      <Row gutter={16} style={{ marginBottom: '20px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable>
            <Statistic
              title="Courses Started"
              value={stats.totalCourses}
              prefix={<BookOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable>
            <Statistic
              title="Completed"
              value={stats.completedCourses}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable>
            <Statistic
              title="Average Progress"
              value={stats.averageProgress}
              suffix="%"
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable>
            <Statistic
              title="Questions Asked"
              value={stats.totalQuestions}
              prefix={<HistoryOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Course Progress Section */}
      <Card
        title={
          <Space>
            <BookOutlined />
            <span>Your Course Progress</span>
          </Space>
        }
        style={{ marginBottom: '20px' }}
      >
        {courseProgress.length > 0 ? (
          <List
            dataSource={courseProgress}
            renderItem={(item) => (
              <List.Item
                actions={[
                  <Button
                    size="small"
                    icon={<EditOutlined />}
                    onClick={() => {
                      setEditingNotes(item.course_id);
                      setNoteText(item.notes || '');
                    }}
                  >
                    Notes
                  </Button>
                ]}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Text strong>{item.course_title || `Course ${item.course_id}`}</Text>
                      <Tag color={getProgressColor(item.completion_percentage)}>
                        {getProgressStatus(item.completion_percentage)}
                      </Tag>
                    </Space>
                  }
                  description={
                    <div>
                      <Progress
                        percent={item.completion_percentage}
                        strokeColor={getProgressColor(item.completion_percentage)}
                        style={{ marginBottom: '8px' }}
                      />
                      <Text type="secondary">
                        Last accessed: {new Date(item.last_accessed).toLocaleDateString()}
                      </Text>
                      {item.notes && (
                        <Paragraph
                          style={{
                            marginTop: '8px',
                            padding: '8px',
                            background: '#f0f0f0',
                            borderRadius: '4px'
                          }}
                        >
                          <Text italic>Notes: {item.notes}</Text>
                        </Paragraph>
                      )}
                      {/* Quick progress update buttons */}
                      <div style={{ marginTop: '10px' }}>
                        <Space>
                          <Button
                            size="small"
                            onClick={() => handleUpdateProgress(
                              item.course_id,
                              item.course_title,
                              Math.min(100, item.completion_percentage + 10)
                            )}
                          >
                            +10%
                          </Button>
                          <Button
                            size="small"
                            type="primary"
                            icon={<CheckCircleOutlined />}
                            onClick={() => handleUpdateProgress(item.course_id, item.course_title, 100)}
                            disabled={item.completion_percentage >= 100}
                          >
                            Mark Complete
                          </Button>
                        </Space>
                      </div>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty
            description="No courses started yet"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" onClick={() => window.location.href = '/'}>
              Browse Courses
            </Button>
          </Empty>
        )}
      </Card>

      {/* Recent Chat History */}
      <Card
        title={
          <Space>
            <HistoryOutlined />
            <span>Recent Learning Conversations</span>
          </Space>
        }
      >
        {chatHistory.length > 0 ? (
          <Timeline mode="left">
            {chatHistory.slice(0, 10).map((item, index) => (
              <Timeline.Item
                key={index}
                label={new Date(item.created_at).toLocaleString()}
                color={index === 0 ? 'green' : 'blue'}
              >
                <Card size="small" hoverable>
                  <Text strong>You asked:</Text>
                  <Paragraph ellipsis={{ rows: 2, expandable: true }}>
                    {item.question}
                  </Paragraph>
                  <Text strong>NvidiAdvisor answered:</Text>
                  <Paragraph ellipsis={{ rows: 3, expandable: true }}>
                    {item.answer}
                  </Paragraph>
                </Card>
              </Timeline.Item>
            ))}
          </Timeline>
        ) : (
          <Empty
            description="No chat history yet"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Text type="secondary">Start asking questions to build your learning history!</Text>
          </Empty>
        )}
      </Card>

      {/* Session Management Section */}
      <Card
        title={
          <Space>
            <SafetyOutlined />
            <span>Active Sessions</span>
          </Space>
        }
        extra={
          <Popconfirm
            title="Logout from all other devices?"
            description="This will end all your sessions except the current one."
            onConfirm={handleLogoutAllDevices}
            okText="Yes"
            cancelText="No"
          >
            <Button
              danger
              icon={<LogoutOutlined />}
              disabled={sessions.length <= 1}
            >
              Logout All Other Devices
            </Button>
          </Popconfirm>
        }
        style={{ marginBottom: '20px' }}
      >
        {sessionsLoading ? (
          <Spin />
        ) : sessions.length > 0 ? (
          <Table
            dataSource={sessions.map((session, index) => ({
              ...session,
              key: session.session_token || index
            }))}
            pagination={false}
            columns={[
              {
                title: 'Device',
                key: 'device',
                render: (_, record) => (
                  <Space>
                    {record.is_current ? (
                      <Badge status="success" text={<><DesktopOutlined /> Current Session</>} />
                    ) : (
                      <><MobileOutlined /> Other Device</>
                    )}
                  </Space>
                )
              },
              {
                title: 'Login Time',
                dataIndex: 'created_at',
                key: 'created_at',
                render: (date) => new Date(date).toLocaleString()
              },
              {
                title: 'Expires At',
                dataIndex: 'expires_at',
                key: 'expires_at',
                render: (date) => {
                  const expiryDate = new Date(date);
                  const now = new Date();
                  const hoursLeft = Math.round((expiryDate - now) / (1000 * 60 * 60));

                  return (
                    <Space>
                      <Text>{expiryDate.toLocaleString()}</Text>
                      {hoursLeft > 0 && (
                        <Tag color={hoursLeft < 2 ? 'red' : hoursLeft < 6 ? 'orange' : 'green'}>
                          {hoursLeft}h left
                        </Tag>
                      )}
                    </Space>
                  );
                }
              },
              {
                title: 'Action',
                key: 'action',
                render: (_, record) => (
                  record.is_current ? (
                    <Tag color="green">Current</Tag>
                  ) : (
                    <Popconfirm
                      title="Revoke this session?"
                      description="This device will be logged out."
                      onConfirm={() => handleRevokeSession(record.session_token)}
                      okText="Yes"
                      cancelText="No"
                    >
                      <Button
                        danger
                        size="small"
                        icon={<DeleteOutlined />}
                      >
                        Revoke
                      </Button>
                    </Popconfirm>
                  )
                )
              }
            ]}
          />
        ) : (
          <Empty
            description="No active sessions"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}

        <div style={{ marginTop: '16px', padding: '12px', background: '#f0f0f0', borderRadius: '4px' }}>
          <Text type="secondary">
            <SafetyOutlined /> Sessions automatically expire after 24 hours of inactivity.
            You can have multiple active sessions across different devices.
          </Text>
        </div>
      </Card>

      {/* Notes Edit Modal */}
      <Modal
        title="Edit Course Notes"
        open={editingNotes !== null}
        onOk={() => {
          const course = courseProgress.find(c => c.course_id === editingNotes);
          if (course) {
            handleSaveNotes(course.course_id, course.course_title, course.completion_percentage);
          }
        }}
        onCancel={() => {
          setEditingNotes(null);
          setNoteText('');
        }}
      >
        <TextArea
          value={noteText}
          onChange={(e) => setNoteText(e.target.value)}
          placeholder="Add your notes about this course..."
          rows={4}
        />
      </Modal>
    </motion.div>
  );
};

export default UserDashboard;