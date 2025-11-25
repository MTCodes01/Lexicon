import httpx
import asyncio

API_URL = "http://localhost:8000"
LOGIN_URL = f"{API_URL}/api/v1/auth/login"
REGISTER_URL = f"{API_URL}/api/v1/auth/register"
CATEGORIES_URL = f"{API_URL}/notes/categories"

DEFAULT_CATEGORIES = [
    {
        "name": "Personal",
        "color": "#3B82F6",  # Blue
        "icon": "👤",
        "description": "Personal notes and tasks"
    },
    {
        "name": "Work",
        "color": "#EF4444",  # Red
        "icon": "💼",
        "description": "Work-related items"
    },
    {
        "name": "Ideas",
        "color": "#F59E0B",  # Amber
        "icon": "💡",
        "description": "Creative ideas and brainstorming"
    },
    {
        "name": "Journal",
        "color": "#10B981",  # Emerald
        "icon": "📔",
        "description": "Daily journal entries"
    }
]

async def seed_categories():
    email = "admin@example.com"
    password = "adminpassword123"
    
    async with httpx.AsyncClient() as client:
        # 1. Try to Login
        print(f"Attempting to login as {email}...")
        try:
            response = await client.post(LOGIN_URL, json={"email": email, "password": password})
            
            if response.status_code == 401:
                print("Login failed. Attempting to register...")
                # Try to register
                reg_response = await client.post(REGISTER_URL, json={
                    "email": email,
                    "password": password,
                    "full_name": "Admin User"
                })
                if reg_response.status_code == 201:
                    print("Registration successful! Logging in...")
                    response = await client.post(LOGIN_URL, json={"email": email, "password": password})
                else:
                    print(f"Registration failed: {reg_response.text}")
                    return

            if response.status_code != 200:
                print(f"Authentication failed: {response.text}")
                return

            token = response.json()["token"]["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authenticated successfully.")

            # 2. Get existing categories
            print("Checking existing categories...")
            response = await client.get(CATEGORIES_URL, headers=headers)
            if response.status_code != 200:
                print(f"Failed to fetch categories: {response.status_code}")
                print(response.text)
                return
            
            existing_categories = response.json()
            print(f"Found {len(existing_categories)} existing categories.")
            existing_names = {c["name"] for c in existing_categories}

            # 3. Create missing categories
            for cat in DEFAULT_CATEGORIES:
                if cat["name"] in existing_names:
                    print(f"Category '{cat['name']}' already exists. Skipping.")
                else:
                    print(f"Creating category '{cat['name']}'...")
                    response = await client.post(CATEGORIES_URL, json=cat, headers=headers)
                    if response.status_code == 201:
                        print(f"  ✅ Created '{cat['name']}'")
                    else:
                        print(f"  ❌ Failed to create '{cat['name']}': {response.text}")

            print("\n✨ Category seeding completed!")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(seed_categories())
