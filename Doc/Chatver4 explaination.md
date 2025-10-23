 🔍 STEP 1: User Opens Browser → http://localhost:5173     

  1A. Vite Serves the React App

  📄 web_app/frontend/vite.config.js:5-16 — This
  configures Vite to serve your app:
  export default defineConfig({
    plugins: [react()],        // ← Enables JSX
  transformation
    server: {                  // ← Development server      
  config
      proxy: {                 // ← THIS IS THE PROXY!      
  🎯
        '/api': {              // ← Any request starting    
   with /api...
          target: 'http://localhost:5000',  // ← ...gets    
   forwarded to Flask!
          changeOrigin: true,
          secure: false,
        }
      }
    }
  })

  What happens:
  - Vite starts a server on port 5173
  - Serves your index.html (empty shell)
  - Bundles all your JavaScript files into one

  ---
  1B. Browser Downloads JavaScript Bundle

  📄 web_app/frontend/index.html (Vite auto-generates       
  this):
  <div id="root"></div>           <!-- Empty container      
  -->
  <script type="module" src="/src/main.jsx"></script>       
  <!-- Loads React -->

  ---
  1C. React Renders the UI

  📄 web_app/frontend/src/main.jsx:6-9 — Entry point,       
  runs in the browser:
  createRoot(document.getElementById('root')).render(       
    <StrictMode>
      <App />   // ← Renders your main App component        
    </StrictMode>,
  )

  📄 web_app/frontend/src/App.jsx:19-21 — App loads
  immediately:
  useEffect(() => {
    fetchCourses();    // ← Triggers API call when
  component mounts!
  }, []);

  📄 web_app/frontend/src/App.jsx:23-33 — Makes first       
  API call:
  const fetchCourses = async () => {
    try {
      const response = await axios.get('/api/courses');     
   // ← LINE 25: API CALL!
      setCourses(response.data);   // ← Updates React       
  state with courses
      setLoading(false);
    } catch (error) {
      console.error('Error fetching courses:', error);      
      message.error('Failed to load courses');
      setLoading(false);
    }
  };

  ---
  🎯 THE PROXY IN ACTION (Step 1C)

  When line 25 executes axios.get('/api/courses'):

  1. Browser makes request to:
  http://localhost:5173/api/courses
  2. Vite proxy intercepts
  (web_app/frontend/vite.config.js:8-14):
    - Sees the request starts with /api
    - Checks proxy config: '/api': { target:
  'http://localhost:5000' }
    - Forwards request to:
  http://localhost:5000/api/courses
  3. Flask receives the request (web_app/app.py:57-104):    
  @app.route('/api/courses', methods=['GET'])  # ← LINE     
  57: Flask endpoint
  def get_courses():
      """Optional: Get list of all courses for
  display"""
      try:
          conn = sqlite3.connect(db_path)   # ← LINE 64:    
   Query database
          # ... database queries ...
          return jsonify(courses)           # ← LINE        
  101: Return JSON

  4. Flask returns JSON → Vite forwards to browser →        
  React updates UI

  ---
  ★ Insight ─────────────────────────────────────
  The proxy acts as a "middleman" in
  web_app/frontend/vite.config.js:8-14:

  Without proxy, you'd need:
  axios.get('http://localhost:5000/api/courses')  // ❌     
  CORS errors!

  With proxy, you write:
  axios.get('/api/courses')  // ✅ Vite handles the
  routing!

  The proxy also solves CORS (Cross-Origin Resource         
  Sharing) issues. Browsers block requests between
  different ports (5173 → 5000) for security. The proxy     
  makes the browser think everything comes from port        
  5173!
  ─────────────────────────────────────────────────

  ---
  🔍 STEP 2: User Asks a Question in Chat

  2A. React Captures Input

  📄 
  web_app/frontend/src/components/ChatWidget.jsx:230-243    
   — User types in textarea:
  <TextArea
    value={inputValue}              // ← LINE 231:
  Controlled input
    onChange={(e) => setInputValue(e.target.value)}  //     
  ← LINE 232: Updates state
    onPressEnter={(e) => {          // ← LINE 233: Enter    
   key triggers send
      if (!e.shiftKey) {
        e.preventDefault();
        handleSend();                // ← LINE 236:
  Calls the send function
      }
    }}
    placeholder="Ask about courses..."
    // ...
  />

  ---
  2B. Makes axios Call to /api/chat

  📄 
  web_app/frontend/src/components/ChatWidget.jsx:74-117     
  — The send handler:
  const handleSend = async () => {
    if (!inputValue.trim()) return;  // ← LINE 75:
  Validation

    // LINE 77-82: Create user message object
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);  // ←      
  LINE 84: Add to chat UI
    setInputValue('');   // ← LINE 85: Clear input
    setLoading(true);    // ← LINE 86: Show loading
  spinner

    try {
      // 🎯 LINE 89-91: THE API CALL!
      const response = await axios.post('/api/chat', {      
        question: inputValue
      });

      // LINE 93-98: Create bot response message
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.data.answer,  // ← LINE 96:       
  Extract answer from JSON
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);  // ←     
  LINE 100: Add to UI
    } catch (error) {
      console.error('Chat error:', error);
      // ... error handling ...
    } finally {
      setLoading(false);  // ← LINE 115: Hide spinner       
    }
  };

  ---
  2C. Vite Proxies Request to Flask

  Same proxy as before!
  web_app/frontend/vite.config.js:8-14

  When line 89 executes axios.post('/api/chat', ...):       

  1. Browser sends to: http://localhost:5173/api/chat       
  2. Vite proxy sees /api prefix
  3. Forwards to: http://localhost:5000/api/chat

  ---
  2D. Flask Calls RAG System

  📄 web_app/app.py:38-55 — Flask endpoint receives the     
  chat request:
  @app.route('/api/chat', methods=['POST'])  # ← LINE       
  38: Defines endpoint
  def chat():
      """Handle chat messages and return RAG
  responses"""
      try:
          data = request.get_json()          # ← LINE       
  42: Parse JSON body
          question = data.get('question', '') # ← LINE      
  43: Extract question

          if not question:                   # ← LINE       
  45: Validation
              return jsonify({'error': 'No question
  provided'}), 400

          # 🎯 LINE 49: CALLS YOUR RAG SYSTEM!
          answer =
  get_retriever().answer_question(question)

          return jsonify({'answer': answer}) # ← LINE       
  51: Return JSON response

      except Exception as e:
          print(f"Error in chat: {e}")       # ← LINE       
  54: Error logging
          return jsonify({'error': 'Sorry, I encountered    
   an error...'}), 500

  📄 web_app/app.py:20-26 — The RAG retriever (lazy
  loading):
  def get_retriever():
      """Get or initialize the RAG retriever (lazy
  loading)."""
      global retriever
      if retriever is None:
          print("Initializing RAG retriever on first        
  request...")
          retriever = CourseRAGRetriever(db_path)  # ←      
  Loads AI model
      return retriever

  ---
  2E. Returns JSON Response

  Flask → Vite → React:

  1. Flask returns (app.py:51):
  {"answer": "The prerequisites for Deep Learning
  are..."}
  2. Vite forwards to browser (unchanged)
  3. React updates UI (ChatWidget.jsx:96):
  content: response.data.answer  // ← Extracts "answer"     
  field from JSON

  ---
  2F. React Updates UI Instantly (No Page Reload!)

  📄 web_app/frontend/src/components/ChatWidget.jsx:100:    
  setMessages(prev => [...prev, botMessage]);  // ←
  Updates state

  📄 
  web_app/frontend/src/components/ChatWidget.jsx:206-210    
   — Messages render:
  <AnimatePresence>
    {messages.map(message => (
      <MessageBubble key={message.id} message={message}     
  />  // ← Re-renders with new message
    ))}
  </AnimatePresence>

  No window.location.reload() needed! React
  automatically re-renders when state changes.

  ---
  🔍 STEP 3: User Navigates Between Pages

  📄 web_app/frontend/src/App.jsx:63-70 — Menu
  navigation:
  <Menu
    theme="dark"
    mode="horizontal"
    selectedKeys={[activeView]}         // ← LINE 66:       
  Highlights current page
    items={menuItems}
    onClick={(e) => setActiveView(e.key)}  // ← LINE 68:    
   Changes view state
    style={{ flex: 1, minWidth: 0, justifyContent:
  'center' }}
  />

  📄 web_app/frontend/src/App.jsx:35-46 — Menu items        
  definition:
  const menuItems = [
    {
      key: 'catalog',
      icon: <BookOutlined />,
      label: 'Course Catalog',
    },
    {
      key: 'tree',
      icon: <PartitionOutlined />,
      label: 'Learning Paths',
    },
  ];

  📄 web_app/frontend/src/App.jsx:80-84 — Conditional       
  rendering:
  {loading ? (
    <div className="loading-container">
      <Spin size="large" tip="Loading courses..." />        
    </div>
  ) : (
    <>
      {activeView === 'catalog' && <CourseCatalog
  courses={courses} />}  // ← LINE 81
      {activeView === 'tree' && <LearningPathTree
  courses={courses} />}  // ← LINE 82
    </>
  )}

  What happens when you click "Learning Paths":

  1. Line 68: onClick sets activeView = 'tree'
  2. Line 82: Condition activeView === 'tree' becomes       
  true
  3. React re-renders only the <Content> section
  4. No server request! No Flask involved!
  5. Instant! Just JavaScript swapping components

  ---
  📊 VISUAL SUMMARY: THE COMPLETE FLOW

  ┌─────────────────────────────────────────────────────    
  ────────────┐
  │ BROWSER (http://localhost:5173)
             │
  ├─────────────────────────────────────────────────────    
  ────────────┤
  │
              │
  │  main.jsx:6-9  →  Renders App.jsx
             │
  │
              │
  │  App.jsx:25    →  axios.get('/api/courses')
             │
  │                   ↓
              │
  │  ChatWidget:89 →  axios.post('/api/chat',
  {question})          │
  │                   ↓
              │
  └───────────────────┼─────────────────────────────────    
  ────────────┘
                      │
                      │ Request to /api/*
                      ↓
  ┌─────────────────────────────────────────────────────    
  ────────────┐
  │ VITE PROXY (vite.config.js:8-14)  🎯 THE MIDDLEMAN!     
            │
  ├─────────────────────────────────────────────────────    
  ────────────┤
  │
              │
  │  Intercepts:  /api/courses
              │
  │  Forwards to: http://localhost:5000/api/courses
              │
  │
              │
  │  Intercepts:  /api/chat
              │
  │  Forwards to: http://localhost:5000/api/chat
              │
  │
              │
  └───────────────────┼─────────────────────────────────    
  ────────────┘
                      │
                      │ Forwarded request
                      ↓
  ┌─────────────────────────────────────────────────────    
  ────────────┐
  │ FLASK (http://localhost:5000)
             │
  ├─────────────────────────────────────────────────────    
  ────────────┤
  │
              │
  │  app.py:57  @app.route('/api/courses')
             │
  │             → Query SQLite database
              │
  │             → Return JSON: [{title: "...", ...}]        
              │
  │
              │
  │  app.py:38  @app.route('/api/chat')
             │
  │             → Extract question from request
              │
  │  app.py:49  →
  get_retriever().answer_question(question)        │        
  │             → Return JSON: {answer: "..."}
              │
  │
              │
  └─────────────────────────────────────────────────────    
  ────────────┘

  ---
  ★ Insight ─────────────────────────────────────
  Why This Architecture?

  Separation of Concerns:
  - Vite (Port 5173) handles: UI, animations, routing,      
  user interactions
  - Flask (Port 5000) handles: Database, AI/RAG,
  business logic
  - Proxy connects them seamlessly!

  Benefits:
  1. Independent development: Frontend and backend teams    
   can work separately
  2. Easy scaling: Deploy React to CDN, Flask to
  different servers
  3. Technology flexibility: Could swap React for Vue       
  without touching Flask!
  4. Better performance: Static files (HTML/JS/CSS)
  served by Vite, only API calls hit Flask

  Flask alone would render HTML on every request (slow,     
  no smooth animations).
  React + Flask gives you the best of both worlds!
  ─────────────────────────────────────────────────

  ---
  🔑 KEY TAKEAWAYS

  | Component     | File & Lines         | Role
                    |
  |---------------|----------------------|--------------    
  ------------------|
  | Entry Point   | main.jsx:6-9         | Boots up
  React app             |
  | Main App      | App.jsx:19-33        | Fetches
  courses on load        |
  | Chat UI       | ChatWidget.jsx:89-91 | Sends chat       
  messages            |
  | THE PROXY 🎯  | vite.config.js:8-14  | Forwards         
  /api/ to Flask*       |
  | Flask Courses | app.py:57-104        | Returns
  course list            |
  | Flask Chat    | app.py:38-55         | Calls RAG,       
  returns answer      |
  | Navigation    | App.jsx:68, 81-82    | Client-side      
  routing (instant!) |
