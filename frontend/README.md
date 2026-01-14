# Frontend - Document QA System

Modular Streamlit-based web interface for the Document QA API.

## Structure

```
frontend/
├── app.py                 # Main application entry point
├── config.py              # Configuration and constants
├── __init__.py           # Package initialization
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── api_client.py      # API communication
│   ├── auth.py            # Authentication helpers
│   └── formatters.py      # Display formatting utilities
├── components/            # UI components
│   ├── __init__.py
│   ├── sidebar.py         # Sidebar with session controls
│   ├── upload_tab.py      # Document upload tab
│   ├── chat_tab.py        # Q&A chat tab
│   ├── analysis_tab.py    # Document analysis tab
│   └── documents_tab.py   # Document viewer tab
└── styles/
    └── custom.css         # Custom CSS styles
```

## Running the Application

### From project root:
```bash
streamlit run frontend/app.py
```

### Or using the old entry point (deprecated):
```bash
streamlit run streamlit_app.py
```

## Adding New Features

### Add a new tab:
1. Create a new component file in `components/`
2. Define a `render_<tab_name>_tab()` function
3. Import and add to `components/__init__.py`
4. Add tab in `app.py` and call the render function

### Add a new API endpoint:
1. Add the function in `utils/api_client.py`
2. Export it from `utils/__init__.py`
3. Use it in your component

### Customize styling:
- Edit `styles/custom.css` for global styles
- Use inline styles in components for component-specific styling

## Configuration

Edit `config.py` to change:
- API URL and endpoints
- Page configuration (title, icon, layout)
- Entity colors for NER highlighting
- Confidence thresholds
- API timeout values

## Benefits of Modular Structure

- **Maintainability**: Each component is isolated and easy to modify
- **Reusability**: Components can be reused across different pages
- **Testing**: Individual modules can be tested separately
- **Collaboration**: Multiple developers can work on different components
- **Scalability**: Easy to add new features without affecting existing code
- **Clarity**: Clear separation of concerns (config, utils, components, styles)
