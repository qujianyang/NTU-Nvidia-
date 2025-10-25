import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, message, Steps } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { gsap } from 'gsap';
import { motion, AnimatePresence } from 'framer-motion';
import MagneticButton from './MagneticButton';
import { useAuth } from '../context/AuthContext';
import { ROUTES } from '../constants/routes';
import './RegisterPage.css';

const { Step } = Steps;

const RegisterPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({});
  const { register } = useAuth();
  const navigate = useNavigate();

  const containerRef = useRef(null);
  const cardRef = useRef(null);
  const starsRef = useRef(null);

  // Animated starfield background
  useEffect(() => {
    if (!starsRef.current) return;

    const canvas = starsRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const stars = [];
    const starCount = 200;

    class Star {
      constructor() {
        this.reset();
        this.y = Math.random() * canvas.height;
      }

      reset() {
        this.x = Math.random() * canvas.width;
        this.y = -10;
        this.size = Math.random() * 2 + 0.5;
        this.speed = Math.random() * 3 + 1;
        this.opacity = Math.random() * 0.8 + 0.2;
        this.twinkle = Math.random() * 0.05;
      }

      update() {
        this.y += this.speed;
        this.opacity += this.twinkle;

        if (this.opacity > 1 || this.opacity < 0.2) {
          this.twinkle = -this.twinkle;
        }

        if (this.y > canvas.height) {
          this.reset();
        }
      }

      draw() {
        ctx.save();
        ctx.fillStyle = `rgba(118, 185, 0, ${this.opacity})`;
        ctx.shadowBlur = this.size * 2;
        ctx.shadowColor = '#76b900';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    // Create stars
    for (let i = 0; i < starCount; i++) {
      stars.push(new Star());
    }

    // Animation loop
    let animationId;
    const animate = () => {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      stars.forEach(star => {
        star.update();
        star.draw();
      });

      animationId = requestAnimationFrame(animate);
    };

    animate();

    return () => cancelAnimationFrame(animationId);
  }, []);

  // 3D tilt effect
  const handleMouseMove = (e) => {
    if (!cardRef.current) return;

    const rect = cardRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2;

    gsap.to(cardRef.current, {
      rotateY: x * 10,
      rotateX: -y * 10,
      duration: 0.5,
      ease: 'power2.out',
      transformPerspective: 1000,
    });
  };

  const handleMouseLeave = () => {
    gsap.to(cardRef.current, {
      rotateY: 0,
      rotateX: 0,
      duration: 0.5,
      ease: 'power2.out',
    });
  };

  // Multi-step form navigation
  const nextStep = () => {
    form.validateFields().then(values => {
      setFormData({ ...formData, ...values });

      gsap.to('.step-content', {
        opacity: 0,
        x: -50,
        duration: 0.3,
        onComplete: () => {
          setCurrentStep(currentStep + 1);
          gsap.fromTo('.step-content',
            { opacity: 0, x: 50 },
            { opacity: 1, x: 0, duration: 0.3 }
          );
        }
      });
    });
  };

  const prevStep = () => {
    gsap.to('.step-content', {
      opacity: 0,
      x: 50,
      duration: 0.3,
      onComplete: () => {
        setCurrentStep(currentStep - 1);
        gsap.fromTo('.step-content',
          { opacity: 0, x: -50 },
          { opacity: 1, x: 0, duration: 0.3 }
        );
      }
    });
  };

  const onFinish = async (values) => {
    const finalData = { ...formData, ...values };
    setLoading(true);

    try {
      const result = await register(
        finalData.username,
        finalData.email,
        finalData.password
      );

      if (result.success) {
        // Success animation
        gsap.timeline()
          .to(cardRef.current, {
            scale: 1.1,
            duration: 0.3,
            ease: 'power2.in',
          })
          .to(cardRef.current, {
            scale: 0,
            opacity: 0,
            rotateY: 180,
            duration: 0.7,
            ease: 'power2.in',
          })
          .call(() => {
            navigate(ROUTES.DASHBOARD);
          });
      } else {
        setLoading(false);
        // Error shake
        gsap.to(cardRef.current, {
          x: [-10, 10, -10, 10, 0],
          duration: 0.4,
        });
      }
    } catch (error) {
      setLoading(false);
    }
  };

  // Step content components
  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="step-content">
            <h3 className="step-title">Create Your Account</h3>
            <Form.Item
              name="username"
              rules={[
                { required: true, message: 'Please choose a username!' },
                { min: 3, message: 'Username must be at least 3 characters!' }
              ]}
            >
              <Input
                prefix={<UserOutlined className="input-icon" />}
                placeholder="Choose a username"
                size="large"
                className="glass-input"
              />
            </Form.Item>

            <Form.Item
              name="email"
              rules={[
                { required: true, message: 'Please input your email!' },
                { type: 'email', message: 'Please enter a valid email!' }
              ]}
            >
              <Input
                prefix={<MailOutlined className="input-icon" />}
                placeholder="Your email address"
                size="large"
                className="glass-input"
              />
            </Form.Item>

            <MagneticButton
              type="primary"
              onClick={nextStep}
              size="large"
              magnetStrength={0.3}
              style={{ width: '100%', height: 48, marginTop: '1rem' }}
            >
              Continue
            </MagneticButton>
          </div>
        );

      case 1:
        return (
          <div className="step-content">
            <h3 className="step-title">Secure Your Account</h3>
            <Form.Item
              name="password"
              rules={[
                { required: true, message: 'Please create a password!' },
                { min: 8, message: 'Password must be at least 8 characters!' }
              ]}
            >
              <Input.Password
                prefix={<LockOutlined className="input-icon" />}
                placeholder="Create a strong password"
                size="large"
                className="glass-input"
              />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              dependencies={['password']}
              rules={[
                { required: true, message: 'Please confirm your password!' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('Passwords do not match!'));
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined className="input-icon" />}
                placeholder="Confirm your password"
                size="large"
                className="glass-input"
              />
            </Form.Item>

            <div className="step-actions">
              <Button
                onClick={prevStep}
                size="large"
                className="glass-button-secondary"
                style={{ marginRight: '1rem' }}
              >
                Back
              </Button>
              <MagneticButton
                type="primary"
                htmlType="submit"
                loading={loading}
                size="large"
                magnetStrength={0.3}
                style={{ flex: 1, height: 48 }}
              >
                {loading ? 'Creating Account...' : 'Join NVIDIA Universe'}
              </MagneticButton>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="register-container" ref={containerRef}>
      {/* Animated Starfield */}
      <canvas ref={starsRef} className="stars-canvas" />

      {/* Gradient Mesh */}
      <div className="gradient-mesh">
        <div className="mesh-gradient gradient-1" />
        <div className="mesh-gradient gradient-2" />
        <div className="mesh-gradient gradient-3" />
        <div className="mesh-gradient gradient-4" />
      </div>

      {/* Register Card */}
      <motion.div
        ref={cardRef}
        className="register-card glass-morphism"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        initial={{ opacity: 0, y: 100 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
      >
        {/* Progress Indicator */}
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${((currentStep + 1) / 2) * 100}%` }}
          />
        </div>

        {/* Header */}
        <div className="register-header">
          <div className="nvidia-logo">
            <span className="logo-text">NVIDIA</span>
            <span className="logo-subtitle">Learning Universe</span>
          </div>
          <h1 className="register-title">Begin Your Journey</h1>
          <p className="register-subtitle">
            Join thousands mastering AI and robotics
          </p>
        </div>

        {/* Step Indicators */}
        <div className="steps-container">
          <Steps current={currentStep} className="glass-steps">
            <Step title="Account" icon={<UserOutlined />} />
            <Step title="Security" icon={<LockOutlined />} />
          </Steps>
        </div>

        {/* Form */}
        <Form
          form={form}
          name="register"
          onFinish={onFinish}
          className="register-form"
          layout="vertical"
        >
          <AnimatePresence mode="wait">
            {renderStepContent()}
          </AnimatePresence>
        </Form>

        {/* Footer */}
        <div className="form-footer">
          <span>Already have an account? </span>
          <Link to={ROUTES.LOGIN} className="login-link">
            Sign in
          </Link>
        </div>

        {/* Decorative Elements */}
        <div className="floating-shapes">
          <div className="shape shape-1" />
          <div className="shape shape-2" />
          <div className="shape shape-3" />
        </div>
      </motion.div>
    </div>
  );
};

export default RegisterPage;