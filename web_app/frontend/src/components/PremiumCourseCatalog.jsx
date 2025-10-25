import React, { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useInView } from 'react-intersection-observer';
import { tokens } from '../styles/tokens';
import './PremiumCourseCatalog.css';

// Register GSAP plugins
gsap.registerPlugin(ScrollTrigger);

// Glassmorphic Card with hover effects
const GlassCard = ({ course, index }) => {
  const cardRef = useRef(null);
  const glowRef = useRef(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const { ref: inViewRef, inView } = useInView({
    threshold: 0.1,
    triggerOnce: true,
  });

  // Combine refs
  const setRefs = (el) => {
    cardRef.current = el;
    inViewRef(el);
  };

  // Entrance animation
  useEffect(() => {
    if (inView && cardRef.current) {
      gsap.fromTo(
        cardRef.current,
        {
          opacity: 0,
          y: 100,
          rotateX: -15,
        },
        {
          opacity: 1,
          y: 0,
          rotateX: 0,
          duration: 1,
          delay: index * 0.1,
          ease: 'power3.out',
        }
      );
    }
  }, [inView, index]);

  // 3D tilt effect on mouse move
  const handleMouseMove = (e) => {
    if (!cardRef.current) return;

    const rect = cardRef.current.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
    const y = ((e.clientY - rect.top) / rect.height - 0.5) * 2;

    setMousePos({ x, y });

    gsap.to(cardRef.current, {
      rotateY: x * 10,
      rotateX: -y * 10,
      duration: 0.5,
      ease: 'power2.out',
      transformPerspective: 1000,
    });

    // Move glow effect
    if (glowRef.current) {
      gsap.to(glowRef.current, {
        x: e.clientX - rect.left - rect.width / 2,
        y: e.clientY - rect.top - rect.height / 2,
        duration: 0.3,
      });
    }
  };

  const handleMouseLeave = () => {
    gsap.to(cardRef.current, {
      rotateY: 0,
      rotateX: 0,
      duration: 0.5,
      ease: 'power2.out',
    });
  };

  const getLevelGradient = (level) => {
    if (!level) return tokens.colors.gradients.dark;
    const levelLower = level.toLowerCase();
    if (levelLower.includes('beginner'))
      return 'linear-gradient(135deg, #52c41a 0%, #73d13d 100%)';
    if (levelLower.includes('intermediate'))
      return 'linear-gradient(135deg, #faad14 0%, #ffc53d 100%)';
    if (levelLower.includes('advanced'))
      return 'linear-gradient(135deg, #f5222d 0%, #ff4d4f 100%)';
    return 'linear-gradient(135deg, #1890ff 0%, #40a9ff 100%)';
  };

  return (
    <div
      ref={setRefs}
      className="glass-card"
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      data-course-id={course.id}
    >
      {/* Glow effect that follows mouse */}
      <div ref={glowRef} className="glow-effect" />

      {/* Level indicator strip */}
      <div
        className="level-strip"
        style={{ background: getLevelGradient(course.level) }}
      />

      {/* Glass background layers */}
      <div className="glass-layer layer-1" />
      <div className="glass-layer layer-2" />

      {/* Content */}
      <div className="card-content">
        <div className="card-header">
          <h3 className="card-title">{course.title}</h3>
          <div className="price-badge">
            {course.price === 'Free' ? (
              <span className="free">FREE</span>
            ) : (
              <span className="paid">{course.price}</span>
            )}
          </div>
        </div>

        <p className="card-description">{course.description}</p>

        <div className="card-meta">
          <span className="meta-item">
            <i className="icon-clock" />
            {course.duration || 'N/A'}
          </span>
          <span className="meta-item">
            <i className="icon-level" />
            {course.level || 'General'}
          </span>
        </div>

        {/* Prerequisites with animation */}
        {course.prerequisites && Array.isArray(course.prerequisites) && course.prerequisites.length > 0 && (
          <div className="prerequisites">
            <span className="prereq-label">Prerequisites:</span>
            <div className="prereq-tags">
              {course.prerequisites.map((prereq) => (
                <span key={prereq} className="prereq-tag">
                  {prereq}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Animated CTA button */}
        <button className="cta-button magnetic-button">
          <span className="button-text">Explore Course</span>
          <span className="button-glow" />
        </button>
      </div>

      {/* Particle effects on hover */}
      <canvas className="particle-canvas" />
    </div>
  );
};

// Hero Section with parallax
const HeroSection = () => {
  const heroRef = useRef(null);
  const titleRef = useRef(null);
  const subtitleRef = useRef(null);

  useEffect(() => {
    // Parallax scrolling
    gsap.to(heroRef.current, {
      yPercent: -50,
      ease: 'none',
      scrollTrigger: {
        trigger: heroRef.current,
        start: 'top top',
        end: 'bottom top',
        scrub: true,
      },
    });

    // Text animations
    const tl = gsap.timeline();

    tl.fromTo(
      titleRef.current,
      { opacity: 0, y: 100, scale: 0.8 },
      { opacity: 1, y: 0, scale: 1, duration: 1.5, ease: 'power4.out' }
    )
    .fromTo(
      subtitleRef.current,
      { opacity: 0, y: 50 },
      { opacity: 1, y: 0, duration: 1, ease: 'power3.out' },
      '-=0.5'
    );

    // Floating animation
    gsap.to(titleRef.current, {
      y: -10,
      duration: 2,
      repeat: -1,
      yoyo: true,
      ease: 'power1.inOut',
    });
  }, []);

  return (
    <div ref={heroRef} className="hero-section">
      <div className="hero-background">
        <div className="gradient-mesh" />
        <div className="noise-texture" />
      </div>

      <div className="hero-content">
        <h1 ref={titleRef} className="hero-title">
          <span className="title-gradient">NVIDIA</span>
          <br />
          Learning Universe
        </h1>
        <p ref={subtitleRef} className="hero-subtitle">
          Master AI and Robotics with Professional Courses
        </p>
      </div>

      {/* Scroll indicator */}
      <div className="scroll-indicator">
        <div className="scroll-dot" />
      </div>
    </div>
  );
};

// Main Premium Catalog Component
const PremiumCourseCatalog = ({ courses }) => {
  const containerRef = useRef(null);
  const [filteredCourses, setFilteredCourses] = useState(courses);

  useEffect(() => {
    // Set up smooth scrolling
    ScrollTrigger.defaults({
      toggleActions: 'play none none reverse',
    });

    return () => {
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
    };
  }, []);

  return (
    <div ref={containerRef} className="premium-catalog">
      <HeroSection />

      {/* Filter Section with animations */}
      <div className="filter-section">
        <div className="filter-container">
          <button className="filter-chip active" data-level="all">
            All Courses
          </button>
          <button className="filter-chip" data-level="beginner">
            Beginner
          </button>
          <button className="filter-chip" data-level="intermediate">
            Intermediate
          </button>
          <button className="filter-chip" data-level="advanced">
            Advanced
          </button>
        </div>
      </div>

      {/* Course Grid */}
      <div className="courses-grid">
        {filteredCourses.map((course, index) => (
          <GlassCard key={course.id} course={course} index={index} />
        ))}
      </div>

      {/* Background decoration */}
      <div className="decoration-orbs">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
      </div>
    </div>
  );
};

export default PremiumCourseCatalog;