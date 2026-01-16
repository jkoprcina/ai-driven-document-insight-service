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
import time

# Configure page
st.set_page_config(**PAGE_CONFIG)

# Apply custom CSS
st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)

# Initialize session state
initialize_session_state()

# Auto-refresh for NER status checking - disabled by default, only when processing
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()
if 'last_checked_ner' not in st.session_state:
    st.session_state.last_checked_ner = False

# Only auto-refresh if explicitly enabled AND a reasonable time has passed
# This prevents constant refreshing that slows down the app
current_time = time.time()
if st.session_state.last_checked_ner and current_time - st.session_state.last_refresh > 5:
    st.session_state.last_refresh = current_time
    # Disable auto-refresh after a while to prevent endless refreshing
    st.session_state.last_checked_ner = False
    st.rerun()

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
