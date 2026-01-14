"""
Question-Answering service using DistilBERT.
Uses transformer-based QA model for extractive question answering.
"""
from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class QAEngine:
    """Question-Answering engine using DistilBERT."""
    
    def __init__(self, rag_engine=None):
        """Initialize QA pipeline with DistilBERT model.
        
        Args:
            rag_engine: Optional RAGEngine for semantic chunk retrieval
        """
        try:
            self.qa_pipeline = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad",
                device=-1  # Use CPU; change to 0 for GPU
            )
            self.rag_engine = rag_engine
        except Exception as e:
            logger.error(f"Error initializing QA pipeline: {e}")
            raise
    
    def answer(self, question: str, context: str, top_k: int = 1) -> dict:
        """
        Answer a question based on the provided context.
        
        Args:
            question: The question to answer
            context: The context document to search for answers
            top_k: Number of top answers to return
            
        Returns:
            Dictionary with answer, score, and positions
        """
        try:
            if not context or not context.strip():
                return {
                    "answer": "No context provided",
                    "score": 0.0,
                    "start": 0,
                    "end": 0
                }
            
            # Limit context to avoid token limits (DistilBERT: ~512 tokens ≈ 2000 chars)
            # Increased to 4000 to handle larger chunks from RAG with multiple retrieved sections
            max_chars = 4000
            if len(context) > max_chars:
                context = context[:max_chars]
            
            result = self.qa_pipeline(question=question, context=context, top_k=top_k)
            
            # Return top result if multiple
            if isinstance(result, list):
                result = result[0]
            
            return {
                "answer": result.get("answer", ""),
                "score": float(result.get("score", 0.0)),
                "start": result.get("start", 0),
                "end": result.get("end", 0)
            }
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": f"Error processing question: {str(e)}",
                "score": 0.0,
                "start": 0,
                "end": 0
            }
    
    def answer_from_documents(self, question: str, documents: dict, session_id: str = None, top_k: int = 1, max_context_length: int = 4000) -> dict:
        """
        Answer a question by searching across multiple documents.
        Uses RAG if available for semantic chunk retrieval.
        
        Args:
            question: The question to answer
            documents: Dictionary of {doc_id: doc_text}
            session_id: Optional session ID for RAG index lookup
            top_k: Number of top answers to return
            max_context_length: Maximum context length for QA model
            
        Returns:
            Dictionary with best answer and source document
        """
        best_answer = {
            "answer": "No answer found",
            "score": 0.0,
            "source": None
        }
        
        # Use RAG if available and session_id provided
        if self.rag_engine and session_id:
            try:
                augmented_context = self.rag_engine.augment_context(session_id, question, max_context_length=max_context_length)
                if augmented_context and augmented_context.strip():
                    result = self.answer(question, augmented_context, top_k=1)
                    if result and result.get("answer"):
                        best_answer = {
                            "answer": result["answer"],
                            "score": result["score"],
                            "source": "RAG-retrieved-chunks"
                        }
                    return best_answer
            except Exception as e:
                logger.warning(f"RAG retrieval failed, falling back to full-document search: {e}")
                # Fall through to document-based search below
        
        # Fall back to searching all documents if RAG unavailable or failed
        for doc_id, doc_text in documents.items():
            result = self.answer(question, doc_text, top_k=1)
            if result["score"] > best_answer["score"]:
                best_answer = {
                    "answer": result["answer"],
                    "score": result["score"],
                    "source": doc_id
                }
        
        return best_answer
