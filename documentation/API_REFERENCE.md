# Document QA API - Complete Reference

## API Version

- **Current Version**: v1
- **Base URL**: `http://localhost:8000`
- **Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

---

## Authentication

### Get Token (Development Only)

**Endpoint**: `POST /api/v1/token`

**Note**: ⚠️ This endpoint is for **testing purposes only**. In production, implement proper user authentication with username/password validation against a database.

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/token
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Usage**: Add header to all protected endpoint requests:
```
Authorization: Bearer <access_token>
```

**Rate Limit**: 5 requests/minute per IP

---

## Document Management

### Create Session

**Endpoint**: `POST /api/v1/session`

**Headers**:
```
Authorization: Bearer <token>
```

**Request**:
```bash
curl -X POST http://localhost:8000/api/v1/session \
  -H "Authorization: Bearer $TOKEN"
```

**Response** (200 OK):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-01-16T10:30:00Z"
}
```

**Rate Limit**: 20 requests/minute per IP

---

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
      "status": "success",
      "text_length": 5234,
      "pages": 3
    },
    {
      "filename": "invoice.png",
      "status": "success",
      "text_length": 1200
    }
  ],
  "message": "2 documents processed successfully"
}
```

**Supported Formats**:
- PDF: `.pdf`
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`

**Limits**:
- Max file size: 50MB (configurable)
- Max files per upload: 10
- Recommended: Keep total context under 100,000 characters for best performance

**Rate Limit**: 10 requests/minute per IP

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
  "created_at": "2026-01-16T10:30:00Z",
  "documents": [
    {
      "filename": "contract.pdf",
      "text": "Full extracted text content here...",
      "entities": [
        {
          "text": "John Smith",
          "label": "PERSON",
          "start": 0,
          "end": 10
        }
      ]
    }
  ],
  "document_count": 2
}
```

**Rate Limit**: 30 requests/minute per IP

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

**Response** (200 OK):
```json
{
  "message": "Session

### Ask Question (Best Answer)

**Endpoint**: `POST /api/v1/ask`

**Description**: Returns the single best answer from all documents in a session, with optional NER entity highlighting.

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
  "highlight_entities": true,
  "max_context_length": 2000
}
```

**Response** (200 OK):
```json
{
  "question": "What is the total contract amount?",
  "answer": "$500,000 per year for all services",
  "confidence": 0.92,
  "source_doc": "contract.pdf",
  "context": "The agreement specifies $500,000 per year for all services including...",
  "entities": [
    {
      "text": "$500,000",
      "label": "MONEY",
      "start": 0,
      "end": 8
    }
  ]
}
```

**Parameters**:
- `session_id` (required): UUID of session
- `question` (required): Question string (max 1000 chars, default: no limit)
- `highlight_entities` (optional): Enable NER entity highlighting (default: false)
- `max_context_length` (optional): Max context chars to consider (default: 2000)

**Rate Limit**: 30 requests/minute per IP
      "label_description": "Monetary amount"
    }
  ]
}
```

**Parameters**:
- `session_id` (required): UUID of session
- `question` (required): Question string (max 1000 chars)
- `doc_id` (optional): Specific document UUID (if null, searches all documents)
- `highlight_entities` (optional): Enable entity highlighting (default: true)
- `max_context_length` (optional): Max context length in chars (default: 4000)

**Errors**:
- `400`: Session not found or no documents in session
- `401`: Missing/invalid token
- `404`: Session not found
- `429`: Rate limit exceeded

---

### Ask Question (All Documents)

**Description**: Returns answers from **each document** in the session separately, allowing you to compare answers across documents.

**Headers**:
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Request**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "What is the payment schedule?",
  "highlight_entities": true,
  "max_context_length": 2000
}
```

**Response** (200 OK):
```json
{
  "question": "What is the payment schedule?",
  "answers": [
    {
      "document": "contract.pdf",
      "answer": "Payments: $250,000 at signing, $250,000 at completion",
      "confidence": 0.89,
      "context": "Section 5: Payment Terms. Payments: $250,000 at signing...",
      "entities": [
        {
          "text": "$250,000",
          "label": "MONEY",
          "start": 0,
          "end": 8
        }
      ]
    },
    {
      "document": "invoice.png",
      "answer": "Monthly installments of $5,000 for 24 months",
      "confidence": 0.76,
      "context": "Installment plan: Monthly installments of $5,000...",
      "entities": [
        {
          "text": "$5,000",
          "label": "MONEY",
          "start": 26,
          "end": 32
        }
      ]
    }
  ],
  "best_answer": {
    "document": "contract.pdf",
    "answer": "Payments: $250,000 at signing, $250,000 at completion",
    "confidence": 0.89
  }
}
```

**Parameters**:
- `session_id` (required): UUID of session
- `question` (required): Question string (max 1000 chars, default: no limit)
- `highlight_entities` (optional): Enable NER entity highlighting (default: false)
- `max_context_length` (optional): Max context chars per document (default: 2000)

**Rate Limit**: 30 requests/minute per IP

**Errors**:
- `400`: No documents in session
- `401`: Missing/invalid token
- `404`: Session not foundd or invalid question
- `401`: Missing/invalid token
- `422`: Validation error
- `429`: Rate limit exceeded

---

## Advanced Features (v2)

**Note**: Entity extraction is now integrated into `/ask` and `/ask-detailed` endpoints with optional `highlight_entities` parameter for seamless entity highlighting in QA responses.

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
{Monitoring & Health

### Health Check

**Endpoint**: `GET /health`

**Description**: Basic health check. No authentication required.

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-16T10:30:00Z"
}
```

---

### Prometheus Metrics

**Endpoint**: `GET /metrics`

**Description**: Prometheus-format metrics for monitoring. No authentication required.

**Response** (200 OK):
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/api/v1/ask"} 1523
...
```

---

### Get Sessions List

**Endpoint**: `GET /api/v1/sessions/count`

**Description**: List all active session IDs.

**Headers**:
```
Authorization: Bearer <token>
```

**Response** (200 OK):
```json
{Named Entity Recognition

NER is **integrated into QA endpoints** via the `highlight_entities` parameter. Supported entity types:

| Entity Type | Description | Examples |
|-------------|-------------|----------|
| PERSON | People names | "John Smith", "Dr. Johnson" |
| ORG | Organizations | "Microsoft", "City Council" |
| GPE | Geopolitical entities | "United States", "California" |
| DATE | Dates and times | "January 2026", "next Tuesday" |
| MONEY | Monetary amounts | "$500,000", "€250" |
| PERCENT | Percentages | "15%", "three percent" |
| TIME | Times | "3:00 PM", "midnight" |
| QUANTITY | Measurements | "500 kg", "10 miles" |

**Usage**: Set `"highlight_entities": true` in `/ask` or `/ask-detailed` requests to receive entity annotations in responses.ndpoint | Rate Limit |
|----------|-----------|
| `POST /api/v1/token` | 5 requests/minute |
| `POST /api/v1/session` | 20 requests/minute |
| `POST /api/v1/upload` | 10 requests/minute |
| `GET /api/v1/session/{id}` | 30 requests/minute |
| `DELETE /api/v1/session/{id}` | 20 requests/minute |
| `POST /api/v1/ask` | 30 requests/minute |
| `POST /api/v1/ask-detailed` | 30 requests/minute |
| `GET /api/v1/sessions/count` | 30 requests/minute |
| `GET /api/v1/cache/stats` | 30 requests/minute |
| `GET /api/v1/models/status` | 30 requests/minute |

# Get token
token_resp = requests.post('http://localhost:8000/api/v1/token')
token = token_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Upload documents
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
print(f"Session: {session_id}")

# Ask question with entity highlighting
ask_resp = requests.post(
    'http://localhost:8000/api/v1/ask',
    json={
        'session_id': session_id,
        'question': 'What is the total contract amount?',
        'highlight_entities': True
    },
    headers=headers
)
result = ask_resp.json()
print(f"Answer: {result['answer']}")
print(f"Confidence: {result['confidence']:.2%}")
if result.get('entities'):
    print(f"Entities: {result['entities']}")
```

### JavaScript/Node.js
```javascript
// Get token
const tokenResp = await fetch('http://localhost:8000/api/v1/token', {
  method: 'POST'
});
const {access_token} = await tokenResp.json();
const headers = {Authorization: `Bearer ${access_token}`};

// Upload documents
const formData = new FormData();
formData.append('files', fileInput.files[0]);
const uploadResp = await fetch('http://localhost:8000/api/v1/upload', {
  method: 'POST',
  headers,
  body: formData
});
const {session_id} = await uploadResp.json();

// Ask question
const askResp = await fetch('http://localhost:8000/api/v1/ask', {
  method: 'POST',
  headers: {...headers, 'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id,
    question: 'What is the total amount?',
    highlight_entities: true
  })
});
const result = await askResp.json();
console.log(`Answer: ${result.answer} (${result.confidence})`);
```

### cURL (Bash)
```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/token | jq -r '.access_token')

# Upload documents
UPLOAD_RESP=$(curl -s -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@contract.pdf" \
  -F "files=@invoice.png")
SESSION_ID=$(echo $UPLOAD_RESP | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# Ask question
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"question\": \"What is the total?\",
    \"highlight_entities\": true
  }" | jq .
  "detail": "Rate limit exceeded"
}
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
  -API Changelog

### v1.0 (Current - January 2026)
- ✅ JWT authentication (`/api/v1/token`)
- ✅ Session management (create, get, delete, list)
- ✅ Document upload (PDF via PyMuPDF, Images via EasyOCR)
- ✅ Question answering (DistilBERT transformer)
- ✅ Named Entity Recognition (spaCy, 12+ entity types)
- ✅ RAG semantic search (FAISS + Sentence-BERT embeddings)
- ✅ Redis caching with in-memory fallback
- ✅ Per-endpoint rate limiting (SlowAPI)
- ✅ Prometheus metrics & monitoring
- ✅ Structured JSON logging
- ✅ Streamlit web UI

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **GitHub README**: ../README.md
- **Deployment Guide**: DEPLOYMENT_CHECKLIST.md

---

**Last Updated**: January 16, 2026  
**API Version**: v1.0  
**Status**: Production Ready (with known limitations - see README.md)

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
