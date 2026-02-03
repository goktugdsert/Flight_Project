from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PilotViewSet, CabinAttendantViewSet, DishRecipeViewSet,
    LanguageViewSet, VehicleTypeViewSet
)

router = DefaultRouter()
router.register(r'pilots', PilotViewSet, basename='pilot')
router.register(r'attendants', CabinAttendantViewSet, basename='cabin-attendant')
router.register(r'recipes', DishRecipeViewSet, basename='recipe')
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'vehicles', VehicleTypeViewSet, basename='vehicle-type')

app_name = 'crew'

urlpatterns = [
    path('', include(router.urls)),
]
