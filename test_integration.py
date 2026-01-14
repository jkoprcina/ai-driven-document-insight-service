"""
Integration test script for the Document QA API.
Tests the entire workflow: upload -> ask -> answer
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check."""
    print("\n=== Testing Health Check ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_root():
    """Test root endpoint."""
    print("\n=== Testing Root Endpoint ===")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"API Name: {data['name']}")
    print(f"Version: {data['version']}")
    assert response.status_code == 200
    print("✓ Root endpoint passed")

def test_upload_pdf():
    """Test PDF upload."""
    print("\n=== Testing PDF Upload ===")
    pdf_path = "test_docs/sample_contract.pdf"
    
    if not Path(pdf_path).exists():
        print(f"⚠ Test document not found: {pdf_path}")
        return None
    
    with open(pdf_path, "rb") as f:
        files = {"files": (pdf_path, f)}
        response = requests.post(f"{BASE_URL}/api/v1/upload", files=files)
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert "session_id" in data
    assert data["documents_uploaded"] > 0
    print("✓ PDF upload passed")
    
    return data["session_id"]

def test_upload_image(session_id):
    """Test image upload to existing session."""
    print("\n=== Testing Image Upload ===")
    img_path = "test_docs/sample_invoice.png"
    
    if not Path(img_path).exists():
        print(f"⚠ Test document not found: {img_path}")
        return session_id
    
    with open(img_path, "rb") as f:
        files = {"files": (img_path, f)}
        response = requests.post(
            f"{BASE_URL}/api/v1/upload",
            files=files,
            params={"session_id": session_id}
        )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert data["documents_uploaded"] > 0
    print("✓ Image upload passed")
    
    return session_id

def test_session_info(session_id):
    """Test getting session info."""
    print("\n=== Testing Session Info ===")
    response = requests.get(f"{BASE_URL}/api/v1/session/{session_id}")
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert data["session_id"] == session_id
    assert data["document_count"] > 0
    print("✓ Session info passed")

def test_ask_question(session_id):
    """Test asking a question."""
    print("\n=== Testing Question Answering ===")
    
    question = "What is the contract amount?"
    payload = {
        "session_id": session_id,
        "question": question
    }
    
    print(f"Question: {question}")
    response = requests.post(f"{BASE_URL}/api/v1/ask", json=payload)
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert "answer" in data
    assert "confidence" in data
    print(f"Answer: {data['answer']}")
    print(f"Confidence: {data['confidence']:.2%}")
    print("✓ Question answering passed")

def test_ask_detailed(session_id):
    """Test detailed question answering."""
    print("\n=== Testing Detailed Question Answering ===")
    
    question = "What are the payment terms?"
    payload = {
        "session_id": session_id,
        "question": question
    }
    
    print(f"Question: {question}")
    response = requests.post(f"{BASE_URL}/api/v1/ask-detailed", json=payload)
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert "answers" in data, "Missing 'answers' in response"
    assert len(data.get("answers", [])) > 0, "No answers returned"
    print("✓ Detailed question answering passed")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Document QA API Integration Tests")
    print("=" * 60)
    
    try:
        test_health()
        test_root()
        
        session_id = test_upload_pdf()
        if session_id:
            session_id = test_upload_image(session_id)
            test_session_info(session_id)
            
            # Wait a moment for model loading
            print("\n⏳ Loading QA model (this may take a minute on first run)...")
            time.sleep(2)
            
            test_ask_question(session_id)
            test_ask_detailed(session_id)
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
