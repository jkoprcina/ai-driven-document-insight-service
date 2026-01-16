"""
Retrieval-Augmented Generation (RAG) service using embeddings and FAISS.
Provides semantic search and context retrieval for improved QA.
"""
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import logging
import os
import shutil

logger = logging.getLogger(__name__)

class RAGEngine:
    """Retrieval-Augmented Generation engine using FAISS and embeddings."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_dir: str = "./rag_indices",
        cache_manager=None
    ):
        """
        Initialize RAG engine.
        
        Args:
            model_name: Sentence transformer model name
            index_dir: Directory to store FAISS indices
            cache_manager: Optional CacheManager for caching embeddings
        """
        self.model = SentenceTransformer(model_name)
        self.index_dir = index_dir
        self.cache_manager = cache_manager
        self.indices = {}  # {session_id: {"index": faiss_index, "texts": [texts], "metadata": {}}}
        
        os.makedirs(index_dir, exist_ok=True)
    
    def create_session_index(self, session_id: str, documents: Dict[str, str]) -> bool:
        """
        Create FAISS index for documents in a session.
        
        Args:
            session_id: Session ID
            documents: Dictionary of {doc_id: doc_text}
            
        Returns:
            Success status
        """
        try:
            # Split documents into chunks
            chunks = []
            chunk_metadata = []
            chunk_size = 500
            chunk_overlap = 50
            
            for doc_id, text in documents.items():
                # Split into overlapping chunks
                for i in range(0, len(text), chunk_size - chunk_overlap):
                    chunk = text[i:i + chunk_size]
                    if len(chunk.strip()) > 50:  # Skip very small chunks
                        chunks.append(chunk)
                        chunk_metadata.append({
                            "doc_id": doc_id,
                            "start": i,
                            "end": min(i + chunk_size, len(text))
                        })
            
            if not chunks:
                logger.warning(f"No valid chunks found for session {session_id}")
                return False
            
            # Generate embeddings
            embeddings = self.model.encode(chunks, convert_to_numpy=True)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings.astype('float32'))
            
            # Store in memory
            self.indices[session_id] = {
                "index": index,
                "embeddings": embeddings,
                "texts": chunks,
                "metadata": chunk_metadata,
                "documents": documents
            }
            
            # Cache embeddings if cache manager available
            if self.cache_manager:
                embeddings_dict = {
                    "chunks": chunks,
                    "metadata": chunk_metadata,
                    "embeddings": embeddings.tolist()  # Convert numpy to list for serialization
                }
                self.cache_manager.cache_embeddings(session_id, embeddings_dict)
                logger.info(f"Cached embeddings for session {session_id}")
            
            logger.info(f"Created RAG index for session {session_id} with {len(chunks)} chunks")
            return True
        
        except Exception as e:
            logger.error(f"Error creating session index: {e}")
            return False
    
    def retrieve_relevant_chunks(
        self,
        session_id: str,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Retrieve most relevant chunks for a query.
        
        Args:
            session_id: Session ID
            query: Query text
            top_k: Number of top chunks to retrieve
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            if session_id not in self.indices:
                logger.warning(f"No index found for session {session_id}")
                return []
            
            # Encode query
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            
            # Search
            index = self.indices[session_id]["index"]
            distances, indices = index.search(query_embedding, min(top_k, index.ntotal))
            
            # Retrieve chunks
            results = []
            texts = self.indices[session_id]["texts"]
            metadata = self.indices[session_id]["metadata"]
            
            for idx, (distance, chunk_idx) in enumerate(zip(distances[0], indices[0])):
                if chunk_idx < 0:  # Invalid index
                    continue
                
                results.append({
                    "rank": idx + 1,
                    "chunk": texts[chunk_idx],
                    "distance": float(distance),
                    "similarity": 1 / (1 + float(distance)),  # Convert distance to similarity
                    "metadata": metadata[chunk_idx]
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            return []
    
    def augment_context(
        self,
        session_id: str,
        question: str,
        max_context_length: int = 4000
    ) -> str:
        """
        Augment context for QA by retrieving relevant chunks.
        Uses semantic search to find relevant sections, sorted in document order.
        
        Args:
            session_id: Session ID
            question: Question text
            max_context_length: Maximum length of augmented context (default 4000 chars)
            
        Returns:
            Augmented context string with chunks in natural document order
        """
        try:
            # Retrieve relevant chunks ranked by semantic similarity
            chunks = self.retrieve_relevant_chunks(session_id, question, top_k=10)
            
            if not chunks:
                # Fallback to all documents if no chunks found
                docs = self.indices[session_id]["documents"]
                context = "\n\n".join(docs.values())
            else:
                # Sort chunks by original document position for natural reading flow
                chunks_sorted = sorted(chunks, key=lambda x: x["metadata"]["start"])
                # Combine chunks in document order
                context = "\n\n".join([chunk["chunk"] for chunk in chunks_sorted])
            
            # Truncate if needed
            if len(context) > max_context_length:
                context = context[:max_context_length]
            
            return context
        
        except Exception as e:
            logger.error(f"Error augmenting context: {e}")
            return ""
    
    def clear_session_index(self, session_id: str) -> bool:
        """Clear index for a session."""
        if session_id in self.indices:
            del self.indices[session_id]
            logger.info(f"Cleared index for session {session_id}")
            return True
        return False
    
    def get_index_stats(self, session_id: str) -> Optional[Dict]:
        """Get statistics about a session's index."""
        if session_id not in self.indices:
            return None
        
        idx_data = self.indices[session_id]
        return {
            "session_id": session_id,
            "num_chunks": idx_data["index"].ntotal,
            "num_documents": len(idx_data["documents"]),
            "embedding_dimension": idx_data["embeddings"].shape[1],
            "embedding_model": self.model.get_sentence_embedding_dimension()
        }
    
    def delete_session(self, session_id: str) -> None:
        """
        Delete RAG index and data for a session to free memory.
        Called when session is deleted.
        """
        try:
            # Delete from memory
            if session_id in self.indices:
                del self.indices[session_id]
            
            # Delete from disk
            index_path = f"./rag_indices/{session_id}"
            if os.path.exists(index_path):
                shutil.rmtree(index_path, ignore_errors=True)
                logger.info(f"Deleted RAG index for session {session_id}")
        except Exception as e:
            logger.error(f"Error deleting RAG session {session_id}: {e}")
