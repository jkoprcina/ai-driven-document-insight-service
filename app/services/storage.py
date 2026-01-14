"""
Session storage service for managing uploaded documents.
Stores documents in memory with session-based organization.
"""
from typing import Dict, List, Optional
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SessionStorage:
    """In-memory storage for document sessions."""
    
    def __init__(self):
        """Initialize storage."""
        self.sessions: Dict[str, dict] = {}
    
    def create_session(self) -> str:
        """
        Create a new session.
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "documents": {}
        }
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def add_document(self, session_id: str, doc_id: str, filename: str, text: str) -> bool:
        """
        Add document to session.
        
        Args:
            session_id: Session ID
            doc_id: Document ID
            filename: Original filename
            text: Extracted text
            
        Returns:
            Success status
        """
        if session_id not in self.sessions:
            logger.warning(f"Session not found: {session_id}")
            return False
        
        self.sessions[session_id]["documents"][doc_id] = {
            "filename": filename,
            "text": text,
            "added_at": datetime.now(),
            "size": len(text)
        }
        logger.info(f"Added document {doc_id} to session {session_id}")
        return True
    
    def get_documents(self, session_id: str) -> Optional[Dict]:
        """
        Get all documents in session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary of documents or None
        """
        if session_id not in self.sessions:
            return None
        return self.sessions[session_id]["documents"]
    
    def get_document_text(self, session_id: str, doc_id: str) -> Optional[str]:
        """
        Get text for specific document.
        
        Args:
            session_id: Session ID
            doc_id: Document ID
            
        Returns:
            Document text or None
        """
        docs = self.get_documents(session_id)
        if not docs or doc_id not in docs:
            return None
        return docs[doc_id]["text"]
    
    def get_all_texts(self, session_id: str) -> Optional[Dict[str, str]]:
        """
        Get all document texts in session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary of {doc_id: text} or None
        """
        docs = self.get_documents(session_id)
        if not docs:
            return None
        return {doc_id: doc["text"] for doc_id, doc in docs.items()}
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        return session_id in self.sessions
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session: {session_id}")
            return True
        return False
