from django.contrib import admin
from django.urls import path, include

# Imports for JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # --- FIX: Specific routes MUST come BEFORE the general include ---
    # These handle /api/token/ and /api/token/refresh/
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # This handles all other /api/ routes (like /api/predict/ and /api/register/)
    path('api/', include('predictor.urls')),
]

