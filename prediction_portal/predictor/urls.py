from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Main prediction API
    path('predict/<str:ticker>/', views.StockPredictionView.as_view(), name='predict-stock'),
    
    # 10-Year historical chart API
    path('historical-chart/<str:ticker>/', views.HistoricalChartView.as_view(), name='historical-chart'),
]

