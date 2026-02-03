from rest_framework import viewsets
from db.models import Flight, Passenger, Airport, VehicleType
from .serializers import (
    FlightSerializer, 
    PassengerSerializer, 
    PassengerDetailSerializer,
    AirportSerializer, 
    VehicleTypeSerializer
)

class FlightViewSet(viewsets.ModelViewSet):
    """
    GET /api/flights/ -> Lists all flights (The Main System will use this)
    GET /api/flights/5/ -> Returns details for the flight with ID 5
    """
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

class VehicleTypeViewSet(viewsets.ModelViewSet):
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer

class PassengerViewSet(viewsets.ModelViewSet):
    """
    Lists and filters passengers.
    Example: /api/passengers/?flight_number=TK1001
    """
    queryset = Passenger.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PassengerDetailSerializer
        return PassengerSerializer

    def get_queryset(self):
        """
        Filtering logic based on URL parameters
        """
        queryset = Passenger.objects.all()
        
        # 1. Filter by Flight Number
        flight_number = self.request.query_params.get('flight_number')
        if flight_number:
            queryset = queryset.filter(flight__flight_number=flight_number)
            
        # 2. Filter by Seat Type
        seat_type = self.request.query_params.get('seat_type')
        if seat_type:
            queryset = queryset.filter(seat_type=seat_type)
            
        return queryset