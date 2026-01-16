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
  "doc_id": null,
  "highlight_entities": true,
  "max_context_length": 4000
}
```

**Response** (200 OK):
```json
{
  "question": "What is the total contract amount?",
  "answer": "$500,000 per year for all services",
  "confidence": 0.92,
  "source_doc": "contract.pdf",
  "entities": [
    {
      "text": "$500,000",
      "label": "MONEY",
      "start": 0,
      "end": 8,
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
  "question": "What is the payment schedule?",
  "highlight_entities": true,
  "max_context_length": 4000
}
```

**Response** (200 OK):
```json
{
  "question": "What is the payment schedule?",
  "answers": [
    {
      "doc_id": "doc-1-uuid",
      "answer": "Payments: $250,000 at signing, $250,000 at completion",
      "confidence": 0.89,
      "entities": [
        {
          "text": "$250,000",
          "label": "MONEY",
          "start": 0,
          "end": 8,
          "label_description": "Monetary amount"
        }
      ]
    },
    {
      "doc_id": "doc-2-uuid",
      "answer": "Monthly installments of $5,000 for 24 months",
      "confidence": 0.76,
      "entities": []
    }
  ],
  "best_answer": {
    "doc_id": "doc-1-uuid",
    "answer": "Payments: $250,000 at signing, $250,000 at completion",
    "confidence": 0.89,
    "entities": [
      {
        "text": "$250,000",
        "label": "MONEY",
        "start": 0,
        "end": 8,
        "label_description": "Monetary amount"
      }
    ]
  }
}
```

**Parameters**:
- `session_id` (required): UUID of session
- `question` (required): Question string (max 1000 chars)
- `highlight_entities` (optional): Enable entity highlighting (default: true)
- `max_context_length` (optional): Max context length in chars (default: 4000)

**Errors**:
- `400`: No documents in session
- `401`: Missing/invalid token
- `404`: Session not found
- `429`: Rate limit exceeded
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

**Per-endpoint limits** (all rates per IP address):
- `POST /token`: 5 requests/minute
- `POST /session`: 20 requests/minute
- `POST /upload`: 10 requests/minute
- `GET /session/{id}`: 30 requests/minute
- `DELETE /session/{id}`: 20 requests/minute
- `POST /ask`: 30 requests/minute
- `POST /ask-detailed`: 30 requests/minute

**Response Headers**:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 29
X-RateLimit-Reset: 1705319460
```

**Rate Limited Response** (429):
```json
{
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
