# System Validation & Deployment Checklist

## Pre-Deployment Validation

### ✅ Environment Setup
- [ ] Python 3.9+ installed: `python --version`
- [ ] Virtual environment created/activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] spaCy model downloaded: `python -m spacy download en_core_web_sm`
- [ ] CUDA available (optional): `python -c "import torch; print(torch.cuda.is_available())"`

### ✅ Configuration
- [ ] `.env` file created from `.env.example`
- [ ] `SECRET_KEY` set to secure random value
- [ ] `REDIS_URL` configured (Redis running or fallback mode)
- [ ] `LOG_LEVEL` set appropriately (DEBUG/INFO/WARNING)
- [ ] `DEBUG` set to False in production

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

### ✅ Models Loaded
- [ ] QA model loads: Check logs for "Loaded DistilBERT"
- [ ] NER model loads: Check logs for "Loaded spaCy"
- [ ] Embedding model loads: Check logs for "Loaded sentence-transformers"
- [ ] No CUDA errors if GPU disabled

### ✅ API Endpoints
- [ ] Authentication works: `curl -X POST http://localhost:8000/api/v2/login ...`
- [ ] Document upload works: `curl -X POST http://localhost:8000/api/v1/upload ...`
- [ ] QA works: `curl -X POST http://localhost:8000/api/v1/ask ...`
- [ ] Health endpoints work
- [ ] Monitoring endpoints work with auth

---

## Docker Validation

### ✅ Build
- [ ] Build succeeds: `docker build -t doc-qa-api:v2 .`
- [ ] Image size reasonable: `docker images | grep doc-qa-api`
- [ ] No build warnings

### ✅ Run
- [ ] Container starts: `docker run -p 8000:8000 doc-qa-api:v2`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] No permission errors in logs
- [ ] Models load in container

### ✅ Docker Compose
- [ ] Compose up succeeds: `docker-compose up`
- [ ] API and Redis both healthy
- [ ] Networks created correctly: `docker network ls`
- [ ] Volumes mounted: `docker volume ls`

---

## Security Validation

### ✅ Authentication
- [ ] JWT tokens generated: `curl -X POST http://localhost:8000/api/v2/login`
- [ ] Token validation works: Invalid token returns 401
- [ ] Token expiration works: Old token returns 401
- [ ] Endpoints protected with @verify_token

### ✅ Input Validation
- [ ] SQL injection prevented: Special chars in inputs don't break
- [ ] Path traversal prevented: `../../../etc/passwd` rejected
- [ ] Large inputs rejected: File uploads > 50MB fail
- [ ] XSS prevented: `<script>alert(1)</script>` sanitized

### ✅ Rate Limiting
- [ ] Rate limit enforced: >100 requests/60s returns 429
- [ ] Rate limit headers present: `X-RateLimit-*` headers in response
- [ ] Rate limit reset works: Wait and retry succeeds
- [ ] Different limits per endpoint work

### ✅ Headers
- [ ] Security headers present: `Strict-Transport-Security`, `Content-Security-Policy`, `X-Frame-Options`
- [ ] CORS configured correctly
- [ ] No sensitive info in headers

---

## Performance Validation

### ✅ Load Testing
- [ ] API handles 100 concurrent requests
- [ ] Response times < 1s (excluding first model load)
- [ ] First request takes 5-15s (model loading)
- [ ] Memory usage stays < 2GB
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
- [ ] All requests logged: `tail -f logs/app.log`
- [ ] Log format valid JSON: `grep "api_request" logs/app.log | python -m json.tool`
- [ ] Log levels correct: DEBUG, INFO, WARNING, ERROR
- [ ] File rotation works: Check logs/ directory

### ✅ Metrics
- [ ] Prometheus endpoint responds: `curl http://localhost:8000/metrics`
- [ ] Metrics valid format: Can be parsed by Prometheus
- [ ] All metric types present: counter, gauge, histogram
- [ ] Request counts increment
- [ ] Latency distributions correct

### ✅ Health Checks
- [ ] `/health` returns 200
- [ ] `/api/v2/health/detailed` shows all services operational
- [ ] Model status endpoint works
- [ ] Cache stats endpoint works
- [ ] Session count endpoint works

---

## Feature Validation

### ✅ Document Handling
- [ ] PDF extraction works: `test_docs/sample_contract.pdf`
- [ ] Image OCR works: `test_docs/sample_invoice.png`
- [ ] Multi-document sessions work
- [ ] Session deletion works

### ✅ Question Answering
- [ ] Simple questions answered: "What is X?"
- [ ] Complex questions answered: Multi-part questions
- [ ] Multi-document QA works: Answers from all docs
- [ ] Confidence scores reasonable: 0.5-1.0 range

### ✅ NER
- [ ] Entities extracted: PERSON, ORG, DATE, MONEY
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
- [ ] Domain certificate valid
- [ ] Load balancer configured
- [ ] Database backups scheduled
- [ ] Monitoring alerts configured

---

## Dependency Validation

### ✅ Required Packages
- [ ] fastapi==0.109.0: `pip show fastapi`
- [ ] uvicorn==0.27.0: `pip show uvicorn`
- [ ] torch==2.1.2: `pip show torch`
- [ ] transformers==4.36.2: `pip show transformers`
- [ ] spacy==3.7.2: `pip show spacy`
- [ ] sentence-transformers==2.2.2: `pip show sentence-transformers`
- [ ] faiss-cpu==1.7.4: `pip show faiss-cpu`
- [ ] redis==5.0.1: `pip show redis`
- [ ] pydantic==2.5.3: `pip show pydantic`
- [ ] pydantic-settings==2.1.0: `pip show pydantic-settings`

### ✅ Optional Packages
- [ ] pytest==7.4.4: For testing
- [ ] black==23.12.1: Code formatting
- [ ] pylint==3.0.3: Linting
- [ ] mypy==1.7.1: Type checking

---

## First-Time Setup Checklist

### Step 1: Clone & Install
```bash
# Clone repository
git clone <repo>
cd AI-INTERVIEW

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Or: venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Download models
python -m spacy download en_core_web_sm
```
**Checklist**:
- [ ] All packages installed without errors
- [ ] No version conflicts
- [ ] Virtual environment activated

### Step 2: Configure
```bash
# Copy environment template
cp .env.example .env

# Edit with editor
nano .env  # Or use your preferred editor

# Set critical values:
# SECRET_KEY=<generate-random-string>
# REDIS_URL=redis://localhost:6379/0
```
**Checklist**:
- [ ] .env file created
- [ ] SECRET_KEY set to secure random value
- [ ] REDIS_URL updated for your setup

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
