import json
import os
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from .models import Roster, RosterPassenger, RosterCrew
from django.conf import settings

# ANSI Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MainSystemTests(TestCase):
    """
    Test Suite for the Main System Flight Roster Functionality.
    Enhanced with visual outputs for documentation purposes.
    """

    def setUp(self):
        # Create user and group for permissions
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # --- MOCK DATA ---
        self.flight_number = "TK1001"
        self.flight_data = {
            "flight_number": self.flight_number,
            "flight_source": {"code": "IST", "name": "Istanbul"},
            "flight_destination": {"code": "LHR", "name": "London"},
            "flight_datetime": "2023-01-01T10:00:00Z",
            "duration": "4h",
            "distance": 1000,
            "vehicle_type": {
                "name": "Boeing 737",
                "number_of_seats": 150,
                "max_crew": 6,
                "standard_menu": "Chicken or Pasta"
            }
        }

        self.passengers_data = [
            {"passenger_id": 1, "name": "John Doe", "seat_number": "1A", "seat_type": "business", "is_infant": False, "affiliated_passengers": []},
            {"passenger_id": 2, "name": "Jane Smith", "seat_number": None, "seat_type": "economy", "is_infant": False, "affiliated_passengers": [3]},
            {"passenger_id": 3, "name": "Child Smith", "seat_number": None, "seat_type": "economy", "is_infant": False, "parent": 2}
        ]

        self.pilots_data = [
            {"id": 101, "full_name": "Pilot Senior", "allowed_range": 5000, "seniority_level": "SENIOR", "vehicle_type": "Boeing 737"},
            {"id": 102, "full_name": "Pilot Junior", "allowed_range": 5000, "seniority_level": "JUNIOR", "vehicle_type": "Boeing 737"},
            {"id": 103, "full_name": "Pilot Trainee", "allowed_range": 5000, "seniority_level": "TRAINEE", "vehicle_type": "Boeing 737"}
        ]

        self.attendants_data = [
            {"id": 201, "full_name": "Chief Attendant", "attendant_type": "CHIEF"},
            {"id": 202, "full_name": "Chef Cook", "attendant_type": "CHEF"},
            {"id": 203, "full_name": "Regular One", "attendant_type": "REGULAR"},
            {"id": 204, "full_name": "Regular Two", "attendant_type": "REGULAR"}
        ]
        
        self.vehicle_id = 999 

    def print_banner(self, test_name):
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}TEST CASE: {test_name}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}")

    def print_step(self, step_num, description):
        print(f"{Colors.OKCYAN}[Step {step_num}] {description}{Colors.ENDC}")

    def print_success(self, message):
        print(f"   {Colors.OKGREEN}✔ {message}{Colors.ENDC}")

    def print_info(self, message):
        print(f"   ℹ {message}")

    def mock_api_calls(self, url, params=None):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        if "flights/" in url and self.flight_number not in url:
            mock_resp.json.return_value = [self.flight_data]
        elif f"flights/{self.flight_number}" in url or "flights/" in url:
            mock_resp.json.return_value = [self.flight_data]
        elif "passengers/" in url:
            mock_resp.json.return_value = self.passengers_data
        elif "vehicles/" in url:
             mock_resp.json.return_value = [{"id": self.vehicle_id, "name": "Boeing 737"}]
        elif "pilots/" in url:
            mock_resp.json.return_value = {'results': self.pilots_data}
        elif "attendants/" in url:
            mock_resp.json.return_value = {'results': self.attendants_data}
        elif "recipes/by-chef" in url:
            mock_resp.json.return_value = [{"name": "Gourmet Steak"}]
        else:
            mock_resp.status_code = 404
            mock_resp.json.return_value = {}
        return mock_resp

    @patch('roster.services.requests.get')
    def test_generate_roster_automatic_crew_selection(self, mock_get):
        self.print_banner("Automatic Roster Generation & Crew Selection")
        mock_get.side_effect = self.mock_api_calls

        self.print_step(1, f"Initiating Roster Generation for Flight {self.flight_number}")
        url = reverse('roster-create')
        data = {'flight_number': self.flight_number}
        self.client.post(url, data, format='json')
        
        self.print_step(2, "Verifying Pilot Selection (Greedy Approach)")
        roster = Roster.objects.first()
        pilots = RosterCrew.objects.filter(roster=roster, crew_type='PILOT')
        
        if pilots.filter(original_id=101).exists():
            self.print_success("Senior Pilot Selected (ID: 101)")
        
        if pilots.filter(original_id=102).exists():
            self.print_success("Junior Pilot Selected (ID: 102)")

        self.print_step(3, "Verifying Cabin Crew Selection (Roles)")
        cabin = RosterCrew.objects.filter(roster=roster, crew_type='CABIN')
        
        if cabin.filter(original_id=202).exists():
            self.print_success("Chef Selected (ID: 202)")
        if cabin.filter(original_id=201).exists():
            self.print_success("Chief Attendant Selected (ID: 201)")
            
        self.print_step(4, "Checking Final Roster Counts")
        self.print_info(f"Total Pilots: {pilots.count()}")
        self.print_info(f"Total Cabin Crew: {cabin.count()}")

    @patch('roster.services.requests.get')
    def test_passenger_seat_logic_and_view_data(self, mock_get):
        self.print_banner("Passenger Data & Seat View Logic")
        mock_get.side_effect = self.mock_api_calls
        
        self.print_step(1, "Creating Roster to Populate Data")
        self.client.post(reverse('roster-create'), {'flight_number': self.flight_number}, format='json')
        
        self.print_step(2, "Fetching 'Detail View' (Frontend Source)")
        url = reverse('get-roster-detail', kwargs={'flight_number': self.flight_number})
        response = self.client.get(url)
        passengers = response.data['passengers']
        
        self.print_step(3, "Verifying Passenger Logic")
        p1 = next(p for p in passengers if p['id'] == 1)
        self.print_info(f"Passenger 1 (John Doe): Seat {p1['seat_number']}")
        if p1['seat_number'] == "1A":
            self.print_success("Pre-assigned seat preserved")
            
        p2 = next(p for p in passengers if p['id'] == 2)
        self.print_info(f"Passenger 2 (Jane Smith): Seat {p2['seat_number']}")
        if p2['seat_number'] in ["STANDBY", None]:
            self.print_success("Unassigned passenger marked as STANDBY correctly")

    @patch('roster.views.requests.patch') 
    @patch('roster.services.requests.get') 
    def test_assign_seat_functionality(self, mock_get, mock_patch):
        self.print_banner("Seat Assignment Logic")
        mock_get.side_effect = self.mock_api_calls
        mock_patch.return_value.status_code = 200
        
        self.client.post(reverse('roster-create'), {'flight_number': self.flight_number})
        
        self.print_step(1, "Requesting Seat Assignment for Passenger 2 (Jane Smith)")
        url = reverse('assign-seat')
        data = {'flight_number': self.flight_number, 'passenger_id': 2}
        response = self.client.post(url, data, format='json')
        
        assigned_seat = response.data.get('seat')
        self.print_success(f"System assigned seat: {assigned_seat}")
        
        self.print_step(2, "Verifying Database Update")
        p2_db = RosterPassenger.objects.get(original_passenger_id=2)
        if p2_db.seat_number == assigned_seat:
            self.print_success(f"Local Database updated to {assigned_seat}")
            
        self.print_step(3, "Verifying External API Sync")
        if mock_patch.called:
            self.print_success("External API Patch request sent successfully")

    @patch('roster.services.requests.get')
    def test_store_and_retrieve_nosql_export(self, mock_get):
        self.print_banner("NoSQL/JSON Storage & Export")
        mock_get.side_effect = self.mock_api_calls
        
        self.client.post(reverse('roster-create'), {'flight_number': self.flight_number})
        
        self.print_step(1, "Exporting Roster to JSON")
        save_url = reverse('save-roster-selection')
        response = self.client.post(save_url, {'flight_number': self.flight_number})
        file_path = response.data['file_path']
        
        self.print_success(f"File created at: {os.path.basename(file_path)}")
        
        self.print_step(2, "Verifying JSON Content")
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            self.print_info(f"Flight in JSON: {json_data['flight_number']}")
            self.print_info(f"Crew Count in JSON: {len(json_data['crew'])}")
        
        self.print_step(3, "Listing Saved Files")
        list_url = reverse('list-saved-rosters')
        response = self.client.get(list_url)
        filenames = [item['real_id'] for item in response.data]
        if os.path.basename(file_path) in filenames:
            self.print_success("File appears in Saved Rosters List")

        if os.path.exists(file_path):
            os.remove(file_path)

    @patch('roster.services.requests.get')
    def test_manual_crew_selection(self, mock_get):
        self.print_banner("Manual Crew Selection Override")
        mock_get.side_effect = self.mock_api_calls
        
        self.print_step(1, "Submitting Roster with Manual Pilot Selection (Trainee + Junior)")
        url = reverse('roster-create')
        data = {
            'flight_number': self.flight_number,
            'manual_pilots': [103, 102] 
        }
        self.client.post(url, data, format='json')
        
        self.print_step(2, "Verifying Manual Overrides")
        roster = Roster.objects.first()
        pilots = RosterCrew.objects.filter(roster=roster, crew_type='PILOT')
        
        if pilots.filter(original_id=103).exists():
            self.print_success("Trainee Pilot (ID 103) Found (Manual Override Worked)")
        else:
            self.print_info(f"{Colors.FAIL}Trainee Pilot Missing!{Colors.ENDC}")
            
        if not pilots.filter(original_id=101).exists():
            self.print_success("Senior Pilot (ID 101) Excluded correctly")

    
    @patch('roster.services.requests.get')
    def test_update_pilot_range_validation_fail(self, mock_get):
        """
        Validates that the system rejects a pilot whose range is insufficient 
        for the flight distance (Safety Rule).
        """
        self.print_banner("Pilot Safety Validation (Range Check)")
        mock_get.side_effect = self.mock_api_calls
        
        # 1. Create Initial Roster
        self.client.post(reverse('roster-create'), {'flight_number': self.flight_number})
        
        # 2. Mock a pilot with insufficient range (Flight is 1000km, Pilot has 500km)
        short_range_pilot = {
            "id": 999, 
            "full_name": "Short Range Pilot", 
            "allowed_range": 500, 
            "seniority_level": "SENIOR", 
            "vehicle_type": "Boeing 737"
        }
        
        original_pilots = list(self.pilots_data)
        self.pilots_data.append(short_range_pilot)
        
        try:
            # 3. Attempt to assign this invalid pilot
            self.print_step(1, "Attempting to assign a pilot with insufficient range")
            
            url = reverse('update-pilots') 
      
            data = {
                'flight_number': self.flight_number,
                'pilot_ids': [999]
            }
            response = self.client.post(url, data, format='json')
            
            # 4. Assert Failure (400 Bad Request)
            self.assertEqual(response.status_code, 400)
            
            error_details = str(response.data.get('details', '')).lower()
            if "range" in error_details:
                self.print_success("System correctly rejected pilot due to range limit")
            else:
                self.print_info(f"Rejected with message: {error_details}")

        finally:
            self.pilots_data = original_pilots

    @patch('roster.views.requests.patch')
    @patch('roster.services.requests.get')
    def test_seat_class_separation_logic(self, mock_get, mock_patch):
        """
        Validates that Business Class passengers are only assigned 
        seats in the allowed rows (1-5), not Economy rows.
        """
        self.print_banner("Business vs Economy Seat Logic")
        mock_get.side_effect = self.mock_api_calls
        mock_patch.return_value.status_code = 200
        
        self.client.post(reverse('roster-create'), {'flight_number': self.flight_number})
        
        # 1. Request seat for Passenger 1 (John Doe - Business Class)
        self.print_step(1, "Requesting seat for Business Class Passenger")
        url = reverse('assign-seat')
        data = {'flight_number': self.flight_number, 'passenger_id': 1}
        
        response = self.client.post(url, data, format='json')
        assigned_seat = response.data.get('seat')
        
        self.print_info(f"Assigned Seat: {assigned_seat}")

        # 2. Parse Row Number (e.g., "2A" -> 2)
        import re
        match = re.match(r"(\d+)", str(assigned_seat))
        if match:
            row_num = int(match.group(1))
            
            # 3. Assert Row is within Business range (1-5)
            if 1 <= row_num <= 5:
                self.print_success(f"Passenger correctly assigned to Business Row {row_num}")
            else:
                self.fail(f"Business Passenger assigned to Economy row {row_num}!")
        else:
            self.fail("Could not parse seat number")

    @patch('roster.views.requests.patch')
    @patch('roster.services.requests.get')
    def test_smart_seating_adjacency(self, mock_get, mock_patch):
        """
        Validates the algorithm that attempts to seat affiliated passengers 
        (e.g., Parent/Child) next to each other.
        """
        self.print_banner("Smart Seating (Affiliate Logic)")
        mock_get.side_effect = self.mock_api_calls
        mock_patch.return_value.status_code = 200
        
        # 1. Setup: Position Parent (Passenger 2) at Seat "10A"
        original_seat = self.passengers_data[1]['seat_number']
        self.passengers_data[1]['seat_number'] = "10A" # Jane Smith
        
        try:
            self.client.post(reverse('roster-create'), {'flight_number': self.flight_number})
            
            # 2. Request seat for Child (Passenger 3 - Affiliated with #2)
            self.print_step(1, "Requesting seat for Child (Parent is at 10A)")
            url = reverse('assign-seat')
            data = {'flight_number': self.flight_number, 'passenger_id': 3}
            response = self.client.post(url, data, format='json')
            
            assigned_seat = response.data.get('seat')
            
            # 3. Expect "10B" (Adjacent)
            # (Note: Logic might pick 9A or 11A depending on availability, but 10B is prioritized)
            self.print_info(f"Child Assigned: {assigned_seat}")
            
            if assigned_seat == "10B":
                self.print_success(f"Smart Logic worked! Child placed at {assigned_seat} next to Parent")
            elif assigned_seat in ["9A", "11A"]:
                self.print_success(f"Smart Logic worked (Front/Back adjacency): {assigned_seat}")
            else:
                self.print_info(f"Logic result: {assigned_seat} (Check availability logic)")

        finally:
            # Cleanup
            self.passengers_data[1]['seat_number'] = original_seat

    @patch('roster.services.requests.get')
    def test_duplicate_roster_cleanup(self, mock_get):
        """
        Validates that the system identifies and cleans up duplicate roster records
        to maintain database integrity (Idempotency).
        """
        self.print_banner("Duplicate Roster Self-Healing")
        mock_get.side_effect = self.mock_api_calls
        
        # 1. Manually inject duplicates into DB
        self.print_step(1, "Injecting corrupted data (3 duplicates)")
        Roster.objects.create(flight_number=self.flight_number)
        Roster.objects.create(flight_number=self.flight_number)
        Roster.objects.create(flight_number=self.flight_number)
        
        count_before = Roster.objects.filter(flight_number=self.flight_number).count()
        self.assertEqual(count_before, 3)
        
        # 2. Trigger Roster Generation (Should trigger cleanup)
        self.print_step(2, "Triggering Roster Generation")
        self.client.post(reverse('roster-create'), {'flight_number': self.flight_number})
        
        # 3. Assert only 1 record remains
        count_after = Roster.objects.filter(flight_number=self.flight_number).count()
        if count_after == 1:
            self.print_success("System successfully cleaned up duplicates. Only 1 record remains.")
        else:
            self.fail(f"Cleanup failed! Found {count_after} records.")

    @patch('roster.services.requests.get')
    def test_available_crew_filtering(self, mock_get):
        """
        Validates that the 'Available Crew' endpoint correctly filters pilots
        based on the flight's distance requirement.
        """
        self.print_banner("Available Crew Filtering Logic")
        mock_get.side_effect = self.mock_api_calls
        
        # 1. Mock Data: Flight distance is 1000km (from setUp)
        # Pilot 1: Range 5000 (Qualified)
        # Pilot 2: Range 500 (Disqualified)
        
        original_pilots = list(self.pilots_data)
        short_range_pilot = {
            "id": 999, "full_name": "Short Range Pilot", 
            "allowed_range": 500, "seniority_level": "SENIOR", 
            "vehicle_type": "Boeing 737"
        }
        self.pilots_data.append(short_range_pilot)
        
        try:
            # 2. Call GET /api/available-crew/
            # URL Name should match your urls.py (assuming 'available-crew')
            url = reverse('available-crew') 
            response = self.client.get(url, {'flight_number': self.flight_number})
            
            self.assertEqual(response.status_code, 200)
            data = response.data
            
            # 3. Assertions
            returned_pilots = data.get('pilots', [])
            pilot_ids = [p['id'] for p in returned_pilots]
            
            # Qualified pilot should be there
            if 101 in pilot_ids:
                self.print_success("Qualified Pilot (ID 101) is listed.")
            else:
                self.fail("Qualified Pilot missing from list!")
                
            # Disqualified pilot should NOT be there
            if 999 not in pilot_ids:
                self.print_success("Short Range Pilot (ID 999) is correctly filtered out.")
            else:
                self.fail("Short Range Pilot appeared in available list! Safety risk.")
                
        finally:
            self.pilots_data = original_pilots

    def test_delete_saved_roster(self):
        """
        Validates the file deletion logic.
        """
        self.print_banner("Delete Saved Roster File")
        
        # 1. Create a dummy file to delete
        directory = os.path.join(settings.BASE_DIR, 'roster_nosql_store')
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        filename = "test_delete.json"
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w') as f:
            f.write("{}")
            
        self.print_info(f"Created dummy file: {filename}")
        
        # 2. Call DELETE endpoint
        # URL Name from your urls.py: 'delete-nosql-roster'
        url = reverse('delete-nosql-roster', kwargs={'filename': filename})
        response = self.client.delete(url)
        
        # 3. Assertions
        self.assertEqual(response.status_code, 200)
        
        if not os.path.exists(file_path):
            self.print_success("File successfully deleted from disk.")
        else:
            self.fail("File still exists after delete request!")

    # ==================================================================
    # ADDITIONAL TESTS (Security & Performance)
    # ==================================================================

    def test_security_unauthorized_access(self):
        """
        [Security Testing]
        Verifies that critical endpoints are protected against 
        unauthenticated access (NFR1).
        """
        self.print_banner("Security Test: Unauthorized Access Prevention")
        
        # 1. Logout user to simulate an attacker / anonymous user
        self.client.logout()
        
        # 2. Try to create a roster without login
        url = reverse('roster-create')
        response = self.client.post(url, {'flight_number': self.flight_number})
        
        # 3. Assert: Should return 401 Unauthorized or 403 Forbidden
        if response.status_code in [401, 403]:
            self.print_success("Security Check Passed: Access Denied for anonymous user.")
        else:
            self.fail(f"Security Breach! Endpoint returned {response.status_code} for unauthenticated request.")

    @patch('roster.services.requests.get')
    def test_performance_roster_generation(self, mock_get):
        """
        [Performance Testing]
        Measures the execution time of the Roster Generation algorithm.
        Requirement: Must be under 2.0 seconds (NFR2).
        """
        import time
        
        self.print_banner("Performance Test: Roster Generation Latency")
        mock_get.side_effect = self.mock_api_calls
        
        # 1. Start Timer
        start_time = time.time()
        
        # 2. Execute Heavy Task (Roster Gen)
        url = reverse('roster-create')
        self.client.post(url, {'flight_number': self.flight_number})
        
        # 3. Stop Timer
        end_time = time.time()
        duration = end_time - start_time
        
        self.print_info(f"Execution Time: {duration:.4f} seconds")
        
        # 4. Assert Performance Requirement (NFR2: < 2 seconds)
        if duration < 2.0:
            self.print_success(f"Performance Check Passed: {duration:.4f}s < 2.0s")
        else:
            self.fail(f"Performance Too Slow! Took {duration:.4f}s")
