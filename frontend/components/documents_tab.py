"""
Documents tab component for viewing extracted text with NER highlighting.
"""
import streamlit as st
from utils import get_session_info, display_entities
from utils.formatters import highlight_entities_in_text
import time


def render_documents_tab():
    """Render the documents tab for viewing extracted text"""
    st.header("📄 Documents")
    
    if not st.session_state.session_id:
        st.info("👈 Upload documents in the Upload tab first")
        return
    
    # Auto-refresh button
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.button("🔄", help="Refresh to check NER status", use_container_width=True):
            st.rerun()
    
    session_info = get_session_info(st.session_state.session_id)
    
    if not session_info or not session_info.get('documents'):
        st.info("No documents uploaded yet. Upload documents in the Upload tab to view them here.")
        return
    
    documents = session_info['documents']
    
    # Document selector with key to maintain state
    doc_names = [doc['filename'] for doc in documents]
    if 'selected_doc_index' not in st.session_state:
        st.session_state.selected_doc_index = 0
    
    selected_doc = st.selectbox(
        "Select a document to view",
        options=range(len(doc_names)),
        format_func=lambda i: doc_names[i],
        key='selected_doc_index'
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
        # Use 'added_at' from session info, not 'created_at'
        uploaded = selected_document.get('added_at', 'N/A')
        st.metric("Uploaded", uploaded[:10] if isinstance(uploaded, str) else str(uploaded))
    
    st.divider()
    
    # Check NER status
    ner_status = selected_document.get('ner_status', 'pending')
    
    # Extract and display document text with entity highlighting
    try:
        # Get the extracted text
        doc_text = selected_document.get('text', '')
        
        if not doc_text:
            st.warning("No text extracted from this document")
            return
        
        st.subheader("Extracted Text with Entities")
        
        if ner_status == "pending" or ner_status == "processing":
            # Show loading state
            with st.spinner(f"⏳ Loading NER..."):
                # Optionally refresh to check updated status
                st.info(f"🔄 Named Entity Recognition is being processed... (Status: {ner_status})")
                # Auto-refresh every 2 seconds while NER is processing
                if ner_status == "processing":
                    time.sleep(2)
                    st.rerun()
        
        elif ner_status == "completed":
            # NER is done, display entities
            entities_data = selected_document.get('entities')
            
            # Only show as completed if we actually have entities data
            if not entities_data:
                st.info("⏳ NER processing just completed, refreshing...")
                time.sleep(1)
                st.rerun()
                return
            
            if entities_data and isinstance(entities_data, dict):
                entity_list = entities_data.get('entities', [])
                
                if entity_list:
                    st.write(f"**Found {len(entity_list)} Entities:**")
                    
                    # Group entities by type
                    entities_by_type = {}
                    for ent in entity_list:
                        ent_type = ent.get('label', 'UNKNOWN')
                        if ent_type not in entities_by_type:
                            entities_by_type[ent_type] = []
                        entities_by_type[ent_type].append(ent.get('text', ''))
                    
                    # Display entities grouped by type
                    for ent_type, ent_texts in sorted(entities_by_type.items()):
                        st.caption(f"**{ent_type}:** {', '.join(set(ent_texts))}")
                    
                    st.divider()
                else:
                    st.info("💡 No named entities found in this document. Named entities include: PERSON, ORG, LOCATION, DATE, MONEY, PERCENT, FACILITY")
            
            # Display text with inline highlighting
            st.write("**Full Document Text:**")
            
            # For large documents, limit the highlighted display to avoid performance issues
            display_limit = 100000  # 100k characters
            
            if entities_data and isinstance(entities_data, dict):
                entity_list = entities_data.get('entities', [])
                if entity_list and len(doc_text) <= display_limit:
                    # Use the formatter to create highlighted text for smaller documents
                    highlighted_text = highlight_entities_in_text(doc_text, entity_list)
                    st.markdown(highlighted_text, unsafe_allow_html=True)
                elif entity_list and len(doc_text) > display_limit:
                    # For large documents, show plain text to avoid performance issues
                    st.warning(f"⚠️ Document is large ({len(doc_text):,} chars). Showing plain text for performance. Entities were still extracted.")
                    st.text_area(
                        "Document Content",
                        value=doc_text,
                        height=400,
                        disabled=True
                    )
                else:
                    st.text_area(
                        "Document Content",
                        value=doc_text,
                        height=400,
                        disabled=True
                    )
            else:
                st.text_area(
                    "Document Content",
                    value=doc_text,
                    height=400,
                    disabled=True
                )
        
        elif ner_status == "failed":
            st.error("❌ NER processing failed for this document. Please try re-uploading.")
            st.write("**Full Document Text:**")
            st.text_area(
                "Document Content",
                value=doc_text,
                height=400,
                disabled=True
            )
        
        else:
            # Unknown status
            st.warning(f"Unknown NER status: {ner_status}")
            st.write("**Full Document Text:**")
            st.text_area(
                "Document Content",
                value=doc_text,
                height=400,
                disabled=True
            )
    
    except Exception as e:
        st.error(f"Error displaying document: {str(e)}")
