"""
Document upload and management routes.
Handles POST /upload for document ingestion.
"""
from fastapi import APIRouter, UploadFile, File, Request, HTTPException, Depends, BackgroundTasks
from typing import List
import uuid
import logging
import os
import tempfile
from app.services.extractor import TextExtractor
from app.dependencies import verify_token
from app.middleware import limiter
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize extractor (safe: OCR loads lazily)
extractor = TextExtractor()


async def process_ner_background(session_id: str, doc_id: str, text: str, session_storage, ner_service):
    """
    Process NER extraction in background.
    
    Args:
        session_id: Session ID
        doc_id: Document ID
        text: Document text
        session_storage: Session storage instance
        ner_service: NER service instance
    """
    try:
        logger.info(f"[NER-{doc_id[:8]}] Starting NER processing (text length: {len(text)} chars)")
        session_storage.set_ner_status(session_id, doc_id, "processing")
        
        if not text or len(text) == 0:
            logger.warning(f"[NER-{doc_id[:8]}] Document has no text, skipping NER")
            session_storage.set_ner_status(session_id, doc_id, "completed")
            return
        
        # Process in chunks for large documents
        chunk_size = 50000
        all_entities = []
        
        if len(text) > chunk_size:
            logger.info(f"[NER-{doc_id[:8]}] Processing in chunks (total: {len(text)} chars, chunk size: {chunk_size})")
            chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
            
            for idx, chunk in enumerate(chunks):
                logger.info(f"[NER-{doc_id[:8]}] Processing chunk {idx+1}/{len(chunks)} (size: {len(chunk)} chars)")
                chunk_result = ner_service.highlight_entities(chunk, format_type="dict")
                chunk_entities = chunk_result.get('entities', [])
                
                # Adjust entity positions for the chunk offset
                offset = idx * chunk_size
                for ent in chunk_entities:
                    ent['start'] += offset
                    ent['end'] += offset
                
                all_entities.extend(chunk_entities)
                logger.info(f"[NER-{doc_id[:8]}] Chunk {idx+1} found {len(chunk_entities)} entities (total so far: {len(all_entities)})")
            
            entities = {
                "text": text,
                "entities": all_entities
            }
        else:
            logger.info(f"[NER-{doc_id[:8]}] Processing full text in single pass")
            entities = ner_service.highlight_entities(text, format_type="dict")
        
        logger.info(f"[NER-{doc_id[:8]}] NER processing complete, found {len(entities.get('entities', []))} total entities")
        
        session_storage.set_entities(session_id, doc_id, entities)
        logger.info(f"[NER-{doc_id[:8]}] COMPLETED - NER entities saved to storage")
    except Exception as e:
        logger.error(f"[NER-{doc_id[:8]}] ERROR: {type(e).__name__}: {str(e)}", exc_info=True)
        session_storage.set_ner_status(session_id, doc_id, "failed")

@limiter.limit("20/minute")
@router.post("/session")
async def create_session(request: Request, token: dict = Depends(verify_token)):
    """
    Create a new document session.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Session ID
    """
    session_storage = request.app.state.session_storage
    session_id = session_storage.create_session()
    
    return {
        "session_id": session_id,
        "status": "created"
    }

@limiter.limit("10/minute")
@router.post("/upload")
async def upload_documents(
    request: Request,
    background_tasks: BackgroundTasks,
    token: dict = Depends(verify_token),
    files: List[UploadFile] = File(...),
    session_id: str = None
):
    """
    Upload one or more documents (PDF or image).
    
    Args:
        request: FastAPI request object
        files: List of uploaded files
        session_id: Optional session ID. If not provided, creates new session.
        background_tasks: FastAPI background tasks
        
    Returns:
        Dictionary with session_id and uploaded documents info
    """
    session_storage = request.app.state.session_storage
    ner_service = request.app.state.ner if hasattr(request.app.state, 'ner') else None
    
    # Create session if not provided
    if not session_id:
        session_id = session_storage.create_session()
    elif not session_storage.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    uploaded_docs = []
    
    for file in files:
        try:
            # Validate file type
            allowed_extensions = {".pdf", ".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext not in allowed_extensions:
                logger.warning(f"Unsupported file type: {file.filename}")
                continue
            
            # Save temp file and extract text
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
                    tmp_path = tmp.name
                    content = await file.read()
                    tmp.write(content)
                    tmp.flush()
                
                # Extract text (file is now closed)
                try:
                    text = extractor.extract(tmp_path)
                except Exception as e:
                    # If OCR unavailable and image provided, return a clear error
                    logger.error(f"Extraction failed for {file.filename}: {e}")
                    uploaded_docs.append({
                        "filename": file.filename,
                        "status": "error",
                        "error": f"Extraction failed: {str(e)}"
                    })
                    continue
                
                # Generate document ID
                doc_id = str(uuid.uuid4())
                
                # Store in session
                session_storage.add_document(
                    session_id=session_id,
                    doc_id=doc_id,
                    filename=file.filename,
                    text=text
                )
                
                # Schedule NER processing in background
                if ner_service:
                    if background_tasks:
                        background_tasks.add_task(
                            process_ner_background,
                            session_id,
                            doc_id,
                            text,
                            session_storage,
                            ner_service
                        )
                        logger.info(f"Scheduled background NER task for document {doc_id}")
                    else:
                        logger.warning(f"BackgroundTasks not available, skipping NER for document {doc_id}")
                
                uploaded_docs.append({
                    "doc_id": doc_id,
                    "filename": file.filename,
                    "text_length": len(text),
                    "status": "success"
                })
                
                logger.info(f"Processed {file.filename} -> {doc_id}")
                
            except Exception as e:
                logger.error(f"Error processing {file.filename}: {e}")
                uploaded_docs.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
            finally:
                # Clean up temp file (with retry logic for Windows)
                if tmp_path and os.path.exists(tmp_path):
                    import time
                    for attempt in range(3):
                        try:
                            os.unlink(tmp_path)
                            break
                        except PermissionError:
                            if attempt < 2:
                                time.sleep(0.2 * (attempt + 1))  # Exponential backoff
                            else:
                                logger.warning(f"Could not delete temp file: {tmp_path}")
                        except Exception as e:
                            logger.warning(f"Error cleaning up temp file: {e}")
                            break
        
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {e}")
            uploaded_docs.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })
    
    # Create RAG index if documents were successfully uploaded
    if any(d["status"] == "success" for d in uploaded_docs):
        try:
            documents = session_storage.get_all_texts(session_id)
            if documents and request.app.state.rag:
                success = request.app.state.rag.create_session_index(session_id, documents)
                logger.info(f"RAG index created for session {session_id}: {success}")
        except Exception as e:
            logger.warning(f"Failed to create RAG index for session {session_id}: {e}")
            # Continue anyway - RAG is optional for functionality
    
    return {
        "session_id": session_id,
        "documents_uploaded": len([d for d in uploaded_docs if d["status"] == "success"]),
        "documents": uploaded_docs
    }

@limiter.limit("30/minute")
@router.get("/session/{session_id}")
async def get_session_info(request: Request, session_id: str, token: dict = Depends(verify_token)):
    """
    Get information about a session and its documents.
    
    Args:
        request: FastAPI request object
        session_id: Session ID
        
    Returns:
        Session information and document list
    """
    session_storage = request.app.state.session_storage
    
    if not session_storage.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get session and documents
    session = session_storage.sessions.get(session_id, {})
    docs = session_storage.get_documents(session_id)
    
    return {
        "session_id": session_id,
        "created_at": session.get("created_at", "Unknown").isoformat() if hasattr(session.get("created_at"), "isoformat") else str(session.get("created_at", "Unknown")),
        "document_count": len(docs) if docs else 0,
        "documents": [
            {
                "doc_id": doc_id,
                "filename": doc["filename"],
                "text": doc["text"],
                "text_length": doc["size"],
                "added_at": doc["added_at"].isoformat(),
                "ner_status": doc.get("ner_status", "pending"),
                "entities": doc.get("entities")
            }
            for doc_id, doc in (docs.items() if docs else [])
        ]
    }

@limiter.limit("20/minute")
@router.delete("/session/{session_id}")
async def delete_session(request: Request, session_id: str, token: dict = Depends(verify_token)):
    """
    Delete a session and all its documents.
    Cleans up RAG indices and cached results if available.
    
    Args:
        request: FastAPI request object
        session_id: Session ID
        
    Returns:
        Confirmation message
    """
    session_storage = request.app.state.session_storage
    
    if not session_storage.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Clean up RAG index if available
    if request.app.state.rag:
        try:
            request.app.state.rag.delete_session(session_id)
            logger.info(f"Cleaned up RAG index for session {session_id}")
        except Exception as e:
            logger.warning(f"Failed to clean up RAG index for session {session_id}: {e}")
    
    # Clear cache entries for this session
    if request.app.state.cache:
        try:
            count = request.app.state.cache.clear_session(session_id)
            logger.info(f"Cleared {count} cache entries for session {session_id}")
        except Exception as e:
            logger.warning(f"Failed to clear cache for session {session_id}: {e}")
    
    session_storage.clear_session(session_id)
    
    return {
        "status": "deleted",
        "session_id": session_id
    }
