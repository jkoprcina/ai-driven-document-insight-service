#!/bin/bash
# Setup script for Document QA API
# This script automates the setup process

set -e

echo "🚀 Document QA API - Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "  Found Python $python_version"

# Create virtual environment
echo ""
echo "✓ Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  Virtual environment created"
else
    echo "  Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "  Virtual environment activated"

# Upgrade pip
echo ""
echo "✓ Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo ""
echo "✓ Installing Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "  Dependencies installed"

# Download spaCy model
echo ""
echo "✓ Downloading spaCy model..."
python -m spacy download en_core_web_sm > /dev/null 2>&1
echo "  spaCy model downloaded"

# Create .env file
echo ""
echo "✓ Creating environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  .env file created from template"
    echo "  ⚠️  Please edit .env to set SECRET_KEY and other settings"
else
    echo "  .env file already exists"
fi

# Create necessary directories
echo ""
echo "✓ Creating directories..."
mkdir -p logs
mkdir -p model_cache
echo "  Directories created"

# Validation
echo ""
echo "✓ Validating setup..."
python -c "import fastapi, pydantic, torch, transformers; print('  All imports OK')" 2>/dev/null || {
    echo "  ✗ Some imports failed. Try: pip install -r requirements.txt"
    exit 1
}

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Start the API: python main.py"
echo "3. Open browser: http://localhost:8000/docs"
echo ""
echo "For Streamlit UI:"
echo "  pip install streamlit"
echo "  streamlit run streamlit_app.py"
echo ""
echo "Run tests:"
echo "  python test_integration.py"
echo ""
