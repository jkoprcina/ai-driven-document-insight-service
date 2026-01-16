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
        # Verify NER status is initialized to "pending"
        assert session["documents"]["doc1"]["ner_status"] == "pending"
        assert session["documents"]["doc1"]["entities"] is None

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

    def test_set_ner_status(self):
        """Test setting NER status for a document"""
        storage = SessionStorage()
        session_id = storage.create_session()
        storage.add_document(session_id, "doc1", "test.pdf", "text")
        
        # Test setting to processing
        result = storage.set_ner_status(session_id, "doc1", "processing")
        assert result is True
        assert storage.get_ner_status(session_id, "doc1") == "processing"
        
        # Test setting to completed
        result = storage.set_ner_status(session_id, "doc1", "completed")
        assert result is True
        assert storage.get_ner_status(session_id, "doc1") == "completed"
        
        # Test setting to failed
        result = storage.set_ner_status(session_id, "doc1", "failed")
        assert result is True
        assert storage.get_ner_status(session_id, "doc1") == "failed"

    def test_set_entities(self):
        """Test storing extracted entities"""
        storage = SessionStorage()
        session_id = storage.create_session()
        storage.add_document(session_id, "doc1", "test.pdf", "text")
        
        entities = {
            "text": "John Smith works at Acme Inc.",
            "entities": [
                {"text": "John Smith", "label": "PERSON", "start": 0, "end": 10},
                {"text": "Acme Inc.", "label": "ORG", "start": 20, "end": 29}
            ]
        }
        
        result = storage.set_entities(session_id, "doc1", entities)
        assert result is True
        
        # Verify entities are stored
        doc = storage.sessions[session_id]["documents"]["doc1"]
        assert doc["entities"] == entities
        # Verify status is set to completed
        assert doc["ner_status"] == "completed"

    def test_get_documents(self):
        """Test retrieving all documents from session"""
        storage = SessionStorage()
        session_id = storage.create_session()
        storage.add_document(session_id, "doc1", "test1.pdf", "text1")
        storage.add_document(session_id, "doc2", "test2.pdf", "text2")
        
        docs = storage.get_documents(session_id)
        assert docs is not None
        assert len(docs) == 2
        assert "doc1" in docs
        assert "doc2" in docs

    def test_get_all_texts(self):
        """Test retrieving all document texts"""
        storage = SessionStorage()
        session_id = storage.create_session()
        storage.add_document(session_id, "doc1", "test1.pdf", "content1")
        storage.add_document(session_id, "doc2", "test2.pdf", "content2")
        
        texts = storage.get_all_texts(session_id)
        assert texts is not None
        assert texts["doc1"] == "content1"
        assert texts["doc2"] == "content2"
