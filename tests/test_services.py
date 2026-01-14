"""
Service layer tests
"""
import pytest
from app.services.storage import DocumentStorage


def test_storage_create_session():
    """Test session creation in storage"""
    storage = DocumentStorage()
    session_id = storage.create_session()
    assert session_id is not None
    assert len(session_id) > 0


def test_storage_get_session():
    """Test retrieving session from storage"""
    storage = DocumentStorage()
    session_id = storage.create_session()
    session = storage.get_session(session_id)
    assert session is not None
    assert session["session_id"] == session_id


def test_storage_add_document():
    """Test adding document to session"""
    storage = DocumentStorage()
    session_id = storage.create_session()
    
    doc_id = storage.add_document(
        session_id=session_id,
        filename="test.pdf",
        text="Sample text content"
    )
    
    assert doc_id is not None
    session = storage.get_session(session_id)
    assert len(session["documents"]) == 1


def test_storage_delete_session():
    """Test deleting session"""
    storage = DocumentStorage()
    session_id = storage.create_session()
    
    result = storage.delete_session(session_id)
    assert result is True
    
    session = storage.get_session(session_id)
    assert session is None
