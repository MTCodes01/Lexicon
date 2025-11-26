import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1/auth"

def test_register():
    email = "testuser@example.com"
    password = "password123"
    
    # Clean up if exists (optional, or just use random email)
    import time
    email = f"testuser_{int(time.time())}@example.com"
    
    payload = {
        "email": email,
        "password": password,
        "is_active": True,
        "is_admin": False,
        "is_owner": False
    }
    
    print(f"Registering user: {email}")
    try:
        response = requests.post(f"{BASE_URL}/register", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("Registration successful!")
            return True
        else:
            print("Registration failed.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if test_register():
        sys.exit(0)
    else:
        sys.exit(1)
