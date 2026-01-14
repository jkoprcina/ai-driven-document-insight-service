"""
Styles package initialization.
"""
# Read the CSS directly from the file
CUSTOM_CSS = """
<style>
    .main {
        max-width: 100%;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
    }
    .answer-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .confidence-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .confidence-high {
        background-color: #90EE90;
        color: #000;
    }
    .confidence-medium {
        background-color: #FFD700;
        color: #000;
    }
    .confidence-low {
        background-color: #FF6B6B;
        color: #fff;
    }
</style>
"""

__all__ = ['CUSTOM_CSS']
