"""
Documents tab component for viewing extracted text with NER highlighting.
"""
import streamlit as st
from utils import get_session_info, extract_entities, display_entities
from utils.formatters import highlight_entities_in_text


def render_documents_tab():
    """Render the documents tab for viewing extracted text"""
    st.header("📄 Documents")
    
    if not st.session_state.session_id:
        st.info("👈 Upload documents in the Upload tab first")
        return
    
    session_info = get_session_info(st.session_state.session_id)
    
    if not session_info or not session_info.get('documents'):
        st.info("No documents uploaded yet. Upload documents in the Upload tab to view them here.")
        return
    
    documents = session_info['documents']
    
    # Document selector
    doc_names = [doc['filename'] for doc in documents]
    selected_doc = st.selectbox(
        "Select a document to view",
        options=range(len(doc_names)),
        format_func=lambda i: doc_names[i]
    )
    
    selected_document = documents[selected_doc]
    
    st.subheader(f"📋 {selected_document['filename']}")
    
    # Document metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Characters", f"{selected_document.get('text_length', 0):,}")
    with col2:
        char_count = selected_document.get('text_length', 0)
        est_words = max(1, char_count // 5)
        st.metric("Est. Words", f"{est_words:,}")
    with col3:
        st.metric("Uploaded", selected_document.get('created_at', 'N/A')[:10])
    
    st.divider()
    
    # Extract and display document text with entity highlighting
    try:
        # Get the extracted text
        doc_text = selected_document.get('text', '')
        
        if not doc_text:
            st.warning("No text extracted from this document")
            return
        
        # Extract entities using NER
        entities = extract_entities(doc_text)
        
        # Display text with entity highlighting
        st.subheader("Extracted Text with Entities")
        
        if entities:
            st.write(f"**Found {len(entities)} Entities:**")
            display_entities(entities)
            st.divider()
        else:
            st.info("💡 No named entities found in this section. Named entities include: PERSON, ORG, LOCATION, DATE, MONEY, PERCENT, FACILITY")
        
        # Display text with inline highlighting
        st.write("**Full Document Text:**")
        
        if entities:
            # Use the formatter to create highlighted text
            highlighted_text = highlight_entities_in_text(doc_text, entities)
            st.markdown(highlighted_text, unsafe_allow_html=True)
        else:
            # Show plain text if no entities
            st.text_area(
                "Document Content",
                value=doc_text,
                height=400,
                disabled=True
            )
    except Exception as e:
        st.error(f"Error displaying document: {str(e)}")
