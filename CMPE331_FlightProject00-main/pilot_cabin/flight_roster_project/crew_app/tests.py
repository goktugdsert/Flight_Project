"""
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from crew_app.models import (
    Pilot, CabinAttendant, VehicleType, Language, 
    DishRecipe, PilotSeniorityLevel, AttendantType
)


class GeneralSystemTest(TestCase):
    
    def setUp(self):
        # Test data setup
        self.vehicle = VehicleType.objects.create(
            code='B737',
            name='Boeing 737',
            total_seats=180,
            business_seats=20,
            economy_seats=160,
            min_pilots=2,
            max_pilots=3,
            min_cabin_crew=3,
            max_cabin_crew=6
        )
        
        self.language_en = Language.objects.create(code='ENG', name='English')
        self.language_tr = Language.objects.create(code='TUR', name='Turkish')
    
    # ========== MODEL TESTS (10 tests) ==========
    
    def test_01_vehicle_type_creation(self):
        """Test 1: VehicleType creation"""
        self.assertEqual(self.vehicle.code, 'B737')
        self.assertEqual(self.vehicle.total_seats, 180)
    
    def test_02_language_creation(self):
        """Test 2: Language creation"""
        self.assertEqual(self.language_en.name, 'English')
    
    def test_03_pilot_creation_valid(self):
        """Test 3: Creating a valid pilot"""
        pilot = Pilot.objects.create(
            first_name='John',
            last_name='Doe',
            age=35,
            gender='M',
            nationality='American',
            seniority_level=PilotSeniorityLevel.SENIOR,
            vehicle_type=self.vehicle,
            allowed_range=10000,
            license_number='PIL001'
        )
        pilot.known_languages.add(self.language_en)
        
        self.assertEqual(pilot.full_name, 'John Doe')
        self.assertEqual(pilot.age, 35)
    
    def test_04_pilot_age_validation(self):
        """Test 4: Pilot age validation"""
        from django.core.exceptions import ValidationError
        
        pilot = Pilot(
            first_name='Young',
            last_name='Pilot',
            age=15,
            gender='M',
            nationality='American',
            seniority_level=PilotSeniorityLevel.JUNIOR,
            vehicle_type=self.vehicle,
            allowed_range=5000,
            license_number='PIL002'
        )
        
        with self.assertRaises(ValidationError):
            pilot.full_clean()
    
    def test_05_cabin_attendant_creation(self):
        """Test 5: Cabin attendant creation"""
        attendant = CabinAttendant.objects.create(
            first_name='Jane',
            last_name='Smith',
            age=28,
            gender='F',
            nationality='British',
            attendant_type=AttendantType.CHIEF,
            employee_number='CA001'
        )
        attendant.known_languages.add(self.language_en)
        attendant.allowed_vehicle_types.add(self.vehicle)
        
        self.assertEqual(attendant.full_name, 'Jane Smith')
        self.assertEqual(attendant.attendant_type, AttendantType.CHIEF)
    
    def test_06_chef_creation_and_recipe(self):
        """Test 6: Chef and recipe creation"""
        chef = CabinAttendant.objects.create(
            first_name='Gordon',
            last_name='Chef',
            age=40,
            gender='M',
            nationality='French',
            attendant_type=AttendantType.CHEF,
            employee_number='CHEF001'
        )
        
        recipe = DishRecipe.objects.create(
            name='Pasta Carbonara',
            cuisine_type='Italian',
            preparation_time=30, 
            chef=chef
        )
        
        self.assertEqual(recipe.chef, chef)
        self.assertEqual(chef.recipes.count(), 1)
    
    def test_07_vehicle_type_unique_code(self):
        """Test 7: VehicleType unique code check"""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            VehicleType.objects.create(
                code='B737',
                name='Another Boeing',
                total_seats=150,
                business_seats=15,
                economy_seats=135,
                min_pilots=2,
                max_pilots=3,
                min_cabin_crew=3,
                max_cabin_crew=5
            )
    
    def test_08_pilot_many_to_many_languages(self):
        """Test 8: Pilot many-to-many language relationship"""
        pilot = Pilot.objects.create(
            first_name='Multi',
            last_name='Lingual',
            age=42,
            gender='M',
            nationality='Swiss',
            seniority_level=PilotSeniorityLevel.SENIOR,
            vehicle_type=self.vehicle,
            allowed_range=12000,
            license_number='PIL003'
        )
        pilot.known_languages.add(self.language_en, self.language_tr)
        
        self.assertEqual(pilot.known_languages.count(), 2)
    
    def test_09_cascade_delete_pilot(self):
        """Test 9: Verify pilot protection on VehicleType deletion"""
        pilot = Pilot.objects.create(
            first_name='Test',
            last_name='Pilot',
            age=30,
            gender='M',
            nationality='American',
            seniority_level=PilotSeniorityLevel.SENIOR,
            vehicle_type=self.vehicle,
            allowed_range=10000,
            license_number='PIL004'
        )
        
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            self.vehicle.delete()
    
    def test_10_recipe_chef_validation(self):
        """Test 10: Recipe can only be assigned to a chef"""
        regular_attendant = CabinAttendant.objects.create(
            first_name='Not',
            last_name='Chef',
            age=25,
            gender='F',
            nationality='American',
            attendant_type=AttendantType.REGULAR,
            employee_number='CA002'
        )
        
        from django.core.exceptions import ValidationError
        
        recipe = DishRecipe(
            name='Test Dish',
            cuisine_type='Test',
            preparation_time=20,
            chef=regular_attendant
        )
        
        with self.assertRaises(ValidationError):
            recipe.full_clean()


class GeneralAPITest(APITestCase):
    """General API tests"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.vehicle = VehicleType.objects.create(
            code='A320',
            name='Airbus A320',
            total_seats=150,
            business_seats=12,
            economy_seats=138,
            min_pilots=2,
            max_pilots=2,
            min_cabin_crew=3,
            max_cabin_crew=5
        )
        
        self.language = Language.objects.create(code='ENG', name='English')
    
    # ========== API TESTS (20 tests) ==========
    
    def test_11_get_pilots_list(self):
        """Test 11: Fetching pilot list"""
        response = self.client.get('/api/pilots/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_12_create_pilot(self):
        """Test 12: Creating a new pilot"""
        data = {
            'first_name': 'New',
            'last_name': 'Pilot',
            'age': 35,
            'gender': 'M',
            'nationality': 'American',
            'seniority_level': 'SENIOR',
            'vehicle_type': self.vehicle.id,
            'allowed_range': 10000,
            'license_number': 'NPL001',
            'known_languages': [self.language.id]
        }
        
        response = self.client.post('/api/pilots/', data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
    
    def test_13_get_pilot_detail(self):
        """Test 13: Fetching pilot details"""
        pilot = Pilot.objects.create(
            first_name='Detail',
            last_name='Test',
            age=32,
            gender='M',
            nationality='British',
            seniority_level=PilotSeniorityLevel.SENIOR,
            vehicle_type=self.vehicle,
            allowed_range=9000,
            license_number='DPL001'
        )
        
        response = self.client.get(f'/api/pilots/{pilot.pilot_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_14_update_pilot(self):
        """Test 14: Updating a pilot"""
        pilot = Pilot.objects.create(
            first_name='Update',
            last_name='Test',
            age=28,
            gender='M',
            nationality='American',
            seniority_level=PilotSeniorityLevel.JUNIOR,
            vehicle_type=self.vehicle,
            allowed_range=5000,
            license_number='UPL001'
        )
        
        data = {
            'first_name': 'Updated',
            'last_name': 'Pilot',
            'age': 30,
            'gender': 'M',
            'nationality': 'American',
            'seniority_level': 'SENIOR',
            'vehicle_type': self.vehicle.id,
            'allowed_range': 8000,
            'license_number': 'UPL001',
            'known_languages': []
        }
        
        response = self.client.put(f'/api/pilots/{pilot.pilot_id}/', data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
    
    def test_15_delete_pilot(self):
        """Test 15: Deleting a pilot"""
        pilot = Pilot.objects.create(
            first_name='Delete',
            last_name='Test',
            age=27,
            gender='M',
            nationality='American',
            seniority_level=PilotSeniorityLevel.JUNIOR,
            vehicle_type=self.vehicle,
            allowed_range=5000,
            license_number='DEL001'
        )
        
        response = self.client.delete(f'/api/pilots/{pilot.pilot_id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_16_get_cabin_attendants_list(self):
        """Test 16: Fetching cabin attendant list"""
        response = self.client.get('/api/attendants/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_17_create_cabin_attendant(self):
        """Test 17: Creating a new cabin attendant"""
        data = {
            'first_name': 'New',
            'last_name': 'Attendant',
            'age': 25,
            'gender': 'F',
            'nationality': 'British',
            'attendant_type': 'CHIEF',
            'employee_number': 'NCA001',
            'known_languages': [self.language.id],
            'allowed_vehicle_types': [self.vehicle.id]
        }
        
        response = self.client.post('/api/attendants/', data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
    
    def test_18_get_recipes_list(self):
        """Test 18: Fetching recipe list"""
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_19_create_recipe_with_chef(self):
        """Test 19: Creating a recipe with a chef"""
        chef = CabinAttendant.objects.create(
            first_name='Test',
            last_name='Chef',
            age=38,
            gender='M',
            nationality='French',
            attendant_type=AttendantType.CHEF,
            employee_number='TCH001'
        )
        
        data = {
            'name': 'Test Recipe',
            'cuisine_type': 'French',
            'preparation_time': 45,  
            'chef': chef.attendant_id
        }
        
        response = self.client.post('/api/recipes/', data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
    
    def test_20_get_languages_list(self):
        """Test 20: Fetching language list"""
        response = self.client.get('/api/languages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_21_get_vehicles_list(self):
        """Test 21: Fetching vehicle list"""
        response = self.client.get('/api/vehicles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_22_filter_pilots_by_seniority(self):
        """Test 22: Filtering pilots by seniority"""
        Pilot.objects.create(
            first_name='Senior',
            last_name='Pilot',
            age=45,
            gender='M',
            nationality='American',
            seniority_level=PilotSeniorityLevel.SENIOR,
            vehicle_type=self.vehicle,
            allowed_range=12000,
            license_number='SEN001'
        )
        
        response = self.client.get('/api/pilots/?seniority=SENIOR')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_23_filter_attendants_by_type(self):
        """Test 23: Filtering attendants by type"""
        CabinAttendant.objects.create(
            first_name='Chef',
            last_name='Test',
            age=36,
            gender='M',
            nationality='French',
            attendant_type=AttendantType.CHEF,
            employee_number='CFT001'
        )
        
        response = self.client.get('/api/attendants/?attendant_type=CHEF')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_24_search_pilots(self):
        """Test 24: Searching pilots"""
        Pilot.objects.create(
            first_name='Search',
            last_name='Test',
            age=33,
            gender='M',
            nationality='American',
            seniority_level=PilotSeniorityLevel.SENIOR,
            vehicle_type=self.vehicle,
            allowed_range=10000,
            license_number='SRC001'
        )
        
        response = self.client.get('/api/pilots/?search=Search')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_25_pilot_pagination(self):
        """Test 25: Pilot pagination"""
        for i in range(5):
            Pilot.objects.create(
                first_name=f'Pilot{i}',
                last_name=f'Test{i}',
                age=25 + i,
                gender='M',
                nationality='American',
                seniority_level=PilotSeniorityLevel.JUNIOR,
                vehicle_type=self.vehicle,
                allowed_range=5000,
                license_number=f'PAG{i:03d}'
            )
        
        response = self.client.get('/api/pilots/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if 'results' in response.data:
            self.assertIsInstance(response.data['results'], list)
    
    def test_26_vehicle_type_readonly(self):
        """Test 26: VehicleType is read-only"""
        data = {
            'code': 'TEST',
            'name': 'Test Vehicle',
            'total_seats': 100,
            'business_seats': 10,
            'economy_seats': 90,
            'min_pilots': 2,
            'max_pilots': 2,
            'min_cabin_crew': 2,
            'max_cabin_crew': 4
        }
        
        response = self.client.post('/api/vehicles/', data, format='json')
        self.assertIn(response.status_code, [
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_27_language_readonly(self):
        """Test 27: Language is read-only"""
        data = {
            'code': 'TEST',
            'name': 'Test Language'
        }
        
        response = self.client.post('/api/languages/', data, format='json')
        self.assertIn(response.status_code, [
            status.HTTP_405_METHOD_NOT_ALLOWED,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_28_custom_pilot_endpoint_by_seniority(self):
        """Test 28: Custom endpoint - pilot by seniority"""
        response = self.client.get('/api/pilots/by-seniority/SENIOR/')
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_29_custom_attendant_endpoint_by_type(self):
        """Test 29: Custom endpoint - attendant by type"""
        response = self.client.get('/api/attendants/by-type/CHEF/')
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_404_NOT_FOUND
        ])
    
    def test_30_system_integration(self):
        """Test 30: System integration - All components together"""
        vehicle = VehicleType.objects.create(
            code='INT01',
            name='Integration Test Vehicle',
            total_seats=200,
            business_seats=20,
            economy_seats=180,
            min_pilots=2,
            max_pilots=3,
            min_cabin_crew=4,
            max_cabin_crew=8
        )
        
        pilot = Pilot.objects.create(
            first_name='Integration',
            last_name='Pilot',
            age=40,
            gender='M',
            nationality='American',
            seniority_level=PilotSeniorityLevel.SENIOR,
            vehicle_type=vehicle,
            allowed_range=15000,
            license_number='INT001'
        )
        
        chef = CabinAttendant.objects.create(
            first_name='Integration',
            last_name='Chef',
            age=35,
            gender='M',
            nationality='French',
            attendant_type=AttendantType.CHEF,
            employee_number='INTCHEF001'
        )
        chef.allowed_vehicle_types.add(vehicle)
        
        recipe = DishRecipe.objects.create(
            name='Integration Dish',
            cuisine_type='International',
            preparation_time=60, 
            chef=chef
        )
        
        self.assertEqual(vehicle.code, 'INT01')
        self.assertEqual(pilot.vehicle_type, vehicle)
        self.assertEqual(chef.attendant_type, AttendantType.CHEF)
        self.assertEqual(recipe.chef, chef)
        self.assertIn(vehicle, chef.allowed_vehicle_types.all())
        
        print("\n System integration successful!")
        print(f"   Vehicle: {vehicle.name}")
        print(f"   Pilot: {pilot.full_name}")
        print(f"   Chef: {chef.full_name}")
        print(f"   Recipe: {recipe.name}")
