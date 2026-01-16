#!/usr/bin/env python
"""Test RAG integration in the QA API."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_rag_integration():
    """Test RAG integration end-to-end."""
    print("=" * 60)
    print("Testing RAG Integration")
    print("=" * 60)
    
    # Get token
    print("\n[1] Getting authentication token...")
    token_resp = requests.post(f"{BASE_URL}/api/v1/token")
    if token_resp.status_code != 200:
        print(f"ERROR: Failed to get token: {token_resp.text}")
        return False
    
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("SUCCESS: Token obtained")
    
    # Create session
    print("\n[2] Creating session...")
    session_resp = requests.post(f"{BASE_URL}/api/v1/session", headers=headers)
    if session_resp.status_code != 200:
        print(f"ERROR: Failed to create session: {session_resp.text}")
        return False
    
    session_id = session_resp.json()["session_id"]
    print(f"SUCCESS: Session created: {session_id}")
    
    # Upload documents
    print("\n[3] Uploading test documents...")
    test_files = ["test_docs/JosipKoprcinaResume.pdf", "test_docs/roman_history.pdf"]
    
    files_list = []
    for test_file in test_files:
        try:
            with open(test_file, "rb") as f:
                files_list.append(("files", (test_file.split("/")[-1], f, "application/octet-stream")))
                
                upload_resp = requests.post(
                    f"{BASE_URL}/api/v1/upload?session_id={session_id}",
                    headers=headers,
                    files=files_list
                )
                files_list = []  # Reset for next iteration
        except FileNotFoundError:
            print(f"WARNING: Test file not found: {test_file}")
            continue
    
    # Try upload with both files
    files_list = []
    for test_file in test_files:
        try:
            f = open(test_file, "rb")
            files_list.append(("files", (test_file.split("/")[-1], f, "application/octet-stream")))
        except FileNotFoundError:
            pass
    
    if files_list:
        upload_resp = requests.post(
            f"{BASE_URL}/api/v1/upload?session_id={session_id}",
            headers=headers,
            files=files_list
        )
        for _, (_, f, _) in files_list:
            f.close()
        
        if upload_resp.status_code == 200:
            result = upload_resp.json()
            print(f"SUCCESS: Uploaded {result['documents_uploaded']} document(s)")
        else:
            print(f"ERROR: Upload failed with status {upload_resp.status_code}: {upload_resp.text}")
            return False
    else:
        print("WARNING: No test files found, skipping upload test")
    
    # Ask question to test RAG
    print("\n[4] Asking question to test RAG retrieval...")
    question_data = {
        "session_id": session_id,
        "question": "What is the total amount?",
        "highlight_entities": True
    }
    
    qa_resp = requests.post(f"{BASE_URL}/api/v1/ask", headers=headers, json=question_data)
    
    if qa_resp.status_code == 200:
        result = qa_resp.json()
        print(f"SUCCESS: Got answer")
        print(f"  Answer: {result['answer']}")
        print(f"  Confidence: {result['confidence']:.4f}")
        print(f"  Source: {result['source_doc']}")
        if result.get("entities"):
            print(f"  Entities found: {len(result['entities'])}")
            for entity in result["entities"][:3]:  # Show first 3
                print(f"    - {entity['text']} ({entity['label']})")
    else:
        print(f"ERROR: QA failed with status {qa_resp.status_code}: {qa_resp.text}")
        return False
    
    # Ask detailed question
    print("\n[5] Testing detailed QA endpoint...")
    qa_detailed_resp = requests.post(f"{BASE_URL}/api/v1/ask-detailed", headers=headers, json=question_data)
    
    if qa_detailed_resp.status_code == 200:
        result = qa_detailed_resp.json()
        print(f"SUCCESS: Got detailed answer")
        print(f"  Best answer: {result['answer']}")
        print(f"  Total answers from documents: {len(result['answers'])}")
        for answer in result["answers"][:2]:
            print(f"  - [{answer['confidence']:.4f}] {answer['answer'][:50]}...")
    else:
        print(f"ERROR: Detailed QA failed with status {qa_detailed_resp.status_code}")
    
    print("\n" + "=" * 60)
    print("RAG Integration Test Complete")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_rag_integration()
        exit(0 if success else 1)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
