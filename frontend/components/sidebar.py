"""
Sidebar component for session management and settings.
"""
import streamlit as st
from utils import delete_session, get_session_info, get_sessions_list
from config import API_BASE_URL


def render_sidebar():
    """Render the sidebar with session controls and settings"""
    with st.sidebar:
        st.header("⚙️ Controls")
        
        if st.session_state.session_id:
            st.success(f"Session: `{st.session_state.session_id[:8]}...`")
            
            if st.button("🔄 New Session", use_container_width=True):
                # Preserve current chat history per-session
                if 'session_histories' not in st.session_state:
                    st.session_state.session_histories = {}
                if st.session_state.session_id and st.session_state.chat_history:
                    st.session_state.session_histories[st.session_state.session_id] = st.session_state.chat_history
                # Reset to start a fresh session
                st.session_state.session_id = None
                st.session_state.documents = []
                st.session_state.chat_history = []
                st.rerun()
            
            if st.button("🗑️ Delete Session", use_container_width=True):
                if delete_session(st.session_state.session_id):
                    st.success("Session deleted")
                    # Remove saved history for this session if present
                    if 'session_histories' in st.session_state and st.session_state.session_id in st.session_state.session_histories:
                        del st.session_state.session_histories[st.session_state.session_id]
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

        # Switch to an existing session
        with st.expander("🔁 Switch to Existing Session"):
            # List available sessions (best effort)
            sessions = get_sessions_list()
            if sessions:
                selected = st.selectbox(
                    "Select an existing session",
                    options=sessions,
                    format_func=lambda s: f"{s[:8]}..."
                )
                if st.button("Switch to Selected", use_container_width=True, key="switch_session_select"):
                    # Save current session's chat history before switching
                    if 'session_histories' not in st.session_state:
                        st.session_state.session_histories = {}
                    if st.session_state.session_id and st.session_state.chat_history:
                        st.session_state.session_histories[st.session_state.session_id] = st.session_state.chat_history
                    # Load selected session
                    info = get_session_info(selected)
                    if info:
                        st.session_state.session_id = selected
                        st.session_state.documents = info.get("documents", [])
                        # Restore chat history for selected session if available
                        st.session_state.chat_history = st.session_state.session_histories.get(selected, [])
                        st.success(f"Switched to session {selected[:8]}...")
                        st.rerun()
                    else:
                        st.error("Selected session not found")
            else:
                st.info("No active sessions found from server")

            existing_id = st.text_input(
                "Existing session_id",
                value="",
                placeholder="Paste a previous session_id (UUID)"
            )
            if st.button("Switch Session", use_container_width=True, key="switch_session_btn"):
                sid = existing_id.strip()
                if not sid:
                    st.warning("Please enter a session_id")
                else:
                    # Save current session's chat history before switching
                    if 'session_histories' not in st.session_state:
                        st.session_state.session_histories = {}
                    if st.session_state.session_id and st.session_state.chat_history:
                        st.session_state.session_histories[st.session_state.session_id] = st.session_state.chat_history
                    # Load pasted session
                    info = get_session_info(sid)
                    if info:
                        st.session_state.session_id = sid
                        st.session_state.documents = info.get("documents", [])
                        st.session_state.chat_history = st.session_state.session_histories.get(sid, [])
                        st.success(f"Switched to session {sid[:8]}...")
                        st.rerun()
                    else:
                        st.error("Session not found or no longer available")
