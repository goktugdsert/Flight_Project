from django.contrib import admin
from django.urls import path, include
from roster.serializers import CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('roster.urls')),
    
    # --- AUTHENTICATION ENDPOINTS ---
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), # Login (Get Token)
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # Refresh Token
]