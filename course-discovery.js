// Sample Course Data
const coursesData = [
    {
        id: 1,
        title: "Introduction to Python for AI",
        description: "Learn Python fundamentals with a focus on AI and data science applications. Perfect for beginners.",
        difficulty: "beginner",
        duration: 4,
        prerequisites: [],
        topics: ["python", "programming-basics"],
        gpuRequired: false,
        thumbnail: "🐍",
        learningObjectives: ["Python syntax", "Data structures", "Functions", "Libraries for AI"]
    },
    {
        id: 2,
        title: "Neural Networks Fundamentals",
        description: "Understanding the building blocks of neural networks and deep learning architectures.",
        difficulty: "intermediate",
        duration: 8,
        prerequisites: [1],
        topics: ["neural-networks", "deep-learning"],
        gpuRequired: true,
        thumbnail: "🧠",
        learningObjectives: ["Perceptrons", "Backpropagation", "Activation functions", "Training neural nets"]
    },
    {
        id: 3,
        title: "Computer Vision with PyTorch",
        description: "Build state-of-the-art computer vision models using PyTorch and modern architectures.",
        difficulty: "advanced",
        duration: 12,
        prerequisites: [1, 2],
        topics: ["computer-vision", "deep-learning", "python"],
        gpuRequired: true,
        thumbnail: "👁️",
        learningObjectives: ["CNNs", "Image classification", "Object detection", "Image segmentation"]
    },
    {
        id: 4,
        title: "Natural Language Processing Basics",
        description: "Introduction to NLP techniques for text processing and language understanding.",
        difficulty: "intermediate",
        duration: 10,
        prerequisites: [1],
        topics: ["nlp", "python", "deep-learning"],
        gpuRequired: true,
        thumbnail: "💬",
        learningObjectives: ["Text preprocessing", "Word embeddings", "Sentiment analysis", "Named entity recognition"]
    },
    {
        id: 5,
        title: "Machine Learning Mathematics",
        description: "Essential mathematical concepts for understanding machine learning algorithms.",
        difficulty: "beginner",
        duration: 6,
        prerequisites: [],
        topics: ["mathematics", "linear-algebra", "statistics"],
        gpuRequired: false,
        thumbnail: "📊",
        learningObjectives: ["Linear algebra", "Calculus", "Probability", "Statistics"]
    },
    {
        id: 6,
        title: "Deep Learning with TensorFlow",
        description: "Master TensorFlow for building and deploying deep learning models at scale.",
        difficulty: "intermediate",
        duration: 10,
        prerequisites: [1, 2],
        topics: ["deep-learning", "python", "neural-networks"],
        gpuRequired: true,
        thumbnail: "🔥",
        learningObjectives: ["TensorFlow basics", "Keras API", "Model deployment", "TensorFlow Serving"]
    },
    {
        id: 7,
        title: "Reinforcement Learning",
        description: "Learn how to build intelligent agents that learn through interaction with environments.",
        difficulty: "advanced",
        duration: 15,
        prerequisites: [1, 2, 5],
        topics: ["reinforcement-learning", "python", "deep-learning"],
        gpuRequired: true,
        thumbnail: "🎮",
        learningObjectives: ["Q-Learning", "Deep Q-Networks", "Policy gradients", "Actor-Critic methods"]
    },
    {
        id: 8,
        title: "Data Preprocessing & Feature Engineering",
        description: "Master the art of preparing data for machine learning models.",
        difficulty: "beginner",
        duration: 5,
        prerequisites: [1],
        topics: ["data-science", "python", "feature-engineering"],
        gpuRequired: false,
        thumbnail: "🔧",
        learningObjectives: ["Data cleaning", "Feature scaling", "Feature selection", "Handling missing data"]
    },
    {
        id: 9,
        title: "Transformers and LLMs",
        description: "Dive deep into transformer architecture and large language models.",
        difficulty: "advanced",
        duration: 20,
        prerequisites: [1, 2, 4],
        topics: ["nlp", "deep-learning", "transformers"],
        gpuRequired: true,
        thumbnail: "🤖",
        learningObjectives: ["Attention mechanism", "BERT", "GPT architecture", "Fine-tuning LLMs"]
    },
    {
        id: 10,
        title: "MLOps and Model Deployment",
        description: "Learn to deploy, monitor, and maintain ML models in production environments.",
        difficulty: "intermediate",
        duration: 8,
        prerequisites: [1, 2],
        topics: ["mlops", "deployment", "python"],
        gpuRequired: false,
        thumbnail: "🚀",
        learningObjectives: ["Model versioning", "CI/CD for ML", "Model monitoring", "A/B testing"]
    }
];

// Sample Learning Paths
const learningPaths = [
    {
        id: 1,
        name: "AI Engineer Track",
        description: "Become a professional AI engineer with comprehensive training",
        courseSequence: [1, 5, 2, 6, 10],
        totalDuration: 33,
        careerOutcome: "AI/ML Engineer",
        icon: "🎯"
    },
    {
        id: 2,
        name: "Computer Vision Specialist",
        description: "Master computer vision from basics to advanced applications",
        courseSequence: [1, 2, 3],
        totalDuration: 24,
        careerOutcome: "Computer Vision Engineer",
        icon: "📸"
    },
    {
        id: 3,
        name: "NLP Expert Path",
        description: "Specialize in natural language processing and language models",
        courseSequence: [1, 2, 4, 9],
        totalDuration: 42,
        careerOutcome: "NLP Engineer",
        icon: "📝"
    },
    {
        id: 4,
        name: "Data Scientist Journey",
        description: "Complete path to becoming a data scientist",
        courseSequence: [1, 5, 8, 2, 6],
        totalDuration: 33,
        careerOutcome: "Data Scientist",
        icon: "📈"
    }
];

// Application State
let filteredCourses = [...coursesData];
let currentView = 'grid';
let activeFilters = {
    difficulty: 'all',
    duration: [],
    topics: [],
    gpuRequired: null,
    search: ''
};

// DOM Elements
const coursesGrid = document.getElementById('coursesGrid');
const pathsGrid = document.getElementById('pathsGrid');
const searchInput = document.getElementById('searchInput');
const filterToggle = document.getElementById('filterToggle');
const filterSidebar = document.getElementById('filterSidebar');
const clearFiltersBtn = document.getElementById('clearFilters');
const courseModal = document.getElementById('courseModal');
const modalClose = document.getElementById('modalClose');
const modalBody = document.getElementById('modalBody');

// Initialize Application
function init() {
    renderLearningPaths();
    renderCourses();
    setupEventListeners();
}

// Render Learning Paths
function renderLearningPaths() {
    pathsGrid.innerHTML = learningPaths.map(path => `
        <div class="path-card" data-path-id="${path.id}">
            <div class="path-header">
                <div class="path-icon">${path.icon}</div>
                <div class="path-info">
                    <h3>${path.name}</h3>
                    <p>${path.description}</p>
                </div>
            </div>
            <div class="path-stats">
                <div class="stat">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M8 2V8L11 11" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    <span>${path.totalDuration} hours</span>
                </div>
                <div class="stat">
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M2 4H14M4 8H12M6 12H10" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    <span>${path.courseSequence.length} courses</span>
                </div>
            </div>
        </div>
    `).join('');
}

// Render Courses
function renderCourses() {
    const coursesHTML = filteredCourses.map(course => `
        <div class="course-card" data-course-id="${course.id}">
            <div class="course-thumbnail">
                ${course.thumbnail}
                <span class="difficulty-badge ${course.difficulty}">${course.difficulty}</span>
            </div>
            <div class="course-content-card">
                <h3 class="course-title">${course.title}</h3>
                <p class="course-description">${course.description}</p>
                ${course.prerequisites.length > 0 ? `
                    <div class="prerequisites-indicator">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M8 2L14 8L8 14L2 8L8 2Z" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        <span>Prerequisites required</span>
                    </div>
                ` : ''}
                <div class="course-meta">
                    <div class="meta-item">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
                            <path d="M8 4V8L10 10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        </svg>
                        <span>${course.duration} hours</span>
                    </div>
                    ${course.gpuRequired ? `
                        <div class="gpu-badge">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <rect x="2" y="4" width="12" height="8" stroke="currentColor" stroke-width="1.5"/>
                                <path d="M5 7H11M5 9H11" stroke="currentColor" stroke-width="1.5"/>
                            </svg>
                            <span>GPU Required</span>
                        </div>
                    ` : ''}
                </div>
                <button class="start-course-btn">Start Course</button>
            </div>
        </div>
    `).join('');
    
    coursesGrid.innerHTML = coursesHTML;
}

// Filter Courses
function filterCourses() {
    filteredCourses = coursesData.filter(course => {
        // Difficulty filter
        if (activeFilters.difficulty !== 'all' && course.difficulty !== activeFilters.difficulty) {
            return false;
        }
        
        // Duration filter
        if (activeFilters.duration.length > 0) {
            const duration = course.duration;
            const durationMatch = activeFilters.duration.some(filter => {
                if (filter === 'short') return duration < 4;
                if (filter === 'medium') return duration >= 4 && duration <= 8;
                if (filter === 'long') return duration > 8;
                return false;
            });
            if (!durationMatch) return false;
        }
        
        // Topics filter
        if (activeFilters.topics.length > 0) {
            const hasMatchingTopic = activeFilters.topics.some(topic => 
                course.topics.includes(topic)
            );
            if (!hasMatchingTopic) return false;
        }
        
        // GPU filter
        if (activeFilters.gpuRequired !== null && course.gpuRequired !== activeFilters.gpuRequired) {
            return false;
        }
        
        // Search filter
        if (activeFilters.search) {
            const searchLower = activeFilters.search.toLowerCase();
            const matchesSearch = 
                course.title.toLowerCase().includes(searchLower) ||
                course.description.toLowerCase().includes(searchLower) ||
                course.topics.some(topic => topic.toLowerCase().includes(searchLower));
            if (!matchesSearch) return false;
        }
        
        return true;
    });
    
    renderCourses();
}

// Setup Event Listeners
function setupEventListeners() {
    // Search functionality
    searchInput.addEventListener('input', (e) => {
        activeFilters.search = e.target.value;
        filterCourses();
    });
    
    // Filter toggle for mobile
    filterToggle.addEventListener('click', () => {
        filterSidebar.classList.toggle('active');
    });
    
    // Difficulty filter
    document.querySelectorAll('input[name="difficulty"]').forEach(input => {
        input.addEventListener('change', (e) => {
            activeFilters.difficulty = e.target.value;
            filterCourses();
        });
    });
    
    // Duration filter
    document.querySelectorAll('.duration-filter').forEach(input => {
        input.addEventListener('change', (e) => {
            if (e.target.checked) {
                activeFilters.duration.push(e.target.value);
            } else {
                activeFilters.duration = activeFilters.duration.filter(d => d !== e.target.value);
            }
            filterCourses();
        });
    });
    
    // Topics filter
    document.querySelectorAll('.topic-filter').forEach(input => {
        input.addEventListener('change', (e) => {
            if (e.target.checked) {
                activeFilters.topics.push(e.target.value);
            } else {
                activeFilters.topics = activeFilters.topics.filter(t => t !== e.target.value);
            }
            filterCourses();
        });
    });
    
    // GPU filter
    document.getElementById('gpuFilter').addEventListener('change', (e) => {
        activeFilters.gpuRequired = e.target.checked ? true : null;
        filterCourses();
    });
    
    // Clear filters
    clearFiltersBtn.addEventListener('click', () => {
        activeFilters = {
            difficulty: 'all',
            duration: [],
            topics: [],
            gpuRequired: null,
            search: ''
        };
        
        // Reset form elements
        document.querySelector('input[name="difficulty"][value="all"]').checked = true;
        document.querySelectorAll('.duration-filter').forEach(input => input.checked = false);
        document.querySelectorAll('.topic-filter').forEach(input => input.checked = false);
        document.getElementById('gpuFilter').checked = false;
        searchInput.value = '';
        
        filterCourses();
    });
    
    // View toggle
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentView = btn.dataset.view;
            coursesGrid.className = currentView === 'list' ? 'courses-grid list-view' : 'courses-grid';
        });
    });
    
    // Goal buttons
    document.querySelectorAll('.goal-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const goal = btn.dataset.goal;
            const path = learningPaths.find(p => 
                p.careerOutcome.toLowerCase().includes(goal.replace('-', ' '))
            );
            if (path) {
                showPathDetails(path);
            }
        });
    });
    
    // Course card clicks
    coursesGrid.addEventListener('click', (e) => {
        const card = e.target.closest('.course-card');
        if (card) {
            const courseId = parseInt(card.dataset.courseId);
            const course = coursesData.find(c => c.id === courseId);
            if (course) {
                showCourseDetails(course);
            }
        }
    });
    
    // Path card clicks
    pathsGrid.addEventListener('click', (e) => {
        const card = e.target.closest('.path-card');
        if (card) {
            const pathId = parseInt(card.dataset.pathId);
            const path = learningPaths.find(p => p.id === pathId);
            if (path) {
                showPathDetails(path);
            }
        }
    });
    
    // Modal close
    modalClose.addEventListener('click', closeModal);
    courseModal.addEventListener('click', (e) => {
        if (e.target === courseModal) {
            closeModal();
        }
    });
}

// Show Course Details
function showCourseDetails(course) {
    const prerequisites = course.prerequisites.map(id => 
        coursesData.find(c => c.id === id)?.title || 'Unknown'
    );
    
    modalBody.innerHTML = `
        <div class="course-detail">
            <div class="detail-header">
                <div class="detail-thumbnail">${course.thumbnail}</div>
                <div class="detail-info">
                    <h2>${course.title}</h2>
                    <div class="detail-badges">
                        <span class="difficulty-badge ${course.difficulty}">${course.difficulty}</span>
                        <span class="duration-badge">${course.duration} hours</span>
                        ${course.gpuRequired ? '<span class="gpu-required">GPU Required</span>' : ''}
                    </div>
                </div>
            </div>
            
            <div class="detail-section">
                <h3>Description</h3>
                <p>${course.description}</p>
            </div>
            
            <div class="detail-section">
                <h3>Learning Objectives</h3>
                <ul>
                    ${course.learningObjectives.map(obj => `<li>${obj}</li>`).join('')}
                </ul>
            </div>
            
            ${prerequisites.length > 0 ? `
                <div class="detail-section">
                    <h3>Prerequisites</h3>
                    <ul>
                        ${prerequisites.map(prereq => `<li>${prereq}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
            
            <div class="detail-section">
                <h3>Topics Covered</h3>
                <div class="topic-tags">
                    ${course.topics.map(topic => `
                        <span class="topic-tag">${topic}</span>
                    `).join('')}
                </div>
            </div>
            
            <div class="detail-actions">
                <button class="btn-primary">Start Learning</button>
                <button class="btn-secondary">Add to Path</button>
            </div>
        </div>
    `;
    
    courseModal.classList.add('active');
}

// Show Path Details
function showPathDetails(path) {
    const pathCourses = path.courseSequence.map(id => 
        coursesData.find(c => c.id === id)
    ).filter(Boolean);
    
    modalBody.innerHTML = `
        <div class="path-detail">
            <div class="detail-header">
                <div class="path-icon-large">${path.icon}</div>
                <div class="detail-info">
                    <h2>${path.name}</h2>
                    <p>${path.description}</p>
                    <div class="path-meta">
                        <span>${path.totalDuration} total hours</span>
                        <span>${pathCourses.length} courses</span>
                        <span>Career: ${path.careerOutcome}</span>
                    </div>
                </div>
            </div>
            
            <div class="detail-section">
                <h3>Course Sequence</h3>
                <div class="course-sequence">
                    ${pathCourses.map((course, index) => `
                        <div class="sequence-item">
                            <div class="sequence-number">${index + 1}</div>
                            <div class="sequence-content">
                                <h4>${course.title}</h4>
                                <p>${course.description}</p>
                                <div class="sequence-meta">
                                    <span class="difficulty-badge ${course.difficulty}">${course.difficulty}</span>
                                    <span>${course.duration} hours</span>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div class="detail-actions">
                <button class="btn-primary">Start This Path</button>
                <button class="btn-secondary">Download Syllabus</button>
            </div>
        </div>
    `;
    
    courseModal.classList.add('active');
}

// Close Modal
function closeModal() {
    courseModal.classList.remove('active');
    modalBody.innerHTML = '';
}

// Add modal-specific styles
const modalStyles = document.createElement('style');
modalStyles.textContent = `
    .course-detail,
    .path-detail {
        max-width: 100%;
    }
    
    .detail-header {
        display: flex;
        gap: var(--spacing-xl);
        margin-bottom: var(--spacing-xl);
        padding-bottom: var(--spacing-xl);
        border-bottom: 2px solid var(--gray-200);
    }
    
    .detail-thumbnail,
    .path-icon-large {
        width: 120px;
        height: 120px;
        background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4rem;
    }
    
    .detail-info h2 {
        margin-bottom: var(--spacing-md);
        color: var(--gray-900);
    }
    
    .detail-badges,
    .path-meta {
        display: flex;
        gap: var(--spacing-md);
        flex-wrap: wrap;
    }
    
    .duration-badge,
    .gpu-required {
        padding: var(--spacing-xs) var(--spacing-sm);
        background: var(--gray-100);
        border-radius: var(--radius-sm);
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .gpu-required {
        background: rgba(239, 68, 68, 0.1);
        color: var(--danger-color);
    }
    
    .detail-section {
        margin-bottom: var(--spacing-xl);
    }
    
    .detail-section h3 {
        margin-bottom: var(--spacing-md);
        color: var(--gray-900);
    }
    
    .detail-section ul {
        list-style: none;
        padding: 0;
    }
    
    .detail-section li {
        padding: var(--spacing-sm) 0;
        padding-left: var(--spacing-lg);
        position: relative;
    }
    
    .detail-section li::before {
        content: '✓';
        position: absolute;
        left: 0;
        color: var(--secondary-color);
        font-weight: bold;
    }
    
    .topic-tags {
        display: flex;
        gap: var(--spacing-sm);
        flex-wrap: wrap;
    }
    
    .topic-tag {
        padding: var(--spacing-xs) var(--spacing-md);
        background: var(--gray-100);
        border-radius: var(--radius-md);
        font-size: 0.875rem;
        color: var(--gray-700);
    }
    
    .course-sequence {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-lg);
    }
    
    .sequence-item {
        display: flex;
        gap: var(--spacing-md);
        padding: var(--spacing-lg);
        background: var(--gray-50);
        border-radius: var(--radius-md);
        border: 2px solid var(--gray-200);
    }
    
    .sequence-number {
        width: 40px;
        height: 40px;
        background: var(--primary-color);
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        flex-shrink: 0;
    }
    
    .sequence-content {
        flex: 1;
    }
    
    .sequence-content h4 {
        margin-bottom: var(--spacing-sm);
        color: var(--gray-900);
    }
    
    .sequence-content p {
        color: var(--gray-600);
        font-size: 0.875rem;
        margin-bottom: var(--spacing-sm);
    }
    
    .sequence-meta {
        display: flex;
        gap: var(--spacing-md);
    }
    
    .detail-actions {
        display: flex;
        gap: var(--spacing-md);
        margin-top: var(--spacing-xl);
        padding-top: var(--spacing-xl);
        border-top: 2px solid var(--gray-200);
    }
    
    .btn-primary,
    .btn-secondary {
        padding: var(--spacing-md) var(--spacing-xl);
        border-radius: var(--radius-md);
        font-size: 1rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
    }
    
    .btn-primary {
        background: var(--primary-color);
        color: white;
    }
    
    .btn-primary:hover {
        background: var(--primary-dark);
    }
    
    .btn-secondary {
        background: white;
        color: var(--primary-color);
        border: 2px solid var(--primary-color);
    }
    
    .btn-secondary:hover {
        background: var(--gray-50);
    }
    
    @media (max-width: 768px) {
        .detail-header {
            flex-direction: column;
            text-align: center;
        }
        
        .detail-thumbnail,
        .path-icon-large {
            margin: 0 auto;
        }
        
        .detail-actions {
            flex-direction: column;
        }
        
        .btn-primary,
        .btn-secondary {
            width: 100%;
        }
    }
`;

document.head.appendChild(modalStyles);

// Initialize the application
document.addEventListener('DOMContentLoaded', init);