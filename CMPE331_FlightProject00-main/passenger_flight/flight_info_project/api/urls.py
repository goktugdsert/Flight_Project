from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlightViewSet, PassengerViewSet, AirportViewSet, VehicleTypeViewSet

router = DefaultRouter()
router.register(r'flights', FlightViewSet)
router.register(r'passengers', PassengerViewSet)
router.register(r'airports', AirportViewSet)
router.register(r'vehicles', VehicleTypeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]