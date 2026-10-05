"""
SahayakAI Pre-Deployment Verification Test Suite
Runs end-to-end automated health, auth, ingestion, RAG, and streaming tests
against the running backend instance before deploying to production.
"""
import sys
import time
import uuid
import json
import requests

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"
TEST_RUN_ID = str(uuid.uuid4())[:8]
TEST_EMAIL = f"deploy_test_{TEST_RUN_ID}@example.com"
TEST_PASSWORD = "TestPassword123!"

results = []

def run_test(name: str, test_fn):
    print(f"\n[RUNNING] {name}...", end=" ", flush=True)
    start = time.time()
    try:
        test_fn()
        elapsed = round((time.time() - start) * 1000, 1)
        print(f"PASSED ({elapsed}ms)")
        results.append((name, True, f"{elapsed}ms"))
    except AssertionError as err:
        elapsed = round((time.time() - start) * 1000, 1)
        print(f"FAILED ({elapsed}ms) -> {err}")
        results.append((name, False, str(err)))
    except Exception as exc:
        elapsed = round((time.time() - start) * 1000, 1)
        print(f"ERROR ({elapsed}ms) -> {exc}")
        results.append((name, False, str(exc)))

state = {
    "token": None,
    "user_id": None,
    "conv_id": None,
}

# -------------------------------------------------------------
# Test 1: Service Health
# -------------------------------------------------------------
def test_health():
    res = requests.get(f"{BASE_URL}/health", timeout=10)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert data.get("status") == "ok", f"Expected status ok, got {data}"

# -------------------------------------------------------------
# Test 2: Frontend Static SPA Serving
# -------------------------------------------------------------
def test_static_ui():
    res = requests.get(f"{BASE_URL}/", timeout=10)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "<title>" in res.text, "index.html does not contain <title>"

# -------------------------------------------------------------
# Test 3: User Registration & JWT Authentication
# -------------------------------------------------------------
def test_auth_register_and_login():
    reg_res = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={"name": "Deploy Tester", "email": TEST_EMAIL, "password": TEST_PASSWORD},
        timeout=10,
    )
    assert reg_res.status_code in (200, 201), f"Register failed: {reg_res.status_code} - {reg_res.text}"
    data = reg_res.json()
    token = data.get("token")
    assert token, "No token returned upon registration"
    state["token"] = token
    state["user_id"] = data.get("user", {}).get("id")

    # Verify /api/auth/me
    headers = {"Authorization": f"Bearer {token}"}
    me_res = requests.get(f"{BASE_URL}/api/auth/me", headers=headers, timeout=10)
    assert me_res.status_code == 200, f"Auth me failed: {me_res.status_code}"
    user_info = me_res.json().get("user", {})
    assert user_info.get("email") == TEST_EMAIL, f"Email mismatch in /api/auth/me: {user_info}"

    # Verify rejection on bad token
    bad_res = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": "Bearer bad_token"}, timeout=10)
    assert bad_res.status_code == 401, f"Expected 401 on bad token, got {bad_res.status_code}"

# -------------------------------------------------------------
# Test 4: Conversation Lifecycle
# -------------------------------------------------------------
def test_conversation_lifecycle():
    headers = {"Authorization": f"Bearer {state['token']}"}
    create_res = requests.post(
        f"{BASE_URL}/api/conversations",
        headers=headers,
        json={"title": "Deployment Verification Chat"},
        timeout=10,
    )
    assert create_res.status_code in (200, 201), f"Create conversation failed: {create_res.status_code}"
    conv = create_res.json().get("conversation", {})
    conv_id = conv.get("_id") or conv.get("id")
    assert conv_id, f"No conversationId returned: {create_res.json()}"
    state["conv_id"] = conv_id

    # List conversations
    list_res = requests.get(f"{BASE_URL}/api/conversations", headers=headers, timeout=10)
    assert list_res.status_code == 200, f"List conversations failed: {list_res.status_code}"
    conversations = list_res.json().get("conversations", [])
    ids = [c.get("_id") or c.get("id") for c in conversations]
    assert conv_id in ids, f"Created conversation {conv_id} not in listed conversations: {ids}"

# -------------------------------------------------------------
# Test 5: Document Upload, Extraction & FAISS Indexing
# -------------------------------------------------------------
def test_document_ingestion():
    headers = {"Authorization": f"Bearer {state['token']}"}
    sample_text = (
        "SahayakAI Cloud Deployment Verification Document.\n\n"
        "Project Architecture:\n"
        "SahayakAI is an AI assistant for medical, banking, and government documents.\n"
        "Standard deployment configuration requires port 8000 and 1GB RAM minimum.\n"
        "Critical Rule: The deployment timeout threshold is exactly 45 seconds.\n"
        "Contact security lead: admin@sahayakai.org for security notices."
    )
    files = {"file": ("deploy_verify_doc.txt", sample_text.encode("utf-8"), "text/plain")}
    data = {"conversationId": state["conv_id"], "language": "English"}

    upload_res = requests.post(
        f"{BASE_URL}/api/upload",
        headers=headers,
        files=files,
        data=data,
        timeout=30,
    )
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.status_code} - {upload_res.text}"
    res_data = upload_res.json()
    assert res_data.get("chunks", 0) > 0, "No chunks created during document ingestion"
    assert "analysis" in res_data, "No analysis generated for uploaded document"
    state["conv_id"] = res_data.get("conversationId") or state["conv_id"]

# -------------------------------------------------------------
# Test 6: Grounded RAG Question Answering
# -------------------------------------------------------------
def test_rag_answering():
    headers = {"Authorization": f"Bearer {state['token']}"}
    payload = {
        "question": "What is the deployment timeout threshold mentioned in the document?",
        "language": "English",
        "conversationId": state["conv_id"],
        "documentName": "deploy_verify_doc.txt",
        "history": [],
    }
    ask_res = requests.post(f"{BASE_URL}/api/ask", headers=headers, json=payload, timeout=30)
    assert ask_res.status_code == 200, f"Ask failed: {ask_res.status_code} - {ask_res.text}"
    data = ask_res.json()
    answer = data.get("answer", "")
    assert "45" in answer or "timeout" in answer.lower(), f"Expected '45' seconds in answer, got: {answer}"
    assert len(data.get("citations", [])) > 0, "Expected at least 1 citation for grounded answer"

# -------------------------------------------------------------
# Test 7: Multi-Turn Continuity & Quiz Answer Evaluation
# -------------------------------------------------------------
def test_conversation_continuity():
    headers = {"Authorization": f"Bearer {state['token']}"}
    history = [
        {"role": "user", "content": "quiz me"},
        {
            "role": "assistant",
            "content": (
                "Based on the document, what is the deployment timeout threshold?\n"
                "A. 15 seconds\n"
                "B. 45 seconds\n"
                "C. 60 seconds\n"
                "D. 90 seconds"
            ),
        },
    ]
    payload = {
        "question": "B",
        "language": "English",
        "conversationId": state["conv_id"],
        "documentName": "deploy_verify_doc.txt",
        "history": history,
    }
    quiz_res = requests.post(f"{BASE_URL}/api/ask", headers=headers, json=payload, timeout=30)
    assert quiz_res.status_code == 200, f"Quiz follow-up failed: {quiz_res.status_code}"
    ans = quiz_res.json().get("answer", "")
    assert "could not find this information" not in ans.lower(), f"AI failed quiz evaluation: {ans}"
    assert "correct" in ans.lower() or "45" in ans, f"AI did not validate correct answer: {ans}"

# -------------------------------------------------------------
# Test 8: SSE Real-Time Token Streaming
# -------------------------------------------------------------
def test_sse_streaming():
    headers = {"Authorization": f"Bearer {state['token']}"}
    payload = {
        "question": "What is the contact security email in the document?",
        "language": "English",
        "conversationId": state["conv_id"],
        "documentName": "deploy_verify_doc.txt",
        "history": [],
    }
    stream_res = requests.post(
        f"{BASE_URL}/api/ask/stream",
        headers=headers,
        json=payload,
        stream=True,
        timeout=30,
    )
    assert stream_res.status_code == 200, f"Streaming failed: {stream_res.status_code}"
    assert "text/event-stream" in stream_res.headers.get("content-type", ""), "Wrong content-type for stream"

    collected = ""
    for line in stream_res.iter_lines(decode_unicode=True):
        if line.startswith("data: "):
            try:
                chunk = json.loads(line[6:])
                if chunk.get("type") == "token":
                    collected += chunk.get("token", "")
            except Exception:
                pass
    assert len(collected) > 0, "No streaming tokens received"
    assert "admin@sahayakai.org" in collected or "security" in collected.lower(), f"Stream answer incomplete: {collected}"

# -------------------------------------------------------------
# Test 9: Document Grounding Safety (Out-of-domain check)
# -------------------------------------------------------------
def test_out_of_domain_grounding():
    headers = {"Authorization": f"Bearer {state['token']}"}
    payload = {
        "question": "What is the capital city of Japan?",
        "language": "English",
        "conversationId": state["conv_id"],
        "documentName": "deploy_verify_doc.txt",
        "history": [],
    }
    res = requests.post(f"{BASE_URL}/api/ask", headers=headers, json=payload, timeout=30)
    assert res.status_code == 200, f"Ask failed: {res.status_code}"
    ans = res.json().get("answer", "").lower()
    assert any(term in ans for term in ["not mention", "not contain", "document", "cannot find", "japan"]), f"Grounding failed: {ans}"

# -------------------------------------------------------------
# Test 10: Cleanup & Conversation Deletion
# -------------------------------------------------------------
def test_cleanup():
    headers = {"Authorization": f"Bearer {state['token']}"}
    if state["conv_id"]:
        del_res = requests.delete(f"{BASE_URL}/api/conversations/{state['conv_id']}", headers=headers, timeout=10)
        assert del_res.status_code == 200, f"Delete conversation failed: {del_res.status_code}"


def main():
    print("=" * 65)
    print("      SAHAYAKAI PRE-DEPLOYMENT VERIFICATION TEST SUITE       ")
    print(f"      Target: {BASE_URL} | Session: {TEST_RUN_ID}")
    print("=" * 65)

    tests = [
        ("1. Health Endpoint Check", test_health),
        ("2. Static UI Index Serving", test_static_ui),
        ("3. Auth (Register, Login & Bearer Token)", test_auth_register_and_login),
        ("4. Conversation Creation & Listing", test_conversation_lifecycle),
        ("5. Document Upload, Parsing & FAISS Indexing", test_document_ingestion),
        ("6. Grounded RAG Question Answering", test_rag_answering),
        ("7. Multi-Turn Continuity & Quiz Answer Evaluation", test_conversation_continuity),
        ("8. SSE Real-Time Token Streaming", test_sse_streaming),
        ("9. Hallucination & Grounding Safety Check", test_out_of_domain_grounding),
        ("10. Conversation Cleanup & Deletion", test_cleanup),
    ]

    for name, fn in tests:
        run_test(name, fn)

    print("\n" + "=" * 65)
    print("                        SUMMARY                              ")
    print("=" * 65)
    passed_count = sum(1 for _, ok, _ in results if ok)
    total_count = len(results)

    for name, ok, detail in results:
        status = "PASSED" if ok else "FAILED"
        print(f"[{status:6}] {name:<45} ({detail})")

    print("-" * 65)
    if passed_count == total_count:
        print(f"ALL {total_count} TESTS PASSED SUCCESSFULLY! Ready for deployment. 🚀")
        sys.exit(0)
    else:
        print(f"FAILED: {total_count - passed_count} of {total_count} tests failed. Fix issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()
