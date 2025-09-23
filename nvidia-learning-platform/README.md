# NVIDIA Learning Platform

A comprehensive interactive learning platform that transforms NVIDIA's training PDF into two powerful tools:

## 🚀 Features

### 1. Interactive Visual Pathway Map
- **D3.js-powered visualization** showing course relationships and prerequisites
- **Role-based filtering** for Developers and Administrators
- **Skill-based course discovery** with smart filtering
- **Progress tracking** with visual indicators
- **Difficulty color coding** (Beginner: Green, Intermediate: Blue, Advanced: Purple)
- **Interactive zoom and pan** for exploring complex pathways

### 2. AI-Powered Conversational Assistant
- **LangChain integration** for intelligent course recommendations
- **Personalized learning paths** based on goals, skills, and constraints
- **Multi-path suggestions** (fastest, comprehensive, budget-friendly)
- **Context-aware responses** considering time and budget limitations
- **Skill gap analysis** to identify learning priorities

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **D3.js** for interactive visualizations
- **Next.js 14** for the AI assistant
- **TailwindCSS** for styling
- **Zustand** for state management
- **React Query** for data fetching

### Backend
- **Fastify** for high-performance API
- **Prisma** ORM with PostgreSQL
- **LangChain** with OpenAI GPT-4
- **Zod** for validation

## 📦 Project Structure

```
nvidia-learning-platform/
├── apps/
│   ├── pathway-visualizer/    # Interactive visual map
│   ├── ai-assistant/          # Conversational AI interface
│   └── backend/               # API and database
├── packages/
│   └── shared/               # Shared types and data
└── turbo.json               # Turborepo configuration
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- PostgreSQL 14+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nvidia-learning-platform.git
cd nvidia-learning-platform
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:

Create `.env` files in each app directory:

**apps/backend/.env:**
```env
DATABASE_URL="postgresql://user:password@localhost:5432/nvidia_learning"
```

**apps/ai-assistant/.env.local:**
```env
OPENAI_API_KEY=your_openai_api_key
NEXT_PUBLIC_API_URL=http://localhost:3001
```

4. Set up the database:
```bash
cd apps/backend
npx prisma migrate dev
npx prisma db seed
```

5. Start all services:
```bash
npm run dev
```

The applications will be available at:
- Pathway Visualizer: http://localhost:3000
- AI Assistant: http://localhost:3002
- Backend API: http://localhost:3001

## 🎯 Key Features Breakdown

### Visual Pathway Map
- **Entry Points**: Choose Developer or Administrator role
- **Smart Filtering**: Filter by skills like "LLMs", "Computer Vision", "Infrastructure"
- **Progress Tracking**: Mark courses as completed and track overall progress
- **Course Details**: Click any course for detailed information including:
  - Duration and pricing
  - Prerequisites and next courses
  - Skills covered
  - Certification availability

### AI Assistant
- **Natural Language**: Ask questions in plain English
- **Contextual Understanding**: Considers your role, skills, budget, and time
- **Path Recommendations**: Get multiple learning path options
- **Course Scheduling**: Export learning plans to calendar
- **Progress Integration**: Syncs with visual map progress

## 📊 Data Model

The platform uses a comprehensive data model including:
- **Courses**: 50+ NVIDIA courses with metadata
- **Learning Paths**: Pre-defined and custom paths
- **User Profiles**: Role, skills, goals, constraints
- **Progress Tracking**: Course completion and notes
- **Conversations**: AI chat history and recommendations

## 🔄 Development Workflow

This project uses Turborepo for monorepo management:

```bash
# Run all apps in development
npm run dev

# Build all apps
npm run build

# Run tests
npm run test

# Lint code
npm run lint
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- NVIDIA for the comprehensive learning resources
- The open-source community for the amazing tools and libraries

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

Built with passion for making AI education accessible and engaging!