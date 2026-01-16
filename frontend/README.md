# 🎨 Document QA System - Web Interface

Modern, modular Streamlit-based web interface for the Document QA API.

## ✨ Features

### Core Capabilities
- **📤 Drag-and-Drop Upload**: Easy document upload (PDF, PNG, JPG, etc.)
- **💬 Interactive Chat**: Natural language Q&A interface with chat history
- **📊 Document Analysis**: Entity extraction and statistical analysis
- **📄 Document Viewer**: Browse uploaded documents with NER highlighting
- **🔄 Session Management**: Switch between multiple document sessions seamlessly

### Advanced Features
- **Session Switching**: Easy switching between active sessions with dropdown picker
- **Chat History Persistence**: Per-session conversation history automatically saved
- **Entity Highlighting**: Visual highlighting of people, organizations, dates, money, etc.
- **Confidence Scoring**: Real-time confidence indicators for answers
- **JWT Authentication**: Automatic token management
- **Responsive Design**: Clean, professional UI with custom CSS styling

## 🏗️ Architecture

```
frontend/
├── app.py                 # Main Streamlit application entry point
├── config.py              # Configuration (API URL, colors, timeouts)
├── __init__.py           # Package initialization
│
├── components/            # Modular UI components
│   ├── sidebar.py         # Session controls & settings
│   ├── upload_tab.py      # Document upload interface
│   ├── chat_tab.py        # Q&A chat with history
│   ├── documents_tab.py   # Document viewer with NER
│   ├── analysis_tab.py    # Entity analysis dashboard
│   └── __init__.py
│
├── utils/                 # Utility modules
│   ├── api_client.py      # API communication & requests
│   ├── auth.py            # JWT token management
│   ├── formatters.py      # Display formatting & entity styling
│   └── __init__.py
│
└── styles/
    └── custom.css         # Custom CSS for styling
```

## 🚀 Quick Start

### Prerequisites
```bash
# Backend must be running first
python main.py
# Or with Docker:
docker-compose up
```

### Installation & Running

**Option 1: From project root (Recommended)**
```bash
# Install Streamlit dependencies
pip install -r requirements-streamlit.txt

# Run the frontend
streamlit run frontend/app.py
```

**Option 2: Direct run**
```bash
cd frontend
pip install -r ../requirements-streamlit.txt
streamlit run app.py
```

**Access the UI**: http://localhost:8501

### First Time Setup
1. Ensure backend API is running at http://localhost:8000
2. Launch frontend: `streamlit run frontend/app.py`
3. Frontend automatically gets JWT token
4. Upload documents in the **Upload** tab
5. Ask questions in the **Chat** tab

## 📖 User Guide

### 1. Upload Tab
- Click **Browse files** or drag-and-drop documents
- Supported formats: PDF, PNG, JPG, JPEG, BMP, GIF, TIFF
- Multiple files can be uploaded at once
- Automatic text extraction using PyMuPDF (PDF) and EasyOCR (images)
- Documents added to current session

### 2. Chat Tab
- Type your question in natural language
- Press Enter or click **Ask** to submit
- View answer with confidence score
- See source document for the answer
- Entity highlighting shows people, organizations, dates, money, etc.
- **Chat history persists per session** - switch sessions and return to previous conversations

### 3. Documents Tab
- Browse all uploaded documents in current session
- View extracted text
- See entity extraction results
- Filter by document name

### 4. Analysis Tab
- Statistical overview of all documents
- Entity type distribution charts
- Most common entities
- Document metadata

### 5. Sidebar Controls
- **Session Info**: Current session ID displayed
- **Session Picker**: Dropdown to switch between active sessions
- **Paste Session ID**: Alternative way to switch sessions by pasting ID
- **New Session**: Start fresh with new documents
- **Delete Session**: Remove current session and all documents
- **Settings**: Configure API URL and other options

## ⚙️ Configuration

Edit [config.py](config.py) to customize:

```python
# API Configuration
API_BASE_URL = "http://localhost:8000"  # Backend API URL
API_TIMEOUT = 120  # Request timeout in seconds

# UI Configuration
PAGE_TITLE = "Document QA System"
PAGE_ICON = "📄"
LAYOUT = "wide"

# Entity Highlighting Colors
ENTITY_COLORS = {
    "PERSON": "#FF6B6B",
    "ORG": "#4ECDC4",
    "GPE": "#45B7D1",
    "DATE": "#FFA07A",
    "MONEY": "#98D8C8",
    # ... more entity types
}

# Confidence Thresholds
CONFIDENCE_HIGH = 0.7   # Green indicator
CONFIDENCE_MED = 0.4    # Yellow indicator
# Below 0.4: Red indicator
```

## 🛠️ Development Guide

### Adding a New Tab

1. **Create component file**: `components/new_feature_tab.py`
```python
import streamlit as st

def render_new_feature_tab():
    """Render the new feature tab"""
    st.header("🆕 New Feature")
    st.write("Your content here")
```

2. **Export from components**: Add to `components/__init__.py`
```python
from .new_feature_tab import render_new_feature_tab
```

3. **Add tab in main app**: Update `app.py`
```python
from components import render_new_feature_tab

# In main():
tab1, tab2, tab_new = st.tabs(["Upload", "Chat", "New Feature"])
with tab_new:
    render_new_feature_tab()
```

### Adding a New API Endpoint

1. **Add API function**: `utils/api_client.py`
```python
def new_api_function(session_id: str, param: str):
    """Call new API endpoint"""
    token = get_token()
    response = requests.post(
        f"{API_BASE_URL}/api/v1/new-endpoint",
        headers={"Authorization": f"Bearer {token}"},
        json={"session_id": session_id, "param": param}
    )
    return response.json()
```

2. **Export from utils**: Add to `utils/__init__.py`
```python
from .api_client import new_api_function
```

3. **Use in component**
```python
from utils import new_api_function

result = new_api_function(st.session_state.session_id, "value")
```

### Customizing Styles

**Global styles** - Edit `styles/custom.css`:
```css
.custom-class {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
}
```

**Inline styles** - In component:
```python
st.markdown(
    "<div class='custom-class'>Styled content</div>",
    unsafe_allow_html=True
)
```

## 🧩 Component Reference

### Sidebar Component (`sidebar.py`)
- `render_sidebar()`: Main sidebar rendering
- Manages session state and controls
- Handles session switching dropdown
- Provides settings interface

### Upload Tab (`upload_tab.py`)
- `render_upload_tab()`: Document upload interface
- Drag-and-drop file uploader
- Calls `/api/v1/upload` endpoint
- Updates session state with documents

### Chat Tab (`chat_tab.py`)
- `render_chat_tab()`: Q&A chat interface
- Maintains per-session chat history
- Calls `/api/v1/ask` endpoint
- Displays confidence scores and entities

### Documents Tab (`documents_tab.py`)
- `render_documents_tab()`: Document viewer
- Shows extracted text
- Displays entity highlighting
- Fetches from `/api/v1/session/{id}`

### Analysis Tab (`analysis_tab.py`)
- `render_analysis_tab()`: Statistical dashboard
- Entity distribution charts
- Document metadata overview
- Common entity analysis

## 🔧 Utility Modules

### API Client (`api_client.py`)
Functions for backend communication:
- `get_token()`: Get JWT authentication token
- `upload_documents()`: Upload files
- `ask_question()`: Submit Q&A query
- `get_session_info()`: Fetch session details
- `delete_session()`: Remove session
- `get_sessions_list()`: List active sessions

### Authentication (`auth.py`)
- `get_auth_token()`: Retrieve or generate JWT token
- Automatic token caching
- Token refresh logic

### Formatters (`formatters.py`)
Display utilities:
- `display_entities()`: Render entity badges
- `get_confidence_color()`: Color coding for scores
- `format_entity_html()`: HTML formatting for NER
- `truncate_text()`: Text truncation helpers

## ✅ Benefits of Modular Architecture

- **🔧 Maintainability**: Each component is isolated and easy to modify
- **♻️ Reusability**: Components can be reused across different pages/apps
- **🧪 Testability**: Individual modules can be unit tested
- **👥 Collaboration**: Multiple developers can work on different components
- **📈 Scalability**: Easy to add new features without breaking existing code
- **📖 Clarity**: Clear separation of concerns (config, utils, components, styles)
- **🎨 Customization**: Easy to theme and style independently

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Ensure backend API is running: `python main.py` |
| Port 8501 in use | Kill process or change port: `streamlit run frontend/app.py --server.port 8502` |
| Missing dependencies | Install: `pip install -r requirements-streamlit.txt` |
| Token errors | Backend must be running with `/api/v1/token` endpoint |
| Session not found | Session may have been deleted or backend restarted |
| Unicode errors | Use UTF-8 encoding: `$env:PYTHONIOENCODING="utf-8"` (Windows) |

## 📦 Dependencies

Core dependencies (from `requirements-streamlit.txt`):
- `streamlit` - Web UI framework
- `requests` - HTTP client for API calls
- `python-jose` - JWT token handling
- `plotly` - Interactive charts (optional for analysis tab)

## 🔗 Related Documentation

- **[Main README](../README.md)**: Complete project overview
- **[API Reference](../documentation/API_REFERENCE.md)**: Backend API documentation
- **[Deployment Guide](../documentation/DEPLOYMENT_CHECKLIST.md)**: Production deployment

---

**Last Updated**: January 16, 2026  
**Version**: 1.0  
**Status**: Production Ready
