from django.urls import path
# Fix 1: Import the correct class name 'StockPredictionView'
from .views import StockPredictionView 

urlpatterns = [
    # Fix 2: Update the path to capture the ticker from the URL
    # This now matches the URL the frontend is calling
    path('predict/<str:ticker>/', StockPredictionView.as_view(), name='predict-stock'),
]

