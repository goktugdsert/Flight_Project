from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# ==================== CHOICES ====================
# These are like dropdown options

class PilotSeniorityLevel(models.TextChoices):
    SENIOR = 'SENIOR', 'Senior'
    JUNIOR = 'JUNIOR', 'Junior'
    TRAINEE = 'TRAINEE', 'Trainee'

class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    OTHER = 'O', 'Other'

class AttendantType(models.TextChoices):
    CHIEF = 'CHIEF', 'Chief'
    REGULAR = 'REGULAR', 'Regular'
    CHEF = 'CHEF', 'Chef'

# ==================== SUPPORTING MODELS ====================

class VehicleType(models.Model):
    """Aircraft types - like Boeing 737, Airbus A320"""
    code = models.CharField(max_length=10, unique=True)  # Example: "B737"
    name = models.CharField(max_length=100)  # Example: "Boeing 737"
    total_seats = models.IntegerField(validators=[MinValueValidator(1)])
    business_seats = models.IntegerField(validators=[MinValueValidator(0)])
    economy_seats = models.IntegerField(validators=[MinValueValidator(0)])
    min_pilots = models.IntegerField(default=2, validators=[MinValueValidator(1)])
    max_pilots = models.IntegerField(default=4, validators=[MinValueValidator(1)])
    min_cabin_crew = models.IntegerField(default=4, validators=[MinValueValidator(1)])
    max_cabin_crew = models.IntegerField(default=16, validators=[MinValueValidator(1)])
    standard_menu = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicle_types'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class Language(models.Model):
    """Languages - like English, Turkish, Spanish"""
    code = models.CharField(max_length=3, unique=True)  # Example: "ENG", "TUR"
    name = models.CharField(max_length=50)  # Example: "English", "Turkish"

    class Meta:
        db_table = 'languages'
        ordering = ['name']

    def __str__(self):
        return self.name

# ==================== PILOT MODEL ====================

class Pilot(models.Model):
    """Pilots (Flight Crew)"""
    pilot_id = models.AutoField(primary_key=True)
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(21), MaxValueValidator(65)])
    gender = models.CharField(max_length=1, choices=Gender.choices)
    nationality = models.CharField(max_length=100)
    
    # Professional Information
    seniority_level = models.CharField(
        max_length=10, 
        choices=PilotSeniorityLevel.choices
    )
    vehicle_type = models.ForeignKey(
        VehicleType, 
        on_delete=models.PROTECT,
        related_name='pilots',
        help_text="Which aircraft type this pilot can fly"
    )
    allowed_range = models.IntegerField(
        validators=[MinValueValidator(0)],
        help_text="Maximum flight distance in km"
    )
    
    # Additional Information
    known_languages = models.ManyToManyField(Language, related_name='pilots')
    is_active = models.BooleanField(default=True)
    license_number = models.CharField(max_length=50, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pilots'
        ordering = ['-seniority_level', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['seniority_level', 'is_active']),
            models.Index(fields=['vehicle_type', 'is_active']),
        ]

    def __str__(self):
        return f"Pilot {self.pilot_id}: {self.first_name} {self.last_name} ({self.seniority_level})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# ==================== CABIN CREW MODEL ====================

class CabinAttendant(models.Model):
    """Flight Attendants (Cabin Crew)"""
    attendant_id = models.AutoField(primary_key=True)
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(65)])
    gender = models.CharField(max_length=1, choices=Gender.choices)
    nationality = models.CharField(max_length=100)
    
    # Professional Information
    attendant_type = models.CharField(
        max_length=10, 
        choices=AttendantType.choices
    )
    
    # Vehicle restrictions (can work on multiple aircraft types)
    allowed_vehicle_types = models.ManyToManyField(
        VehicleType,
        related_name='cabin_attendants',
        help_text="Which aircraft types this attendant can work on"
    )
    
    # Additional Information
    known_languages = models.ManyToManyField(Language, related_name='cabin_attendants')
    is_active = models.BooleanField(default=True)
    employee_number = models.CharField(max_length=50, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cabin_attendants'
        ordering = ['attendant_type', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['attendant_type', 'is_active']),
        ]

    def __str__(self):
        return f"Attendant {self.attendant_id}: {self.first_name} {self.last_name} ({self.attendant_type})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# ==================== RECIPE MODEL ====================

class DishRecipe(models.Model):
    """Food recipes created by chef attendants"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cuisine_type = models.CharField(max_length=100, blank=True)
    preparation_time = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Preparation time in minutes"
    )
    chef = models.ForeignKey(
        CabinAttendant,
        on_delete=models.CASCADE,
        related_name='recipes',
        limit_choices_to={'attendant_type': AttendantType.CHEF}
    )
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dish_recipes'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} by {self.chef.full_name}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.chef.attendant_type != AttendantType.CHEF:
            raise ValidationError("Recipes can only be assigned to chef attendants")