# System Validation & Deployment Checklist

## Pre-Deployment Validation

# Production Deployment Checklist

## Pre-Deployment Validation

### ✅ Environment Setup
- [ ] Python 3.11+ installed: `python --version`
- [ ] Virtual environment created/activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] spaCy model downloaded: `python -m spacy download en_core_web_sm`
- [ ] CUDA available (optional): `python -c "import torch; print(torch.cuda.is_available())"`

### ✅ Configuration
- [ ] `.env` file created from `.env.example`
- [ ] `SECRET_KEY` set to secure random value (32+ chars): `openssl rand -hex 32`
- [ ] `REDIS_URL` configured (if using Redis)
- [ ] `LOG_LEVEL` set to INFO or WARNING (not DEBUG)
- [ ] `DEBUG` set to False in production
- [ ] `ALLOWED_ORIGINS` set to specific domains (not `["*"]`)
- [ ] `MAX_FILE_SIZE` configured appropriately
- [ ] `MAX_CONTEXT_LENGTH` tuned for your use case

### ✅ Code Quality
- [ ] Syntax check: `python -m py_compile app/*.py app/**/*.py`
- [ ] Linting: `pylint app/ --fail-under=8.0`
- [ ] Type checking: `mypy app/`
- [ ] Unit tests pass: `pytest tests/ -v`
- [ ] Integration tests pass: `python test_integration.py`

### ✅ Services Running
- [ ] Redis running (if not using fallback): `redis-cli ping`
- [ ] API starts without errors: `python main.py`
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] Metrics endpoint available: `curl http://localhost:8000/metrics`
- [ ] Interactive docs accessible: http://localhost:8000/docs

### ✅ Models Loaded
- [ ] QA model loads: Check logs for "DistilBERT"
- [ ] NER model loads: Check logs for "spaCy model loaded" (optional, degrades gracefully)
- [ ] Embedding model loads: Check logs for "sentence-transformers" (optional for RAG)
- [ ] No CUDA errors if GPU disabled

### ✅ Token generation works: `curl -X POST http://localhost:8000/api/v1/token`
- [ ] Session creation works: `curl -X POST http://localhost:8000/api/v1/session -H "Authorization: Bearer $TOKEN"`
- [ ] Document upload works: `curl -X POST http://localhost:8000/api/v1/upload -H "Authorization: Bearer $TOKEN" -F "files=@test.pdf"`
- [ ] QA works: `curl -X POST http://localhost:8000/api/v1/ask -H "Authorization: Bearer $TOKEN" -d '{"session_id":"...","question":"test"}'`
- [ ] Session info works: `curl http://localhost:8000/api/v1/session/SESSION_ID -H "Authorization: Bearer $TOKEN"`
- [ ] Session deletion works: `curl -X DELETE http://localhost:8000/api/v1/session/SESSION_ID -H "Authorization: Bearer $TOKEN"`
- [ ] Sessions list works: `curl http://localhost:8000/api/v1/sessions/count -H "Authorization: Bearer $TOKEN"`
- [ ] Health endpoints work: `curl http://localhost:8000/health`
- [ ] Monitoring endpoints work: `curl http://localhost:8000/metrics`
- [ ] Monitoring endpoints work with auth

--- .`
- [ ] Image size reasonable (<2GB): `docker images | grep doc-qa-api`
- [ ] No build warnings or errors
- [ ] All dependencies installed correctly

### ✅ Run
- [ ] Container starts: `docker run -p 8000:8000 doc-qa-api`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] No permission errors in logs
- [ ] Models load in container (check logs)
- [ ] API accessible from host machine

### ✅ Docker Compose
- [ ] Compose up succeeds: `docker-compose up`
- [ ] API container healthy
- [ ] Redis container healthy (if included)
- [ ] Networks created correctly: `docker network ls`
- [ ] Volumes mounted: `docker volume ls`
- [ ] Services can communicate with each other
### ✅ Docker Compose
- [ ] Compose up succeeds: `docker-compose up`
- [ ] API and Redis both healthy1/token`
- [ ] Token validation works: Invalid token returns 401
- [ ] Protected endpoints require authentication
- [ ] Token format is secure (HS256 signing)
- [ ] **⚠️ PRODUCTION**: Replace open `/token` endpoint with proper user authentication

### ✅ Input Validation
- [ ] Pydantic models validate all inputs
- [ ] Path traversal prevented: `../../../etc/passwd` rejected in filenames
- [ ] Large inputs rejected: File uploads > MAX_FILE_SIZE fail
- [ ] XSS prevented: HTML/script tags in inputs sanitized
- [ ] Question length limits enforced

### ✅ Rate Limiting
- [ ] Rate limit enforced: Exceeding limits returns 429
- [ ] Rate limit headers present: `X-RateLimit-*` in responses
- [ ] Rate limit reset works: Wait and retry succeeds
- [ ] Different limits per endpoint work correctly
- [ ] **⚠️ PRODUCTION NOTE**: IP-based limiting has NAT limitations

### ✅ Headers & CORS
- [ ] Security headers present: Check response headers for HSTS, CSP, X-Frame-Options
- [ ] CORS configured correctly: Not `allow_origins=["*"]` in production
- [ ] No sensitive info in headers or error messages
- [ ] Content-Type headers correct
- [ ] Rate limit enforced: >100 requests/60s returns 429
- [ ] Rate limit headers present: `X-RateLimit-*` headers in response
- [ ] Rate limit r50+ concurrent requests without errors
- [ ] Response times < 1s (excluding first model load)
- [ ] First request takes 5-10s (model loading - normal)
- [ ] Memory usage reasonable (< 2GB for CPU, < 4GB with GPU)
- [ ] CPU usage < 80% under normal load

### ✅ Caching
- [ ] Cache hit rate > 50%: Check `/api/v1/cache/stats`
- [ ] QA results cached: Duplicate questions return instantly
- [ ] Cache works with Redis (if configured)
- [ ] In-memory fallback works if Redis unavailable
- [ ] Cache TTL honored

### ✅ Model Performance
- [ ] QA inference < 500ms (CPU) or < 100ms (GPU)
- [ ] NER inference < 200ms
- [ ] Text extraction < 2s for typical documents
- [ ] Image OCR < 5s per page
- [ ] CPU usage reasonable (< 80%)

### ✅ Caching
- [ ] Cache hit rate > 60%: Check `/api/v2/cache/stats`
- [ ] Embeddings cached: Second identical query faster
- [ ] QA results cached: Duplicate questions instant
- [ ] Cache expires: TTL honored

### ✅ Model Performance
- [ ] QA inference < 500ms: Check logs
- [ ] NER inference < 200ms: Check logs
- [ ] Embedding inference < 150ms: Check logs
- [ ] Batch processing faster than individual

---

## Monitoring Validation

### ✅ Logging
- [ ] All requests logged:  with status
- [ ] `/metrics` shows Prometheus metrics
- [ ] Model status endpoint works: `/api/v1/models/status`
- [ ] Cache stats endpoint works: `/api/v1/cache/stats`
- [ ] Session count endpoint works: `/api/v1/sessions/count`
### ✅ Metrics
- [ ] Prometheus endpoint responds: `curl http://localhost:8000/metrics`
- [ ] Metrics valid format: Can be parsed by Prometheus
- [ ] All metric types present: counter, gauge, histogram
- [ ] Request counts increment
- [ ] Latency distributions correct

### ✅ Health Checks
- [ ] `/health` returns 200
- [ ] `/api/v2/health/detailed` shows all services operational
- [ ] Model status endpoint Upload `test_docs/sample_contract.pdf`
- [ ] Image OCR works: Upload `test_docs/sample_invoice.png`
- [ ] Multi-document sessions work: Upload multiple files
- [ ] Session deletion works and cleans up resources
- [ ] Large documents handled gracefully

### ✅ Question Answering
- [ ] Simple questions answered: "What is X?"
- [ ] Complex questions work: Multi-part questions
- [ ] Multi-document QA works: `/api/v1/ask-detailed`
- [ ] Confidence scores reasonable: 0.5-1.0 range
- [ ] Context extraction accurate

### ✅ NER (Optional Feature)
- [ ] Entities extracted when `highlight_entities=true`
- [ ] Common entity types recognized: PERSON, ORG, DATE, MONEY, GPE
- [ ] Entity offsets correct for highlighting
- [ ] Works gracefully if spaCy model not loaded

### ✅ RAG / Semantic Search (Optional Feature)
- [ ] Similar chunks retrieved when RAG enabled
- [ ] Relevance scores reasonable: 0-1 range
- [ ] Works gracefully if embedding model not loaded
- [ ] Improves answer quality for longer document, ORG, DATE, MONEY
- [ ] Output formats work: dict, html, markdown
- [ ] Entity highlighting works
- [ ] Multi-document NER works

### ✅ RAG / Semantic Search
- [ ] Similar chunks retrieved
- [ ] Relevance scores reasonable: 0-1 range
- [ ] Top-K results configurable
- [ ] Chunk-based retrieval works

---

## Deployment Validation

### ✅ Development
- [ ] Runs on localhost:8000
- [ ] Debug mode can be enabled
- [ ] Auto-reload works
- [ ] Logs show detailed info

### ✅ Staging
- [ ] Runs on staging server
- [ ] Debug mode disabled
- [ ] All URLs point to staging
- [ ] Secrets configured securely

### ✅ Production
- [ ] HTTPS configured
- [Production-Only Requirements

### ⚠️ Critical for Production

#### 1. User Authentication System
**Current State**: Open `/api/v1/token` endpoint generates tokens without validation.

**Required Changes**:
- [ ] Implement user registration and login system
- [ ] Create user database (PostgreSQL/MongoDB)
- [ ] Hash passwords with bcrypt
- [ ] Validate credentials before issuing tokens
- [ ] Add username/user_id to JWT payload
- [ ] Implement token refresh mechanism

#### 2. Persistent Session Storage
**Current State**: In-memory storage, lost on restart.

**Required Changes**:
- [ ] Set up PostgreSQL or MongoDB database
- [ ] Create sessions table/collection
- [ ] Migrate SessionStorage to use database
- [ ] Implement session persistence across restarts
- [ ] Add session expiration cleanup job

#### 3. Secure Configuration
**Current State**: Hardcoded defaults exist.

**Required Changes**:
- [ ] Generate secure random `SECRET_KEY`: `openssl rand -hex 32`
- [ ] Set `DEBUG=False`
- [ ] Configure-url>
cd AI-INTERVIEW

# Automated setup (recommended)
# Windows:
.\setup.bat

# Linux/Mac:
bash setup.sh

# OR Manual setup:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
**Checklist**:
- [ ] All packages installed without errors
- [ ] No version conf (Optional)
```bash
# API works with defaults, but you can customize:
# Copy environment template if it exists
cp .env.example .env  # Optional

# Edit configuration
nano .env  # Or use your preferred editor

# Key settings (all have defaults):
# SECRET_KEY=<generate with: openssl rand -hex 32>
# REDIS_URL=redis://localhost:6379/0
# MAX_CONTEXT_LENGTH=2000
# DEBUG=false
```
**Checklist**:
- [ ] Configuration reviewed (or using defaults)
- [ ] SECRET_KEY changed from default (if production)
- [ ] REDIS_URL uLocally
```bash
# Validate setup
python setup_validation.py

# Run unit tests
pytest tests/ -v

# Run integration tests
python test_integration.py
python test_auth.py
python test_caching_integration.py
python test_rag_integration.py
```
**Checklist**:
- [ ] Setup validation passes
- [ ] Unit tests pass (8 tests)
- [ ] Integrationd Changes**:
- [ ] Automated database backups (daily minimum)
- [ ] Backup verification and restore testing
- [ ] Disaster recovery plan documented
- [ ] Model files backed up to S3/cloud storage
- [ ] Configuration backups

---

## Dependency Validation

### ✅ Core Required Packages
- [ ] fastapi==0.109.0: `pip show fastapi`
- [ ] uvicorn==0.27.0: `pip show uvicorn`
- [ ] pydantic==2.5.3: `pip show pydantic`
- [ ] pydantic-settings==2.1.0: `pip show pydantic-settings`
- [ ] python-jose[cryptography]: `pip show python-jose`
- [ ] bcrypt: `pip show bcrypt`
- [ ] slowapi: `pip show slowapi`
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/token | jq -r '.access_token')
echo "Token: $TOKEN"

# Create session
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/session \
  -H "Authorization: Bearer $TOKEN")
echo "Session: $SESSION_RESPONSE"

# Upload document
UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@test_docs/sample_contract.pdf")
SESSION_ID=$(echo $UPLOAD_RESPONSE | jq -r '.session_id')
echo "Upload result: $UPLOAD_RESPONSE"

# Ask question
ANSWER=$(curl -s -X POST http://localhost:8000/api/v1/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"question\":\"What is this document about?\",\"highlight_entities\":true}")
echo "Answer: $ANSWER"
```
**Checklist**:
- [ ] Token generation returns access_token
- [ ] Session creation returns session_id
- [ ] Upload returns session_id and documents array
- [ ] Ask returns answer with confidence score
- [ ] Entities returned when highlight_entities=tru
---Web Interface (Streamlit) Validation

### ✅ Frontend Setup
- [ ] Streamlit dependencies installed: `pip install -r requirements-streamlit.txt`
- [ ] Frontend launches: `streamlit run frontend/app.py`
- [ ] Accessible at: http://localhost:8501
- [ ] No import errors

### ✅ Frontend Features
- [ ] Upload tab: Drag-and-drop file upload works
- [ ] Chat tab: Question answering interface works
- [ ] Documents tab: Document viewer with NER highlighting
- [ ] Analysis tab: Entity analysis and statistics
- [ ] Sidebar: Session switching and management works
- [ ] Session history persists during UI session

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Kill process: `lsof -i :8000` (Linux/Mac) or `netstat -ano \| findstr :8000` (Windows) |
| Redis connection failed | Check: `redis-cli ping` or disable Redis (uses in-memory fallback) |
| spaCy model not found | Download: `python -m spacy download en_core_web_sm` |
| Out of memory | Set `MAX_CONTEXT_LENGTH=1000` in .env or reduce document size |
| Slow first request | Normal (model loading 5-10s), subsequent requests <1s |
| 401 Unauthorized | Generate new token: `curl -X POST http://localhost:8000/api/v1/token` |
| 429 Rate Limited | Wait 60 seconds or reduce request rate |
| 404 Session not found | Verify session_id from upload response |
| Pillow ANTIALIAS error | Ensure pillow==9.5.0: `pip install pillow==9.5.0` |
| Import errors | Reinstall dependencies: `pip install -r requirements.txt --force-reinstall` |

---

## Sign-Off Checklist

**Deployment Date**: _______________

**Deployed By**: _______________

**Environment**: [ ] Development  [ ] Staging  [ ] Production

**Pre-Deployment Status**:
- [ ] All validation checks passed ✅
- [ ] Tests passed (unit + integration)
- [ ] Security review completed
- [ ] Performance benchmarks acceptable
- [ ] Documentation reviewed and updated

**Production-Only Requirements** (if deploying to production):
- [ ] User authentication system implemented
- [ ] Database configured for persistent storage
- [ ] SECRET_KEY changed from default
- [ ] HTTPS/SSL configured
- [ ] Monitoring and alerting set up
- [ ] Backup strategy implemented
- [ ] CORS restricted to specific origins
- [ ] Load balancer configured (if multi-instance)

**Known Issues**:
```
(Document any known limitations or issues here)
See README.md "Known Limitations" section for testing version notes.
```

**Rollback Plan**:
```
(Document rollback procedure if deployment fails)
```

**Sign-Off**:
- [ ] Technical Lead: _______________
- [ ] Security Review: _______________
- [ ] DevOps Approval: _______________

---

**Document Version**: 2.0  
**Last Updated**: January 16, 2026  
**Compatible with**: API v1.0, Python 3.11+

---

## Additional Resources

- **README.md**: Complete user documentation
- **API_REFERENCE.md**: Full API endpoint documentation
- **frontend/README.md**: Web UI component documentation
- **Interactive API Docs**: http://localhost:8000/docsd for your setup

### Step 3: Test locally
```bash
# Run tests
pytest tests/ -v

# Run integration test
python test_integration.py

# Check setup
python setup_validation.py
```
**Checklist**:
- [ ] All tests pass
- [ ] No module import errors
- [ ] Models load successfully

### Step 4: Start API
```bash
# Option A: Direct Python
python main.py

# Option B: Uvicorn
uvicorn main:app --reload

# Option C: Docker
docker-compose up
```
**Checklist**:
- [ ] Server starts without errors
- [ ] "Application startup complete" message
- [ ] Port 8000 accessible
- [ ] Health check passes: `curl http://localhost:8000/health`

### Step 5: Test API
```bash
# Get token
curl -X POST http://localhost:8000/api/v2/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"secret"}'

# Save token
export TOKEN="<token_value>"

# Upload document
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@test_docs/sample_contract.pdf"

# Save session ID
export SESSION_ID="<session_id_value>"

# Ask question
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"question\":\"What is mentioned?\"}"
```
**Checklist**:
- [ ] Login returns token
- [ ] Upload returns session_id
- [ ] Ask returns answer with confidence

---

## Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Port 8000 already in use | Kill process: `lsof -i :8000` → `kill -9 <PID>` |
| Redis connection failed | Check Redis running: `redis-cli ping` |
| spaCy model not found | Download: `python -m spacy download en_core_web_sm` |
| Out of memory | Reduce context size in .env: `MAX_CONTEXT_LENGTH=1000` |
| Slow first request | Normal - models loading (5-15s), subsequent < 1s |
| 401 Unauthorized | Generate new token: `curl -X POST .../api/v2/login` |
| 429 Rate Limited | Wait 60 seconds or reduce request rate |
| 404 Session not found | Use current session_id from upload response |

---

## Sign-Off

**Date**: _______________

**Validator**: _______________

**Status**:
- [ ] All checks passed ✅
- [ ] Ready for production deployment
- [ ] Known issues documented below

**Known Issues**:
```
(List any known limitations or issues)
```

**Notes**:
```
(Any additional observations or recommendations)
```

---

**Document Version**: 1.0
**Last Updated**: 2024-01-15
**API Version**: 2.0.0
