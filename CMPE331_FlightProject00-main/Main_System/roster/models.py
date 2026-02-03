from django.db import models

class Roster(models.Model):
    """
    Represents the final generated flight roster.
    Stores the processed and final version of data retrieved from APIs.
    """
    flight_number = models.CharField(max_length=10) # e.g., TK1001
    flight_date = models.DateTimeField(auto_now_add=True) # Roster creation date
    is_finalized = models.BooleanField(default=False) # Is the list confirmed?

    def __str__(self):
        return f"Roster for {self.flight_number} - {self.flight_date.strftime('%Y-%m-%d')}"

class RosterPassenger(models.Model):
    """
    Passengers included in the Roster.
    Important: Data is copied here from the API because we perform the seat assignments locally.
    """
    roster = models.ForeignKey(Roster, on_delete=models.CASCADE, related_name='passengers')
    original_passenger_id = models.IntegerField() # ID from the API (for reference)
    name = models.CharField(max_length=100)
    seat_number = models.CharField(max_length=10) # Seat assigned by us or existing seat
    is_infant = models.BooleanField(default=False)
    
    # Linked parent (if infant) or affiliated passenger (to sit together)
    related_passenger = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.name} - {self.seat_number}"

class RosterCrew(models.Model):
    """
    Crew members assigned to the Roster (Pilots and Cabin Crew).
    """
    CREW_TYPE_CHOICES = (
        ('PILOT', 'Pilot'),
        ('CABIN', 'Cabin Crew'),
    )
    
    roster = models.ForeignKey(Roster, on_delete=models.CASCADE, related_name='crew_members')
    original_id = models.IntegerField() # ID from the API
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50) # Senior, Chief, Chef, etc.
    crew_type = models.CharField(max_length=10, choices=CREW_TYPE_CHOICES)
    
    # Optional seat assignment for Pilots and Crew
    assigned_seat = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.role})"