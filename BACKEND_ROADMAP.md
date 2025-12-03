# Backend Development Roadmap
## Making NVIDIA Course Advisor Production-Ready

**Project Status:** MVP → Production-Ready Service
**Last Updated:** 2025-12-02

---

## 🎯 Overview

This roadmap outlines the steps needed to transform the NVIDIA Course Advisor from a prototype into a production-ready service. Tasks are organized by priority and category.

---

## 🚀 Phase 0: Dynamic Learning Path Generator (Current Sprint)

### ⬜ 0. Implement Dynamic Learning Path Generator
**Status:** ⏳ In Progress
**Priority:** Highest
**Effort:** 3-4 days

**Tasks:**
- **Sub-task 1: AI Backend "Brain"**
  - [ ] Create `pdf_ingestion_system/learning_path_generator.py`.
  - [ ] Build in-memory Knowledge Graph from course data using `networkx`.
  - [ ] Implement Hybrid Retrieval logic (Semantic Search + Graph Expansion).
  - [ ] Implement Topological Sort to generate the ordered learning path.
- **Sub-task 2: API Layer**
  - [ ] Create `/api/generate_learning_path` endpoint in `web_app/app.py`.
  - [ ] Integrate the API with the backend "Brain" module.
- **Sub-task 3: Frontend UI**
  - [ ] Create UI elements in `web_app/templates/learning_paths.html`.
  - [ ] Write JavaScript in `web_app/static/learning_paths.js` to call the API.
  - [ ] Dynamically render the generated learning path for the user.

**Files to create/modify:**
- `pdf_ingestion_system/learning_path_generator.py` (NEW)
- `requirements.txt` (add `networkx`)
- `web_app/app.py`
- `web_app/templates/learning_paths.html`
- `web_app/static/learning_paths.js`

**Benefits:**
- Creates a "breakthrough" feature for the NVIDIA demo.
- Moves the system from a reactive Q&A bot to a proactive, intelligent "advisor".
- Demonstrates advanced capabilities (Graph-RAG, multi-hop reasoning, explainability).

---

## ✅ Phase 1: Critical Infrastructure (3/3 Complete)

### ✓ 1. Environment Configuration
**Status:** ✅ Complete
**Priority:** Critical
**Effort:** 2 hours

**What was done:**
- [x] Created centralized config module (`web_app/config.py`)
- [x] Added `.env` file for environment variables
- [x] Added `.env.example` template for documentation
- [x] Updated all modules to use config instead of hardcoded values
- [x] Added configuration validation on startup

**Files modified:**
- `web_app/config.py` (NEW)
- `.env` (NEW)
- `.env.example` (NEW)
- `web_app/app.py`
- `web_app/auth.py`
- `pdf_ingestion_system/rag_retriever.py`

**Benefits:**
- Secure secret management
- Easy environment switching (dev/staging/prod)
- No hardcoded credentials in code

---

### ✓ 2. Rate Limiting on API Endpoints
**Status:** ✅ Complete
**Priority:** Critical
**Effort:** 2 hours

**What was done:**
- [x] Added Flask-Limiter dependency
- [x] Configured rate limits for critical endpoints
- [x] Added custom 429 error handler
- [x] Made limits configurable via environment

**Rate limits applied:**
- `/api/login`: 5 requests/minute (prevent brute force)
- `/api/register`: 3 requests/minute (prevent spam)
- `/api/chat`: 20 requests/minute (prevent API abuse)
- Global default: 100 requests/minute

**Files modified:**
- `requirements.txt`
- `web_app/config.py`
- `web_app/app.py`
- `.env`
- `.env.example`

**Benefits:**
- Protection against brute force attacks
- Prevention of API abuse
- Reduced server load from malicious traffic

---

### ✓ 3. Production Server (Gunicorn)
**Status:** ✅ Complete
**Priority:** Critical
**Effort:** 3 hours

**What was done:**
- [x] Added Gunicorn and gevent dependencies
- [x] Created WSGI entry point (`web_app/wsgi.py`)
- [x] Created Gunicorn configuration file
- [x] Created startup scripts (Linux + Windows)
- [x] Configured worker processes and timeouts

**Configuration:**
- Workers: 4 (configurable based on CPU cores)
- Worker class: gevent (I/O-bound, optimized for LLM)
- Timeout: 180s (matches LLM requirements)
- Graceful restarts: Enabled
- Max requests per worker: 1000 (prevents memory leaks)

**Files created:**
- `web_app/wsgi.py`
- `gunicorn.conf.py`
- `start_server.sh`
- `start_server.bat`

**Benefits:**
- Multi-process concurrency (handle multiple users)
- Graceful worker restarts
- Production-grade stability
- Better performance under load

---

## 🔒 Phase 2: Security Hardening (0/2 Complete)

### ⬜ 4. Password Complexity Requirements
**Status:** ⏳ Pending
**Priority:** High
**Effort:** 1-2 hours

**Tasks:**
- [ ] Add password validation function in `auth.py`
- [ ] Require minimum 8 characters (already implemented)
- [ ] Require at least 1 uppercase letter
- [ ] Require at least 1 lowercase letter
- [ ] Require at least 1 number
- [ ] Require at least 1 special character
- [ ] Add password strength indicator on frontend
- [ ] Return clear error messages for invalid passwords

**Files to modify:**
- `web_app/auth.py` (add validation function)
- `web_app/app.py` (use validation in register endpoint)
- `web_app/config.py` (add password requirements config)
- `web_app/templates/signup.html` (add frontend validation)

**Configuration to add:**
```bash
PASSWORD_MIN_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=True
PASSWORD_REQUIRE_LOWERCASE=True
PASSWORD_REQUIRE_DIGITS=True
PASSWORD_REQUIRE_SPECIAL=True
```

**Benefits:**
- Stronger account security
- Reduced risk of account compromise
- Compliance with security best practices

---

### ⬜ 5. Account Lockout After Failed Logins
**Status:** ⏳ Pending
**Priority:** High
**Effort:** 3-4 hours

**Tasks:**
- [ ] Create `login_attempts` table in database
- [ ] Track failed login attempts by email/IP
- [ ] Lock account after 5 failed attempts (configurable)
- [ ] Add 15-minute lockout period (configurable)
- [ ] Add unlock mechanism (time-based or admin)
- [ ] Send email notification on account lockout
- [ ] Add "Forgot Password" flow
- [ ] Add captcha after 3 failed attempts (optional)

**Database schema:**
```sql
CREATE TABLE login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    ip_address TEXT,
    attempt_time TIMESTAMP NOT NULL,
    successful BOOLEAN DEFAULT 0,
    locked_until TIMESTAMP
);
CREATE INDEX idx_login_email ON login_attempts(email);
CREATE INDEX idx_login_time ON login_attempts(attempt_time);
```

**Files to modify:**
- `pdf_ingestion_system/course_database.py` (add table)
- `web_app/auth.py` (add lockout logic)
- `web_app/app.py` (check lockout before login)

**Benefits:**
- Protection against brute force attacks
- Reduced unauthorized access attempts
- User notification of suspicious activity

---

## 💾 Phase 3: Database Upgrade (0/1 Complete)

### ⬜ 6. Migrate SQLite to PostgreSQL
**Status:** ⏳ Pending
**Priority:** High (for production)
**Effort:** 6-8 hours

**Tasks:**
- [ ] Install PostgreSQL and psycopg2 driver
- [ ] Create database migration scripts
- [ ] Update database connection logic
- [ ] Add connection pooling (SQLAlchemy or psycopg2.pool)
- [ ] Migrate existing data from SQLite
- [ ] Update all SQL queries (PostgreSQL syntax)
- [ ] Add database backup strategy
- [ ] Create database migration system (Alembic)
- [ ] Test all CRUD operations
- [ ] Update documentation

**Why migrate:**
- SQLite uses file-based locking (single writer)
- PostgreSQL supports concurrent connections
- Better performance under load
- ACID compliance
- Better JSON support
- Row-level locking

**Files to modify:**
- `requirements.txt` (add `psycopg2-binary`, `SQLAlchemy`)
- `web_app/config.py` (add PostgreSQL connection string)
- `web_app/auth.py` (update connection logic)
- `web_app/app.py` (update connection logic)
- `pdf_ingestion_system/course_database.py` (update queries)

**Configuration to add:**
```bash
DATABASE_TYPE=postgresql  # or sqlite
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=nvidia_courses
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

**Migration strategy:**
1. Set up PostgreSQL locally
2. Create schema in PostgreSQL
3. Export data from SQLite
4. Import data to PostgreSQL
5. Run tests
6. Switch production

**Benefits:**
- Support for concurrent users
- Better performance
- Production-grade reliability
- Better scalability

---

## 🔄 Phase 4: Resilience & Reliability (0/1 Complete)

### ⬜ 7. Retry Logic for Ollama API
**Status:** ⏳ Pending
**Priority:** Medium
**Effort:** 2-3 hours

**Tasks:**
- [ ] Add retry library (`tenacity` or custom)
- [ ] Implement exponential backoff
- [ ] Add retry logic to `_call_ollama()` in `rag_retriever.py`
- [ ] Configure max retries (default: 3)
- [ ] Add circuit breaker pattern (optional)
- [ ] Add fallback message on total failure
- [ ] Log retry attempts
- [ ] Add retry metrics

**Retry strategy:**
```python
# Exponential backoff: 1s, 2s, 4s
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
def _call_ollama(self, prompt: str) -> str:
    # ... existing code
```

**Files to modify:**
- `requirements.txt` (add `tenacity>=8.2.0`)
- `pdf_ingestion_system/rag_retriever.py`
- `web_app/config.py` (add retry config)

**Configuration to add:**
```bash
OLLAMA_MAX_RETRIES=3
OLLAMA_RETRY_MIN_WAIT=1
OLLAMA_RETRY_MAX_WAIT=10
```

**Benefits:**
- Handles transient network failures
- Improved reliability
- Better user experience (fewer errors)

---

## 📊 Phase 5: Monitoring & Observability (0/1 Complete)

### ⬜ 8. Proper Logging Framework
**Status:** ⏳ Pending
**Priority:** Medium
**Effort:** 3-4 hours

**Tasks:**
- [ ] Replace all `print()` statements with `logging`
- [ ] Add structured logging (JSON format)
- [ ] Configure log levels (DEBUG, INFO, WARNING, ERROR)
- [ ] Add file rotation (daily or size-based)
- [ ] Log request/response for all API calls
- [ ] Add correlation IDs for request tracing
- [ ] Configure different loggers (app, auth, rag, database)
- [ ] Add log aggregation setup (optional: Loki, ELK)

**Logging structure:**
```python
import logging
import logging.handlers

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(
            'logs/app.log',
            maxBytes=10485760,  # 10MB
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

**Files to modify:**
- `web_app/app.py` (add logging middleware)
- `web_app/auth.py` (replace print with logging)
- `pdf_ingestion_system/rag_retriever.py` (replace print)
- `web_app/config.py` (add logging config)

**Configuration to add:**
```bash
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=10
LOG_FORMAT=json  # or text
```

**Benefits:**
- Centralized log management
- Better debugging capabilities
- Production troubleshooting
- Audit trail for compliance

---

## 🐳 Phase 6: DevOps & Deployment (0/1 Complete)

### ⬜ 9. Docker Containerization
**Status:** ⏳ Pending
**Priority:** Medium
**Effort:** 4-6 hours

**Tasks:**
- [ ] Create `Dockerfile` for application
- [ ] Create `docker-compose.yml` for multi-service setup
- [ ] Add `.dockerignore` file
- [ ] Create separate Dockerfile for development
- [ ] Configure volume mounts for database
- [ ] Add health check endpoint
- [ ] Create Docker Compose services:
  - App (Flask + Gunicorn)
  - PostgreSQL
  - Redis (for rate limiting)
  - Nginx (reverse proxy)
  - Ollama (LLM service)
- [ ] Add environment variable injection
- [ ] Create CI/CD pipeline (GitHub Actions)
- [ ] Document deployment process

**Dockerfile structure:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "web_app.wsgi:app"]
```

**Files to create:**
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `nginx.conf`
- `.github/workflows/deploy.yml`

**Benefits:**
- Consistent deployment environment
- Easy scaling (Docker Swarm or Kubernetes)
- Simplified dependency management
- Portable across cloud providers

---

## 🧪 Phase 7: Testing & Quality (0/1 Complete)

### ⬜ 10. Unit and Integration Tests
**Status:** ⏳ Pending
**Priority:** Medium
**Effort:** 8-10 hours

**Tasks:**
- [ ] Set up pytest framework
- [ ] Create test database fixtures
- [ ] Write unit tests for auth module
- [ ] Write unit tests for RAG retriever
- [ ] Write unit tests for course database
- [ ] Write API integration tests
- [ ] Add test coverage reporting (pytest-cov)
- [ ] Set minimum coverage threshold (80%)
- [ ] Add pre-commit hooks for testing
- [ ] Create CI pipeline for automated testing

**Test structure:**
```
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures
├── test_auth.py          # Authentication tests
├── test_api.py           # API endpoint tests
├── test_rag.py           # RAG retriever tests
├── test_database.py      # Database tests
└── test_integration.py   # End-to-end tests
```

**Files to create:**
- `tests/` directory with test files
- `pytest.ini` configuration
- `conftest.py` for fixtures
- `.coveragerc` for coverage config

**Dependencies to add:**
```txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-flask>=1.2.0
pytest-mock>=3.11.0
```

**Benefits:**
- Catch bugs before production
- Confidence in refactoring
- Documentation via tests
- Faster development cycles

---

## 🚀 Phase 8: Additional Production Features (0/7 Complete)

### ⬜ 11. Health Check Endpoint
**Status:** ⏳ Pending
**Effort:** 1 hour

**Tasks:**
- [ ] Add `/health` endpoint
- [ ] Check database connection
- [ ] Check Ollama API availability
- [ ] Check vector store status
- [ ] Return JSON with service status

---

### ⬜ 12. CORS Configuration
**Status:** ⏳ Pending
**Effort:** 1 hour

**Tasks:**
- [ ] Add Flask-CORS dependency
- [ ] Configure allowed origins
- [ ] Configure allowed methods
- [ ] Configure allowed headers

---

### ⬜ 13. API Documentation
**Status:** ⏳ Pending
**Effort:** 3-4 hours

**Tasks:**
- [ ] Add Flask-RESTX or Flask-Smorest
- [ ] Add OpenAPI/Swagger documentation
- [ ] Document all API endpoints
- [ ] Add request/response examples
- [ ] Host Swagger UI at `/docs`

---

### ⬜ 14. Caching Layer
**Status:** ⏳ Pending
**Effort:** 4-5 hours

**Tasks:**
- [ ] Add Redis for caching
- [ ] Cache common questions
- [ ] Cache course data
- [ ] Add cache invalidation logic
- [ ] Configure TTL for different data types

---

### ⬜ 15. Email Notifications
**Status:** ⏳ Pending
**Effort:** 3-4 hours

**Tasks:**
- [ ] Add email sending capability (Flask-Mail)
- [ ] Email verification on registration
- [ ] Password reset emails
- [ ] Account lockout notifications
- [ ] Weekly progress reports (optional)

---

### ⬜ 16. Background Jobs
**Status:** ⏳ Pending
**Effort:** 5-6 hours

**Tasks:**
- [ ] Add Celery for async tasks
- [ ] Add Redis as message broker
- [ ] Move email sending to background
- [ ] Add periodic cleanup tasks
- [ ] Add course data refresh tasks

---

### ⬜ 17. Nginx Reverse Proxy
**Status:** ⏳ Pending
**Effort:** 2-3 hours

**Tasks:**
- [ ] Create nginx.conf
- [ ] Configure SSL/TLS
- [ ] Configure static file serving
- [ ] Configure load balancing
- [ ] Add rate limiting at Nginx level

---

## 📈 Progress Tracker

| Phase | Tasks | Completed | Progress |
|-------|-------|-----------|----------|
| Phase 0: Dynamic Learning Path Generator | 1 | 0 | ⬜ 0% |
| Phase 1: Critical Infrastructure | 3 | 3 | ✅ 100% |
| Phase 2: Security Hardening | 2 | 0 | ⬜ 0% |
| Phase 3: Database Upgrade | 1 | 0 | ⬜ 0% |
| Phase 4: Resilience | 1 | 0 | ⬜ 0% |
| Phase 5: Monitoring | 1 | 0 | ⬜ 0% |
| Phase 6: DevOps | 1 | 0 | ⬜ 0% |
| Phase 7: Testing | 1 | 0 | ⬜ 0% |
| Phase 8: Additional Features | 7 | 0 | ⬜ 0% |
| **TOTAL** | **18** | **3** | **17%** |

---

## 🎯 Recommended Implementation Order

### Sprint 0 (Current) - Breakthrough Feature for Demo
1. ⬜ Dynamic Learning Path Generator

### Sprint 1 (Post-Demo) - Security & Stability
2. ⬜ Password Complexity Requirements
3. ⬜ Account Lockout

### Sprint 2 (Post-Demo) - Database & Logging
4. ⬜ PostgreSQL Migration
5. ⬜ Proper Logging Framework
6. ⬜ Health Check Endpoint

### Sprint 3 (Post-Demo) - Resilience & DevOps
7. ⬜ Retry Logic for Ollama
8. ⬜ Docker Containerization
9. ⬜ CORS Configuration

### Sprint 4 (Post-Demo) - Testing & Documentation
10. ⬜ Unit and Integration Tests
11. ⬜ API Documentation
12. ⬜ Nginx Reverse Proxy

### Sprint 5+ (Optional) - Advanced Features
13. ⬜ Caching Layer
14. ⬜ Email Notifications
15. ⬜ Background Jobs

---

## 📚 Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Libraries Used
- Flask 2.3.3 - Web framework
- Flask-Login 0.6.3 - Session management
- Flask-Limiter 3.5.0 - Rate limiting
- Gunicorn 21.2.0 - WSGI server
- LangChain - RAG framework
- ChromaDB - Vector database

### Performance Targets
- API response time: < 200ms (cached) / < 5s (LLM)
- Concurrent users: 100+
- Uptime: 99.9%
- Database query time: < 50ms

---

## 🔐 Security Checklist

- [x] Environment variables for secrets
- [x] Rate limiting on API endpoints
- [x] Session cookie security (HTTPONLY, SAMESITE)
- [x] Password hashing (PBKDF2)
- [ ] Password complexity requirements
- [ ] Account lockout mechanism
- [ ] HTTPS/SSL in production
- [ ] CORS configuration
- [ ] SQL injection prevention (parameterized queries) ✓
- [ ] XSS prevention (template escaping)
- [ ] CSRF protection
- [ ] Input validation on all endpoints
- [ ] API authentication tokens
- [ ] Regular security audits

---

## 📝 Notes

- **Development vs Production:** Keep Flask dev server for development, use Gunicorn for production
- **Database:** SQLite is fine for < 10 concurrent users, PostgreSQL for production
- **Scaling:** Use Redis for rate limiting when running multiple servers
- **Monitoring:** Consider adding Prometheus + Grafana for production metrics
- **Backups:** Implement automated database backups daily
- **Documentation:** Keep this roadmap updated as tasks are completed

---

**Last Updated:** 2025-01-27
**Maintainer:** Development Team
**Next Review:** After Sprint 1 completion
