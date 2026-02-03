import requests

# defining base api endpoints
FLIGHT_API_URL = "http://127.0.0.1:8000/api"
CREW_API_URL = "http://127.0.0.1:8002/api"

class FlightService:
    @staticmethod
    def get_all_flights():
        """fetch list of all available flights"""
        try:
            response = requests.get(f"{FLIGHT_API_URL}/flights/")
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Connection Error: {e}")
        return []

    @staticmethod
    def get_flight_passengers(flight_number):
        try:
            response = requests.get(f"{FLIGHT_API_URL}/passengers/", params={'flight_number': flight_number})
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Connection Error: {e}")
        return []
    
    @staticmethod
    def get_flight_details(flight_id):
        try:
            response = requests.get(f"{FLIGHT_API_URL}/flights/{flight_id}/")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error: {e}")
        return None

class CrewService:
    @staticmethod
    def get_vehicle_id_by_name(vehicle_name):
        """
        need to swap the vehicle name (string) with its database ID to make queries work.
        """
        try:
            # querying the api with search param
            response = requests.get(f"{CREW_API_URL}/vehicles/", params={'search': vehicle_name})
            if response.status_code == 200:
                data = response.json()
                
                # handle pagination: sometimes the data is wrapped in 'results', sometimes it's just a list.
                results = data.get('results', data) if isinstance(data, dict) else data

                if results:
                    for vehicle in results:
                        if vehicle['name'] == vehicle_name:
                            return vehicle['id']
        except Exception as e:
            print(f"Vehicle ID Lookup Error: {e}")
        return None
    
    @staticmethod
    def get_all_attendants():
        """
        grab all the cabin crew data from the crew service.
        """
        try:
            # endpoint for attendants
            url = f"{CREW_API_URL}/attendants/" 
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                # check if response is paginated or flat list
                if isinstance(data, dict) and 'results' in data:
                    return data['results']
                return data
            return []
        except Exception as e:
            print(f"Cabin Crew Fetch Error: {e}")
            return []

    @staticmethod
    def get_all_pilots():
        """
        fetch every pilot without filtering. needed for the general info page.
        """
        try:
            # endpoint: /api/pilots/
            response = requests.get(f"{CREW_API_URL}/pilots/")
            
            if response.status_code == 200:
                data = response.json()
                
                # --- pagination check (keeping logic consistent) ---
                if isinstance(data, dict) and 'results' in data:
                    return data['results']
                
                return data 
            else:
                print(f"Pilot List Error: Status {response.status_code}")
                return []
        except Exception as e:
            print(f"All Pilots API Error: {e}")
            return []

    @staticmethod
    def get_pilots_for_vehicle(vehicle_name):
        # step 1: get the ID first since the API expects that
        vehicle_id = CrewService.get_vehicle_id_by_name(vehicle_name)
        if not vehicle_id: 
            return []

        # step 2: hit the endpoint with the ID
        try:
            response = requests.get(f"{CREW_API_URL}/pilots/", params={'vehicle_type': vehicle_id})
            if response.status_code == 200:
                data = response.json()
                
                # DRF sometimes wraps response in a dict, check for 'results' key
                if isinstance(data, dict) and 'results' in data:
                    return data['results']
                
                # otherwise assume it's a flat list
                return data 
        except Exception as e:
            print(f"Pilot API Error: {e}")
        return []

    @staticmethod
    def get_attendants_for_vehicle(vehicle_name):
        vehicle_id = CrewService.get_vehicle_id_by_name(vehicle_name)
        if not vehicle_id: 
            return []

        try:
            response = requests.get(f"{CREW_API_URL}/attendants/", params={'vehicle_type': vehicle_id})
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, dict) and 'results' in data:
                    return data['results']
                return data
        except Exception as e:
            print(f"Cabin API Error: {e}")
        return []
    
    @staticmethod
    def get_chef_recipes(chef_id):
        """
        get recipes associated with a specific chef ID.
        """
        try:
            response = requests.get(f"{CREW_API_URL}/recipes/by-chef/{chef_id}/")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Recipe Fetch Error: {e}")
        return []
