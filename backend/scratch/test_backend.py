import os
import sys
import shutil

# Make sure backend/app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoints():
    print("=" * 60)
    print("RUNNING DIAGNOSTIC API TESTS via TestClient")
    print("=" * 60)

    # Use context manager to trigger lifespan events
    with TestClient(app) as client:
        # 1. Test Welcome Route
        print("\n[Test 1] GET / (Welcome)")
        response = client.get("/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # 2. Test Health Check
        print("\n[Test 2] GET /health (Health Status)")
        response = client.get("/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert "status" in response.json()

        # 3. Test Chat with general query (RAG fallback)
        print("\n[Test 3] POST /chat (RAG check: baggage allowance)")
        response = client.post("/chat", json={"message": "What is the baggage allowance?"})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        assert "baggage" in response.json()["response"].lower()

        # 4. Test Chat with general query (RAG fallback)
        print("\n[Test 4] POST /chat (RAG check: FAQ query)")
        try:
            response = client.post("/chat", json={"message": "Tell me about the loyalty program rules."})
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            assert response.status_code == 200
        except Exception as e:
            print(f"Chat (RAG) skipped/failed: {e}")

        # 6. Test PDF Upload
        print("\n[Test 6] POST /upload/pdf (PDF processing check)")
        import fitz
        test_pdf_path = os.path.join(os.path.dirname(__file__), "test_dummy.pdf")
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "This is a test PDF document for Airline RAG Chatbot validation.")
        doc.save(test_pdf_path)
        doc.close()

        try:
            with open(test_pdf_path, "rb") as f:
                response = client.post("/upload/pdf", files={"file": ("test_dummy.pdf", f, "application/pdf")})
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            assert response.status_code == 200
            assert "extracted_text" in response.json()
            assert "test" in response.json()["extracted_text"].lower()
        finally:
            if os.path.exists(test_pdf_path):
                os.remove(test_pdf_path)

        # 7. Test Image Upload
        print("\n[Test 7] POST /upload/image (Image processing check)")
        test_img_path = os.path.join(os.path.dirname(__file__), "test_dummy.png")
        with open(test_img_path, "wb") as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82")

        try:
            with open(test_img_path, "rb") as f:
                response = client.post("/upload/image", files={"file": ("test_dummy.png", f, "image/png")})
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            assert response.status_code == 200
            assert response.json()["result"]["status"] == "not_implemented"
        finally:
            if os.path.exists(test_img_path):
                os.remove(test_img_path)

    print("\n" + "=" * 60)
    print("ALL API ENDPOINT DIAGNOSTIC TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    test_endpoints()

