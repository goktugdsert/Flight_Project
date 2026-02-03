from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny

from .models import (
    Pilot, CabinAttendant, VehicleType, Language, 
    DishRecipe, PilotSeniorityLevel, AttendantType
)
from .serializers import (
    PilotListSerializer, PilotDetailSerializer, PilotCreateUpdateSerializer,
    CabinAttendantListSerializer, CabinAttendantDetailSerializer, 
    CabinAttendantCreateUpdateSerializer, DishRecipeSerializer,
    DishRecipeCreateUpdateSerializer, LanguageSerializer, VehicleTypeSerializer
)

# ==================== PILOT VIEWS ====================

class PilotViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Pilots
    - List all pilots
    - Create new pilot
    - Get pilot details
    - Update pilot
    - Delete pilot
    """
    queryset = Pilot.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'license_number', 'nationality']
    ordering_fields = ['pilot_id', 'seniority_level', 'age', 'allowed_range']
    ordering = ['-seniority_level', 'last_name']
    
    def get_queryset(self):
        """Get pilots with filters"""
        queryset = Pilot.objects.select_related('vehicle_type').prefetch_related('known_languages')
        
        # Filter by seniority level
        seniority = self.request.query_params.get('seniority_level')
        if seniority:
            queryset = queryset.filter(seniority_level=seniority)
        
        # Filter by vehicle type
        vehicle_type = self.request.query_params.get('vehicle_type')
        if vehicle_type:
            queryset = queryset.filter(vehicle_type_id=vehicle_type)
        
        # Filter by minimum range
        min_range = self.request.query_params.get('min_allowed_range')
        if min_range:
            queryset = queryset.filter(allowed_range__gte=min_range)
        
        # Filter by nationality
        nationality = self.request.query_params.get('nationality')
        if nationality:
            queryset = queryset.filter(nationality__icontains=nationality)
        
        # Filter by language
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(known_languages__code=language)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.distinct()
    
    def get_serializer_class(self):
        """Choose which serializer to use"""
        if self.action == 'list':
            return PilotListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PilotCreateUpdateSerializer
        return PilotDetailSerializer
    
    @action(detail=False, methods=['get'], url_path='by-seniority/(?P<level>[^/.]+)')
    def by_seniority(self, request, level=None):
        """Get pilots by seniority level: /api/pilots/by-seniority/SENIOR/"""
        if level not in dict(PilotSeniorityLevel.choices):
            return Response(
                {'error': f'Invalid seniority level. Choose: SENIOR, JUNIOR, or TRAINEE'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pilots = self.get_queryset().filter(seniority_level=level, is_active=True)
        serializer = PilotListSerializer(pilots, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-vehicle/(?P<vehicle_id>[0-9]+)')
    def by_vehicle(self, request, vehicle_id=None):
        """Get pilots who can fly specific aircraft: /api/pilots/by-vehicle/1/"""
        try:
            vehicle = VehicleType.objects.get(id=vehicle_id)
        except VehicleType.DoesNotExist:
            return Response(
                {'error': 'Vehicle type not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        pilots = self.get_queryset().filter(vehicle_type=vehicle, is_active=True)
        serializer = PilotListSerializer(pilots, many=True)
        return Response({
            'vehicle': VehicleTypeSerializer(vehicle).data,
            'pilots': serializer.data,
            'count': pilots.count()
        })
    
    @action(detail=False, methods=['get'])
    def available_for_flight(self, request):
        """
        Get pilots available for a specific flight
        Usage: /api/pilots/available_for_flight/?vehicle_type_id=1&flight_distance=5000
        """
        vehicle_type_id = request.query_params.get('vehicle_type_id')
        flight_distance = request.query_params.get('flight_distance')
        
        if not vehicle_type_id:
            return Response(
                {'error': 'vehicle_type_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            vehicle_type_id=vehicle_type_id,
            is_active=True
        )
        
        if flight_distance:
            queryset = queryset.filter(allowed_range__gte=flight_distance)
        
        # Group by seniority
        senior_pilots = queryset.filter(seniority_level=PilotSeniorityLevel.SENIOR)
        junior_pilots = queryset.filter(seniority_level=PilotSeniorityLevel.JUNIOR)
        trainee_pilots = queryset.filter(seniority_level=PilotSeniorityLevel.TRAINEE)
        
        return Response({
            'senior_pilots': PilotListSerializer(senior_pilots, many=True).data,
            'junior_pilots': PilotListSerializer(junior_pilots, many=True).data,
            'trainee_pilots': PilotListSerializer(trainee_pilots, many=True).data,
            'counts': {
                'senior': senior_pilots.count(),
                'junior': junior_pilots.count(),
                'trainee': trainee_pilots.count(),
                'total': queryset.count()
            }
        })

# ==================== CABIN CREW VIEWS ====================

class CabinAttendantViewSet(viewsets.ModelViewSet):
    """
    API endpoints for Cabin Attendants
    - List all attendants
    - Create new attendant
    - Get attendant details
    - Update attendant
    - Delete attendant
    """
    queryset = CabinAttendant.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'employee_number', 'nationality']
    ordering_fields = ['attendant_id', 'attendant_type', 'age']
    ordering = ['attendant_type', 'last_name']
    
    def get_queryset(self):
        """Get cabin attendants with filters"""
        queryset = CabinAttendant.objects.prefetch_related(
            'allowed_vehicle_types',
            'known_languages',
            Prefetch('recipes', queryset=DishRecipe.objects.filter(is_active=True))
        )
        
        # Filter by attendant type
        attendant_type = self.request.query_params.get('attendant_type')
        if attendant_type:
            queryset = queryset.filter(attendant_type=attendant_type)
        
        # Filter by vehicle type
        vehicle_type = self.request.query_params.get('vehicle_type')
        if vehicle_type:
            queryset = queryset.filter(allowed_vehicle_types__id=vehicle_type)
        
        # Filter by nationality
        nationality = self.request.query_params.get('nationality')
        if nationality:
            queryset = queryset.filter(nationality__icontains=nationality)
        
        # Filter by language
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(known_languages__code=language)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.distinct()
    
    def get_serializer_class(self):
        """Choose which serializer to use"""
        if self.action == 'list':
            return CabinAttendantListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CabinAttendantCreateUpdateSerializer
        return CabinAttendantDetailSerializer
    
    @action(detail=False, methods=['get'], url_path='by-type/(?P<attendant_type>[^/.]+)')
    def by_type(self, request, attendant_type=None):
        """Get attendants by type: /api/cabin-crew/by-type/CHIEF/"""
        if attendant_type not in dict(AttendantType.choices):
            return Response(
                {'error': f'Invalid type. Choose: CHIEF, REGULAR, or CHEF'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        attendants = self.get_queryset().filter(attendant_type=attendant_type, is_active=True)
        serializer = CabinAttendantListSerializer(attendants, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-vehicle/(?P<vehicle_id>[0-9]+)')
    def by_vehicle(self, request, vehicle_id=None):
        """Get attendants who can work on specific aircraft: /api/cabin-crew/by-vehicle/1/"""
        try:
            vehicle = VehicleType.objects.get(id=vehicle_id)
        except VehicleType.DoesNotExist:
            return Response(
                {'error': 'Vehicle type not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        attendants = self.get_queryset().filter(allowed_vehicle_types=vehicle, is_active=True)
        serializer = CabinAttendantListSerializer(attendants, many=True)
        return Response({
            'vehicle': VehicleTypeSerializer(vehicle).data,
            'attendants': serializer.data,
            'count': attendants.count()
        })
    
    @action(detail=False, methods=['get'])
    def available_for_flight(self, request):
        """
        Get cabin crew available for a specific flight
        Usage: /api/cabin-crew/available_for_flight/?vehicle_type_id=1
        """
        vehicle_type_id = request.query_params.get('vehicle_type_id')
        
        if not vehicle_type_id:
            return Response(
                {'error': 'vehicle_type_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            allowed_vehicle_types__id=vehicle_type_id,
            is_active=True
        )
        
        # Group by type
        chiefs = queryset.filter(attendant_type=AttendantType.CHIEF)
        regulars = queryset.filter(attendant_type=AttendantType.REGULAR)
        chefs = queryset.filter(attendant_type=AttendantType.CHEF)
        
        return Response({
            'chiefs': CabinAttendantListSerializer(chiefs, many=True).data,
            'regulars': CabinAttendantListSerializer(regulars, many=True).data,
            'chefs': CabinAttendantListSerializer(chefs, many=True).data,
            'counts': {
                'chief': chiefs.count(),
                'regular': regulars.count(),
                'chef': chefs.count(),
                'total': queryset.count()
            }
        })

# ==================== SUPPORTING VIEWS ====================

class DishRecipeViewSet(viewsets.ModelViewSet):
    """API endpoints for Recipes"""
    queryset = DishRecipe.objects.select_related('chef').all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', 'cuisine_type', 'chef__first_name', 'chef__last_name']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DishRecipeCreateUpdateSerializer
        return DishRecipeSerializer
    
    @action(detail=False, methods=['get'], url_path='by-chef/(?P<chef_id>[0-9]+)')
    def by_chef(self, request, chef_id=None):
        """Get all recipes by a specific chef: /api/recipes/by-chef/1/"""
        try:
            chef = CabinAttendant.objects.get(attendant_id=chef_id)
            if chef.attendant_type != AttendantType.CHEF:
                return Response(
                    {'error': 'This attendant is not a chef'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except CabinAttendant.DoesNotExist:
            return Response(
                {'error': 'Chef not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        recipes = self.queryset.filter(chef=chef, is_active=True)
        serializer = DishRecipeSerializer(recipes, many=True)
        return Response(serializer.data)


class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for Languages (read-only)"""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']


class VehicleTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoints for Vehicle Types (read-only)"""
    queryset = VehicleType.objects.all()
    serializer_class = VehicleTypeSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['code', 'name']