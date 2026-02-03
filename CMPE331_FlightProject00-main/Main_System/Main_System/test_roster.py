import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8001/api"
USERNAME = "admin"
PASSWORD = "admin" 

def test_create_roster(flight_number):
    print(f"\n--- STARTING TEST FOR FLIGHT: {flight_number} ---")

    # STEP 1: Authentication
    print("1. Logging in...")
    token = None
    try:
        auth_payload = {"username": USERNAME, "password": PASSWORD}
        response = requests.post(f"{BASE_URL}/token/", data=auth_payload)
        
        if response.status_code == 200:
            token = response.json().get('access')
            print("Login successful! Token received.")
        else:
            print(f"Login failed! Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return
    except Exception as e:
        print(f"Connection Error during login: {e}")
        return

    print("-" * 30)

    # STEP 2: Request Roster Creation (Using the Token)
    print(f"2. Requesting Roster for {flight_number}...")
    
    url = f"{BASE_URL}/create-roster/"
    payload = {"flight_number": flight_number}
    
    # Add the token to the Authorization header
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            
            print("\nROSTER CREATED SUCCESSFULLY!")
            print(f"Flight Number : {data['flight_info']['number']}")
            print(f"Vehicle Type  : {data['flight_info']['vehicle']}")
            print(f"Capacity      : {data['flight_info']['capacity']}")
            print(f"Flight Menu   : {data['flight_info'].get('menu')}")
            
            stats = data['stats']
            print(f"Total Pax     : {stats['total_passengers']}")
            print(f"Total Crew    : {stats['total_crew']}")
            
            # Check Crew Members
            print("\n--- CREW MEMBERS ---")
            if data['crew']:
                for member in data['crew']:
                    print(f"- {member['name']} ({member['role']})")
            else:
                print("No crew found! Check Crew API (Port 8002).")

        else:
            print("Failed to create roster.")
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    target_flight = "TK1002" 
    test_create_roster(target_flight)
