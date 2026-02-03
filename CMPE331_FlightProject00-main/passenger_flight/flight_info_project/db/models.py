from django.db import models
from django.db.models import Q 

class VehicleType(models.Model):
    """
    defines the aircraft model, including capacity for both crew and passengers.
    """
    name = models.CharField(max_length=100)
    number_of_seats = models.IntegerField()
    seating_plan = models.TextField()  # text description of how seats are laid out
    max_crew = models.IntegerField()
    max_passengers = models.IntegerField()
    standard_menu = models.TextField()  # default food options for this vehicle
    
    def __str__(self):
        return self.name


class Airport(models.Model):
    """
    standard airport model with location data.
    """
    code = models.CharField(max_length=3, unique=True)  # 3-letter IATA code
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Flight(models.Model):
    flight_number = models.CharField(max_length=6, unique=True)
    
    flight_datetime = models.DateTimeField()  # departure time (minute precision)
    duration = models.DurationField()  # expected duration
    distance = models.DecimalField(max_digits=10, decimal_places=2)  # total distance in km/miles
    
    flight_source = models.ForeignKey(
        Airport, 
        on_delete=models.PROTECT, 
        related_name='departing_flights'
    )
    
    flight_destination = models.ForeignKey(
        Airport, 
        on_delete=models.PROTECT, 
        related_name='arriving_flights'
    )
    
    vehicle_type = models.ForeignKey(
        VehicleType, 
        on_delete=models.PROTECT,
        related_name='flights'
    )
    
    is_shared = models.BooleanField(default=False)
    shared_airline_name = models.CharField(max_length=200, null=True, blank=True)
    shared_flight_number = models.CharField(max_length=6, null=True, blank=True)  # format: AANNNN
    
    connecting_flight = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='connected_from'
    )
    
    def __str__(self):
       return f"{self.flight_number} - {self.flight_source.code} to {self.flight_destination.code}"

class Passenger(models.Model):
    """
    core passenger model. handles links between people (parents/affiliates) and flights.
    """
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    SEAT_TYPE_CHOICES = [
        ('business', 'Business'),
        ('economy', 'Economy'),
    ]
    
    passenger_id = models.AutoField(primary_key=True)
    
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name='passengers'
    )
    
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    nationality = models.CharField(max_length=100)
    seat_type = models.CharField(
        max_length=10, 
        choices=SEAT_TYPE_CHOICES,
        null=True,
        blank=True
    )  
    
    seat_number = models.CharField(max_length=10, null=True, blank=True)
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='infants'
    )
    
    affiliated_passengers = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='affiliated_with'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['flight', 'seat_number'],
                condition=models.Q(seat_number__isnull=False),
                name='unique_seat_per_flight'
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(age__gte=3) | 
                    (models.Q(age__lte=2) & models.Q(parent__isnull=False))
                ),
                name='infants_must_have_parent'
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(age__gte=3) | 
                    (models.Q(age__lte=2) & models.Q(seat_number__isnull=True))
                ),
                name='infants_no_seat'
            ),
        ]

        indexes = [
            models.Index(fields=['flight', 'seat_type']),
            models.Index(fields=['age']),
            models.Index(fields=['parent']),
        ]

        ordering = ['flight', 'seat_number']
        
    def __str__(self):
        return f"{self.name} - Flight {self.flight.flight_number}"
    
    def is_infant(self):
        """helper to determine if passenger is a baby (0-2 years)"""
        return 0 <= self.age <= 2
    
    def clean(self):
        """custom validation logic before saving"""
        from django.core.exceptions import ValidationError
        
        # rule: babies need a linked parent
        if self.is_infant() and not self.parent:
            raise ValidationError("Infants (age 0-2) must have a parent assigned.")
        
        # infants sit on laps, no seat number assigned
        if self.is_infant() and self.seat_number:
            raise ValidationError("Infants (age 0-2) cannot have seat assignments.")
        
        # infants don't need a seat type either
        if self.is_infant() and self.seat_type:
            raise ValidationError("Infants (age 0-2) cannot have a seat type.")
        
        # regular passengers need to specify class (business/economy)
        if not self.is_infant() and not self.seat_type:
            raise ValidationError("Adult/child passengers must have a seat type (business or economy).")
        
        # validation: can't link a parent from a different flight
        if self.parent and self.parent.flight != self.flight:
            raise ValidationError("Parent must be on the same flight.")
        
        # limit the buddy list to max 2 people
        if self.pk and self.affiliated_passengers.count() > 2:
            raise ValidationError("Maximum 2 affiliated passengers allowed.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
