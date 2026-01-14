"""
Upload tab component for document upload and management.
"""
import streamlit as st
from utils import upload_documents


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
                        st.rerun()
    
    # Display uploaded documents for current session only
    if st.session_state.documents and st.session_state.session_id:
        st.subheader("📄 Extracted Documents")
        
        for i, doc in enumerate(st.session_state.documents):
            with st.expander(f"📄 {doc['filename']}", expanded=(i==0)):
                if doc.get('status') == 'success':
                    st.caption(f"✅ Successfully extracted")
                    st.caption(f"Text length: {doc.get('text_length', 0)} characters")
                    
                    # Show placeholder since full text isn't in the response
                    st.info("✓ Document processed and indexed for Q&A")
                else:
                    st.error(f"❌ Error: {doc.get('error', 'Unknown error')}")
