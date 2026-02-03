import requests

# Settings
BASE_URL = "http://127.0.0.1:8001/api"
USERNAME = "admin"      
PASSWORD = "admin"      

def test_security():
    print("SECURITY TEST STARTING...\n")

    # SCENARIO 1: Access without Token (Should Fail)
    print("1. Attempting Access without Token...")
    try:
        response = requests.post(f"{BASE_URL}/create-roster/", json={"flight_number": "TK1001"})
        if response.status_code == 401:
            print("SUCCESS: System denied access! (401 Unauthorized)")
        else:
            print(f"ERROR: System is unprotected! Code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 30)

    # SCENARIO 2: Obtaining Token (Login)
    print("2. Logging In (Token Request)...")
    token = None
    try:
        login_data = {"username": USERNAME, "password": PASSWORD}
        response = requests.post(f"{BASE_URL}/token/", data=login_data)
        
        if response.status_code == 200:
            token = response.json().get('access')
            print("SUCCESS: Token received!")
            print(f"Token (First 20 chars): {token[:20]}...")
        else:
            print(f"ERROR: Login failed! Code: {response.status_code}")
            print("Check username or password.")
            return 
    except Exception as e:
        print(f"Error: {e}")
        return

    print("-" * 30)

    # SCENARIO 3: Access with Token (Should Succeed)
    print("3. Attempting to Create Roster with Token...")
    try:
        # Adding Token to Header
        headers = {"Authorization": f"Bearer {token}"}
        
        payload = {"flight_number": "TK1001"}
        response = requests.post(f"{BASE_URL}/create-roster/", json=payload, headers=headers)
        
        if response.status_code == 201:
            print("SUCCESS: Access granted and Roster created!")
            print(f"Message: {response.json().get('message')}")
        else:
            print(f"ERROR: Received error despite having token. Code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_security()
