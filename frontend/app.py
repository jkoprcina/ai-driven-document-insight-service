"""
Main entry point for the Document QA System Streamlit application.
"""
import streamlit as st
from components import (
    render_sidebar,
    render_upload_tab,
    render_chat_tab,
    render_documents_tab,
    render_analysis_tab
)
from utils.auth import initialize_session_state
from config import PAGE_CONFIG
from styles import CUSTOM_CSS

# Configure page
st.set_page_config(**PAGE_CONFIG)

# Apply custom CSS
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# Main app layout
st.title("📄 Document QA System")
st.markdown("Upload documents and ask questions using AI-powered analysis")

# Sidebar
render_sidebar()

# Main content - Tabbed interface
tab1, tab2, tab3, tab4 = st.tabs([
    "📤 Upload Documents",
    "💬 Ask Questions",
    "📊 Analysis",
    "📑 View Documents"
])

with tab1:
    render_upload_tab()

with tab2:
    render_chat_tab()

with tab3:
    render_analysis_tab()

with tab4:
    render_documents_tab()
