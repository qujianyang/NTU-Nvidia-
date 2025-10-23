import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message, Space, Select, Row, Col } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, TeamOutlined, RocketOutlined, TrophyOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const RegisterPage = ({ onLogin }) => {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/register', {
        email: values.email,
        password: values.password,
        full_name: values.full_name,
        role_department: values.role_department,
        learning_goals: values.learning_goals,
        experience_level: values.experience_level
      }, {
        withCredentials: true
      });

      if (response.data.success) {
        message.success('Registration successful! Welcome aboard!');
        onLogin(response.data.user);
        navigate('/');  // Redirect to main app
      }
    } catch (error) {
      if (error.response?.data?.error) {
        message.error(error.response.data.error);
      } else {
        message.error('Registration failed. Please try again.');
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
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px 0'
    }}>
      <Card
        style={{
          width: 600,
          maxHeight: '90vh',
          overflow: 'auto',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
        }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8 }}>
              Join NVIDIA Learning Hub
            </Title>
            <Text type="secondary">
              Create your account to start your AI & Robotics journey
            </Text>
          </div>

          <Form
            form={form}
            name="register"
            onFinish={handleSubmit}
            layout="vertical"
            size="large"
          >
            {/* Basic Information */}
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="full_name"
                  rules={[
                    { required: true, message: 'Please enter your full name' }
                  ]}
                >
                  <Input
                    prefix={<UserOutlined />}
                    placeholder="Full Name"
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
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
              </Col>
            </Row>

            {/* Password */}
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="password"
                  rules={[
                    { required: true, message: 'Please enter a password' },
                    { min: 6, message: 'Password must be at least 6 characters' }
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="Password"
                  />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="confirmPassword"
                  dependencies={['password']}
                  rules={[
                    { required: true, message: 'Please confirm your password' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('password') === value) {
                          return Promise.resolve();
                        }
                        return Promise.reject(new Error('Passwords do not match'));
                      },
                    }),
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined />}
                    placeholder="Confirm Password"
                  />
                </Form.Item>
              </Col>
            </Row>

            {/* Professional Information */}
            <Form.Item
              name="role_department"
              rules={[
                { required: false }
              ]}
            >
              <Input
                prefix={<TeamOutlined />}
                placeholder="Role/Department (e.g., Student, ML Engineer, Researcher)"
              />
            </Form.Item>

            {/* Experience Level */}
            <Form.Item
              name="experience_level"
              rules={[
                { required: true, message: 'Please select your experience level' }
              ]}
            >
              <Select
                placeholder="Select your experience level in robotics/AI"
                suffixIcon={<TrophyOutlined />}
              >
                <Option value="beginner">Beginner - Just starting out</Option>
                <Option value="intermediate">Intermediate - Some experience</Option>
                <Option value="advanced">Advanced - Significant experience</Option>
                <Option value="expert">Expert - Industry professional</Option>
              </Select>
            </Form.Item>

            {/* Learning Goals */}
            <Form.Item
              name="learning_goals"
              rules={[
                { required: false }
              ]}
            >
              <TextArea
                rows={3}
                placeholder="What are your learning goals? (e.g., Build AI applications, Master deep learning, Robotics simulation)"
                prefix={<RocketOutlined />}
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
                Create Account
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center' }}>
            <Text>
              Already have an account?{' '}
              <Link to="/login" style={{ color: '#76b900', fontWeight: 'bold' }}>
                Login
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

export default RegisterPage;