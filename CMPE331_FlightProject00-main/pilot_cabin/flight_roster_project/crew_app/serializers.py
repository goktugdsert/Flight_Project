from rest_framework import serializers
from .models import (
    Pilot, CabinAttendant, VehicleType, Language, 
    DishRecipe, PilotSeniorityLevel, AttendantType
)

# ==================== SUPPORTING SERIALIZERS ====================

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'code', 'name']

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = [
            'id', 'code', 'name', 'total_seats', 'business_seats', 
            'economy_seats', 'min_pilots', 'max_pilots', 
            'min_cabin_crew', 'max_cabin_crew', 'standard_menu'
        ]

class VehicleTypeMinimalSerializer(serializers.ModelSerializer):
    """Smaller version - just basic info"""
    class Meta:
        model = VehicleType
        fields = ['id', 'code', 'name']

# ==================== PILOT SERIALIZERS ====================

class PilotListSerializer(serializers.ModelSerializer):
    """For showing list of pilots"""
    full_name = serializers.ReadOnlyField()
    
    vehicle_types = serializers.SlugRelatedField(
        source='vehicle_type', 
        read_only=True, 
        slug_field='name'
    )
    
    known_languages = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Pilot
        fields = [
            'pilot_id', 'full_name', 'age', 'gender', 'nationality',
            'seniority_level', 'vehicle_types', 'allowed_range',
            'known_languages', 'is_active'
        ]

class PilotDetailSerializer(serializers.ModelSerializer):
    """For showing ONE pilot with all details"""
    full_name = serializers.ReadOnlyField()
    vehicle_type = VehicleTypeSerializer(read_only=True)
    known_languages = LanguageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pilot
        fields = [
            'pilot_id', 'first_name', 'last_name', 'full_name', 
            'age', 'gender', 'nationality', 'seniority_level',
            'vehicle_type', 'allowed_range', 'known_languages',
            'is_active', 'license_number', 'created_at', 'updated_at'
        ]

class PilotCreateUpdateSerializer(serializers.ModelSerializer):
    """For creating or updating a pilot"""
    known_languages = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Language.objects.all()
    )
    
    class Meta:
        model = Pilot
        fields = [
            'first_name', 'last_name', 'age', 'gender', 'nationality',
            'seniority_level', 'vehicle_type', 'allowed_range',
            'known_languages', 'is_active', 'license_number'
        ]

# ==================== CABIN CREW SERIALIZERS ====================

class DishRecipeSerializer(serializers.ModelSerializer):
    chef_name = serializers.CharField(source='chef.full_name', read_only=True)
    
    class Meta:
        model = DishRecipe
        fields = [
            'id', 'name', 'description', 'cuisine_type',
            'preparation_time', 'chef', 'chef_name', 'is_active'
        ]

class CabinAttendantListSerializer(serializers.ModelSerializer):
    """For showing list of cabin attendants"""
    full_name = serializers.ReadOnlyField()
    
    vehicle_types = serializers.SlugRelatedField(
        source='allowed_vehicle_types', 
        many=True, 
        read_only=True, 
        slug_field='name'
    )
    
    known_languages = serializers.StringRelatedField(many=True)
    

    known_recipes = serializers.SlugRelatedField(
        source='recipes', 
        many=True,
        read_only=True,
        slug_field='name' 
    )
    
    class Meta:
        model = CabinAttendant
        fields = [
            'attendant_id', 'full_name', 'age', 'gender', 'nationality',
            'attendant_type', 'vehicle_types', 'known_languages',
            'known_recipes', 'is_active'
        ]

class CabinAttendantDetailSerializer(serializers.ModelSerializer):
    """For showing ONE cabin attendant with all details"""
    full_name = serializers.ReadOnlyField()
    allowed_vehicle_types = VehicleTypeSerializer(many=True, read_only=True)
    known_languages = LanguageSerializer(many=True, read_only=True)
    recipes = DishRecipeSerializer(many=True, read_only=True)
    
    class Meta:
        model = CabinAttendant
        fields = [
            'attendant_id', 'first_name', 'last_name', 'full_name',
            'age', 'gender', 'nationality', 'attendant_type',
            'allowed_vehicle_types', 'known_languages', 'is_active',
            'employee_number', 'recipes', 'created_at', 'updated_at'
        ]

class CabinAttendantCreateUpdateSerializer(serializers.ModelSerializer):
    """For creating or updating a cabin attendant"""
    known_languages = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Language.objects.all()
    )
    allowed_vehicle_types = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=VehicleType.objects.all()
    )
    
    class Meta:
        model = CabinAttendant
        fields = [
            'first_name', 'last_name', 'age', 'gender', 'nationality',
            'attendant_type', 'allowed_vehicle_types', 'known_languages',
            'is_active', 'employee_number'
        ]

# ==================== RECIPE SERIALIZERS ====================

class DishRecipeCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DishRecipe
        fields = [
            'name', 'description', 'cuisine_type',
            'preparation_time', 'chef', 'is_active'
        ]
    
    def validate_chef(self, value):
        if value.attendant_type != AttendantType.CHEF:
            raise serializers.ValidationError(
                "Recipes can only be assigned to attendants with CHEF type"
            )
        return value
