import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from db.models import Passenger, Flight, Airport, VehicleType

fake = Faker()

class Command(BaseCommand):
    help = 'Safely populates the database with random data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Scanning database...")
        
        Passenger.objects.all().delete()
        self.stdout.write("Old passengers cleaned up.")
        # Flight.objects.all().delete()
        
        # 1. check basic data existence
        if Airport.objects.count() == 0:
            self.create_airports()
        if VehicleType.objects.count() == 0:
            self.create_vehicle_types()

        # 2. fetch ALL flights from the db
        all_flights = Flight.objects.all()
        
        if not all_flights.exists():
            self.stdout.write("No flights found. Creating sample flights...")
            airports = list(Airport.objects.all())
            vehicles = list(VehicleType.objects.all())
            all_flights = self.create_flights(airports, vehicles)
        
        self.stdout.write(f"Found {len(all_flights)} flights total. Checking passenger data...")

        # 3. iterate through each flight
        for flight in all_flights:
            # if flight already has passengers, DON'T TOUCH it
            if flight.passengers.count() > 0:
                self.stdout.write(f"{flight.flight_number} already full ({flight.passengers.count()} pax). Skipping.")
                continue
            
            # if flight is empty, fill it up!
            self.stdout.write(f"{flight.flight_number} looks empty. Generating passengers...")
            self.create_passengers_for_flight(flight)

        self.stdout.write(self.style.SUCCESS('Operation completed successfully!'))
        
    def create_airports(self):
        airports_data = [
            ("IST", "Istanbul Airport", "Istanbul", "Turkey"),
            ("JFK", "John F. Kennedy", "New York", "USA"),
            ("LHR", "Heathrow", "London", "UK"),
            ("CDG", "Charles de Gaulle", "Paris", "France"),
            ("FRA", "Frankfurt Airport", "Frankfurt", "Germany"),
        ]
        created_airports = []
        for code, name, city, country in airports_data:
            obj, created = Airport.objects.get_or_create(
                code=code,
                defaults={'name': name, 'city': city, 'country': country}
            )
            created_airports.append(obj)
        return created_airports

    def create_vehicle_types(self):
        vehicles_data = [
            {"name": "Boeing 737", "seats": 180, "crew": 9, "pax": 180},
            {"name": "Airbus A320", "seats": 160, "crew": 8, "pax": 160},
            {"name": "Boeing 777", "seats": 250, "crew": 12, "pax": 250},
        ]
        created_vehicles = []
        for v in vehicles_data:
            obj, created = VehicleType.objects.get_or_create(
                name=v["name"],
                defaults={
                    'number_of_seats': v["seats"],
                    'seating_plan': "3-3 layout",
                    'max_crew': v["crew"],
                    'max_passengers': v["pax"],
                    'standard_menu': "Standard Chicken or Pasta"
                }
            )
            created_vehicles.append(obj)
        return created_vehicles

    def create_flights(self, airports, vehicles):
        created_flights = []
        flight_codes = ["TK1001", "TK2040", "TK3050", "TK1111", "TK1234", "BA2121", "TK9876", "TK0606"]

        for i, code in enumerate(flight_codes):
            source = airports[i % len(airports)]
            dest = airports[(i + 1) % len(airports)]
            vehicle = random.choice(vehicles)
            
            flight = Flight.objects.create(
                flight_number=code,
                flight_datetime=timezone.now() + timedelta(days=random.randint(1, 30)),
                duration=timedelta(hours=random.randint(2, 10)),
                distance=random.randint(1000, 8000),
                flight_source=source,
                flight_destination=dest,
                vehicle_type=vehicle,
                is_shared=False
            )
            created_flights.append(flight)
        
        self.stdout.write(f"{len(created_flights)} flights created.")
        return created_flights

    def create_passengers_for_flight(self, flight):
        # --- 1. OCCUPANCY RATE ---
        occupancy_rate = random.uniform(0.40, 0.55)
        target_passengers = int(flight.vehicle_type.max_passengers * occupancy_rate)
        
        # --- 2. SEAT POOLS (STRUCTURED) ---
        # We need structured data (row, col) to find adjacent seats
        eco_cols = ['A', 'B', 'C', 'D', 'E', 'F']
        biz_cols = ['A', 'C', 'D', 'F']
        
        # Helper to build pool
        available_business = [{'row': r, 'col': c, 'code': f"{r}{c}", 'type': 'business'} 
                              for r in range(1, 6) for c in biz_cols]
        
        available_economy = [{'row': r, 'col': c, 'code': f"{r}{c}", 'type': 'economy'} 
                             for r in range(6, 31) for c in eco_cols]

        # --- HELPER FUNCTIONS ---
        def get_pair_seats(seat_list):
            """Finds 2 seats in the same row"""
            seat_list.sort(key=lambda x: (x['row'], x['col']))
            from itertools import groupby
            for (row, _), row_seats_iter in groupby(seat_list, key=lambda x: (x['row'], x['type'])):
                row_seats = list(row_seats_iter)
                if len(row_seats) >= 2:
                    pair = row_seats[:2] # Take first two adjacent
                    for s in pair: seat_list.remove(s)
                    return pair
            return None

        def get_solo_seat(seat_list):
            if not seat_list: return None
            seat = random.choice(seat_list) # Random pick for solos
            seat_list.remove(seat)
            return seat

        adult_passengers = []
        current_count = 0

        # --- STEP A: Create Adults (Solo or Pairs) ---
        while current_count < target_passengers:
            
            # 10% chance for a connected pair (adjacent seats), 90% solo
            is_pair = random.random() < 0.10
            
            # Determine class (15% business)
            seat_class = 'business' if random.random() < 0.15 else 'economy'
            pool = available_business if seat_class == 'business' else available_economy
            
            # Fallback if pool empty
            if not pool:
                seat_class = 'economy' if seat_class == 'business' else 'business'
                pool = available_business if seat_class == 'business' else available_economy
            
            if not pool: break # Plane full

            seats_to_assign = []

            if is_pair and (target_passengers - current_count) >= 2:
                seats_to_assign = get_pair_seats(pool)
                # If no adjacent seats found, fall back to two solo seats
                if not seats_to_assign:
                    s1 = get_solo_seat(pool)
                    s2 = get_solo_seat(pool)
                    if s1 and s2: seats_to_assign = [s1, s2]
                    elif s1: seats_to_assign = [s1]
            else:
                s = get_solo_seat(pool)
                if s: seats_to_assign = [s]

            # Create the passenger objects
            created_now = []
            for seat_data in seats_to_assign:
                gender = random.choice(['M', 'F'])
                name = fake.name_male() if gender == 'M' else fake.name_female()
                
                # 10% chance of NO SEAT (Standby/Not assigned yet) - Preservation of old logic
                final_seat_num = seat_data['code']
                if random.random() < 0.10: 
                    final_seat_num = None

                try:
                    p = Passenger.objects.create(
                        flight=flight,
                        name=name,
                        age=random.randint(3, 80),
                        gender=gender,
                        nationality=fake.country(),
                        seat_type=seat_class,
                        seat_number=final_seat_num
                    )
                    adult_passengers.append(p)
                    created_now.append(p)
                    current_count += 1
                except:
                    continue
            
            # Link them if they were a pair
            if len(created_now) == 2:
                p1, p2 = created_now
                p1.affiliated_passengers.add(p2)
                # p2 automatically links to p1 due to ManyToMany symmetric=True usually, 
                # but adding one side is enough.

        # --- STEP B: Create Infants (UNCHANGED) ---
        # Keeping your original infant logic exactly as it was
        for _ in range(random.randint(2, 5)):
            if not adult_passengers: break
            parent = random.choice(adult_passengers)
            
            Passenger.objects.create(
                flight=flight,
                name=fake.first_name() + " " + parent.name.split()[-1],
                age=random.randint(0, 2),
                gender=random.choice(['M', 'F']),
                nationality=parent.nationality,
                seat_type=None, 
                seat_number=None, # no seat assignment for infants
                parent=parent
            )

        self.stdout.write(f"Added {current_count} passengers for flight {flight.flight_number}.")