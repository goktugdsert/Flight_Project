from rest_framework import serializers
from db.models import Flight, Passenger, Airport, VehicleType

# --- 1. Basic Serializers ---

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = '__all__'

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = '__all__'

class FlightSerializer(serializers.ModelSerializer):
    flight_source = AirportSerializer(read_only=True)
    flight_destination = AirportSerializer(read_only=True)
    vehicle_type = VehicleTypeSerializer(read_only=True)
    
    # --- PASSENGER COUNT ---
    passenger_count = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = '__all__'

    # counts total passengers for each flight instance
    def get_passenger_count(self, obj):
        # try the default related_name 'passengers' first
        if hasattr(obj, 'passengers'):
            return obj.passengers.count()
        
        # if that fails, try the standard django default 'passenger_set'
        if hasattr(obj, 'passenger_set'):
            return obj.passenger_set.count()
            
        # return 0 if neither exists
        return 0

# --- 2. Advanced Passenger Serializer ---

class PassengerSerializer(serializers.ModelSerializer):
    flight_number = serializers.CharField(source='flight.flight_number', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    is_infant = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Passenger
        fields = [
            'passenger_id',
            'flight',
            'flight_number',
            'name',
            'age',
            'gender',
            'nationality',
            'seat_type',
            'seat_number',
            'parent',
            'parent_name',
            'affiliated_passengers',
            'is_infant',
        ]
        read_only_fields = ['passenger_id']

    def get_is_infant(self, obj):
        return obj.is_infant()
    
    def validate_age(self, value):
        if value < 0 or value > 150:
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value
    
    def validate(self, data):
        """
        Check that the passenger data is valid, considering partial updates (PATCH).
        """
        # 1. get the current instance data
        instance = self.instance
        
        # 2. if field is in incoming data, use it; otherwise fallback to existing instance data
        age = data.get('age', instance.age if instance else None)
        parent = data.get('parent', instance.parent if instance else None)
        seat_number = data.get('seat_number', instance.seat_number if instance else None)
        seat_type = data.get('seat_type', instance.seat_type if instance else None)
        
        # Helper: is this an infant?
        is_infant = (age is not None and 0 <= age <= 2)
        
        # --- VALIDATION LOGIC ---
        
        # 1. Infant Checks
        if is_infant:
            if not parent:
                raise serializers.ValidationError({"parent": "Infants (age 0-2) must have a parent assigned."})
            if seat_number:
                raise serializers.ValidationError({"seat_number": "Infants (age 0-2) cannot have seat assignments."})
            if seat_type:
                pass 
        
        # 2. Adult Checks
        else:
            if not seat_type:
                raise serializers.ValidationError({"seat_type": "Adult/child passengers must have a seat type."})
        
        # 3. Parent Flight Check
        current_flight = data.get('flight', instance.flight if instance else None)
        
        if parent:
            # need to verify parent is on the same flight.
            if hasattr(parent, 'flight') and parent.flight != current_flight:
                 raise serializers.ValidationError({"parent": "Parent must be on the same flight."})
        
        return data

class PassengerDetailSerializer(serializers.ModelSerializer):
    """
    Used when the Main System views a single passenger to show full details
    of all related persons (infants, affiliates).
    """
    flight = FlightSerializer(read_only=True)
    parent = PassengerSerializer(read_only=True)
    infants = PassengerSerializer(many=True, read_only=True)
    affiliated_passengers = PassengerSerializer(many=True, read_only=True)
    is_infant = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Passenger
        fields = [
            'passenger_id',
            'flight',
            'name',
            'age',
            'gender',
            'nationality',
            'seat_type',
            'seat_number',
            'parent',
            'infants',
            'affiliated_passengers',
            'is_infant',
        ]
    
    def get_is_infant(self, obj):
        return obj.is_infant()
