import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import FlightService, CrewService
from .models import Roster, RosterPassenger, RosterCrew
import random
from rest_framework.permissions import IsAuthenticated
import json
import os
from django.conf import settings
from datetime import datetime
from django.db import transaction  
from .permissions import IsStandardUser
    

class AvailableCrewView(APIView):
    """
    grabs all suitable crew (pilots with correct range + vehicle type matching)
    for the manual selection box on the frontend.
    usage: GET /api/available-crew/?flight_number=TK1001
    """
    permission_classes = [IsAuthenticated, IsStandardUser]
    def get(self, request):
        flight_number = request.query_params.get('flight_number')
        if not flight_number:
            return Response({"error": "Flight number required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. fetch flight details
        all_flights = FlightService.get_all_flights()
        flight_info = next((f for f in all_flights if f['flight_number'] == flight_number), None)
        
        if not flight_info:
            return Response({"error": "Flight not found"}, status=status.HTTP_404_NOT_FOUND)

        vehicle_name = flight_info['vehicle_type']['name']
        flight_distance = float(flight_info.get('distance', 0))

        # 2. filter pilots by vehicle type and range check
        all_pilots = CrewService.get_pilots_for_vehicle(vehicle_name)
        qualified_pilots = [
            p for p in all_pilots 
            if float(p.get('allowed_range', 0)) >= flight_distance
        ]

        # 3. get eligible cabin crew
        all_attendants = CrewService.get_attendants_for_vehicle(vehicle_name)

        return Response({
            "vehicle": vehicle_name,
            "flight_distance": flight_distance,
            "pilots": qualified_pilots,
            "attendants": all_attendants
        })

class FlightListView(APIView):
    permission_classes = [IsAuthenticated, IsStandardUser]
    def get(self, request):
        flights = FlightService.get_all_flights()
        return Response(flights, status=status.HTTP_200_OK)
    

class PilotListView(APIView):
    permission_classes = [IsAuthenticated, IsStandardUser] # only logged-in users can see this

    def get(self, request):
        # asking service layer for all pilots.
        try:
            pilots = CrewService.get_all_pilots() 
            return Response(pilots, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CabinCrewListView(APIView):
    permission_classes = [IsAuthenticated, IsStandardUser]

    def get(self, request):
        try:
            crew = CrewService.get_all_attendants()
            return Response(crew, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RosterCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStandardUser]
    
    def post(self, request):
        flight_number = request.data.get('flight_number')
        
        # handle manual selections from frontend (populated when switch is toggled)
        manual_pilot_ids = request.data.get('manual_pilots', [])
        manual_attendant_ids = request.data.get('manual_attendants', [])
        
        if not flight_number:
            return Response({"error": "Flight number is required"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. get flight info from main system
        all_flights = FlightService.get_all_flights()
        flight_info = next((f for f in all_flights if f['flight_number'] == flight_number), None)
        
        vehicle_name = "Unknown"
        vehicle_capacity = 0  
        flight_distance = 0
        standard_menu = "Standard Airline Food"
        
        # target crew size (should ideally come from DB)
        target_total_crew = 6 

        # response vars
        source_info, dest_info, flight_dt, duration = {}, {}, "", ""
        flight_menu = standard_menu

        if flight_info:
            try:
                raw_dist = flight_info.get('distance', 0)
                if isinstance(raw_dist, (int, float)):
                    flight_distance = float(raw_dist)
                elif isinstance(raw_dist, str):
                    import re
                    clean_dist = re.sub(r"[^0-9\.]", "", raw_dist)
                    if clean_dist:
                        flight_distance = float(clean_dist)
            except:
                flight_distance = 0

            if 'vehicle_type' in flight_info:
                vt = flight_info['vehicle_type']
                if isinstance(vt, dict):
                    vehicle_name = vt.get('name', vehicle_name)
                    vehicle_capacity = vt.get('number_of_seats', 0) 
                    
                    target_total_crew = vt.get('max_crew', 6)
                    
                    standard_menu = vt.get('standard_menu', standard_menu)

            source_info = flight_info.get('flight_source', {})
            dest_info = flight_info.get('flight_destination', {})
            flight_dt = flight_info.get('flight_datetime') or flight_info.get('departure_time') or ""
            duration = flight_info.get('duration', "")

        existing_rosters = Roster.objects.filter(flight_number=flight_number)
        
        if existing_rosters.count() > 1:
            print(f"DEBUG: Found duplicates for {flight_number}. Cleaning up...")
            first_roster = existing_rosters.first()
            # keep the first one, delete the rest
            existing_rosters.exclude(pk=first_roster.pk).delete()
            roster = first_roster
        elif existing_rosters.count() == 1:
            roster = existing_rosters.first()
        else:
            roster = Roster.objects.create(flight_number=flight_number)
        
        RosterPassenger.objects.filter(roster=roster).delete()
        RosterCrew.objects.filter(roster=roster).delete()

        # ==========================================
        # SECTION A: CREW ASSIGNMENT
        # ==========================================
        assigned_crew = []
        
        # --- 1. PILOTS ---
        all_pilots = CrewService.get_pilots_for_vehicle(vehicle_name)
        qualified_pilots = [p for p in all_pilots if float(p.get('allowed_range', 0)) >= flight_distance]
        
        selected_pilots = []

        if manual_pilot_ids:
            str_manual_ids = [str(x) for x in manual_pilot_ids]
            for p in qualified_pilots:
                p_id = p.get('pilot_id', p.get('id'))
                if str(p_id) in str_manual_ids:
                    selected_pilots.append(p)
        else:
            # auto selection logic based on seniority
            seniors = [p for p in qualified_pilots if p.get('seniority_level') == 'SENIOR']
            juniors = [p for p in qualified_pilots if p.get('seniority_level') == 'JUNIOR']
            trainees = [p for p in qualified_pilots if p.get('seniority_level') == 'TRAINEE']
            
            if seniors: selected_pilots.append(seniors[0])
            if juniors: selected_pilots.append(juniors[0])
            if len(selected_pilots) < 2 and trainees: selected_pilots.append(trainees[0])
            if len(selected_pilots) < 2 and len(seniors) > 1: selected_pilots.append(seniors[1])

        # save pilots to DB
        for p in selected_pilots:
            c = RosterCrew.objects.create(
                roster=roster,
                original_id=p.get('pilot_id', p.get('id', 0)),
                name=p.get('full_name', p.get('first_name', 'Unknown')),
                role=p.get('seniority_level', 'UNKNOWN'),
                crew_type='PILOT'
            )
            assigned_crew.append({
                "name": c.name, 
                "role": c.role, 
                "type": "PILOT",
                "original_id": c.original_id
            })

        # --- 2. CABIN CREW (BASED ON TARGET COUNT) ---
        
        # subtract pilots from total, use remainder for cabin slots
        cabin_slots_needed = target_total_crew - len(selected_pilots)
        if cabin_slots_needed < 3: cabin_slots_needed = 3 # minimum safety requirement

        print(f"DEBUG: Filling {cabin_slots_needed} cabin slots for {flight_number}")

        raw_attendants = CrewService.get_attendants_for_vehicle(vehicle_name)
        
        attendants_data = []
        seen_ids = set()
        for att in raw_attendants:
            a_id = att.get('attendant_id', att.get('id'))
            if a_id and a_id not in seen_ids:
                seen_ids.add(a_id)
                attendants_data.append(att)
        
        selected_attendants = []

        if manual_attendant_ids:
            # manual selection overrides logic
            str_manual_ids = [str(x) for x in manual_attendant_ids]
            for att in attendants_data:
                a_id = att.get('attendant_id', att.get('id'))
                if str(a_id) in str_manual_ids:
                    selected_attendants.append(att)
        else:
            # Auto distribution logic
            chiefs = [c for c in attendants_data if c.get('attendant_type') == 'CHIEF']
            regulars = [c for c in attendants_data if c.get('attendant_type') == 'REGULAR']
            chefs = [c for c in attendants_data if c.get('attendant_type') == 'CHEF']
            
            # 1. add a chef
            if cabin_slots_needed > 0 and chefs:
                selected_attendants.append(chefs[0])
                chefs.pop(0)
                cabin_slots_needed -= 1
            
            # 2. add a chief
            if cabin_slots_needed > 0 and chiefs:
                selected_attendants.append(chiefs[0])
                chiefs.pop(0)
                cabin_slots_needed -= 1

            # 3. fill remaining with regulars
            while cabin_slots_needed > 0 and regulars:
                selected_attendants.append(regulars[0])
                regulars.pop(0)
                cabin_slots_needed -= 1
            
            # 4. still need slots? fallback to other types
            extra_chiefs_limit = 3
            while cabin_slots_needed > 0 and chiefs and extra_chiefs_limit > 0:
                selected_attendants.append(chiefs[0])
                chiefs.pop(0)
                extra_chiefs_limit -= 1
                cabin_slots_needed -= 1
            
            if cabin_slots_needed > 0 and chefs:
                selected_attendants.append(chefs[0])
                chefs.pop(0)
                cabin_slots_needed -= 1
            
        # Menu Logic based on Chef
        flight_menu = standard_menu
        active_chef = next((a for a in selected_attendants if a.get('attendant_type') == 'CHEF'), None)
        if active_chef:
            chef_id = active_chef.get('attendant_id', active_chef.get('id'))
            try:
                recipes = CrewService.get_chef_recipes(chef_id)
                if recipes:
                    random_recipe = random.choice(recipes)
                    recipe_name = random_recipe.get('name', 'Special Meal')
                    flight_menu = f"{recipe_name} (Prepared by Chef {active_chef.get('full_name')})"
            except: pass

        # write cabin crew to DB
        for att in selected_attendants:
            c = RosterCrew.objects.create(
                roster=roster,
                original_id=att.get('attendant_id', att.get('id', 0)),
                name=att.get('full_name', att.get('first_name', 'Unknown')),
                role=att.get('attendant_type', 'UNKNOWN'),
                crew_type='CABIN'
            )
            assigned_crew.append({
                "name": c.name, 
                "role": c.role, 
                "type": "CABIN",
                "original_id": c.original_id
            })

        # ==========================================
        # SECTION B: PASSENGERS
        # ==========================================
        api_passengers = FlightService.get_flight_passengers(flight_number)
        final_passenger_objects = []
        processed_ids = set()
        
        for p_data in api_passengers:
            p_id = p_data.get('passenger_id')
            original_seat = p_data.get('seat_number')
            is_infant = p_data.get('is_infant', False)
            
            if is_infant:
                final_seat = "INFANT" # special code for infants
            elif original_seat:
                final_seat = original_seat # preserve existing seat
            else:
                final_seat = None # if no seat, send null to frontend (assignment pending)
            
            rp = RosterPassenger.objects.create(
                roster=roster,
                original_passenger_id=p_id,
                name=p_data.get('name', 'Unknown'),
                seat_number=final_seat if final_seat else "STANDBY",
                is_infant=is_infant
            )
            
             # sending 'final_seat' (could be None) as seat_number here
            final_passenger_objects.append({
                "id": p_id,
                "name": rp.name,
                "age": p_data.get('age', 0),
                "gender": p_data.get('gender', 'N/A'),
                "nationality": p_data.get('nationality', 'N/A'),
                "seat_number": final_seat if final_seat else "STANDBY", # frontend mapping will handle this
                "type": p_data.get('seat_type', 'economy'),
                "is_infant": rp.is_infant,
                "parent_id": p_data.get('parent'),
                "affiliated_passengers": p_data.get('affiliated_passengers', [])
            })

            processed_ids.add(p_id)

        # --- FINAL RESPONSE ---
        return Response({
            "message": "Roster generated successfully",
            "flight_info": {
                "number": flight_number,
                "vehicle": vehicle_name,
                "capacity": vehicle_capacity,
                "menu": flight_menu,
                "source": source_info,
                "destination": dest_info,
                "datetime": flight_dt,
                "duration": duration,
                "distance": flight_distance
            },
            "stats": {
                "total_passengers": len(final_passenger_objects),
                "total_crew": len(assigned_crew)
            },
            "crew": assigned_crew,
            "passengers": final_passenger_objects
        }, status=status.HTTP_201_CREATED)
            
class UpdatePilotRosterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        flight_number = request.data.get('flight_number')
        new_pilot_ids = request.data.get('pilot_ids', []) 

        if not flight_number or not new_pilot_ids:
            return Response({"error": "Flight number and pilot IDs are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        
        existing_rosters = Roster.objects.filter(flight_number=flight_number)
        
        if not existing_rosters.exists():
            return Response({"error": "Roster not found. Please create a roster first."}, status=status.HTTP_404_NOT_FOUND)

        if existing_rosters.count() > 1:
            print(f"DEBUG: Duplicate rosters found for {flight_number}. Fixing...")
            roster = existing_rosters.first() 
            existing_rosters.exclude(pk=roster.pk).delete()
        else:
            roster = existing_rosters.first()
        # -----------------------------------------------------------------

        all_flights = FlightService.get_all_flights()
        flight_info = next((f for f in all_flights if f['flight_number'] == flight_number), None)
        
        if not flight_info:
            return Response({"error": "Flight info not found in Main System"}, status=status.HTTP_404_NOT_FOUND)

        vehicle_name = flight_info.get('vehicle_type', {}).get('name', 'Unknown')
        
        raw_dist = flight_info.get('distance')
        try:
            flight_distance = float(raw_dist) if raw_dist is not None else 0
        except (ValueError, TypeError):
            flight_distance = 0

        # 2. Validation
        candidate_pilots = CrewService.get_pilots_for_vehicle(vehicle_name)
        target_ids = [str(pid) for pid in new_pilot_ids]
        
        valid_pilots_to_save = []
        errors = []

        for pid in target_ids:
            pilot_data = next((p for p in candidate_pilots if str(p.get('pilot_id', p.get('id'))) == pid), None)
            
            if not pilot_data:
                errors.append(f"Pilot {pid} is not certified for {vehicle_name}")
                continue

            pilot_range = float(pilot_data.get('allowed_range', 0))
            if pilot_range < flight_distance:
                errors.append(f"Pilot {pilot_data.get('full_name')} range ({pilot_range}) is less than flight distance ({flight_distance})")
                continue

            valid_pilots_to_save.append(pilot_data)

        if errors:
            return Response({
                "error": "Validation Failed",
                "details": errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 3. Database Update
        RosterCrew.objects.filter(roster=roster, crew_type='PILOT').delete()

        assigned_crew = []
        for p in valid_pilots_to_save:
            c = RosterCrew.objects.create(
                roster=roster,
                original_id=p.get('pilot_id', p.get('id')),
                name=p.get('full_name', 'Unknown'),
                role=p.get('seniority_level', 'UNKNOWN'),
                crew_type='PILOT'
            )
            assigned_crew.append({
                "name": c.name,
                "role": c.role,
                "original_id": c.original_id
            })

        return Response({
            "message": "Pilots updated successfully",
            "flight_number": flight_number,
            "current_pilots": assigned_crew
        }, status=status.HTTP_200_OK)

        # 3. DB Update (Transaction-like)
        RosterCrew.objects.filter(roster=roster, crew_type='PILOT').delete()

        assigned_crew = []
        for p in valid_pilots_to_save:
            c = RosterCrew.objects.create(
                roster=roster,
                original_id=p.get('pilot_id', p.get('id')),
                name=p.get('full_name', 'Unknown'),
                role=p.get('seniority_level', 'UNKNOWN'),
                crew_type='PILOT'
            )
            assigned_crew.append({
                "name": c.name,
                "role": c.role,
                "original_id": c.original_id
            })

        return Response({
            "message": "Pilots updated successfully",
            "flight_number": flight_number,
            "current_pilots": assigned_crew
        }, status=status.HTTP_200_OK)
    
class AssignSeatView(APIView):
    permission_classes = [IsAuthenticated, IsStandardUser]

    def post(self, request):
        passenger_id = request.data.get('passenger_id')
        flight_number = request.data.get('flight_number')

        if not passenger_id or not flight_number:
            return Response({"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Fetch Passengers (to find logic)
        api_passengers = FlightService.get_flight_passengers(flight_number)
        
        # Check for pagination (is 'results' key present?)
        if isinstance(api_passengers, dict) and 'results' in api_passengers:
            api_passengers = api_passengers['results']

        target_passenger = next((p for p in api_passengers if str(p['passenger_id']) == str(passenger_id)), None)

        if not target_passenger:
            return Response({"error": "Passenger not found"}, status=status.HTTP_404_NOT_FOUND)

        # 2. List Occupied Seats
        occupied_seats = {p['seat_number'] for p in api_passengers if p.get('seat_number')}

        # 3. Prepare Seat Pool
        seat_type = target_passenger.get('seat_type', 'economy')
        
        # Business 2-2 layout
        if seat_type == 'business':
            cols = ['A', 'C', 'D', 'F'] 
            rows = range(1, 6)
        else:
            cols = ['A', 'B', 'C', 'D', 'E', 'F'] 
            rows = range(6, 31)

        available_seats = []
        for r in rows:
            for c in cols:
                seat_code = f"{r}{c}"
                if seat_code not in occupied_seats:
                    available_seats.append(seat_code)

        if not available_seats:
            return Response({"error": "No seats available in this class"}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Smart Assignment Logic
        assigned_seat = None
        affiliates = target_passenger.get('affiliated_passengers', [])
        
        # Check if friends/family are nearby
        for friend_id in affiliates:
            friend = next((p for p in api_passengers if p['passenger_id'] == friend_id), None)
            if friend and friend.get('seat_number'):
                friend_seat = friend['seat_number']
                try:
                    # '10A' -> row:10, col:'A'
                    import re
                    match = re.match(r"([0-9]+)([A-Z])", friend_seat)
                    if match:
                        row_num = int(match.group(1))
                        col_char = match.group(2)
                        
                        if col_char in cols:
                            idx = cols.index(col_char)
                            # check left side
                            if idx > 0:
                                left_seat = f"{row_num}{cols[idx-1]}"
                                if left_seat in available_seats:
                                    assigned_seat = left_seat
                                    break
                            # check right side
                            if idx < len(cols) - 1:
                                right_seat = f"{row_num}{cols[idx+1]}"
                                if right_seat in available_seats:
                                    assigned_seat = right_seat
                                    break
                except Exception as e:
                    print(f"Seat logic error: {e}")
                    continue
        
        # no friends found? pick random
        if not assigned_seat:
            assigned_seat = random.choice(available_seats)

        # --- 5. UPDATE (VIA API) ---
        
        # A) FLIGHT API UPDATE (Remote)
        try:
            update_url = f"http://127.0.0.1:8000/api/passengers/{passenger_id}/"
            print(f"Updating seat via API: {update_url} -> {assigned_seat}")
            requests.patch(update_url, json={'seat_number': assigned_seat})
        except Exception as e:
            print(f"Flight API Connection Error: {e}")

        # B) UPDATE LOCAL DB
        try:
            # Find Roster first
            roster = Roster.objects.filter(flight_number=flight_number).first()
            if roster:
                # Find the passenger record in local DB
                local_passenger = RosterPassenger.objects.filter(
                    roster=roster, 
                    original_passenger_id=passenger_id
                ).first()
                
                if local_passenger:
                    local_passenger.seat_number = assigned_seat
                    local_passenger.save() # COMMIT
                    print(f"Local DB Updated: Passenger {passenger_id} -> {assigned_seat}")
                else:
                    print("Passenger not found in Local DB (RosterPassenger)")
        except Exception as e:
            print(f"Local DB Update Error: {e}")

        return Response({
            "message": "Seat assigned successfully",
            "seat": assigned_seat,
            "passenger": target_passenger.get('name', 'Passenger')
        })

# 1. VIEW FOR SAVING JSON ONLY

class SaveRosterDatabaseView(APIView):
    permission_classes = [IsAuthenticated, IsStandardUser]

    def post(self, request):
        flight_number = request.data.get('flight_number')

        if not flight_number:
            return Response({"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Find and Clean Roster (Duplicate Fix)
            existing_rosters = Roster.objects.filter(flight_number=flight_number)

            if not existing_rosters.exists():
                return Response({"error": "Roster not found (Please create it first)"}, status=status.HTTP_404_NOT_FOUND)
            
            if existing_rosters.count() > 1:
                print(f"DEBUG: Save View found duplicates for {flight_number}. Cleaning up...")
                roster = existing_rosters.first()
                existing_rosters.exclude(pk=roster.pk).delete()
            else:
                roster = existing_rosters.first()

            # 2. Shared Flight Info (FlightService)
            shared_data = {"is_shared": False, "airline": "", "flight_number": ""}
            try:
                all_flights = FlightService.get_all_flights()
                flight_info = next((f for f in all_flights if f['flight_number'] == flight_number), None)
                if flight_info:
                    shared_data["is_shared"] = bool(flight_info.get('is_shared', False))
                    shared_data["airline"] = flight_info.get('shared_airline_name', "")
                    shared_data["flight_number"] = flight_info.get('shared_flight_number', "")
            except Exception as e:
                print(f"Shared Info Fetch Error: {e}")
            
            # 3. Prepare CREW List (Local DB is authority)
            if hasattr(roster, 'crew_members'):
                raw_crew_list = roster.crew_members.all()
            else:
                raw_crew_list = roster.rostercrew_set.all() 

            unique_crew_map = {} 
            for c in raw_crew_list:
                unique_key = f"{c.crew_type}_{getattr(c, 'original_id', 0)}"
                
                if unique_key not in unique_crew_map:
                    raw_id = getattr(c, 'original_id', 0)
                    display_id = raw_id 
                    
                    if c.crew_type == 'PILOT':
                        display_id = f"P{raw_id}"
                    elif c.crew_type == 'CABIN':
                        display_id = f"C{raw_id}"

                    unique_crew_map[unique_key] = {
                        "name": c.name,
                        "role": c.role,
                        "type": c.crew_type,
                        "id": display_id, 
                    }
            
            clean_crew_data = list(unique_crew_map.values())

            # ----------------------------------------------------------------
            # 4. Prepare PASSENGER List
            # ----------------------------------------------------------------
            clean_passenger_data = []
            
            try:
                # A. Fetch Live Passenger List
                api_passengers = FlightService.get_flight_passengers(flight_number)
                
                # Pagination check
                if isinstance(api_passengers, dict):
                    api_passengers = api_passengers.get('results', [])
                if not isinstance(api_passengers, list):
                    api_passengers = []

                # B. Fetch Seat info from Local DB (from Assign Seat actions)
                local_seats = {
                    str(p.original_passenger_id): p.seat_number 
                    for p in RosterPassenger.objects.filter(roster=roster)
                }

                # C. Merge (Mapping)
                for p_data in api_passengers:
                    p_id = p_data.get('passenger_id')
                    if not p_id: continue

                    # Check if local has newer seat info. If not, use API's.
                    str_p_id = str(p_id)
                    current_seat = local_seats.get(str_p_id, p_data.get('seat_number'))
                    
                    # Cleanup
                    final_seat = None if current_seat in ["STANDBY", "INFANT", None] else current_seat

                    clean_passenger_data.append({
                        "name": p_data.get('name', 'Unknown'),
                        "seat": final_seat, # Updated seat info
                        "is_infant": p_data.get('is_infant', False),
                        "id": p_id,
                        "type": p_data.get('seat_type', 'economy')
                    })

            except Exception as e:
                print(f"Passenger Fetch Error in Save: {e}")

            # 5. Create JSON and Write
            full_data = {
                "flight_number": flight_number,
                "roster_id": roster.id,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "shared_flight": shared_data,
                "crew": clean_crew_data,
                "passengers": clean_passenger_data 
            }

            directory = os.path.join(settings.BASE_DIR, 'roster_nosql_store')
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            file_path = os.path.join(directory, f"{flight_number}_roster.json")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, ensure_ascii=False, indent=4)

            return Response({
                "message": f"Roster saved successfully.",
                "file_path": file_path
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Save Error Detail: {str(e)}")
            return Response({"error": f"Server Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 2. VIEW LISTING ONLY JSON FILES
class SavedRostersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        combined_list = []

        # deleted the SQL query completely. just scanning the directory now.
        directory = os.path.join(settings.BASE_DIR, 'roster_nosql_store')
        
        if os.path.exists(directory):
            files = os.listdir(directory)
            # sort files by date (newest first)
            files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)

            for filename in files:
                if filename.endswith(".json"):
                    file_path = os.path.join(directory, filename)
                    
                    timestamp = os.path.getmtime(file_path)
                    date_created = datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M")
                    
                    flight_num = filename.split('_')[0]

                    combined_list.append({
                        "id": filename,
                        "real_id": filename,
                        "flight_number": flight_num,
                        "date_saved": date_created,
                        "db_type": "NOSQL"
                    })

        return Response(combined_list, status=status.HTTP_200_OK)
    
class OpenNoSQLRosterView(APIView):
    """
    Reads the content of a JSON file and returns it.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, filename):
        directory = os.path.join(settings.BASE_DIR, 'roster_nosql_store')
        file_path = os.path.join(directory, filename)

        if not os.path.exists(file_path):
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetRosterView(APIView):
    """
    ULTRA ROBUST VERSION
    1. solves duplicate record issue (using .filter().first()).
    2. patches up bad data (nulls/strings).
    """
    permission_classes = [IsAuthenticated, IsStandardUser]

    def get(self, request, flight_number):
        print(f"--- DEBUG START: Roster Request for {flight_number} ---")
        
        # -----------------------------------------------------------
        # STEP 1: Safely Fetch Roster
        # -----------------------------------------------------------
        try:
            roster = Roster.objects.filter(flight_number=flight_number).first()
            
            if not roster:
                print(f"Roster not found for {flight_number}")
                return Response({"error": "Roster not found"}, status=status.HTTP_404_NOT_FOUND)
                
        except Exception as e:
            print(f"CRITICAL DB ERROR: {e}")
            return Response({"error": "Database Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # -----------------------------------------------------------
        # STEP 2: Get Flight Info (Main System)
        # -----------------------------------------------------------
        flight_info = {}
        try:
            all_flights = FlightService.get_all_flights()
            flight_info = next((f for f in all_flights if f.get('flight_number') == flight_number), {})
        except Exception as e:
            print(f"Flight Service Error: {e}")

        # Safe Distance Parsing
        flight_distance = 0.0
        try:
            raw_dist = flight_info.get('distance', 0)
            # if number, take it
            if isinstance(raw_dist, (int, float)):
                flight_distance = float(raw_dist)
            # if string ("2340 km"), clean it up
            elif isinstance(raw_dist, str):
                import re
                clean_dist = re.sub(r"[^0-9\.]", "", raw_dist)
                if clean_dist:
                    flight_distance = float(clean_dist)
        except Exception as e:
            print(f"Distance Parse Error: {e}")
            flight_distance = 0.0

        # Vehicle Info
        vehicle_name = "Unknown"
        vehicle_capacity = 0
        flight_menu = "Standard Airline Food"
        
        try:
            vt = flight_info.get('vehicle_type')
            if isinstance(vt, dict):
                vehicle_name = vt.get('name', "Unknown")
                vehicle_capacity = vt.get('number_of_seats', 0)
                flight_menu = vt.get('standard_menu', "Standard Airline Food")
            elif isinstance(vt, str):
                vehicle_name = vt
        except:
            pass

        # --- NEW: GET SHARED FLIGHT INFO ---
        is_shared = bool(flight_info.get('is_shared', False))
        shared_airline = flight_info.get('shared_airline_name', "")
        shared_flight_num = flight_info.get('shared_flight_number', "")

        # -----------------------------------------------------------
        # STEP 3: Get Crew List
        # -----------------------------------------------------------
        assigned_crew = []
        chef_found = None # keeping track if chef exists
        try:
            # fetch crew linked to this roster
            crews = RosterCrew.objects.filter(roster=roster)
            for c in crews:
                assigned_crew.append({
                    "name": c.name or "Unknown",
                    "role": c.role or "N/A",
                    "type": c.crew_type,
                    "original_id": c.original_id
                })
                if c.role == 'CHEF':
                    chef_found = c
        except Exception as e:
            print(f"Crew Error: {e}")

        if chef_found:
            try:
                # fetch chef recipes from service
                recipes = CrewService.get_chef_recipes(chef_found.original_id)
                if recipes:
                    # pick a random recipe
                    import random
                    selected_recipe = random.choice(recipes)
                    recipe_name = selected_recipe.get('name', 'Special Chef Meal')
                    
                    # update menu variable
                    flight_menu = f"{recipe_name} (Prepared by Chef {chef_found.name})"
            except Exception as e:
                print(f"Chef Menu Logic Error: {e}")

        # -----------------------------------------------------------
        # STEP 4: Get Passengers
        # -----------------------------------------------------------
        final_passenger_objects = []
        try:
            api_passengers = FlightService.get_flight_passengers(flight_number)
            
            # if dict, convert to list (Pagination check)
            if isinstance(api_passengers, dict):
                api_passengers = api_passengers.get('results', [])
            
            # still not a list? make it empty
            if not isinstance(api_passengers, list):
                api_passengers = []

            # Local DB Seats
            local_seats = {str(p.original_passenger_id): p.seat_number for p in RosterPassenger.objects.filter(roster=roster)}

            for p_data in api_passengers:
                try:
                    if not isinstance(p_data, dict): continue

                    p_id = p_data.get('passenger_id')
                    if not p_id: continue # skip if no ID

                    str_p_id = str(p_id)
                    current_seat = local_seats.get(str_p_id, p_data.get('seat_number'))
                    display_seat = None if current_seat in ["STANDBY", "INFANT", None] else current_seat

                    final_passenger_objects.append({
                        "id": p_id,
                        "name": p_data.get('name', 'Unknown'),
                        "age": p_data.get('age', 0),
                        "gender": p_data.get('gender', 'N/A'),
                        "nationality": p_data.get('nationality', 'N/A'),
                        "seat_number": display_seat,
                        "type": p_data.get('seat_type', 'economy'),
                        "is_infant": p_data.get('is_infant', False),
                        "affiliated_passengers": p_data.get('affiliated_passengers', []),
                        "parent_id": p_data.get('parent')
                    })
                except:
                    continue # continue loop on single passenger error

        except Exception as e:
            print(f"Passenger Service Error: {e}")

        # -----------------------------------------------------------
        # STEP 5: Response
        # -----------------------------------------------------------
        print(f"--- DEBUG END: Success for {flight_number} ---")
        
        return Response({
            "message": "Roster retrieved successfully",
            "flight_info": {
                "number": flight_number,
                "vehicle": vehicle_name,
                "capacity": vehicle_capacity,
                "menu": flight_menu,
                "source": flight_info.get('flight_source', {}) or {},
                "destination": flight_info.get('flight_destination', {}) or {},
                "datetime": flight_info.get('flight_datetime') or "",
                "duration": flight_info.get('duration', ""),
                "distance": flight_distance,
                "shared_flight": {
                    "is_shared": is_shared,
                    "airline": shared_airline,
                    "flight_number": shared_flight_num
                }
                
            },
            "stats": {
                "total_passengers": len(final_passenger_objects),
                "total_crew": len(assigned_crew)
            },
            "crew": assigned_crew,
            "passengers": final_passenger_objects
        }, status=status.HTTP_200_OK)
    
class DeleteNoSQLRosterView(APIView):
    permission_classes = [IsAuthenticated, IsStandardUser]
    def delete(self, request, filename):
        directory = os.path.join(settings.BASE_DIR, 'roster_nosql_store')
        file_path = os.path.join(directory, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return Response({"message": "Deleted"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated, IsStandardUser]

    def get(self, request):
        try:
            # 1. Active Crew Count 
            # This represents total staff 
            all_pilots = CrewService.get_all_pilots()
            all_attendants = CrewService.get_all_attendants()
            total_crew_count = len(all_pilots) + len(all_attendants)

            # 2. Saved Rosters Count (count json files in folder)
            directory = os.path.join(settings.BASE_DIR, 'roster_nosql_store')
            saved_rosters_count = 0
            if os.path.exists(directory):
                # Only count files ending in .json
                saved_rosters_count = len([name for name in os.listdir(directory) if name.endswith('.json')])

            return Response({
                "total_active_crew": total_crew_count,
                "saved_rosters_count": saved_rosters_count
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
