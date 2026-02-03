from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from db.models import Flight, Passenger, Airport, VehicleType


# ============================================================================
# MODEL TESTS - Business Logic & Validation
# ============================================================================

class PassengerModelTest(TestCase):
    """Passenger model validation and business logic tests"""
    
    def setUp(self):
        """Create necessary objects for testing"""
        self.vehicle_type = VehicleType.objects.create(
            name="Boeing 737",
            number_of_seats=180,
            seating_plan="3-3 configuration",
            max_crew=8,
            max_passengers=180,
            standard_menu="Standard meal service"
        )
        
        self.source_airport = Airport.objects.create(
            code="IST",
            name="Istanbul Airport",
            city="Istanbul",
            country="Turkey"
        )
        
        self.dest_airport = Airport.objects.create(
            code="ANK",
            name="Ankara Airport",
            city="Ankara",
            country="Turkey"
        )
        
        self.flight = Flight.objects.create(
            flight_number="TK1001",
            flight_datetime=timezone.now(),
            duration=timedelta(hours=1),
            distance=350.00,
            flight_source=self.source_airport,
            flight_destination=self.dest_airport,
            vehicle_type=self.vehicle_type
        )
    
    def test_adult_passenger_creation(self):
        """Adult passenger should be created successfully"""
        passenger = Passenger.objects.create(
            flight=self.flight,
            name="Ahmet Yilmaz",
            age=35,
            gender="M",
            nationality="Turkish",
            seat_type="economy",
            seat_number="12A"
        )
        
        self.assertEqual(passenger.name, "Ahmet Yilmaz")
        self.assertEqual(passenger.age, 35)
        self.assertFalse(passenger.is_infant())
    
    def test_infant_with_parent(self):
        """Infant passenger should be created with parent"""
        parent = Passenger.objects.create(
            flight=self.flight,
            name="Ayse Yilmaz",
            age=30,
            gender="F",
            nationality="Turkish",
            seat_type="economy",
            seat_number="12B"
        )
        
        infant = Passenger.objects.create(
            flight=self.flight,
            name="Baby Yilmaz",
            age=1,
            gender="M",
            nationality="Turkish",
            parent=parent
        )
        
        self.assertTrue(infant.is_infant())
        self.assertEqual(infant.parent, parent)
        self.assertIsNone(infant.seat_number)
    
    def test_infant_without_parent_raises_error(self):
        """Infant without parent should raise validation error"""
        with self.assertRaises(ValidationError) as context:
            infant = Passenger(
                flight=self.flight,
                name="Baby Yilmaz",
                age=1,
                gender="M",
                nationality="Turkish"
            )
            infant.save()
        
        self.assertIn("parent", str(context.exception).lower())
    
    def test_infant_with_seat_number_raises_error(self):
        """Infant with seat number should raise validation error"""
        parent = Passenger.objects.create(
            flight=self.flight,
            name="Ayse Yilmaz",
            age=30,
            gender="F",
            nationality="Turkish",
            seat_type="economy",
            seat_number="12B"
        )
        
        with self.assertRaises(ValidationError) as context:
            infant = Passenger(
                flight=self.flight,
                name="Baby Yilmaz",
                age=1,
                gender="M",
                nationality="Turkish",
                parent=parent,
                seat_number="12C"
            )
            infant.save()
        
        self.assertIn("seat", str(context.exception).lower())
    
    def test_adult_without_seat_type_raises_error(self):
        """Adult without seat type should raise validation error"""
        with self.assertRaises(ValidationError) as context:
            passenger = Passenger(
                flight=self.flight,
                name="Ahmet Yilmaz",
                age=35,
                gender="M",
                nationality="Turkish",
                seat_number="12A"
            )
            passenger.save()
        
        self.assertIn("seat type", str(context.exception).lower())
    
    def test_is_infant_method(self):
        """is_infant() method should work correctly"""
        parent = Passenger.objects.create(
            flight=self.flight,
            name="Parent",
            age=30,
            gender="F",
            nationality="Turkish",
            seat_type="economy",
            seat_number="12B"
        )
        
        # Age 0, 1, 2 are infants
        infant_0 = Passenger.objects.create(
            flight=self.flight,
            name="Baby 0",
            age=0,
            gender="M",
            nationality="Turkish",
            parent=parent
        )
        
        infant_2 = Passenger.objects.create(
            flight=self.flight,
            name="Baby 2",
            age=2,
            gender="F",
            nationality="Turkish",
            parent=parent
        )
        
        # Age 3+ are not infants
        child = Passenger.objects.create(
            flight=self.flight,
            name="Child 3",
            age=3,
            gender="M",
            nationality="Turkish",
            seat_type="economy",
            seat_number="13A"
        )
        
        self.assertTrue(infant_0.is_infant())
        self.assertTrue(infant_2.is_infant())
        self.assertFalse(child.is_infant())


class FlightModelTest(TestCase):
    """Flight model tests"""
    
    def setUp(self):
        self.vehicle_type = VehicleType.objects.create(
            name="Boeing 737",
            number_of_seats=180,
            seating_plan="3-3 configuration",
            max_crew=8,
            max_passengers=180,
            standard_menu="Standard meal service"
        )
        
        self.source_airport = Airport.objects.create(
            code="IST",
            name="Istanbul Airport",
            city="Istanbul",
            country="Turkey"
        )
        
        self.dest_airport = Airport.objects.create(
            code="JFK",
            name="JFK International",
            city="New York",
            country="USA"
        )
    
    def test_flight_creation(self):
        """Flight should be created successfully"""
        flight = Flight.objects.create(
            flight_number="TK1001",
            flight_datetime=timezone.now(),
            duration=timedelta(hours=10, minutes=30),
            distance=8000.00,
            flight_source=self.source_airport,
            flight_destination=self.dest_airport,
            vehicle_type=self.vehicle_type
        )
        
        self.assertEqual(flight.flight_number, "TK1001")
        self.assertEqual(float(flight.distance), 8000.00)
    
    def test_flight_number_unique(self):
        """Flight number should be unique"""
        Flight.objects.create(
            flight_number="TK1001",
            flight_datetime=timezone.now(),
            duration=timedelta(hours=10),
            distance=8000.00,
            flight_source=self.source_airport,
            flight_destination=self.dest_airport,
            vehicle_type=self.vehicle_type
        )
        
        with self.assertRaises(Exception):
            Flight.objects.create(
                flight_number="TK1001",  # Duplicate
                flight_datetime=timezone.now(),
                duration=timedelta(hours=5),
                distance=1000.00,
                flight_source=self.source_airport,
                flight_destination=self.dest_airport,
                vehicle_type=self.vehicle_type
            )


# ============================================================================
# API TESTS - Endpoints & Integration
# ============================================================================

class FlightAPITest(APITestCase):
    """Flight API endpoint tests"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.vehicle_type = VehicleType.objects.create(
            name="Boeing 737",
            number_of_seats=180,
            seating_plan="3-3 configuration",
            max_crew=8,
            max_passengers=180,
            standard_menu="Standard meal service"
        )
        
        self.source_airport = Airport.objects.create(
            code="IST",
            name="Istanbul Airport",
            city="Istanbul",
            country="Turkey"
        )
        
        self.dest_airport = Airport.objects.create(
            code="JFK",
            name="JFK International",
            city="New York",
            country="USA"
        )
        
        self.flight = Flight.objects.create(
            flight_number="TK1001",
            flight_datetime=timezone.now(),
            duration=timedelta(hours=10, minutes=30),
            distance=8000.00,
            flight_source=self.source_airport,
            flight_destination=self.dest_airport,
            vehicle_type=self.vehicle_type
        )
    
    def test_get_all_flights(self):
        """GET /api/flights/ - Should list all flights"""
        url = reverse('flight-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['flight_number'], 'TK1001')
    
    def test_get_single_flight(self):
        """GET /api/flights/{id}/ - Should retrieve single flight details"""
        url = reverse('flight-detail', kwargs={'pk': self.flight.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['flight_number'], 'TK1001')
    
    def test_update_flight(self):
        """PATCH /api/flights/{id}/ - Should update flight"""
        url = reverse('flight-detail', kwargs={'pk': self.flight.id})
        data = {'distance': '8200.00'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.flight.refresh_from_db()
        self.assertEqual(float(self.flight.distance), 8200.00)
    
    def test_delete_flight(self):
        """DELETE /api/flights/{id}/ - Should delete flight"""
        url = reverse('flight-detail', kwargs={'pk': self.flight.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Flight.objects.count(), 0)
    
    def test_flight_passenger_count(self):
        """passenger_count field should be calculated correctly"""
        Passenger.objects.create(
            flight=self.flight,
            name="Test Passenger",
            age=30,
            gender="M",
            nationality="Turkish",
            seat_type="economy",
            seat_number="12A"
        )
        
        url = reverse('flight-detail', kwargs={'pk': self.flight.id})
        response = self.client.get(url)
        
        self.assertEqual(response.data['passenger_count'], 1)


class PassengerAPITest(APITestCase):
    """Passenger API endpoint tests"""
    
    def setUp(self):
        self.client = APIClient()
        
        self.vehicle_type = VehicleType.objects.create(
            name="Boeing 737",
            number_of_seats=180,
            seating_plan="3-3 configuration",
            max_crew=8,
            max_passengers=180,
            standard_menu="Standard meal service"
        )
        
        self.source_airport = Airport.objects.create(
            code="IST",
            name="Istanbul Airport",
            city="Istanbul",
            country="Turkey"
        )
        
        self.dest_airport = Airport.objects.create(
            code="ANK",
            name="Ankara Airport",
            city="Ankara",
            country="Turkey"
        )
        
        self.flight = Flight.objects.create(
            flight_number="TK1001",
            flight_datetime=timezone.now(),
            duration=timedelta(hours=1),
            distance=350.00,
            flight_source=self.source_airport,
            flight_destination=self.dest_airport,
            vehicle_type=self.vehicle_type
        )
        
        self.passenger = Passenger.objects.create(
            flight=self.flight,
            name="Ahmet Yilmaz",
            age=35,
            gender="M",
            nationality="Turkish",
            seat_type="economy",
            seat_number="12A"
        )
    
    def test_get_all_passengers(self):
        """GET /api/passengers/ - Should list all passengers"""
        url = reverse('passenger-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Ahmet Yilmaz')
    
    def test_get_single_passenger(self):
        """GET /api/passengers/{id}/ - Should retrieve single passenger details"""
        url = reverse('passenger-detail', kwargs={'pk': self.passenger.passenger_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Ahmet Yilmaz')
    
    def test_filter_by_flight_number(self):
        """GET /api/passengers/?flight_number=TK1001 - Should filter by flight number"""
        # Create second flight and passenger
        flight2 = Flight.objects.create(
            flight_number="TK2002",
            flight_datetime=timezone.now(),
            duration=timedelta(hours=2),
            distance=500.00,
            flight_source=self.source_airport,
            flight_destination=self.dest_airport,
            vehicle_type=self.vehicle_type
        )
        
        Passenger.objects.create(
            flight=flight2,
            name="Mehmet Demir",
            age=40,
            gender="M",
            nationality="Turkish",
            seat_type="business",
            seat_number="1A"
        )
        
        url = reverse('passenger-list')
        response = self.client.get(url, {'flight_number': 'TK1001'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['flight_number'], 'TK1001')
    
    def test_filter_by_seat_type(self):
        """GET /api/passengers/?seat_type=economy - Should filter by seat type"""
        Passenger.objects.create(
            flight=self.flight,
            name="Ayse Kaya",
            age=28,
            gender="F",
            nationality="Turkish",
            seat_type="business",
            seat_number="1A"
        )
        
        url = reverse('passenger-list')
        response = self.client.get(url, {'seat_type': 'economy'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['seat_type'], 'economy')
    
    def test_create_adult_passenger(self):
        """POST /api/passengers/ - Should create adult passenger"""
        url = reverse('passenger-list')
        data = {
            'flight': self.flight.id,
            'name': 'Test Passenger',
            'age': 30,
            'gender': 'M',
            'nationality': 'Turkish',
            'seat_type': 'economy',
            'seat_number': '15C'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Passenger.objects.count(), 2)
    
    def test_create_infant_with_parent(self):
        """POST /api/passengers/ - Should create infant with parent"""
        url = reverse('passenger-list')
        data = {
            'flight': self.flight.id,
            'name': 'Baby',
            'age': 1,
            'gender': 'M',
            'nationality': 'Turkish',
            'parent': self.passenger.passenger_id
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        infant = Passenger.objects.get(name='Baby')
        self.assertEqual(infant.parent, self.passenger)
        self.assertTrue(infant.is_infant())
    
    def test_create_infant_without_parent_fails(self):
        """POST /api/passengers/ - Should fail to create infant without parent"""
        url = reverse('passenger-list')
        data = {
            'flight': self.flight.id,
            'name': 'Baby',
            'age': 1,
            'gender': 'M',
            'nationality': 'Turkish'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('parent', response.data)
    
    def test_create_adult_without_seat_type_fails(self):
        """POST /api/passengers/ - Should fail to create adult without seat type"""
        url = reverse('passenger-list')
        data = {
            'flight': self.flight.id,
            'name': 'Adult',
            'age': 30,
            'gender': 'M',
            'nationality': 'Turkish',
            'seat_number': '15C'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('seat_type', response.data)
    
    def test_create_infant_with_seat_number_fails(self):
        """POST /api/passengers/ - Infant should not have seat number"""
        url = reverse('passenger-list')
        data = {
            'flight': self.flight.id,
            'name': 'Baby',
            'age': 1,
            'gender': 'M',
            'nationality': 'Turkish',
            'parent': self.passenger.passenger_id,
            'seat_number': '12C'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('seat_number', response.data)
    
    def test_update_passenger(self):
        """PATCH /api/passengers/{id}/ - Should update passenger"""
        url = reverse('passenger-detail', kwargs={'pk': self.passenger.passenger_id})
        data = {'seat_number': '13B'}
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.passenger.refresh_from_db()
        self.assertEqual(self.passenger.seat_number, '13B')
    
    def test_delete_passenger(self):
        """DELETE /api/passengers/{id}/ - Should delete passenger"""
        url = reverse('passenger-detail', kwargs={'pk': self.passenger.passenger_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Passenger.objects.count(), 0)
    
    def test_duplicate_seat_number_fails(self):
        """Same seat number cannot be used on same flight"""
        url = reverse('passenger-list')
        data = {
            'flight': self.flight.id,
            'name': 'Test Passenger 2',
            'age': 25,
            'gender': 'F',
            'nationality': 'Turkish',
            'seat_type': 'economy',
            'seat_number': '12A'  # Already used seat
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
