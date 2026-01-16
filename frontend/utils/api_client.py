"""
API client for communicating with the Document QA API.
"""
import streamlit as st
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
from typing import Optional, List
from config import (
    API_BASE_URL, 
    API_V1,
    API_HEALTH_TIMEOUT,
    API_UPLOAD_TIMEOUT,
    API_QUESTION_TIMEOUT,
    API_SESSION_TIMEOUT
)
from utils.auth import get_headers


def check_api_health():
    """Check if API is available"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=API_HEALTH_TIMEOUT)
        return response.status_code == 200
    except (RequestException, Timeout, ConnectionError):
        return False


def upload_documents(files, session_id=None):
    """
    Upload documents to API
    
    Args:
        files: List of files to upload
        session_id: Optional session ID to add documents to existing session
    
    Returns:
        API response JSON or None on error
    """
    try:
        upload_files = [("files", file) for file in files]
        params = {}
        if session_id:
            params['session_id'] = session_id
        
        response = requests.post(
            f"{API_V1}/upload",
            files=upload_files,
            params=params,
            headers=get_headers(),
            timeout=API_UPLOAD_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.text}")
            return None
    except (RequestException, Timeout, ConnectionError) as e:
        st.error(f"Error uploading documents: {str(e)}")
        return None


def ask_question(session_id: str, question: str, detailed: bool = False):
    """
    Ask a question about documents
    
    Args:
        session_id: Session ID
        question: Question to ask
        detailed: Whether to get detailed answers from all documents
    
    Returns:
        API response JSON or None on error
    """
    try:
        endpoint = "ask-detailed" if detailed else "ask"
        payload = {
            "session_id": session_id,
            "question": question
        }
        
        response = requests.post(
            f"{API_V1}/{endpoint}",
            json=payload,
            headers=get_headers(),
            timeout=API_QUESTION_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.text}")
            return None
    except (RequestException, Timeout, ConnectionError) as e:
        st.error(f"Error asking question: {str(e)}")
        return None


def get_session_info(session_id: str):
    """
    Get session information
    
    Args:
        session_id: Session ID
    
    Returns:
        Session information JSON or None on error
    """
    try:
        response = requests.get(
            f"{API_V1}/session/{session_id}",
            headers=get_headers(),
            timeout=API_SESSION_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except (RequestException, Timeout, ConnectionError) as e:
        st.error(f"Error retrieving session: {str(e)}")
        return None


def delete_session(session_id: str):
    """
    Delete a session
    
    Args:
        session_id: Session ID to delete
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.delete(
            f"{API_V1}/session/{session_id}",
            headers=get_headers(),
            timeout=API_SESSION_TIMEOUT
        )
        return response.status_code == 200
    except (RequestException, Timeout, ConnectionError) as e:
        st.error(f"Error deleting session: {str(e)}")
        return False


def get_sessions_list():
    """
    Get list of active session IDs from the API
    
    Returns:
        List[str]: session IDs or empty list on error
    """
    try:
        resp = requests.get(
            f"{API_V1}/sessions/count",
            headers=get_headers(),
            timeout=API_SESSION_TIMEOUT
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("sessions", []) or []
        return []
    except (RequestException, Timeout, ConnectionError):
        return []

