export interface Course {
  id: string;
  title: string;
  duration: string;
  price: string;
  type: 'self-paced' | 'instructor-led' | 'certification';
  category: string;
  subcategory?: string;
  prerequisites?: string[];
  nextCourses?: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  certificate: boolean;
  digitalBadge: boolean;
  description?: string;
  skills: string[];
  role: 'developer' | 'administrator' | 'both';
}

export interface LearningPath {
  id: string;
  title: string;
  role: 'developer' | 'administrator';
  category: string;
  courses: string[]; // Course IDs
  description: string;
  totalDuration?: string;
  totalCost?: number;
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  role: 'developer' | 'administrator' | 'both';
  currentSkills: string[];
  targetSkills: string[];
  completedCourses: string[];
  inProgressCourses: string[];
  savedPaths: string[];
  budget?: number;
  timeAvailable?: string;
}

export interface ProgressTracker {
  userId: string;
  courseId: string;
  status: 'not-started' | 'in-progress' | 'completed';
  startDate?: Date;
  completionDate?: Date;
  percentComplete: number;
  notes?: string;
}

export type PathRecommendation = {
  pathId: string;
  score: number;
  reasoning: string;
  estimatedTime: string;
  estimatedCost: number;
  matchedSkills: string[];
  gapSkills: string[];
};