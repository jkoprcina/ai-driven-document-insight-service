"""
Configuration for the Streamlit frontend application.
"""
import streamlit as st

# API Configuration
try:
    API_BASE_URL = st.secrets.get("API_URL", "http://localhost:8000")
except:
    API_BASE_URL = "http://localhost:8000"

API_V1 = f"{API_BASE_URL}/api/v1"

# Page Configuration
PAGE_CONFIG = {
    "page_title": "Document QA System",
    "page_icon": "📄",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Entity color mapping for NER
ENTITY_COLORS = {
    'PERSON': '#FFE5B4',      # Peach
    'ORG': '#B4D7FF',         # Light blue
    'LOCATION': '#B4FFB4',    # Light green
    'DATE': '#FFE5E5',        # Light red
    'MONEY': '#E5D7FF',       # Light purple
    'PERCENT': '#FFFFE5',     # Light yellow
    'FACILITY': '#D7FFFF',    # Cyan
}

# Confidence thresholds
CONFIDENCE_HIGH = 0.80
CONFIDENCE_MEDIUM = 0.60

# Timeouts (seconds)
API_HEALTH_TIMEOUT = 2
API_AUTH_TIMEOUT = 5
API_UPLOAD_TIMEOUT = 120
API_QUESTION_TIMEOUT = 60
API_SESSION_TIMEOUT = 30
