"""
Formatting utilities for displaying data in the UI.
"""
import streamlit as st
from config import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, ENTITY_COLORS


def get_confidence_color(confidence: float) -> str:
    """
    Get color class based on confidence score
    
    Args:
        confidence: Confidence score (0.0 to 1.0)
    
    Returns:
        CSS class name for confidence level
    """
    if confidence >= CONFIDENCE_HIGH:
        return "confidence-high"
    elif confidence >= CONFIDENCE_MEDIUM:
        return "confidence-medium"
    else:
        return "confidence-low"


def display_entities(entities):
    """
    Display highlighted entities from NER
    
    Args:
        entities: List of entity dictionaries with 'text' and 'label' keys
    """
    if not entities:
        return
    
    st.markdown("**🏷️ Named Entities Detected:**")
    
    # Group entities by label
    by_label = {}
    for ent in entities:
        label = ent.get("label", "UNKNOWN")
        if label not in by_label:
            by_label[label] = []
        by_label[label].append(ent.get("text", ""))
    
    # Display in columns
    cols = st.columns(min(3, len(by_label)))
    
    for i, (label, texts) in enumerate(sorted(by_label.items())):
        with cols[i % len(cols)]:
            # Create a color badge for the label
            unique_texts = list(set(texts))
            st.markdown(f"""
            <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 5px 0;">
                <strong>{label}</strong><br>
                {', '.join(unique_texts[:5])}{'...' if len(unique_texts) > 5 else ''}
            </div>
            """, unsafe_allow_html=True)


def highlight_entities_in_text(text: str, entities: list) -> str:
    """
    Create HTML with highlighted entities in text
    
    Args:
        text: Original text
        entities: List of entities with start, end, label, and text
    
    Returns:
        HTML string with highlighted entities
    """
    if not entities:
        return text
    
    # Sort entities by start position (reversed for safe replacement)
    sorted_entities = sorted(entities, key=lambda x: x['start'], reverse=True)
    
    displayed_text = text
    for entity in sorted_entities:
        start = entity.get('start', 0)
        end = entity.get('end', 0)
        label = entity.get('label', 'UNKNOWN')
        
        if 0 <= start < end <= len(displayed_text):
            entity_text = displayed_text[start:end]
            color = ENTITY_COLORS.get(label, '#FFE5E5')
            
            # Create HTML span with background color
            highlighted = f'<mark style="background-color: {color}; padding: 2px 4px; border-radius: 3px; margin: 0 2px;" title="{label}">{entity_text}</mark>'
            
            displayed_text = displayed_text[:start] + highlighted + displayed_text[end:]
    
    return displayed_text
