import requests
import re
import json

# Configuration
BASE_URL = "http://127.0.0.1:8001/api"
USERNAME = "admin"      
PASSWORD = "admin"      

def get_token():
    """Logs in and returns the access token."""
    try:
        response = requests.post(f"{BASE_URL}/token/", data={"username": USERNAME, "password": PASSWORD})
        if response.status_code == 200:
            return response.json().get('access')
        else:
            print(f"Login Failed! Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

def test_seat_distribution():
    # 1. Get Token
    token = get_token()
    if not token:
        return

    # 2. Request Roster Creation
    url = f"{BASE_URL}/create-roster/"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Requesting Roster...")
    try:
        response = requests.post(url, json={"flight_number": "TK1001"}, headers=headers)
        
        if response.status_code != 201:
            print(f"Failed to create roster. Code: {response.status_code}")
            print(response.text)
            return

        data = response.json()
    except Exception as e:
        print(f"Error requesting roster: {e}")
        return

    # 3. Analyze Results
    print(f"\nFlight: {data['flight_info']['number']} - Seat Distribution Analysis")
    print("=" * 60)

    errors = 0
    correct_business = 0
    correct_economy = 0

    for p in data['passengers']:
        seat = p.get('seat_number')
        # Use 'economy' as default if type is missing
        p_type = p.get('type', 'economy') 
        
        if seat == "INFANT" or seat == "STANDBY" or not seat:
            continue

        # Extract row number from seat string (e.g., "12A" -> 12)
        match = re.match(r"(\d+)([A-F])", seat)
        if match:
            row = int(match.group(1))
            
            # --- RULE CHECK ---
            
            # Business: Rows 1-5
            if p_type == 'business':
                if 1 <= row <= 5:
                    correct_business += 1
                else:
                    print(f"ERROR! Business passenger in Economy seat: {p['name']} ({seat})")
                    errors += 1
            
            # Economy: Rows 6-30
            elif p_type == 'economy':
                if row >= 6:
                    correct_economy += 1
                else:
                    # Note: If Economy is full, our algorithm allows upgrading to Business
                    print(f"Warning: Economy passenger in Business seat (Lucky!): {p['name']} ({seat})")

    print("-" * 60)
    print(f"Correct Business Seating : {correct_business}")
    print(f"Correct Economy Seating  : {correct_economy}")
    print(f"Incorrect Seating        : {errors}")

    if errors == 0:
        print("\nRESULT: PERFECT! Seat type separation is working correctly.")
    else:
        print("\nRESULT: There are some issues. Check the algorithm or data.")

if __name__ == "__main__":
    test_seat_distribution()