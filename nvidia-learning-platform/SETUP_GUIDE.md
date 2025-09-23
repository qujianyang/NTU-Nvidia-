# Complete Setup & Usage Guide

## Prerequisites Installation

### 1. Install Node.js (v18 or higher)
- Download from: https://nodejs.org/
- Verify installation: `node --version`

### 2. Install PostgreSQL
- Download from: https://www.postgresql.org/download/windows/
- During installation, remember your password for the 'postgres' user
- Default port: 5432

### 3. Get OpenAI API Key
- Sign up at: https://platform.openai.com/
- Create an API key: https://platform.openai.com/api-keys
- Keep this key safe, you'll need it later

## System Setup

### Step 1: Navigate to the project
```bash
cd C:\Users\user\Documents\GitHub\NTU-Nvidia-\nvidia-learning-platform
```

### Step 2: Install dependencies
```bash
npm install
```

### Step 3: Setup PostgreSQL Database

1. Open pgAdmin or psql terminal
2. Create a new database:
```sql
CREATE DATABASE nvidia_learning;
```

### Step 4: Configure Environment Variables

Create these .env files:

**File 1: `apps/backend/.env`**
```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/nvidia_learning"
PORT=3001
```

**File 2: `apps/ai-assistant/.env.local`**
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
NEXT_PUBLIC_API_URL=http://localhost:3001
```

**File 3: `apps/pathway-visualizer/.env`**
```env
VITE_API_URL=http://localhost:3001
```

### Step 5: Initialize Database
```bash
cd apps/backend
npx prisma generate
npx prisma migrate dev --name init
npm run seed
cd ../..
```

### Step 6: Start All Services
```bash
npm run dev
```

This will start:
- 🎨 **Pathway Visualizer**: http://localhost:5173
- 🤖 **AI Assistant**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:3001

## How to Use the System

### 📊 Using the Visual Pathway Map (http://localhost:5173)

1. **Select Your Role**
   - Click "Developer" or "Administrator" to see relevant courses
   - The visualization will update to show only courses for your role

2. **Explore the Course Network**
   - 🟢 Green nodes = Beginner courses
   - 🔵 Blue nodes = Intermediate courses
   - 🟣 Purple nodes = Advanced courses
   - ➡️ Arrows show prerequisites

3. **Interact with Courses**
   - **Click** any course node to see details
   - **Scroll** to zoom in/out
   - **Drag** to pan around the visualization

4. **Filter by Skills**
   - Use the skill filter sidebar to highlight courses matching specific skills
   - Examples: "CUDA", "Deep Learning", "LLMs"

5. **Track Your Progress**
   - Click "Enroll" on a course to start tracking
   - Progress rings appear around enrolled courses
   - Mark courses as completed to see your learning journey

### 🤖 Using the AI Assistant (http://localhost:3000)

1. **Start Chatting**
   - The assistant will greet you automatically
   - Type your questions in natural language

2. **Example Questions to Ask:**
   - "I want to become an AI engineer, where should I start?"
   - "What's the best path for learning LLMs?"
   - "I have $500 budget and 20 hours per month"
   - "Show me beginner-friendly courses"
   - "What prerequisites do I need for RAG development?"

3. **Set Your Context (Right Panel)**
   - **Role**: Developer or Administrator
   - **Goals**: What you want to achieve
   - **Time**: How many hours you can dedicate
   - **Budget**: Your spending limit
   - **Skills**: Your current knowledge

4. **Use Quick Prompts**
   - Click any quick prompt button to auto-fill common questions

5. **Follow Recommendations**
   - The AI will suggest 2-3 learning paths
   - Each recommendation includes:
     - Course sequence
     - Time estimates
     - Total cost
     - Skill progression

## 🎯 Common Use Cases

### Use Case 1: Complete Beginner
1. Open AI Assistant
2. Type: "I'm completely new to AI, where should I start?"
3. Set context: Role = Developer, Time = 10 hours/week
4. Follow the recommended "AI Developer Foundation Path"

### Use Case 2: Skill-Specific Learning
1. Open Pathway Visualizer
2. Select Role: Developer
3. Filter by skill: "Generative AI"
4. Click on highlighted courses to explore the LLM pathway

### Use Case 3: Budget-Conscious Learning
1. Open AI Assistant
2. Set context: Budget = $200
3. Ask: "What can I learn with a $200 budget?"
4. Get recommendations for self-paced courses within budget

### Use Case 4: Career Transition
1. Open AI Assistant
2. Type: "I'm a software developer wanting to move into AI"
3. Set your current skills: Python, JavaScript
4. Get a customized transition path

## 🔧 Troubleshooting

### If npm install fails:
```bash
# Clear npm cache
npm cache clean --force
# Try again
npm install
```

### If database connection fails:
1. Check PostgreSQL is running
2. Verify password in .env file
3. Ensure database exists: `psql -U postgres -c "\l"`

### If OpenAI API fails:
1. Verify API key is correct
2. Check you have credits in OpenAI account
3. Try a simple test: `curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_KEY"`

### If ports are already in use:
```bash
# Find process using port (Windows)
netstat -ano | findstr :3000
# Kill process
taskkill /PID <process_id> /F
```

## 📝 Quick Commands Reference

```bash
# Start everything
npm run dev

# Start individual apps
cd apps/pathway-visualizer && npm run dev
cd apps/ai-assistant && npm run dev
cd apps/backend && npm run dev

# Database commands
cd apps/backend
npx prisma studio  # Visual database browser
npx prisma migrate reset  # Reset database

# Build for production
npm run build

# Clean everything
npm run clean
```

## 💡 Pro Tips

1. **Start with the AI Assistant** to get personalized recommendations
2. **Use the Visual Map** to explore prerequisites and plan your path
3. **Set realistic time goals** - most courses are 8 hours
4. **Focus on one path** - complete it before starting another
5. **Check prerequisites** - some advanced courses need foundations

## Need Help?

- Check the console for error messages (F12 in browser)
- Ensure all three services are running (check terminal tabs)
- Verify all .env files are created correctly
- Try restarting the services with `Ctrl+C` then `npm run dev`