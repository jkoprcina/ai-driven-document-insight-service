"""
Sidebar component for session management and settings.
"""
import streamlit as st
from utils import delete_session
from config import API_BASE_URL


def render_sidebar():
    """Render the sidebar with session controls and settings"""
    with st.sidebar:
        st.header("⚙️ Controls")
        
        if st.session_state.session_id:
            st.success(f"Session: `{st.session_state.session_id[:8]}...`")
            
            if st.button("🔄 New Session", use_container_width=True):
                st.session_state.session_id = None
                st.session_state.documents = []
                st.session_state.chat_history = []
                st.rerun()
            
            if st.button("🗑️ Delete Session", use_container_width=True):
                if delete_session(st.session_state.session_id):
                    st.success("Session deleted")
                    st.session_state.session_id = None
                    st.session_state.documents = []
                    st.session_state.chat_history = []
                    st.rerun()
        else:
            st.info("👈 Upload documents to get started")
        
        st.divider()
        
        # Settings
        with st.expander("⚙️ Settings"):
            st.write("### API Configuration")
            api_url = st.text_input(
                "API Base URL",
                value=API_BASE_URL,
                help="Default: http://localhost:8000"
            )
            if api_url != API_BASE_URL:
                st.warning("Restart app to apply changes")
