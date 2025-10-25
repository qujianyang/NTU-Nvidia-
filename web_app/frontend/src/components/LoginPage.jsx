import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Checkbox, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { gsap } from 'gsap';
import { motion } from 'framer-motion';
import MagneticButton from './MagneticButton';
import { useAuth } from '../context/AuthContext';
import { ROUTES } from '../constants/routes';
import './LoginPage.css';

const LoginPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const { login } = useAuth();
  const navigate = useNavigate();

  const containerRef = useRef(null);
  const cardRef = useRef(null);
  const particlesRef = useRef(null);

  // Initialize particle effect
  useEffect(() => {
    if (!particlesRef.current) return;

    const canvas = particlesRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const particleCount = 100;

    class Particle {
      constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 0.5;
        this.speedX = Math.random() * 2 - 1;
        this.speedY = Math.random() * 2 - 1;
        this.opacity = Math.random() * 0.5 + 0.2;
      }

      update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x > canvas.width) this.x = 0;
        if (this.x < 0) this.x = canvas.width;
        if (this.y > canvas.height) this.y = 0;
        if (this.y < 0) this.y = canvas.height;
      }

      draw() {
        ctx.fillStyle = `rgba(118, 185, 0, ${this.opacity})`;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fill();
      }
    }

    // Create particles
    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle());
    }

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach(particle => {
        particle.update();
        particle.draw();
      });

      requestAnimationFrame(animate);
    };

    animate();

    // Resize handler
    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // 3D card rotation effect
  const handleMouseMove = (e) => {
    if (!cardRef.current) return;

    const rect = cardRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2;

    setMousePos({ x, y });

    gsap.to(cardRef.current, {
      rotateY: x * 15,
      rotateX: -y * 15,
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

  // Entrance animation
  useEffect(() => {
    const tl = gsap.timeline();

    tl.fromTo(
      cardRef.current,
      {
        opacity: 0,
        scale: 0.8,
        y: 100,
        rotateX: -30,
      },
      {
        opacity: 1,
        scale: 1,
        y: 0,
        rotateX: 0,
        duration: 1.2,
        ease: 'power3.out',
      }
    )
    .fromTo(
      '.form-item',
      {
        opacity: 0,
        x: -50,
      },
      {
        opacity: 1,
        x: 0,
        duration: 0.6,
        stagger: 0.1,
        ease: 'power2.out',
      },
      '-=0.5'
    );
  }, []);

  const onFinish = async (values) => {
    setLoading(true);

    // Success animation preparation
    const successAnimation = () => {
      gsap.timeline()
        .to(cardRef.current, {
          scale: 1.05,
          duration: 0.2,
          ease: 'power2.in',
        })
        .to(cardRef.current, {
          scale: 0.9,
          opacity: 0,
          y: -100,
          duration: 0.5,
          ease: 'power2.in',
        })
        .call(() => {
          navigate(ROUTES.DASHBOARD);
        });
    };

    try {
      const result = await login(values.email, values.password, values.remember);

      if (result.success) {
        successAnimation();
      } else {
        // Error shake animation
        gsap.to(cardRef.current, {
          x: [-10, 10, -10, 10, 0],
          duration: 0.4,
          ease: 'power2.inOut',
        });
        setLoading(false);
      }
    } catch (error) {
      setLoading(false);
    }
  };

  return (
    <div className="login-container" ref={containerRef}>
      {/* Particle Canvas */}
      <canvas ref={particlesRef} className="particles-canvas" />

      {/* Gradient Background */}
      <div className="gradient-bg">
        <div className="gradient-orb orb-1" />
        <div className="gradient-orb orb-2" />
        <div className="gradient-orb orb-3" />
      </div>

      {/* Login Card */}
      <motion.div
        ref={cardRef}
        className="login-card glass-morphism"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        {/* Glow effect */}
        <div
          className="card-glow"
          style={{
            transform: `translate(${mousePos.x * 20}px, ${mousePos.y * 20}px)`,
          }}
        />

        {/* Logo and Title */}
        <div className="login-header">
          <div className="nvidia-logo">
            <span className="logo-text">NVIDIA</span>
            <span className="logo-subtitle">Learning Universe</span>
          </div>
          <h1 className="login-title">Welcome Back</h1>
          <p className="login-subtitle">Continue your learning journey</p>
        </div>

        {/* Login Form */}
        <Form
          form={form}
          name="login"
          onFinish={onFinish}
          className="login-form"
          layout="vertical"
        >
          <Form.Item
            name="email"
            className="form-item"
            rules={[
              { required: true, message: 'Please input your email!' },
              { type: 'email', message: 'Please enter a valid email!' }
            ]}
          >
            <Input
              prefix={<MailOutlined className="input-icon" />}
              placeholder="Email"
              size="large"
              className="glass-input"
            />
          </Form.Item>

          <Form.Item
            name="password"
            className="form-item"
            rules={[{ required: true, message: 'Please input your password!' }]}
          >
            <Input.Password
              prefix={<LockOutlined className="input-icon" />}
              placeholder="Password"
              size="large"
              className="glass-input"
            />
          </Form.Item>

          <Form.Item className="form-item remember-row">
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox className="glass-checkbox">Remember me</Checkbox>
            </Form.Item>
            <a className="forgot-link" href="#">
              Forgot password?
            </a>
          </Form.Item>

          <Form.Item className="form-item">
            <MagneticButton
              type="primary"
              htmlType="submit"
              loading={loading}
              size="large"
              magnetStrength={0.3}
              style={{ width: '100%', height: 48 }}
            >
              {loading ? 'Logging in...' : 'Login to Universe'}
            </MagneticButton>
          </Form.Item>

          <div className="form-footer">
            <span>New to NVIDIA Learning? </span>
            <Link to={ROUTES.REGISTER} className="register-link">
              Create an account
            </Link>
          </div>
        </Form>

        {/* Decorative elements */}
        <div className="corner-decoration top-left" />
        <div className="corner-decoration top-right" />
        <div className="corner-decoration bottom-left" />
        <div className="corner-decoration bottom-right" />
      </motion.div>
    </div>
  );
};

export default LoginPage;