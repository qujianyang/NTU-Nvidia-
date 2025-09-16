import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { PathwayVisualization } from './components/PathwayVisualization';
import { RoleSelector } from './components/RoleSelector';
import { SkillFilter } from './components/SkillFilter';
import { ProgressTracker } from './components/ProgressTracker';
import { CourseDetails } from './components/CourseDetails';
import { RecommendationPanel } from './components/RecommendationPanel';
import './App.css';

const queryClient = new QueryClient();

function App() {
  const [selectedRole, setSelectedRole] = useState<'developer' | 'administrator' | null>(null);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string | null>(null);
  const [userProgress, setUserProgress] = useState<Map<string, number>>(new Map());

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-green-900 to-emerald-900">
        <header className="bg-black/30 backdrop-blur-md border-b border-green-500/20">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
                  <svg className="w-8 h-8 text-black" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z"/>
                  </svg>
                </div>
                <h1 className="text-3xl font-bold text-white">NVIDIA Learning Pathways</h1>
              </div>
              <div className="flex items-center space-x-4">
                <button className="px-4 py-2 bg-green-500 text-black font-semibold rounded-lg hover:bg-green-400 transition">
                  Sign In
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-12 gap-6">
            {/* Left Sidebar - Filters and Role Selection */}
            <div className="col-span-3">
              <div className="bg-black/30 backdrop-blur-md rounded-xl p-6 border border-green-500/20">
                <h2 className="text-xl font-semibold text-white mb-4">Get Started</h2>
                <RoleSelector
                  selectedRole={selectedRole}
                  onRoleSelect={setSelectedRole}
                />

                <div className="mt-6">
                  <SkillFilter
                    selectedSkills={selectedSkills}
                    onSkillsChange={setSelectedSkills}
                    role={selectedRole}
                  />
                </div>

                <div className="mt-6">
                  <RecommendationPanel
                    role={selectedRole}
                    skills={selectedSkills}
                  />
                </div>
              </div>
            </div>

            {/* Center - Main Visualization */}
            <div className="col-span-6">
              <div className="bg-black/30 backdrop-blur-md rounded-xl p-6 border border-green-500/20">
                <PathwayVisualization
                  role={selectedRole}
                  selectedSkills={selectedSkills}
                  onCourseSelect={setSelectedCourse}
                  userProgress={userProgress}
                />
              </div>

              <div className="mt-6 bg-black/30 backdrop-blur-md rounded-xl p-6 border border-green-500/20">
                <ProgressTracker
                  userProgress={userProgress}
                  onProgressUpdate={setUserProgress}
                />
              </div>
            </div>

            {/* Right Sidebar - Course Details */}
            <div className="col-span-3">
              <div className="bg-black/30 backdrop-blur-md rounded-xl p-6 border border-green-500/20">
                <CourseDetails
                  courseId={selectedCourse}
                  onEnroll={(courseId) => {
                    const newProgress = new Map(userProgress);
                    newProgress.set(courseId, 0);
                    setUserProgress(newProgress);
                  }}
                />
              </div>
            </div>
          </div>
        </main>
      </div>
    </QueryClientProvider>
  );
}

export default App;