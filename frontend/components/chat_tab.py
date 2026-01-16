"""
Chat tab component for asking questions about documents.
"""
import streamlit as st
from utils import ask_question, display_entities, get_confidence_color


def render_chat_tab():
    """Render the chat tab for Q&A interactions"""
    st.header("💬 Ask Questions")
    
    if not st.session_state.session_id:
        st.info("👈 Upload documents in the Upload tab first")
        return
    
    # Ensure per-session chat histories mapping exists
    if 'session_histories' not in st.session_state:
        st.session_state.session_histories = {}

    # Display chat history
    st.subheader("Chat History")
    
    if st.session_state.chat_history:
        for i, msg in enumerate(st.session_state.chat_history):
            if msg['role'] == 'user':
                st.chat_message("user").write(msg['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(msg['content'])
                    
                    # Display entities if available
                    if 'entities' in msg and msg['entities']:
                        display_entities(msg['entities'])
                    
                    if 'confidence' in msg:
                        confidence = msg['confidence']
                        color_class = get_confidence_color(confidence)
                        st.markdown(
                            f"<div style='text-align: right; margin-top: -10px;'>"
                            f"<span class='confidence-badge {color_class}'>"
                            f"Confidence: {confidence:.1%}</span></div>",
                            unsafe_allow_html=True
                        )
                        if 'source_doc' in msg:
                            st.caption(f"📄 Source: {msg['source_doc']}")
    
    st.divider()
    
    # Input area with form for proper Enter key handling
    st.subheader("Ask a Question")
    
    with st.form(key="question_form", clear_on_submit=True):
        question = st.text_input(
            "Your question:",
            placeholder="e.g., 'What are the main terms of this agreement?' (press Enter to submit)",
            label_visibility="collapsed"
        )
        
        ask_button = st.form_submit_button("Send 📨", use_container_width=True)
    
    # Ask question
    if ask_button and question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })
        
        with st.spinner("Analyzing documents..."):
            # Request answer from documents
            result = ask_question(st.session_state.session_id, question)
            
            if result:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result.get('answer', 'No answer found'),
                    "confidence": result.get('confidence', 0.0),
                    "source_doc": result.get('source_doc', 'Unknown source'),
                    "entities": result.get('entities')
                })
            else:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "No relevant information found in the documents.",
                    "confidence": 0.0,
                    "source_doc": "None",
                    "entities": None
                })
            # Persist chat history for this session
            st.session_state.session_histories[st.session_state.session_id] = st.session_state.chat_history
            st.rerun()
