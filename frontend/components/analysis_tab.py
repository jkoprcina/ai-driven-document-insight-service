"""
Analysis tab component for document statistics and metrics.
"""
import streamlit as st
from utils import get_session_info


def render_analysis_tab():
    """Render the analysis tab showing document statistics"""
    st.header("📊 Document Analysis")
    
    if not st.session_state.session_id:
        st.info("👈 Upload documents in the Upload tab first")
        return
    
    session_info = get_session_info(st.session_state.session_id)
    
    if not session_info:
        st.error("Unable to retrieve session information")
        return
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "📄 Total Documents",
            len(session_info['documents'])
        )
    
    with col2:
        # Get total characters from session info if available
        total_chars = 0
        if session_info and 'total_text_length' in session_info:
            total_chars = session_info['total_text_length']
        elif session_info and 'documents' in session_info:
            # Fall back to summing document text_length if available
            for doc in session_info['documents']:
                if 'text_length' in doc:
                    total_chars += doc['text_length']
        
        st.metric(
            "🔤 Total Characters",
            f"{total_chars:,}"
        )
    
    with col3:
        st.metric(
            "❓ Questions Asked",
            len(st.session_state.chat_history) // 2
        )
    
    st.divider()
    
    # Document details
    st.subheader("Document Details")
    
    for doc in session_info['documents']:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Filename", doc['filename'])
        with col2:
            char_count = doc.get('text_length', 0)
            st.metric("Characters", f"{char_count:,}")
        with col3:
            # Estimate words from character count
            char_count = doc.get('text_length', 0)
            est_words = max(1, char_count // 5)
            st.metric("Est. Words", f"{est_words:,}")
        with col4:
            st.metric("Created", doc.get('created_at', 'N/A')[:10])
    
    st.divider()
    
    # API Info
    st.subheader("API Information")
    
    created = session_info.get('created_at', 'Unknown')
    doc_count = len(session_info.get('documents', []))
    st.code(f"""
Session ID: {session_info.get('session_id', 'Unknown')}
Created: {created}
Documents: {doc_count}
    """, language="text")
