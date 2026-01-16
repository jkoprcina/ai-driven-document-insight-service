"""
Upload tab component for document upload and management.
"""
import streamlit as st
from utils import upload_documents, get_session_info
import time


def render_upload_tab():
    """Render the upload tab for document upload"""
    st.header("Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose documents",
        type=["pdf", "jpg", "jpeg", "png", "bmp", "gif", "tiff"],
        accept_multiple_files=True,
        help="Upload PDF documents or images. Max 10MB per file."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if uploaded_files:
            st.write(f"📎 {len(uploaded_files)} file(s) selected:")
            for file in uploaded_files:
                st.caption(f"• {file.name} ({file.size / 1024 / 1024:.2f}MB)")
    
    with col2:
        if st.button("🚀 Upload & Process", use_container_width=True):
            if not uploaded_files:
                st.warning("Please select files first")
            else:
                with st.spinner("Uploading and extracting text..."):
                    # Pass existing session_id if available to append documents
                    result = upload_documents(uploaded_files, session_id=st.session_state.session_id)
                    
                    if result:
                        # Set session_id (either new or existing)
                        st.session_state.session_id = result['session_id']
                        
                        # Append new documents to existing list
                        if st.session_state.documents:
                            st.session_state.documents.extend(result['documents'])
                        else:
                            st.session_state.documents = result['documents']
                            st.session_state.chat_history = []  # Only clear chat for first upload
                        
                        st.success(f"✅ Uploaded {len(result['documents'])} document(s)")
                        st.info("📊 NER processing started in background. Check the Documents tab to see progress.")
                        st.session_state.last_checked_ner = True  # Enable auto-refresh
                        st.rerun()
    
    # Display uploaded documents for current session only
    if st.session_state.documents and st.session_state.session_id:
        st.subheader("📄 Extracted Documents")
        
        # Auto-refresh to check NER status
        st.markdown("""
        <style>
        .stButton button { width: 100%; }
        </style>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()
        
        # Fetch latest session info to get real NER status
        try:
            session_info = get_session_info(st.session_state.session_id)
            session_docs = {doc['doc_id']: doc for doc in session_info.get('documents', [])} if session_info else {}
        except Exception as e:
            st.warning(f"Could not refresh status: {str(e)}")
            session_docs = {}
        
        # Check if any NER is still processing
        processing_count = sum(1 for doc in session_docs.values() if doc.get('ner_status') == 'processing')
        pending_count = sum(1 for doc in session_docs.values() if doc.get('ner_status') == 'pending')
        
        if processing_count > 0:
            st.info(f"⏳ NER processing: {processing_count} document(s) in progress...")
        elif pending_count > 0:
            st.info(f"⏳ NER queued: {pending_count} document(s) waiting to process...")
        
        for i, doc in enumerate(st.session_state.documents):
            with st.expander(f"📄 {doc['filename']}", expanded=(i==0)):
                if doc.get('status') == 'success':
                    st.caption(f"✅ Successfully extracted")
                    st.caption(f"Text length: {doc.get('text_length', 0)} characters")
                    
                    # Get real NER status from session
                    doc_id = doc.get('doc_id')
                    session_doc = session_docs.get(doc_id, {}) if doc_id else {}
                    ner_status = session_doc.get('ner_status', 'pending')
                    
                    st.info("✓ Document processed and indexed for Q&A")
                    
                    if ner_status == "pending":
                        st.info("⏳ NER: Waiting to process...")
                    elif ner_status == "processing":
                        st.warning("⏳ NER: Processing in background...")
                    elif ner_status == "completed":
                        st.success("✅ NER: Complete!")
                    elif ner_status == "failed":
                        st.error("❌ NER: Processing failed")
                    else:
                        st.info(f"NER: {ner_status}")
                else:
                    st.error(f"❌ Error: {doc.get('error', 'Unknown error')}")
