"""
Authentication utilities for the Streamlit application.
"""
import streamlit as st
import requests
from config import API_V1, API_AUTH_TIMEOUT


def get_auth_token():
    """Get JWT token for API authentication"""
    if st.session_state.auth_token:
        return st.session_state.auth_token
    
    try:
        response = requests.post(
            f"{API_V1}/token",
            timeout=API_AUTH_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            st.session_state.auth_token = token
            return token
        else:
            st.error(f"Failed to get authentication token: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error getting authentication token: {str(e)}")
        return None


def get_headers():
    """Get request headers with authorization token"""
    headers = {}
    token = get_auth_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "documents" not in st.session_state:
        st.session_state.documents = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "api_available" not in st.session_state:
        st.session_state.api_available = True
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None
