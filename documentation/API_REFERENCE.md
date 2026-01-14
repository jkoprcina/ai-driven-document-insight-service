# Document QA API - Complete Reference

## API Versions

- **v1**: Original endpoints (backward compatible)
- **v2**: Enhanced endpoints with auth, monitoring, NER
- **Base URL**: `http://localhost:8000`

---

## Authentication

### Get Token (Required for v1/v2 endpoints)

**Endpoint**: `POST /api/v2/login`

**Request**:
```json
{
  "username": "testuser",
  "password": "secret"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Usage**: Add header to requests:
```
Authorization: Bearer <access_token>
```

**Errors**:
- `401`: Invalid credentials
- `422`: Missing username/password

---

## Document Management (v1)

### Upload Documents

**Endpoint**: `POST /api/v1/upload`

**Headers**:
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@contract.pdf" \
  -F "files=@invoice.png"
```

**Response** (200 OK):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "documents": [
    {
      "filename": "contract.pdf",
      "type": "application/pdf",
      "text_length": 5234,
      "pages": 3,
      "extracted_at": "2024-01-15T10:30:00Z"
    },
    {
      "filename": "invoice.png",
      "type": "image/png",
      "text_length": 1200,
      "extracted_at": "2024-01-15T10:30:05Z"
    }
  ]
}
```

**Supported Formats**:
- PDF: `.pdf`
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`

**Limits**:
- Max file size: 50MB
- Max files per upload: 10
- Max total session size: 500MB

**Errors**:
- `400`: Invalid file format or too large
- `401`: Missing/invalid token
- `422`: Validation error
- `429`: Rate limit exceeded

---

### Get Session Info

**Endpoint**: `GET /api/v1/session/{session_id}`

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```bash
curl http://localhost:8000/api/v1/session/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2024-01-15T10:30:00Z",
  "documents": [
    {
      "filename": "contract.pdf",
      "type": "application/pdf",
      "text_length": 5234
    }
  ],
  "total_text_length": 6434,
  "document_count": 2
}
```

**Errors**:
- `401`: Missing/invalid token
- `404`: Session not found

---

### Delete Session

**Endpoint**: `DELETE /api/v1/session/{session_id}`

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```bash
curl -X DELETE http://localhost:8000/api/v1/session/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (204 No Content):
```
(empty)
```

**Errors**:
- `401`: Missing/invalid token
- `404`: Session not found

---

## Question Answering (v1)

### Ask Question (Single Best Answer)

**Endpoint**: `POST /api/v1/ask`

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "What is the total contract amount?",
  "top_k": 1,
  "confidence_threshold": 0.5
}
```

**Response** (200 OK):
```json
{
  "question": "What is the total contract amount?",
  "answer": "$500,000 per year",
  "confidence": 0.92,
  "document": "contract.pdf",
  "context": "The contract is valued at $500,000 per year and covers all services...",
  "processing_time_ms": 245
}
```

**Parameters**:
- `session_id` (required): UUID of session
- `question` (required): Question string (max 500 chars)
- `top_k` (optional): Number of answers to consider (default: 1)
- `confidence_threshold` (optional): Min confidence (0-1, default: 0.5)

**Errors**:
- `400`: Session not found or invalid question
- `401`: Missing/invalid token
- `422`: Validation error
- `429`: Rate limit exceeded

---

### Ask Question (All Documents)

**Endpoint**: `POST /api/v1/ask-detailed`

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "What are the payment terms?"
}
```

**Response** (200 OK):
```json
{
  "question": "What are the payment terms?",
  "answers": [
    {
      "document": "contract.pdf",
      "answer": "Payment due within 30 days of invoice",
      "confidence": 0.87,
      "context": "Payment terms: Net 30. All invoices due..."
    },
    {
      "document": "invoice.png",
      "answer": "Due date: February 15, 2024",
      "confidence": 0.79,
      "context": "Invoice #2024-001. Due date: February 15..."
    }
  ],
  "processing_time_ms": 512
}
```

**Parameters**:
- `session_id` (required): UUID of session
- `question` (required): Question string (max 500 chars)

**Errors**:
- `400`: Session not found or invalid question
- `401`: Missing/invalid token
- `422`: Validation error
- `429`: Rate limit exceeded

---

## Advanced Features (v2)

### NER - Named Entity Recognition

**Endpoint**: `POST /api/v2/extract-entities`

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "output_format": "dict"
}
```

**Response** (200 OK) - Format: `dict`:
```json
{
  "entities": {
    "PERSON": ["John Smith", "Jane Doe"],
    "ORG": ["Acme Corp", "Tech Industries"],
    "GPE": ["New York", "California"],
    "DATE": ["January 15, 2024"],
    "MONEY": ["$500,000", "$1.2M"]
  },
  "document_count": 2,
  "total_entities": 15
}
```

**Response** - Format: `html`:
```json
{
  "html": "<p>Contract with <span class=\"entity person\">John Smith</span> for <span class=\"entity money\">$500,000</span>...</p>",
  "document_count": 2
}
```

**Response** - Format: `markdown`:
```json
{
  "markdown": "Contract with **PERSON[John Smith]** for **MONEY[$500,000]**...",
  "document_count": 2
}
```

**Parameters**:
- `session_id` (required): UUID of session
- `output_format` (optional): `dict`, `html`, or `markdown` (default: `dict`)

**Entity Types**:
- `PERSON`: People names
- `ORG`: Organizations
- `GPE`: Geopolitical entities
- `LOC`: Locations
- `DATE`: Dates
- `TIME`: Times
- `MONEY`: Monetary amounts
- `PERCENT`: Percentages
- `FACILITY`: Facilities
- `PRODUCT`: Products
- `EVENT`: Events
- `LAW`: Laws

**Errors**:
- `404`: Session not found
- `401`: Missing/invalid token

---

### RAG - Semantic Search

**Endpoint**: `POST /api/v2/semantic-search`

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "payment schedule",
  "top_k": 3
}
```

**Response** (200 OK):
```json
{
  "query": "payment schedule",
  "results": [
    {
      "chunk": "The payment schedule is as follows: $250,000 due on signing, $250,000 due upon completion.",
      "similarity_score": 0.92,
      "document": "contract.pdf",
      "chunk_id": 5
    },
    {
      "chunk": "Monthly payments of $5,000 are due on the first of each month for 24 months.",
      "similarity_score": 0.88,
      "document": "invoice.png",
      "chunk_id": 12
    }
  ],
  "processing_time_ms": 127
}
```

**Parameters**:
- `session_id` (required): UUID of session
- `query` (required): Search query (max 500 chars)
- `top_k` (optional): Number of results (default: 3, max: 10)

**Errors**:
- `404`: Session not found
- `401`: Missing/invalid token

---

## Health & Monitoring (v2)

### Health Check

**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Detailed Health

**Endpoint**: `GET /api/v2/health/detailed`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "api": "operational",
    "extractor": "operational",
    "qa_model": "operational",
    "ner_model": "operational",
    "embedding_model": "operational",
    "cache": "operational",
    "redis": "fallback_in_memory"
  },
  "uptime_seconds": 3600,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

### Cache Statistics

**Endpoint**: `GET /api/v2/cache/stats`

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "cache_type": "redis_with_fallback",
  "redis_available": false,
  "total_items": 127,
  "embedding_cache_size": 45,
  "qa_cache_size": 82,
  "hit_rate": 0.67,
  "memory_mb": 12.3,
  "ttl_seconds": 3600
}
```

---

### Model Status

**Endpoint**: `GET /api/v2/models/status`

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "models": {
    "qa": {
      "name": "distilbert-base-cased-distilled-squad",
      "status": "loaded",
      "inference_time_ms": 245,
      "last_used": "2024-01-15T10:29:50Z"
    },
    "ner": {
      "name": "en_core_web_sm",
      "status": "loaded",
      "inference_time_ms": 127,
      "last_used": "2024-01-15T10:28:30Z"
    },
    "embedding": {
      "name": "all-MiniLM-L6-v2",
      "status": "loaded",
      "inference_time_ms": 95,
      "last_used": "2024-01-15T10:29:00Z"
    }
  },
  "gpu_available": false,
  "active_sessions": 3
}
```

---

### Prometheus Metrics

**Endpoint**: `GET /metrics`

**Response** (200 OK):
```
# HELP api_requests_total Total API requests
# TYPE api_requests_total counter
api_requests_total{endpoint="/api/v1/ask",method="POST",status="200"} 156

# HELP api_request_duration_seconds Request latency
# TYPE api_request_duration_seconds histogram
api_request_duration_seconds_bucket{endpoint="/api/v1/ask",le="0.1"} 45
api_request_duration_seconds_bucket{endpoint="/api/v1/ask",le="0.5"} 140
api_request_duration_seconds_bucket{endpoint="/api/v1/ask",le="1.0"} 154

# HELP model_inference_time_seconds Model inference latency
# TYPE model_inference_time_seconds histogram
model_inference_time_seconds_bucket{model="qa",le="0.1"} 10
model_inference_time_seconds_bucket{model="qa",le="0.5"} 120

# HELP active_sessions_total Number of active sessions
# TYPE active_sessions_total gauge
active_sessions_total 3

# HELP cache_items_total Number of cached items
# TYPE cache_items_total gauge
cache_items_total 127
```

---

## Session Count

**Endpoint**: `GET /api/v2/sessions/count`

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{
  "active_sessions": 3,
  "total_documents": 7,
  "total_text_size_mb": 45.2,
  "average_documents_per_session": 2.3,
  "oldest_session_age_hours": 24
}
```

---

## Error Responses

All endpoints return standardized error responses:

### 400 - Bad Request
```json
{
  "detail": "Invalid session ID format",
  "error_code": "INVALID_INPUT",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 401 - Unauthorized
```json
{
  "detail": "Missing or invalid authentication token",
  "error_code": "AUTH_REQUIRED",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 404 - Not Found
```json
{
  "detail": "Session not found",
  "error_code": "NOT_FOUND",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 429 - Rate Limited
```json
{
  "detail": "Rate limit exceeded. Max 100 requests per 60 seconds",
  "error_code": "RATE_LIMITED",
  "retry_after_seconds": 30,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 500 - Server Error
```json
{
  "detail": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Rate Limiting

**Limits**:
- Authenticated users: 100 requests / 60 seconds
- Unauthenticated: 10 requests / 60 seconds

**Response Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705319400
```

---

## Pagination & Filtering

### Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### Filtering
```bash
GET /api/v1/documents?status=active&created_after=2024-01-01&sort=-created_at
```

---

## Code Examples

### Python
```python
import requests

token_resp = requests.post(
    'http://localhost:8000/api/v2/login',
    json={'username': 'testuser', 'password': 'secret'}
)
token = token_resp.json()['access_token']

headers = {'Authorization': f'Bearer {token}'}

# Upload
upload_resp = requests.post(
    'http://localhost:8000/api/v1/upload',
    files={'files': open('contract.pdf', 'rb')},
    headers=headers
)
session_id = upload_resp.json()['session_id']

# Ask
ask_resp = requests.post(
    'http://localhost:8000/api/v1/ask',
    json={'session_id': session_id, 'question': 'What is the amount?'},
    headers=headers
)
print(ask_resp.json())
```

### JavaScript
```javascript
// Get token
const tokenResp = await fetch('http://localhost:8000/api/v2/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'testuser', password: 'secret'})
});
const {access_token} = await tokenResp.json();
const headers = {Authorization: `Bearer ${access_token}`};

// Upload
const formData = new FormData();
formData.append('files', file);
const uploadResp = await fetch('http://localhost:8000/api/v1/upload', {
  method: 'POST',
  headers,
  body: formData
});
const {session_id} = await uploadResp.json();

// Ask
const askResp = await fetch('http://localhost:8000/api/v1/ask', {
  method: 'POST',
  headers: {...headers, 'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id,
    question: 'What is the total amount?'
  })
});
console.log(await askResp.json());
```

### cURL
```bash
# Token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v2/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"secret"}' \
  | jq -r '.access_token')

# Upload
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@contract.pdf")
SESSION_ID=$(echo $RESPONSE | jq -r '.session_id')

# Ask
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$SESSION_ID\",\"question\":\"What is the total?\"}"
```

---

## Changelog

### v2.0.0 (Current)
- ✅ NER integration with spaCy
- ✅ RAG with FAISS embeddings
- ✅ Redis caching with fallback
- ✅ JWT authentication
- ✅ Rate limiting
- ✅ Prometheus monitoring
- ✅ Structured logging

### v1.0.0
- ✅ Document upload (PDF/Images)
- ✅ Text extraction (PyMuPDF + EasyOCR)
- ✅ Question answering (DistilBERT)
- ✅ Session management

---

## API Documentation

**Interactive Docs**: http://localhost:8000/api/docs (Swagger UI)
**ReDoc**: http://localhost:8000/api/redoc

---

**Last Updated**: 2024-01-15
**API Version**: 2.0.0
**Status**: Production Ready
