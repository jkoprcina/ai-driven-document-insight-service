# 📄 Document Q&A REST API

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009485?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/Tests-pytest-brightgreen?style=flat&logo=pytest)](tests/)

A production-ready REST API for intelligent document processing with AI-powered question answering. Upload PDFs and images, then ask natural language questions about your documents. Features text extraction, named entity recognition, RAG-based semantic search, Redis caching, JWT authentication, rate limiting, and comprehensive monitoring.

## ✨ Features

### Core Capabilities
- **Multi-format Upload**: PDF, JPG, PNG, BMP, GIF, TIFF support
- **Text Extraction**: PyMuPDF for PDFs + EasyOCR for images (12+ languages)
- **Question Answering**: DistilBERT transformer with confidence scoring
- **Session Management**: UUID-based session tracking with multiple documents per session
- **Multi-document Search**: Find best answer across all uploaded documents

### Advanced Features
- **Named Entity Recognition (NER)**: Extract people, locations, organizations, dates, money, etc. (spaCy)
- **RAG Integration**: FAISS-based vector search for semantic chunk retrieval
- **Smart Caching**: Redis with automatic in-memory fallback
- **JWT Authentication**: Secure token-based API access
- **Rate Limiting**: Configurable per-endpoint limits by IP address
- **Structured Logging**: JSON logs for production monitoring
- **Prometheus Metrics**: Comprehensive monitoring and health checks
- **Security**: Input validation, CORS protection, request size limits

### Web Interface
- **Interactive Streamlit UI**: Drag-and-drop uploads, chat interface, document viewer
- **Session Switching**: Easily switch between multiple document sessions
- **Entity Highlighting**: Visual NER entity highlighting in documents
- **Confidence Scoring**: Real-time answer confidence indicators
- **Chat History**: Per-session conversation tracking

## 🚀 Quick Start

### Option A: Automated Setup (Recommended)
```bash
# Windows
.\setup.bat

# Linux/Mac
bash setup.sh

# Then start the API
python main.py
```

### Option B: Manual Installation
```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Download spaCy NER model
python -m spacy download en_core_web_sm

# 3. Start the API server
python main.py
```

### Option C: Docker
```bash
docker-compose up --build
```

**Access the API**: http://localhost:8000/docs (Interactive Swagger UI)

### Web Interface (Optional)
```bash
# Install Streamlit dependencies
pip install -r requirements-streamlit.txt

# Launch web UI
streamlit run frontend/app.py
```

**Access the UI**: http://localhost:8501

## 📚 API Endpoints

### Authentication
```
POST   /api/v1/token              - Get JWT token (development only)
```

### Document Management
```
POST   /api/v1/session            - Create new session
POST   /api/v1/upload             - Upload documents to session
GET    /api/v1/session/{id}       - Get session info and documents
DELETE /api/v1/session/{id}       - Delete session and cleanup
```

### Question Answering
```
POST   /api/v1/ask                - Ask question (best answer from all docs)
POST   /api/v1/ask-detailed       - Get answers from each document with scores
```

### Monitoring & Health
```
GET    /health                    - API health check
GET    /metrics                   - Prometheus metrics
GET    /api/v1/sessions/count     - List active sessions
GET    /api/v1/cache/stats        - Cache statistics
GET    /api/v1/models/status      - Model loading status
```

## 💡 Usage Examples

### Python Client
```python
import requests

# 1. Get authentication token
token_resp = requests.post('http://localhost:8000/api/v1/token')
token = token_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# 2. Upload documents
files = [
    ('files', open('contract.pdf', 'rb')),
    ('files', open('invoice.png', 'rb'))
]
upload_resp = requests.post(
    'http://localhost:8000/api/v1/upload',
    files=files,
    headers=headers
)
session_id = upload_resp.json()['session_id']
print(f"Session created: {session_id}")

# 3. Ask a question
question = {
    'session_id': session_id,
    'question': 'What is the total contract amount?',
    'highlight_entities': True
}
answer_resp = requests.post(
    'http://localhost:8000/api/v1/ask',
    json=question,
    headers=headers
)
result = answer_resp.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Source: {result['source_doc']}")
if result.get('entities'):
    print(f"Entities found: {len(result['entities'])}")
```

### cURL
```bash
# 1. Get token
curl -X POST http://localhost:8000/api/v1/token

# 2. Upload documents
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@contract.pdf" \
  -F "files=@invoice.jpg"

# 3. Ask question
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "question": "What are the payment terms?",
    "highlight_entities": true
  }'
```

### JavaScript/Node.js
```javascript
// 1. Get token
const tokenResp = await fetch('http://localhost:8000/api/v1/token', {
  method: 'POST'
});
const { access_token } = await tokenResp.json();

// 2. Upload documents
const formData = new FormData();
formData.append('files', document.getElementById('file').files[0]);

const uploadResp = await fetch('http://localhost:8000/api/v1/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` },
  body: formData
});
const { session_id } = await uploadResp.json();

// 3. Ask question
const qaResp = await fetch('http://localhost:8000/api/v1/ask', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    session_id: session_id,
    question: 'What is the contract amount?',
    highlight_entities: true
  })
});
const result = await qaResp.json();
console.log(`Answer: ${result.answer} (${result.confidence})`);
```

## 🏗️ Project Structure

```
AI-INTERVIEW/
├── main.py                          # FastAPI application entry point
│
├── app/
│   ├── config.py                    # Configuration management (env vars, defaults)
│   ├── dependencies.py              # FastAPI dependencies (auth, rate limiting)
│   ├── middleware.py                # Custom middleware (security, logging, rate limiting)
│   │
│   ├── routers/                     # API endpoint handlers
│   │   ├── token.py                 # JWT token generation
│   │   ├── documents.py             # Upload, session management
│   │   ├── qa.py                    # Question answering endpoints
│   │   └── monitoring.py            # Health, metrics, sessions list
│   │
│   └── services/                    # Business logic services
│       ├── extractor.py             # PDF (PyMuPDF) + Image (EasyOCR) extraction
│       ├── qa.py                    # DistilBERT QA engine with RAG
│       ├── ner.py                   # spaCy named entity recognition
│       ├── rag.py                   # FAISS vector search for semantic retrieval
│       ├── cache.py                 # Redis caching with in-memory fallback
│       ├── security.py              # JWT tokens, password hashing, input validation
│       ├── storage.py               # In-memory session storage
│       └── monitoring.py            # Prometheus metrics and logging
│
├── frontend/                        # Streamlit web interface
│   ├── app.py                       # Main Streamlit app
│   ├── config.py                    # Frontend configuration
│   │
│   ├── components/                  # UI components (modular design)
│   │   ├── upload_tab.py            # Document upload interface
│   │   ├── chat_tab.py              # Q&A chat interface
│   │   ├── documents_tab.py         # Document viewer with NER highlighting
│   │   ├── analysis_tab.py          # Document analysis dashboard
│   │   └── sidebar.py               # Session management and settings
│   │
│   ├── utils/                       # Frontend utilities
│   │   ├── api_client.py            # API communication
│   │   ├── auth.py                  # Token management
│   │   └── formatters.py            # Display formatters and entity highlighting
│   │
│   └── styles/
│       └── custom.css               # Custom CSS styling
│
├── tests/                           # Test suite
│   ├── test_api.py                  # API endpoint tests
│   ├── test_services.py             # Service unit tests
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_integration.py          # Full workflow integration tests
│   ├── test_auth.py                 # Authentication tests
│   ├── test_caching_integration.py  # Cache integration tests
│   └── test_rag_integration.py      # RAG system tests
│
├── scripts/
│   └── generate_test_docs.py        # Generate sample test documents
│
├── documentation/
│   ├── API_REFERENCE.md             # Complete API documentation
│   ├── DEPLOYMENT_CHECKLIST.md      # Production deployment guide
│   └── START_HERE.txt               # Quick navigation guide
│
├── test_docs/                       # Sample test documents
├── logs/                            # Application logs (auto-created)
├── model_cache/                     # Cached ML models (auto-created)
├── rag_indices/                     # FAISS vector indices (auto-created)
│
├── requirements.txt                 # Python dependencies (API)
├── requirements-streamlit.txt       # Additional frontend dependencies
├── Dockerfile                       # Docker image definition
├── docker-compose.yml               # Multi-container setup (API + Redis)
├── setup.sh / setup.bat             # Automated setup scripts
├── setup_validation.py              # Validate environment setup
├── .env.example                     # Example environment variables
└── .gitignore                       # Git ignore rules
```

## 🛠️ Technology Stack & Design Choices

| Component | Technology | Why This Choice |
|-----------|-----------|-----------------|
| **Web Framework** | FastAPI | Modern async framework with auto-generated OpenAPI docs, excellent performance, and Python 3.11+ type hints support |
| **PDF Extraction** | PyMuPDF (fitz) | Fastest Python PDF library (C-based), zero external dependencies, handles complex PDFs reliably |
| **Image OCR** | EasyOCR | Superior accuracy on real-world documents, 80+ language support, works well on CPU, actively maintained |
| **QA Model** | DistilBERT | 40% smaller/faster than BERT, 97% accuracy retention on SQuAD benchmark, ideal for CPU inference |
| **NER** | spaCy (en_core_web_sm) | Production-ready, 12+ entity types (PERSON, ORG, MONEY, etc.), fast inference (~100ms), well-documented |
| **Vector Database** | FAISS | Meta's industry-standard library, optimized for CPU, million-scale vector search, no external server needed |
| **Embedding Model** | all-MiniLM-L6-v2 | Lightweight Sentence-BERT model (384 dimensions), excellent semantic similarity, fast encoding |
| **Caching** | Redis | Sub-millisecond latency, persistent cache across restarts, industry standard with fallback to in-memory |
| **Authentication** | JWT + bcrypt | Stateless tokens for horizontal scaling, bcrypt for secure password hashing with salt |
| **Rate Limiting** | SlowAPI | Simple per-endpoint rate limiting by IP address, prevents abuse without complex infrastructure |
| **Monitoring** | Prometheus | Cloud-native standard, rich metric types (counters, gauges, histograms), Grafana integration |
| **Logging** | Python logging | Structured JSON logs with rotation, configurable levels, production-ready |
| **Web UI** | Streamlit | Rapid prototyping, excellent for data apps, Python-native (no separate frontend build), reactive components |
| **Testing** | pytest | Industry-standard Python testing, fixtures, parametrization, excellent FastAPI integration |
| **Containerization** | Docker Compose | Reproducible environments, multi-service orchestration (API + Redis), simple deployment |

### Key Design Decisions

1. **In-Memory Session Storage**: Trade-off for simplicity in testing/demo version. Easily upgradeable to PostgreSQL/MongoDB for production.

2. **Optional Components**: NER, RAG, and Redis gracefully degrade if unavailable. API remains functional with core QA capabilities.

3. **CPU-First Optimization**: All models run efficiently on CPU. GPU support available but not required, making deployment flexible.

4. **Modular Frontend**: Streamlit UI split into reusable components (upload, chat, documents, analysis, sidebar) for maintainability.

5. **Per-Endpoint Rate Limiting**: Different limits for different operations (5/min for token generation, 30/min for questions) instead of global limit.

## 📊 Performance Benchmarks

*Measured on Intel i7-9700K CPU (8 cores), 16GB RAM, no GPU*

| Operation | Average Time | Notes |
|-----------|--------------|-------|
| Model Loading (First Request) | 5-10s | One-time overhead, cached afterward |
| PDF Extraction (10-page doc) | ~1 second | Depends on page complexity and embedded objects |
| Image OCR (A4 page) | 2-5 seconds | Single document, English text |
| Question Answering | 200-500ms | CPU inference with DistilBERT |
| RAG Vector Search (1000 docs) | 10-50ms | FAISS CPU-optimized search |
| NER Processing (1000 words) | ~100-200ms | spaCy pipeline |
| Redis Cache Hit | <5ms | In-memory lookup |
| Full Upload+Extract+NER Pipeline | 3-8 seconds | For typical document |

**GPU Performance**: With CUDA-enabled GPU, QA inference drops to ~50-100ms.

## 🧪 Testing

### Test Documentation & Sample Files

Test documents are located in the **`test_docs/`** folder and are used by the integration test suite:

- **`test_docs/JosipKoprcinaResume.pdf`** - Sample resume PDF for testing document upload and extraction
- **`test_docs/roman_history.pdf`** - Historical text document for testing multi-document Q&A
- **`test_docs/Picture-With-Text-3307742685.png`** - Image file with embedded text for testing OCR and image processing
- Additional test documents generated by `scripts/generate_test_docs.py`

These files are referenced by:
- `test_integration.py` - Full workflow testing (upload, QA, NER)
- `test_auth.py` - Authentication and authorization testing
- Manual API testing with cURL or Postman

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run integration tests (requires API running)
# Uses documents from test_docs/ folder
python test_integration.py

# Test authentication flow
python test_auth.py

# Test caching integration
python test_caching_integration.py

# Test RAG system
python test_rag_integration.py

# Validate setup
python setup_validation.py
```

## 🔒 Security Features

✅ **Input Validation**: Pydantic models validate all request payloads with type checking  
✅ **Rate Limiting**: Per-endpoint limits prevent abuse (5-30 requests/minute)  
✅ **CORS Protection**: Configurable allowed origins (currently open for testing)  
✅ **JWT Authentication**: Stateless bearer tokens with configurable expiration  
✅ **Password Hashing**: bcrypt with automatic salt generation  
✅ **File Size Limits**: Configurable max upload size (default: 50MB)  
✅ **Path Traversal Prevention**: Filename sanitization in uploads  
✅ **SQL Injection Immunity**: No SQL database used (document-based storage)  
✅ **Dependency Pinning**: All requirements locked to specific versions  
✅ **Secure Headers**: X-Content-Type-Options, X-Frame-Options, CSP, HSTS  
✅ **Sensitive Data**: No passwords or tokens logged  

## ⚠️ Known Limitations (Testing Version)

This is a **development/testing version**. Known limitations:

1. **Open Token Generation**: `/token` endpoint requires no authentication. Anyone can generate valid tokens. **Production**: Implement user registration and login with database.

2. **In-Memory Sessions**: All sessions lost on restart. No persistence. **Production**: Use PostgreSQL/MongoDB for session storage.

3. **No User Database**: Tokens don't identify specific users. **Production**: Add user table with proper authentication.

4. **Hardcoded Secret Key**: Default `secret_key` if env var not set. **Production**: Generate strong random secret and set `SECRET_KEY` environment variable.

5. **Redis Optional**: Falls back to in-memory cache. **Production**: Require Redis for multi-instance deployments.

6. **Exposed Metrics**: `/metrics` endpoint has no authentication. **Production**: Restrict with reverse proxy (nginx).

7. **CORS Open**: `allow_origins=["*"]` accepts any domain. **Production**: Whitelist specific origins.

8. **IP-Based Rate Limiting**: Can't distinguish users behind NAT. **Production**: Add user-based rate limits after authentication.

9. **Chat History Not Persisted**: Session chat histories stored in frontend only. **Production**: Store on backend with sessions.

## 📖 Documentation

- **[API_REFERENCE.md](documentation/API_REFERENCE.md)**: Complete endpoint documentation with request/response examples
- **[DEPLOYMENT_CHECKLIST.md](documentation/DEPLOYMENT_CHECKLIST.md)**: Production deployment guide
- **[frontend/README.md](frontend/README.md)**: Web UI architecture and component documentation
- **[START_HERE.txt](documentation/START_HERE.txt)**: Quick navigation guide

## 🚢 Production Deployment

For production deployment, see [DEPLOYMENT_CHECKLIST.md](documentation/DEPLOYMENT_CHECKLIST.md) for:
- Database setup (PostgreSQL with session persistence)
- Redis configuration and clustering
- SSL/TLS certificates and HTTPS setup
- Kubernetes manifests and scaling
- Environment variable management
- Monitoring stack (Prometheus + Grafana)
- Backup and disaster recovery
- Security hardening checklist

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | Change port in `.env`: `PORT=8001` or kill process: `lsof -i :8000` |
| Redis connection failed | Check Redis running: `redis-cli ping` or use in-memory fallback |
| spaCy model not found | Download: `python -m spacy download en_core_web_sm` |
| Out of memory | Reduce `MAX_CONTEXT_LENGTH` in `.env` or increase system RAM |
| Slow first request | Normal (model loading). Subsequent requests <1s |
| 401 Unauthorized | Get new token: `curl -X POST .../api/v1/token` |
| 429 Rate Limited | Wait 60 seconds or adjust limits in `app/routers/*.py` |
| Pillow ANTIALIAS error | Downgrade Pillow: `pip install pillow==9.5.0` |

## 🔮 Future Enhancements

- [ ] PostgreSQL database for persistent storage
- [ ] User authentication with registration/login
- [ ] Multiple QA model options (OpenAI GPT, Anthropic Claude)
- [ ] Batch document processing
- [ ] Document summarization endpoint
- [ ] Multi-language UI support
- [ ] Analytics dashboard in web UI
- [ ] Custom model fine-tuning on domain-specific data
- [ ] Real-time document updates with WebSockets
- [ ] Export Q&A history to CSV/PDF

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI**: For the excellent web framework
- **Hugging Face**: For transformer models and the transformers library
- **Meta AI**: For FAISS vector search
- **Explosion AI**: For spaCy NER
- **EasyOCR**: For robust OCR capabilities
- **Streamlit**: For rapid UI prototyping

---
