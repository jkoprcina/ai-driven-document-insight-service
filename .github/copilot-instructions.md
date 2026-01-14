# Document QA API Workspace Configuration

## Project Status
- [x] Project structure scaffolded
- [x] Core services created (extraction, QA, storage)
- [x] API routers implemented (/upload, /ask)
- [x] Docker configuration created
- [x] Test documents generated
- [x] Dependencies installed
- [x] Application tested (health check, endpoints verified)
- [x] Documentation complete

## Project Structure

- `main.py` - FastAPI application entry point
- `app/`
  - `routers/` - API endpoint handlers
    - `documents.py` - Upload and session management (/upload, /session, DELETE session)
    - `qa.py` - Question answering endpoints (/ask, /ask-detailed)
  - `services/` - Core business logic
    - `extractor.py` - Text extraction (PDF via PyMuPDF + Images via EasyOCR)
    - `qa.py` - QA engine using DistilBERT transformer
    - `storage.py` - Session storage management (in-memory)
- `tests/` - Unit tests (test_api.py)
- `test_docs/` - Sample test documents (sample_contract.pdf, sample_invoice.png)
- `scripts/` - Utility scripts (generate_test_docs.py)
- `Dockerfile` - Container configuration (Python 3.11-slim)
- `docker-compose.yml` - Docker Compose setup
- `requirements.txt` - All Python dependencies
- `README.md` - User-facing documentation
- `DEVELOPER_GUIDE.md` - Detailed technical documentation
- `example_usage.py` - Example API usage
- `test_integration.py` - Integration test suite
- `.vscode/tasks.json` - VS Code task configuration

## Quick Start

### Run Locally
```bash
# API is already running with server at http://localhost:8000
# Test it: http://localhost:8000/health
```

### API Endpoints
- **POST** `/api/v1/upload` - Upload PDF or image documents
- **GET** `/api/v1/session/{session_id}` - Get session info
- **DELETE** `/api/v1/session/{session_id}` - Delete session
- **POST** `/api/v1/ask` - Ask question about documents
- **POST** `/api/v1/ask-detailed` - Get answers from all documents
- **GET** `/health` - Health check

### Test the API
```bash
# Run integration tests
python test_integration.py

# Run example workflow
python example_usage.py

# Run unit tests
pytest tests/ -v
```

### Docker
```bash
# Build image (requires Docker Hub authentication)
docker build -t doc-qa-api .

# Use Docker Compose (same requirement)
docker-compose up
```

## Key Features

1. **Document Upload**: Accept PDF and image files
2. **Text Extraction**: 
   - PyMuPDF for PDF processing
   - EasyOCR for image OCR
3. **Question Answering**: DistilBERT-based extractive QA
4. **Session Management**: Session-based document organization
5. **Multi-document Search**: Find best answer across multiple documents
6. **FastAPI**: Modern async REST API framework

## Architecture

- **Framework**: FastAPI + Uvicorn
- **Extraction**: PyMuPDF + EasyOCR
- **QA Model**: DistilBERT (transformers library)
- **Storage**: In-memory (development), easily upgradeable to database
- **Containerization**: Docker + Docker Compose ready

## Performance Notes

- Model loading: 5-10 seconds on first request
- Context limited to 2000 characters for optimal performance
- GPU support available (CPU by default)
- In-memory storage suitable for development/testing

## Files to Review

- **main.py** - Application entry point and middleware setup
- **README.md** - User documentation and API examples
- **DEVELOPER_GUIDE.md** - Detailed architecture and production guidelines
- **app/services/extractor.py** - Text extraction implementation
- **app/services/qa.py** - QA engine using DistilBERT
- **app/routers/documents.py** - Upload and session management endpoints
- **app/routers/qa.py** - Question-answering endpoints
