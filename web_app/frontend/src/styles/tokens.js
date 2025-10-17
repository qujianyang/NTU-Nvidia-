// NVIDIA-inspired Design Token System
// Mathematical spacing, professional typography, and cinematic colors

export const tokens = {
  // Grid System (8px base unit)
  spacing: {
    xs: '4px',    // 0.5x
    sm: '8px',    // 1x
    md: '16px',   // 2x
    lg: '24px',   // 3x
    xl: '32px',   // 4x
    '2xl': '48px', // 6x
    '3xl': '64px', // 8x
    '4xl': '96px', // 12x
    '5xl': '128px', // 16x
  },

  // Typography Scale (Golden Ratio)
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem', // 36px
    '5xl': '3rem',    // 48px
    '6xl': '3.75rem', // 60px
    '7xl': '4.5rem',  // 72px
    '8xl': '6rem',    // 96px
    '9xl': '8rem',    // 128px
  },

  fontWeight: {
    thin: 100,
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
    black: 900,
  },

  // NVIDIA Color System
  colors: {
    // Primary Green (NVIDIA Brand)
    primary: {
      50: '#f0f9e8',
      100: '#d9f0c3',
      200: '#b9e28a',
      300: '#91ce47',
      400: '#76b900', // Main NVIDIA Green
      500: '#5e9300',
      600: '#4a7500',
      700: '#3a5a00',
      800: '#2b4200',
      900: '#1a2800',
    },

    // Dark Theme Colors (NVIDIA Dark)
    dark: {
      50: '#f5f5f5',
      100: '#e0e0e0',
      200: '#b3b3b3',
      300: '#808080',
      400: '#4d4d4d',
      500: '#333333',
      600: '#1a1a1a', // Main dark background
      700: '#141414',
      800: '#0d0d0d',
      900: '#000000',
    },

    // Gradients
    gradients: {
      primary: 'linear-gradient(135deg, #76b900 0%, #91ce47 100%)',
      dark: 'linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%)',
      glow: 'radial-gradient(circle at 50% 50%, rgba(118, 185, 0, 0.3) 0%, transparent 70%)',
      mesh: `radial-gradient(at 40% 20%, hsla(88, 100%, 36%, 0.3) 0px, transparent 50%),
             radial-gradient(at 80% 0%, hsla(89, 100%, 45%, 0.2) 0px, transparent 50%),
             radial-gradient(at 0% 50%, hsla(88, 100%, 40%, 0.2) 0px, transparent 50%),
             radial-gradient(at 80% 50%, hsla(90, 100%, 35%, 0.15) 0px, transparent 50%),
             radial-gradient(at 0% 100%, hsla(88, 100%, 38%, 0.2) 0px, transparent 50%)`,
      glass: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
    },

    // Semantic Colors
    semantic: {
      success: '#52c41a',
      warning: '#faad14',
      error: '#f5222d',
      info: '#1890ff',
    },
  },

  // Border Radius System
  borderRadius: {
    none: '0',
    sm: '4px',
    base: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    '2xl': '32px',
    full: '9999px',
  },

  // Shadow System (Elevation)
  shadows: {
    none: 'none',
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    base: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    md: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    lg: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
    xl: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    '2xl': '0 35px 60px -15px rgba(0, 0, 0, 0.3)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    glow: '0 0 40px rgba(118, 185, 0, 0.3)',
    glowLg: '0 0 60px rgba(118, 185, 0, 0.4)',
  },

  // Animation Durations
  animation: {
    duration: {
      instant: '100ms',
      fast: '200ms',
      base: '300ms',
      slow: '500ms',
      slower: '800ms',
      slowest: '1000ms',
    },
    easing: {
      linear: 'linear',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
      spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      bounce: 'cubic-bezier(0.68, -0.55, 0.25, 1.35)',
    },
  },

  // Blur Effects
  blur: {
    sm: '4px',
    base: '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
  },

  // Z-Index Layers
  zIndex: {
    negative: -1,
    base: 0,
    dropdown: 100,
    sticky: 200,
    overlay: 300,
    modal: 400,
    popover: 500,
    tooltip: 600,
    toast: 700,
    max: 9999,
  },
};