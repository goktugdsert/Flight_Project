from django.core.management.base import BaseCommand
from django.db import transaction
from crew_app.models import (
    VehicleType, Language, Pilot, CabinAttendant, 
    DishRecipe, PilotSeniorityLevel, AttendantType, Gender
)
import random

class Command(BaseCommand):
    help = 'Adds sample data to the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        with transaction.atomic():
            # Clear existing data
            self.stdout.write('Clearing old data...')
            DishRecipe.objects.all().delete()
            CabinAttendant.objects.all().delete()
            Pilot.objects.all().delete()
            VehicleType.objects.all().delete()
            Language.objects.all().delete()
            
            # Create Languages
            self.stdout.write('Creating languages...')
            languages = self._create_languages()
            
            # Create Vehicle Types
            self.stdout.write('Creating aircraft types...')
            vehicles = self._create_vehicles()
            
            # Create Pilots
            self.stdout.write('Creating pilots...')
            self._create_pilots(vehicles, languages)
            
            # Create Cabin Attendants
            self.stdout.write('Creating cabin crew...')
            self._create_cabin_attendants(vehicles, languages)
            
            self.stdout.write(self.style.SUCCESS('✅ Sample data created successfully!'))
            self._print_statistics()
    
    def _create_languages(self):
        languages_data = [
            ('ENG', 'English'),
            ('TUR', 'Turkish'),
            ('SPA', 'Spanish'),
            ('FRE', 'French'),
            ('GER', 'German'),
            ('ITA', 'Italian'),
            ('ARA', 'Arabic'),
            ('CHI', 'Chinese'),
        ]
        
        languages = []
        for code, name in languages_data:
            lang = Language.objects.create(code=code, name=name)
            languages.append(lang)
        
        return languages
    
    def _create_vehicles(self):
        vehicles_data = [
            {
                'code': 'B737',
                'name': 'Boeing 737',
                'total_seats': 189,
                'business_seats': 20,
                'economy_seats': 169,
                'min_pilots': 2,
                'max_pilots': 3,
                'min_cabin_crew': 5,
                'max_cabin_crew': 8,
                'standard_menu': 'Light snacks, beverages, hot meal option'
            },
            {
                'code': 'A320',
                'name': 'Airbus A320',
                'total_seats': 180,
                'business_seats': 16,
                'economy_seats': 164,
                'min_pilots': 2,
                'max_pilots': 3,
                'min_cabin_crew': 5,
                'max_cabin_crew': 8,
                'standard_menu': 'Snacks, drinks, meal service'
            },
            {
                'code': 'B777',
                'name': 'Boeing 777',
                'total_seats': 396,
                'business_seats': 42,
                'economy_seats': 354,
                'min_pilots': 2,
                'max_pilots': 4,
                'min_cabin_crew': 10,
                'max_cabin_crew': 16,
                'standard_menu': 'Full meal service, premium beverages'
            },
        ]
        
        vehicles = []
        for data in vehicles_data:
            vehicle = VehicleType.objects.create(**data)
            vehicles.append(vehicle)
        
        return vehicles
    
    def _create_pilots(self, vehicles, languages):
        first_names = ['John', 'Sarah', 'Michael', 'Emma', 'David', 'Olivia']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia']
        nationalities = ['USA', 'UK', 'Canada', 'Turkey', 'Germany', 'France']
        
        # Create 5 senior pilots
        for i in range(5):
            pilot = Pilot.objects.create(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                age=random.randint(35, 55),
                gender=random.choice([Gender.MALE, Gender.FEMALE]),
                nationality=random.choice(nationalities),
                seniority_level=PilotSeniorityLevel.SENIOR,
                vehicle_type=random.choice(vehicles),
                allowed_range=random.randint(8000, 15000),
                license_number=f'SNR-{1000+i}',
                is_active=True
            )
            pilot.known_languages.set(random.sample(languages, random.randint(2, 3)))
        
        # Create 10 junior pilots
        for i in range(10):
            pilot = Pilot.objects.create(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                age=random.randint(28, 45),
                gender=random.choice([Gender.MALE, Gender.FEMALE]),
                nationality=random.choice(nationalities),
                seniority_level=PilotSeniorityLevel.JUNIOR,
                vehicle_type=random.choice(vehicles),
                allowed_range=random.randint(3000, 8000),
                license_number=f'JNR-{2000+i}',
                is_active=True
            )
            pilot.known_languages.set(random.sample(languages, random.randint(2, 3)))
        
        # Create 3 trainee pilots
        for i in range(3):
            pilot = Pilot.objects.create(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                age=random.randint(21, 30),
                gender=random.choice([Gender.MALE, Gender.FEMALE]),
                nationality=random.choice(nationalities),
                seniority_level=PilotSeniorityLevel.TRAINEE,
                vehicle_type=random.choice(vehicles[:2]),
                allowed_range=random.randint(1000, 3000),
                license_number=f'TRN-{3000+i}',
                is_active=True
            )
            pilot.known_languages.set(random.sample(languages, random.randint(1, 2)))
    
    def _create_cabin_attendants(self, vehicles, languages):
        first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank']
        last_names = ['Taylor', 'Anderson', 'Thomas', 'Jackson', 'White', 'Harris']
        nationalities = ['USA', 'UK', 'Canada', 'Turkey', 'Germany', 'France']
        
        # Create 3 chiefs
        for i in range(3):
            attendant = CabinAttendant.objects.create(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                age=random.randint(32, 50),
                gender=random.choice([Gender.MALE, Gender.FEMALE]),
                nationality=random.choice(nationalities),
                attendant_type=AttendantType.CHIEF,
                employee_number=f'CHF-{4000+i}',
                is_active=True
            )
            attendant.allowed_vehicle_types.set(random.sample(vehicles, random.randint(2, 3)))
            attendant.known_languages.set(random.sample(languages, random.randint(2, 3)))
        
        # Create 15 regular attendants
        for i in range(15):
            attendant = CabinAttendant.objects.create(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                age=random.randint(22, 45),
                gender=random.choice([Gender.MALE, Gender.FEMALE]),
                nationality=random.choice(nationalities),
                attendant_type=AttendantType.REGULAR,
                employee_number=f'REG-{5000+i}',
                is_active=True
            )
            attendant.allowed_vehicle_types.set(random.sample(vehicles, random.randint(1, 3)))
            attendant.known_languages.set(random.sample(languages, random.randint(2, 3)))
        
        # Create 2 chefs with recipes
        dishes = ['Pasta Carbonara', 'Beef Wellington', 'Sushi Platter', 'Chicken Curry']
        cuisines = ['Italian', 'French', 'Japanese', 'Indian']
        
        for i in range(2):
            chef = CabinAttendant.objects.create(
                first_name=random.choice(first_names),
                last_name=random.choice(last_names),
                age=random.randint(28, 55),
                gender=random.choice([Gender.MALE, Gender.FEMALE]),
                nationality=random.choice(nationalities),
                attendant_type=AttendantType.CHEF,
                employee_number=f'CHE-{6000+i}',
                is_active=True
            )
            chef.allowed_vehicle_types.set(random.sample(vehicles, random.randint(2, 3)))
            chef.known_languages.set(random.sample(languages, random.randint(2, 3)))
            
            # Add 2-3 recipes for each chef
            for j in range(random.randint(2, 3)):
                DishRecipe.objects.create(
                    name=random.choice(dishes),
                    description=f'Delicious dish prepared by our chef',
                    cuisine_type=random.choice(cuisines),
                    preparation_time=random.randint(20, 60),
                    chef=chef,
                    is_active=True
                )
    
    def _print_statistics(self):
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 DATABASE SUMMARY')
        self.stdout.write('='*50)
        
        self.stdout.write(f'Languages: {Language.objects.count()}')
        self.stdout.write(f'Aircraft Types: {VehicleType.objects.count()}')
        
        self.stdout.write(f'\n✈️ Pilots: {Pilot.objects.count()}')
        self.stdout.write(f'  - Senior: {Pilot.objects.filter(seniority_level=PilotSeniorityLevel.SENIOR).count()}')
        self.stdout.write(f'  - Junior: {Pilot.objects.filter(seniority_level=PilotSeniorityLevel.JUNIOR).count()}')
        self.stdout.write(f'  - Trainee: {Pilot.objects.filter(seniority_level=PilotSeniorityLevel.TRAINEE).count()}')
        
        self.stdout.write(f'\n👥 Cabin Crew: {CabinAttendant.objects.count()}')
        self.stdout.write(f'  - Chiefs: {CabinAttendant.objects.filter(attendant_type=AttendantType.CHIEF).count()}')
        self.stdout.write(f'  - Regular: {CabinAttendant.objects.filter(attendant_type=AttendantType.REGULAR).count()}')
        self.stdout.write(f'  - Chefs: {CabinAttendant.objects.filter(attendant_type=AttendantType.CHEF).count()}')
        
        self.stdout.write(f'\n🍽️ Recipes: {DishRecipe.objects.count()}')
        self.stdout.write('='*50 + '\n')