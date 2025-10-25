import React, { useState, useRef, useEffect } from 'react';
import {
  Drawer,
  Input,
  Button,
  Space,
  Avatar,
  Typography,
  Divider,
  List,
  Spin,
  Badge,
  message as antMessage
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  CloseOutlined,
} from '@ant-design/icons';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const { TextArea } = Input;
const { Text, Title } = Typography;

const ChatWidget = ({ open, onClose }) => {
  const { isAuthenticated, user, updateUserProgress } = useAuth();
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: isAuthenticated
        ? `Hello ${user?.full_name || 'there'}! I'm your NVIDIA Course Advisor. Ask me about courses, prerequisites, learning paths, or anything related to your learning journey!`
        : "Hello! I'm your NVIDIA Course Advisor. Ask me about courses, prerequisites, learning paths, or anything related to your learning journey!",
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Make chat globally accessible for course cards
  useEffect(() => {
    window.openChatWithCourse = (course) => {
      onClose(); // Close if already open to trigger re-open
      setTimeout(() => {
        onClose(); // Ensure closed
        setTimeout(() => {
          window.dispatchEvent(new CustomEvent('openChat'));
          setTimeout(() => {
            setInputValue(`Tell me more about ${course.title}`);
          }, 100);
        }, 100);
      }, 100);
    };

    const handleOpenChat = () => {
      onClose(); // This should actually open it - you might need to adjust based on your implementation
    };

    window.addEventListener('openChat', handleOpenChat);
    return () => {
      window.removeEventListener('openChat', handleOpenChat);
      delete window.openChatWithCourse;
    };
  }, [onClose]);

  // Function to detect if a course is mentioned
  const detectCourseInQuestion = (question) => {
    const courseKeywords = ['course', 'learning', 'training', 'prerequisite', 'deep learning',
                          'ai', 'machine learning', 'nvidia', 'fundamentals', 'advanced'];
    const lowerQuestion = question.toLowerCase();
    return courseKeywords.some(keyword => lowerQuestion.includes(keyword));
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputValue; // Store for progress tracking
    setInputValue('');
    setLoading(true);

    try {
      const response = await axios.post('/api/chat', {
        question: currentInput
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.data.answer,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);

      // Track progress if user is authenticated and asking about courses
      if (isAuthenticated && detectCourseInQuestion(currentInput)) {
        // Increment progress for general course exploration
        const progressIncrement = 5; // 5% for each meaningful interaction

        // You could enhance this to detect specific course IDs from the response
        // For now, track general learning engagement
        try {
          await updateUserProgress(
            'general-exploration',
            'Course Exploration & Learning',
            progressIncrement
          );
        } catch (err) {
          console.log('Could not update progress:', err);
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      antMessage.error('Failed to get response');

      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        error: true,
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const MessageBubble = ({ message }) => {
    const isBot = message.type === 'bot';

    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        style={{
          display: 'flex',
          justifyContent: isBot ? 'flex-start' : 'flex-end',
          marginBottom: 16,
        }}
      >
        <Space
          align="start"
          style={{ maxWidth: '80%' }}
          direction={isBot ? 'horizontal' : 'horizontal-reverse'}
        >
          <Avatar
            icon={isBot ? <RobotOutlined /> : <UserOutlined />}
            style={{
              backgroundColor: isBot ? '#76b900' : '#1890ff',
            }}
          />
          <div
            style={{
              background: isBot ? '#f0f0f0' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: isBot ? '#000' : '#fff',
              padding: '12px 16px',
              borderRadius: isBot ? '4px 18px 18px 18px' : '18px 4px 18px 18px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              wordBreak: 'break-word',
            }}
          >
            <Text style={{ color: isBot ? '#000' : '#fff' }}>
              {message.content}
            </Text>
            <div style={{ marginTop: 4 }}>
              <Text
                type="secondary"
                style={{
                  fontSize: 11,
                  color: isBot ? '#666' : 'rgba(255,255,255,0.8)'
                }}
              >
                {new Date(message.timestamp).toLocaleTimeString()}
              </Text>
            </div>
          </div>
        </Space>
      </motion.div>
    );
  };

  return (
    <Drawer
      title={
        <Space>
          <Badge status="success" />
          <Title level={4} style={{ margin: 0 }}>
            NvidiAdvisor
          </Title>
        </Space>
      }
      placement="right"
      onClose={onClose}
      open={open}
      width={420}
      bodyStyle={{ padding: 0, display: 'flex', flexDirection: 'column' }}
      extra={
        <Button
          type="text"
          icon={<CloseOutlined />}
          onClick={onClose}
        />
      }
    >
      {/* Messages Area */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px',
          background: '#fafafa',
        }}
      >
        <AnimatePresence>
          {messages.map(message => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </AnimatePresence>

        {loading && (
          <div style={{ textAlign: 'center', padding: 16 }}>
            <Spin tip="Thinking..." />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div
        style={{
          padding: 16,
          background: '#fff',
          borderTop: '1px solid #f0f0f0',
        }}
      >
        <Space.Compact style={{ width: '100%' }}>
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onPressEnter={(e) => {
              if (!e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask about courses, prerequisites, or learning paths..."
            autoSize={{ minRows: 1, maxRows: 4 }}
            style={{ borderRadius: '8px 0 0 8px' }}
            disabled={loading}
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSend}
            loading={loading}
            style={{
              borderRadius: '0 8px 8px 0',
              height: 'auto',
              minHeight: 32,
            }}
          >
            Send
          </Button>
        </Space.Compact>
        <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
          Press Enter to send, Shift+Enter for new line
        </Text>
      </div>
    </Drawer>
  );
};

export default ChatWidget;