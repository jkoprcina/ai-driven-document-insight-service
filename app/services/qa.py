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
        Uses DistilBERT QA model on the provided context.
        Note: For large documents, use RAG-augmented context via answer_from_documents().
        
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
            
            result = self.qa_pipeline(question=question, context=context, top_k=top_k)
            
            # Handle list response from pipeline
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
    
    def augment_context(self, session_id: str, question: str, max_context_length: int = 4000) -> str:
        """
        Retrieve and combine relevant chunks for context augmentation.
        
        Args:
            session_id: Session ID for RAG index
            question: Question to find relevant context for
            max_context_length: Maximum context length
            
        Returns:
            Augmented context string
        """
        try:
            if not self.rag_engine:
                return ""
            chunks = self.rag_engine.retrieve_relevant_chunks(session_id, question, top_k=3)
            if not chunks:
                return ""
            context = "\n\n".join([c["chunk"] for c in chunks])
            return context[:max_context_length]
        except Exception as e:
            logger.warning(f"Error augmenting context: {e}")
            return ""
    
    def answer_from_documents(self, question: str, documents: dict, session_id: str = None, top_k: int = 1, max_context_length: int = 4000) -> dict:
        """
        Answer a question by searching across documents.
        Uses RAG for semantic retrieval across all documents if available.
        For single small documents or when RAG unavailable, falls back to direct search.
        
        Args:
            question: The question to answer
            documents: Dictionary of {doc_id: doc_text}
            session_id: Optional session ID for RAG index lookup (recommended for better results)
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
        
        # Prioritize RAG for multi-document and large document searches
        if self.rag_engine and session_id:
            try:
                augmented_context = self.augment_context(
                    session_id, 
                    question, 
                    max_context_length=max_context_length
                )
                if augmented_context and augmented_context.strip():
                    result = self.answer(question, augmented_context, top_k=1)
                    if result and result.get("answer"):
                        best_answer = {
                            "answer": result["answer"],
                            "score": result["score"],
                            "source": "RAG-retrieved-chunks"
                        }
                        logger.info(f"Answer found via RAG with score {result['score']:.4f}")
                        return best_answer
                else:
                    logger.warning(f"RAG returned empty context for question: {question}")
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")
                # Fall through to fallback search below
        
        # Fallback: search documents directly
        # This handles cases where RAG is unavailable or for single document searches
        logger.info(f"Falling back to direct document search ({len(documents)} documents)")
        for doc_id, doc_text in documents.items():
            # Limit context to avoid token limits
            context = doc_text[:max_context_length] if len(doc_text) > max_context_length else doc_text
            result = self.answer(question, context, top_k=1)
            if result["score"] > best_answer["score"]:
                best_answer = {
                    "answer": result["answer"],
                    "score": result["score"],
                    "source": doc_id
                }
                logger.info(f"Answer found in document {doc_id} with score {result['score']:.4f}")
        
        return best_answer
