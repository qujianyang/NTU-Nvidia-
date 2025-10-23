import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message, Space, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const { Title, Text } = Typography;

const LoginPage = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/login', {
        email: values.email,
        password: values.password
      }, {
        withCredentials: true  // Important for cookies/sessions
      });

      if (response.data.success) {
        message.success('Login successful!');
        onLogin(response.data.user);
        navigate('/');  // Redirect to main app
      }
    } catch (error) {
      if (error.response?.data?.error) {
        message.error(error.response.data.error);
      } else {
        message.error('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card
        style={{
          width: 400,
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
        }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8 }}>
              Welcome Back
            </Title>
            <Text type="secondary">
              Login to continue your learning journey
            </Text>
          </div>

          <Form
            name="login"
            onFinish={handleSubmit}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: 'Please enter your email' },
                { type: 'email', message: 'Please enter a valid email' }
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="Email"
                type="email"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: 'Please enter your password' }
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
                style={{
                  height: 45,
                  fontSize: 16,
                  background: '#76b900'
                }}
              >
                Login
              </Button>
            </Form.Item>
          </Form>

          <Divider>OR</Divider>

          <div style={{ textAlign: 'center' }}>
            <Text>
              Don't have an account?{' '}
              <Link to="/register" style={{ color: '#76b900', fontWeight: 'bold' }}>
                Register Now
              </Link>
            </Text>
          </div>

          <div style={{ textAlign: 'center' }}>
            <Link to="/" style={{ color: '#666', fontSize: 12 }}>
              Continue as Guest
            </Link>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default LoginPage;