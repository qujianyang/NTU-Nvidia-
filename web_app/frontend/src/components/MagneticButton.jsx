import React, { useRef, useEffect, useState } from 'react';
import { gsap } from 'gsap';
import './MagneticButton.css';

const MagneticButton = ({
  children,
  onClick,
  variant = 'primary',
  size = 'medium',
  magnetStrength = 0.3
}) => {
  const buttonRef = useRef(null);
  const textRef = useRef(null);
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    const button = buttonRef.current;
    if (!button) return;

    const handleMouseMove = (e) => {
      const rect = button.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      // Calculate distance from center
      const distance = Math.sqrt(x * x + y * y);
      const maxDistance = Math.max(rect.width, rect.height);

      // Apply magnetic effect based on distance
      if (distance < maxDistance) {
        const strength = (1 - distance / maxDistance) * magnetStrength;

        gsap.to(button, {
          x: x * strength,
          y: y * strength,
          duration: 0.3,
          ease: 'power2.out',
        });

        // Move text in opposite direction for depth
        if (textRef.current) {
          gsap.to(textRef.current, {
            x: -x * strength * 0.3,
            y: -y * strength * 0.3,
            duration: 0.3,
            ease: 'power2.out',
          });
        }
      }
    };

    const handleMouseLeave = () => {
      gsap.to(button, {
        x: 0,
        y: 0,
        duration: 0.5,
        ease: 'elastic.out(1, 0.3)',
      });

      if (textRef.current) {
        gsap.to(textRef.current, {
          x: 0,
          y: 0,
          duration: 0.5,
          ease: 'elastic.out(1, 0.3)',
        });
      }

      setIsHovered(false);
    };

    const handleMouseEnter = () => {
      setIsHovered(true);
    };

    button.addEventListener('mousemove', handleMouseMove);
    button.addEventListener('mouseleave', handleMouseLeave);
    button.addEventListener('mouseenter', handleMouseEnter);

    return () => {
      button.removeEventListener('mousemove', handleMouseMove);
      button.removeEventListener('mouseleave', handleMouseLeave);
      button.removeEventListener('mouseenter', handleMouseEnter);
    };
  }, [magnetStrength]);

  return (
    <button
      ref={buttonRef}
      className={`magnetic-btn magnetic-btn--${variant} magnetic-btn--${size}`}
      onClick={onClick}
    >
      <span className="magnetic-btn__glow" />
      <span className="magnetic-btn__border">
        <svg width="100%" height="100%">
          <rect
            width="100%"
            height="100%"
            fill="none"
            stroke="url(#gradient)"
            strokeWidth="2"
            strokeDasharray={isHovered ? "0" : "10 5"}
            strokeDashoffset={isHovered ? "0" : "0"}
            className="border-animation"
          />
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#76b900" stopOpacity="1" />
              <stop offset="100%" stopColor="#91ce47" stopOpacity="1" />
            </linearGradient>
          </defs>
        </svg>
      </span>
      <span ref={textRef} className="magnetic-btn__text">
        {children}
      </span>
      <span className="magnetic-btn__particles">
        {[...Array(6)].map((_, i) => (
          <span key={i} className="particle" />
        ))}
      </span>
    </button>
  );
};

// Custom Cursor Component
export const CustomCursor = () => {
  const cursorRef = useRef(null);
  const cursorDotRef = useRef(null);

  useEffect(() => {
    const cursor = cursorRef.current;
    const cursorDot = cursorDotRef.current;
    if (!cursor || !cursorDot) return;

    let mouseX = 0;
    let mouseY = 0;
    let cursorX = 0;
    let cursorY = 0;
    let dotX = 0;
    let dotY = 0;

    const handleMouseMove = (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    };

    // Smooth cursor animation
    const animateCursor = () => {
      // Smooth follow for outer cursor
      cursorX += (mouseX - cursorX) * 0.1;
      cursorY += (mouseY - cursorY) * 0.1;
      cursor.style.transform = `translate(${cursorX - 20}px, ${cursorY - 20}px)`;

      // Faster follow for dot
      dotX += (mouseX - dotX) * 0.3;
      dotY += (mouseY - dotY) * 0.3;
      cursorDot.style.transform = `translate(${dotX - 5}px, ${dotY - 5}px)`;

      requestAnimationFrame(animateCursor);
    };

    // Handle hover states
    const handleMouseOver = (e) => {
      if (e.target.matches('button, a, .clickable')) {
        cursor.classList.add('cursor--hover');
        cursorDot.classList.add('cursor-dot--hover');
      }
    };

    const handleMouseOut = () => {
      cursor.classList.remove('cursor--hover');
      cursorDot.classList.remove('cursor-dot--hover');
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseover', handleMouseOver);
    document.addEventListener('mouseout', handleMouseOut);
    animateCursor();

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseover', handleMouseOver);
      document.removeEventListener('mouseout', handleMouseOut);
    };
  }, []);

  return (
    <>
      <div ref={cursorRef} className="custom-cursor" />
      <div ref={cursorDotRef} className="custom-cursor-dot" />
    </>
  );
};

export default MagneticButton;