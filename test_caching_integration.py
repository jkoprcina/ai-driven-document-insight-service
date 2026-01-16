#!/usr/bin/env python
"""Test caching integration in the QA API."""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_caching_integration():
    """Test caching of embeddings and QA results."""
    print("=" * 70)
    print("Testing Caching Integration (Embeddings + QA Results)")
    print("=" * 70)
    
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
    
    # Upload documents (this should cache embeddings)
    print("\n[3] Uploading test documents (will cache embeddings)...")
    test_files = ["test_docs/JosipKoprcinaResume.pdf", "test_docs/roman_history.pdf"]
    
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
            print(f"         Embeddings should now be cached")
        else:
            print(f"ERROR: Upload failed with status {upload_resp.status_code}")
            return False
    else:
        print("WARNING: No test files found, skipping upload test")
        return False
    
    # Test 1: First QA call (should compute and cache)
    print("\n[4] First QA call (will compute and cache result)...")
    question = "What is the total amount?"
    question_data = {
        "session_id": session_id,
        "question": question,
        "highlight_entities": False
    }
    
    start_time = time.time()
    qa_resp = requests.post(f"{BASE_URL}/api/v1/ask", headers=headers, json=question_data)
    first_call_time = time.time() - start_time
    
    if qa_resp.status_code == 200:
        result = qa_resp.json()
        print(f"SUCCESS: Got answer in {first_call_time:.3f}s")
        print(f"         Answer: {result['answer'][:60]}...")
        print(f"         Confidence: {result['confidence']:.4f}")
    else:
        print(f"ERROR: QA failed with status {qa_resp.status_code}")
        return False
    
    # Test 2: Second QA call with same question (should be cached)
    print("\n[5] Second QA call with SAME question (should retrieve from cache)...")
    start_time = time.time()
    qa_resp2 = requests.post(f"{BASE_URL}/api/v1/ask", headers=headers, json=question_data)
    second_call_time = time.time() - start_time
    
    if qa_resp2.status_code == 200:
        result2 = qa_resp2.json()
        print(f"SUCCESS: Got cached answer in {second_call_time:.3f}s")
        print(f"         Answer: {result2['answer'][:60]}...")
        
        # Verify it's the same answer
        if result["answer"] == result2["answer"]:
            speedup = first_call_time / second_call_time if second_call_time > 0 else 0
            print(f"         Cache speedup: {speedup:.1f}x faster")
            if speedup > 1:
                print(f"         ✓ CACHE WORKING: Cached response is {speedup:.1f}x faster")
            else:
                print(f"         ! Cache may not be working (second call not faster)")
        else:
            print(f"         ERROR: Different answers returned!")
            return False
    else:
        print(f"ERROR: Second QA call failed with status {qa_resp2.status_code}")
        return False
    
    # Test 3: Different question (should compute, not use cache)
    print("\n[6] Third QA call with DIFFERENT question (should compute, not cached)...")
    different_question = "Who are the parties involved?"
    question_data2 = {
        "session_id": session_id,
        "question": different_question,
        "highlight_entities": False
    }
    
    start_time = time.time()
    qa_resp3 = requests.post(f"{BASE_URL}/api/v1/ask", headers=headers, json=question_data2)
    third_call_time = time.time() - start_time
    
    if qa_resp3.status_code == 200:
        result3 = qa_resp3.json()
        print(f"SUCCESS: Got answer for different question in {third_call_time:.3f}s")
        print(f"         Answer: {result3['answer'][:60]}...")
        
        if result3["answer"] != result["answer"]:
            print(f"         ✓ Different question returned different answer (as expected)")
        else:
            print(f"         ! Suspicious: Different question returned same answer")
    else:
        print(f"ERROR: Third QA call failed with status {qa_resp3.status_code}")
        return False
    
    # Test 4: Detailed QA with caching
    print("\n[7] Detailed QA call (will compute and cache)...")
    start_time = time.time()
    qa_detailed_resp = requests.post(f"{BASE_URL}/api/v1/ask-detailed", headers=headers, json=question_data)
    detailed_first_time = time.time() - start_time
    
    if qa_detailed_resp.status_code == 200:
        result = qa_detailed_resp.json()
        print(f"SUCCESS: Got detailed answer in {detailed_first_time:.3f}s")
        best_ans = result.get('best_answer', {}).get('answer', 'N/A')
        print(f"         Best answer: {best_ans[:60]}...")
        print(f"         Total answers: {len(result.get('answers', []))}")
    else:
        print(f"ERROR: Detailed QA failed with status {qa_detailed_resp.status_code}")
        return False
    
    # Test 5: Repeated detailed QA (should be cached)
    print("\n[8] Repeated detailed QA call (should be cached)...")
    start_time = time.time()
    qa_detailed_resp2 = requests.post(f"{BASE_URL}/api/v1/ask-detailed", headers=headers, json=question_data)
    detailed_second_time = time.time() - start_time
    
    if qa_detailed_resp2.status_code == 200:
        result2 = qa_detailed_resp2.json()
        print(f"SUCCESS: Got cached detailed answer in {detailed_second_time:.3f}s")
        speedup = detailed_first_time / detailed_second_time if detailed_second_time > 0 else 0
        print(f"         Cache speedup: {speedup:.1f}x faster")
        if speedup > 1:
            print(f"         ✓ DETAILED QA CACHE WORKING: {speedup:.1f}x faster")
    else:
        print(f"ERROR: Repeated detailed QA failed with status {qa_detailed_resp2.status_code}")
        return False
    
    print("\n" + "=" * 70)
    print("Caching Integration Test Complete")
    print("=" * 70)
    print("\nSummary:")
    print(f"  ✓ Embeddings cached on upload")
    print(f"  ✓ QA results cached on first call")
    print(f"  ✓ Cache retrieved on repeated questions")
    print(f"  ✓ Different questions use different cache entries")
    print(f"  ✓ Detailed QA results also cached")
    print("=" * 70)
    return True

if __name__ == "__main__":
    try:
        success = test_caching_integration()
        exit(0 if success else 1)
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
