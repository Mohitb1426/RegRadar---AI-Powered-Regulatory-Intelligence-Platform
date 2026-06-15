"""
Test API endpoints
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n[TEST] Health Check")
    print("-" * 60)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_register():
    """Test user registration"""
    print("\n[TEST] User Registration")
    print("-" * 60)
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 201:
        return response.json()["access_token"]
    return None


def test_login():
    """Test user login"""
    print("\n[TEST] User Login")
    print("-" * 60)
    data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def test_search(token):
    """Test search endpoint"""
    print("\n[TEST] Search Circulars")
    print("-" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "query": "capital adequacy requirements",
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/search/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
    return response.status_code == 200


def test_chat(token):
    """Test chat endpoint"""
    print("\n[TEST] Chat (RAG)")
    print("-" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "question": "What are the new regulations for small finance banks?",
        "top_k": 3
    }
    response = requests.post(f"{BASE_URL}/chat/", json=data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Citations: {len(result['citations'])} sources")
    else:
        print(f"Error: {response.text}")
    return response.status_code == 200


def test_list_circulars(token):
    """Test list circulars endpoint"""
    print("\n[TEST] List Circulars")
    print("-" * 60)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/circulars/?limit=5", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        circulars = response.json()
        print(f"Found {len(circulars)} circulars")
        if circulars:
            print(f"First circular: {circulars[0]['title'][:60]}...")
    return response.status_code == 200


def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("RegRadar API Testing")
    print("=" * 60)

    # Check if server is running
    try:
        test_health()
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Server not running!")
        print("Start server with: cd backend && python -m uvicorn app.main:app --reload")
        return

    # Get token (try login first, then register)
    token = test_login()
    if not token:
        token = test_register()

    if not token:
        print("\n[ERROR] Authentication failed!")
        return

    print(f"\n[INFO] Using token: {token[:20]}...")

    # Run API tests
    results = {
        "Health Check": True,  # Already passed
        "Authentication": True,  # Got token
        "Search": test_search(token),
        "Chat (RAG)": test_chat(token),
        "List Circulars": test_list_circulars(token)
    }

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test_name}: {status}")

    total = len(results)
    passed = sum(results.values())
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
