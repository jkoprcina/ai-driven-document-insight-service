"""
Question-answering routes.
Handles POST /ask for document QA with optional entity highlighting.
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
from app.services.qa import QAEngine
from app.dependencies import verify_token
from app.middleware import limiter

router = APIRouter()
logger = logging.getLogger(__name__)

# QAEngine will be initialized with RAG engine in main.py
qa_engine = None

def get_qa_engine(request: Request):
    """Get or initialize QA engine with RAG."""
    if not hasattr(request.app.state, 'qa_engine') or request.app.state.qa_engine is None:
        rag_engine = getattr(request.app.state, 'rag', None)
        request.app.state.qa_engine = QAEngine(rag_engine=rag_engine)
    return request.app.state.qa_engine

class QuestionRequest(BaseModel):
    """Request model for QA endpoint."""
    session_id: str
    question: str
    doc_id: str = None  # Optional: specific document ID
    highlight_entities: bool = True  # Enable entity highlighting
    max_context_length: int = 4000  # Max context chars for large documents

class Entity(BaseModel):
    """Entity information."""
    text: str
    label: str
    start: int
    end: int
    label_description: Optional[str] = None

class AnswerResponse(BaseModel):
    """Response model for QA endpoint."""
    question: str
    answer: str
    confidence: float
    source_doc: str = None
    entities: Optional[List[Entity]] = None  # Highlighted entities in answer

@limiter.limit("30/minute")
@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: Request, query: QuestionRequest, token: dict = Depends(verify_token)):
    """
    Ask a question about uploaded documents.
    Optionally uses RAG for semantic chunk retrieval if available.
    Results are cached for repeated questions.
    
    Args:
        request: FastAPI request object
        query: QuestionRequest with session_id, question, and optional doc_id
        
    Returns:
        AnswerResponse with answer and confidence score
    """
    session_storage = request.app.state.session_storage
    qa_engine = get_qa_engine(request)
    cache_manager = request.app.state.cache
    
    # Validate session
    if not session_storage.session_exists(query.session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check cache first (only for multi-doc queries, not single doc)
    cached_result = None
    if not query.doc_id:
        cached_result = cache_manager.get_qa_result(query.session_id, query.question)
        if cached_result:
            logger.info(f"Cache hit for question in session {query.session_id}")
            return AnswerResponse(**cached_result)
    
    # Get documents
    if query.doc_id:
        # Answer from specific document (RAG not used for single doc)
        text = session_storage.get_document_text(query.session_id, query.doc_id)
        if not text:
            raise HTTPException(status_code=404, detail="Document not found")
        documents = {query.doc_id: text}
        # Skip RAG for specific doc queries
        result = qa_engine.answer(query.question, text)
    else:
        # Answer from all documents in session (use RAG if available)
        documents = session_storage.get_all_texts(query.session_id)
        if not documents:
            raise HTTPException(status_code=400, detail="No documents in session")
        # Pass session_id and max_context_length to enable RAG retrieval with configurable context
        result = qa_engine.answer_from_documents(
            query.question, 
            documents, 
            session_id=query.session_id,
            max_context_length=query.max_context_length
        )
    
    # Extract entities from answer if NER is available and requested
    entities = None
    if query.highlight_entities and request.app.state.ner:
        try:
            ner_result = request.app.state.ner.highlight_entities(
                result.get("answer", ""),
                format_type="dict"
            )
            entities = [
                Entity(
                    text=ent["text"],
                    label=ent["label"],
                    start=ent["start"],
                    end=ent["end"],
                    label_description=ent.get("label_description")
                )
                for ent in ner_result.get("entities", [])
            ]
        except Exception as e:
            logger.warning(f"Error extracting entities: {e}")
            entities = None
    
    response_data = {
        "question": query.question,
        "answer": result.get("answer", "No answer found"),
        "confidence": result.get("score", 0.0),
        "source_doc": result.get("source", "Unknown"),
        "entities": entities
    }
    
    # Cache result for multi-doc queries
    if not query.doc_id:
        cache_manager.cache_qa_result(query.session_id, query.question, response_data)
    
    return AnswerResponse(**response_data)

@limiter.limit("30/minute")
@router.post("/ask-detailed")
async def ask_question_detailed(request: Request, query: QuestionRequest, token: dict = Depends(verify_token)):
    """
    Ask a question with detailed response including all document scores.
    Uses RAG for semantic chunk retrieval if available.
    Results are cached for repeated questions.
    
    Args:
        request: FastAPI request object
        query: QuestionRequest
        
    Returns:
        Detailed response with answers from all documents
    """
    session_storage = request.app.state.session_storage
    qa_engine = get_qa_engine(request)
    cache_manager = request.app.state.cache
    
    # Validate session
    if not session_storage.session_exists(query.session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check cache first
    cache_key = f"qa_detailed:{query.session_id}:{query.question}"
    try:
        import hashlib
        question_hash = hashlib.md5(query.question.encode()).hexdigest()
        cache_key = f"qa_detailed:{query.session_id}:{question_hash}"
        cached_result = cache_manager.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for detailed question in session {query.session_id}")
            return cached_result
    except Exception as e:
        logger.warning(f"Error checking cache: {e}")
    
    # Get documents
    documents = session_storage.get_all_texts(query.session_id)
    if not documents:
        raise HTTPException(status_code=400, detail="No documents in session")
    
    # Get answers from each document
    answers = []
    for doc_id, doc_text in documents.items():
        result = qa_engine.answer(query.question, doc_text)
        
        # Extract entities from answer if NER is available and requested
        entities = None
        if query.highlight_entities and request.app.state.ner:
            try:
                ner_result = request.app.state.ner.highlight_entities(
                    result.get("answer", ""),
                    format_type="dict"
                )
                entities = [
                    {
                        "text": ent["text"],
                        "label": ent["label"],
                        "start": ent["start"],
                        "end": ent["end"],
                        "label_description": ent.get("label_description")
                    }
                    for ent in ner_result.get("entities", [])
                ]
            except Exception as e:
                logger.warning(f"Error extracting entities: {e}")
                entities = None
        
        answers.append({
            "doc_id": doc_id,
            "answer": result["answer"],
            "confidence": result["score"],
            "entities": entities
        })
    
    # Sort by confidence
    answers.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
    
    best = answers[0] if answers else {
        "doc_id": "None",
        "answer": "No answer found",
        "confidence": 0.0,
        "entities": None
    }
    
    response_data = {
        "question": query.question,
        "answers": answers,
        "best_answer": best
    }
    
    # Cache result
    try:
        cache_manager.set(cache_key, response_data, ttl=3600)
    except Exception as e:
        logger.warning(f"Error caching detailed QA result: {e}")
    
    return response_data