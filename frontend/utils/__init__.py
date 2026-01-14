"""
Utils package initialization.
"""
from utils.auth import get_auth_token, get_headers, initialize_session_state
from utils.api_client import (
    check_api_health,
    upload_documents,
    ask_question,
    get_session_info,
    delete_session,
    extract_entities
)
from utils.formatters import (
    get_confidence_color,
    display_entities,
    highlight_entities_in_text
)

__all__ = [
    'get_auth_token',
    'get_headers',
    'initialize_session_state',
    'check_api_health',
    'upload_documents',
    'ask_question',
    'get_session_info',
    'delete_session',
    'extract_entities',
    'get_confidence_color',
    'display_entities',
    'highlight_entities_in_text',
]
