import httpx
import json

API_URL = "http://localhost:8000"
LOGIN_URL = f"{API_URL}/api/v1/auth/login"
NOTES_URL = f"{API_URL}/notes/"

def test_create_note():
    # 0. Register (if needed)
    print("Registering user...")
    import time
    email = f"admin_{int(time.time())}@example.com"
    register_data = {
        "email": email,
        "password": "adminpassword123",
        "full_name": "Admin User"
    }
    try:
        reg_response = httpx.post(f"{API_URL}/api/v1/auth/register", json=register_data)
        print(f"Registration status: {reg_response.status_code}")
        if reg_response.status_code != 201:
             print(f"Registration failed: {reg_response.text}")
    except Exception as e:
        print(f"Registration error: {e}")

    # 1. Login
    print("Logging in...")
    login_data = {
        "email": email,
        "password": "adminpassword123"
    }
    try:
        response = httpx.post(LOGIN_URL, json=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
        
        token = response.json()["token"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create Note
        print("Creating note...")
        note_data = {
            "title": "Test Note",
            "content": "<p>This is a test note.</p>",
            "content_type": "html",
            "tags": ["test", "api"]
            # category_id omitted
        }
        
        response = httpx.post(NOTES_URL, json=note_data, headers=headers)
        if response.status_code == 201:
            print("✅ Note created successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failed to create note: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_create_note()
