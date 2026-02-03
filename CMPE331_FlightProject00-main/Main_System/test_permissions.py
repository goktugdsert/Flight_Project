import requests
import sys

# Configuration
BASE_URL = "http://127.0.0.1:8001/api"
USERNAME = "viewonly"
PASSWORD = "viewonly123"

def test_permissions():
    print(f"Testing permissions for user: {USERNAME}")
    
    # 1. Login
    login_url = f"{BASE_URL}/token/"
    try:
        response = requests.post(login_url, json={"username": USERNAME, "password": PASSWORD})
        if response.status_code != 200:
            print(f"FAILED: Login failed. Status: {response.status_code}")
            print(response.text)
            return
        
        data = response.json()
        access_token = data.get("access")
        groups = data.get("groups", [])
        print(f"SUCCESS: Login successful. Groups: {groups}")
        
        if "ViewOnly" not in groups:
            print("WARNING: User is not in 'ViewOnly' group!")

    except Exception as e:
        print(f"FAILED: Could not connect to login endpoint. {e}")
        return

    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Test Allowed Endpoint (Saved Rosters)
    print("\n--- Testing Allowed Endpoint (Saved Rosters) ---")
    try:
        resp = requests.get(f"{BASE_URL}/roster/list-saved/", headers=headers)
        if resp.status_code == 200:
            print("SUCCESS: Access granted to Saved Rosters.")
        else:
            print(f"FAILED: Access denied to Saved Rosters. Status: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. Test Restricted Endpoint (Flight List)
    print("\n--- Testing Restricted Endpoint (Flight List) ---")
    try:
        resp = requests.get(f"{BASE_URL}/flights/", headers=headers)
        if resp.status_code == 403:
            print("SUCCESS: Access correctly denied (403) for Flight List.")
        else:
            print(f"FAILED: Expected 403, got {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")

    # 4. Test Restricted Endpoint (Create Roster)
    print("\n--- Testing Restricted Endpoint (Create Roster) ---")
    try:
        resp = requests.post(f"{BASE_URL}/roster/create/", headers=headers, json={})
        if resp.status_code == 403:
            print("SUCCESS: Access correctly denied (403) for Create Roster.")
        else:
            print(f"FAILED: Expected 403, got {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_permissions()