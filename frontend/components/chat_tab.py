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
            result = ask_question(st.session_state.session_id, question)
            
            if result:
                # Basic answer
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result['answer'],
                    "confidence": result['confidence'],
                    "source_doc": result['source_doc'],
                    "entities": result.get('entities')
                })
                st.rerun()
    
    # Detailed analysis button
    if st.session_state.chat_history:
        st.divider()
        
        with st.expander("📊 View Detailed Analysis"):
            if st.button("Get answers from all documents", use_container_width=True):
                # Get the last user question from chat history
                last_question = None
                for msg in reversed(st.session_state.chat_history):
                    if msg['role'] == 'user':
                        last_question = msg['content']
                        break
                
                if last_question:
                    with st.spinner("Retrieving detailed answers..."):
                        detailed = ask_question(
                            st.session_state.session_id,
                            last_question,
                            detailed=True
                        )
                        
                        if detailed:
                            st.subheader("Answers from All Documents")
                            
                            for i, answer in enumerate(detailed.get('answers', []), 1):
                                col1, col2 = st.columns([0.8, 0.2])
                                
                                with col1:
                                    source = answer.get('doc_id', 'Unknown source')
                                    st.markdown(
                                        f"### [{i}] {source}"
                                    )
                                    st.write(answer.get('answer', 'No answer'))
                                    
                                    # Display entities if available
                                    if answer.get('entities'):
                                        display_entities(answer.get('entities'))
                                
                                with col2:
                                    confidence = answer.get('confidence', 0.0)
                                    color_class = get_confidence_color(confidence)
                                    st.markdown(
                                        f"<div class='confidence-badge {color_class}'>"
                                        f"{confidence:.0%}</div>",
                                        unsafe_allow_html=True
                                    )
