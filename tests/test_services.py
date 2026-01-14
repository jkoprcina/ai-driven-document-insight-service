"""
Service layer tests
"""
import pytest
from app.services.storage import SessionStorage


class TestSessionStorage:
    """Test SessionStorage service"""
    
    def test_create_session(self):
        """Test session creation"""
        storage = SessionStorage()
        session_id = storage.create_session()
        assert session_id is not None
        assert len(session_id) > 0
        assert session_id in storage.sessions

    def test_get_session(self):
        """Test retrieving session"""
        storage = SessionStorage()
        session_id = storage.create_session()
        session = storage.sessions.get(session_id)
        assert session is not None
        assert "documents" in session
        assert "created_at" in session

    def test_add_document(self):
        """Test adding document to session"""
        storage = SessionStorage()
        session_id = storage.create_session()
        
        result = storage.add_document(
            session_id=session_id,
            doc_id="doc1",
            filename="test.pdf",
            text="Sample text content"
        )
        
        assert result is True
        session = storage.sessions[session_id]
        assert "doc1" in session["documents"]

    def test_add_document_invalid_session(self):
        """Test adding document to non-existent session"""
        storage = SessionStorage()
        
        result = storage.add_document(
            session_id="invalid",
            doc_id="doc1",
            filename="test.pdf",
            text="Sample text content"
        )
        
        assert result is False
