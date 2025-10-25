// Route constants for centralized path management
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  CATALOG: '/catalog',
  LEARNING_PATHS: '/paths',
  PROFILE: '/profile',
  LOGOUT: '/logout',
};

// Protected routes that require authentication
export const PROTECTED_ROUTES = [
  ROUTES.DASHBOARD,
  ROUTES.PROFILE,
];

// Public routes (accessible without auth)
export const PUBLIC_ROUTES = [
  ROUTES.HOME,
  ROUTES.LOGIN,
  ROUTES.REGISTER,
  ROUTES.CATALOG,
  ROUTES.LEARNING_PATHS,
];