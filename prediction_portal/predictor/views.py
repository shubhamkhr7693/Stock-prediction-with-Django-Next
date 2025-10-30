from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
import yfinance as yf
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
from django.conf import settings
from datetime import datetime, timedelta

# --- Imports for Registration ---
from rest_framework import generics, serializers
from django.contrib.auth.models import User
# --- End of Registration Imports ---


# --- Load Model and Scaler ---
# Build paths relative to the project's base directory
MODEL_PATH = os.path.join(settings.BASE_DIR, 'stock_predictor.keras')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'scaler.gz')

# Load the trained model and scaler
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except IOError:
    model = None
    scaler = None
except Exception as e:
    print(f"Error loading model or scaler: {e}")
    model = None
    scaler = None

# --- Registration View ---
# We need a serializer for the registration
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # This allows anyone to access this specific view, even unauthenticated users.
    permission_classes = [AllowAny]


# --- Stock Prediction View (Main) ---

class StockPredictionView(APIView):
    """
    API view to predict the next day's stock price for a given ticker.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ticker_symbol = kwargs.get('ticker', None)
        if not ticker_symbol:
            return Response({"error": "No ticker symbol provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not model or not scaler:
             return Response({"error": "Model or scaler not loaded. Run model_builder.py"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # --- Get Exchange Rate ---
            exchange_rate = 83.0 # Default fallback
            try:
                # Correct ticker for USD to INR is "INR=X"
                inr_ticker = yf.Ticker("INR=X")
                inr_data = inr_ticker.history(period="1d")
                
                if not inr_data.empty:
                    exchange_rate = inr_data['Close'].iloc[-1]
                else:
                    print("Warning: Could not fetch INR=X, using fallback rate.")
                    
            except Exception as e:
                print(f"Warning: Could not fetch exchange rate. Defaulting to 83. Error: {e}")

            # 2. Fetch data from Yahoo Finance
            stock = yf.Ticker(ticker_symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365) # Get 1 year of data
            hist = stock.history(start=start_date, end=end_date) 

            if hist.empty:
                return Response({"error": "Invalid ticker or no data found"}, status=status.HTTP_404_NOT_FOUND)

            # 3. Calculate Moving Averages
            ma_100_series = hist['Close'].rolling(window=100).mean()
            ma_200_series = hist['Close'].rolling(window=200).mean()
            
            # Add check for nan on stat card values
            ma_100 = ma_100_series.iloc[-1] if not np.isnan(ma_100_series.iloc[-1]) else 0
            ma_200 = ma_200_series.iloc[-1] if not np.isnan(ma_200_series.iloc[-1]) else 0
            last_close = hist['Close'].iloc[-1]

            # 4. Preprocess Data for Prediction
            data = hist['Close'].values
            
            if len(data) < 60:
                return Response({"error": "Not enough historical data to make a prediction (need at least 60 days)."}, status=status.HTTP_400_BAD_REQUEST)

            scaled_data = scaler.transform(data.reshape(-1, 1))
            
            X_test = []
            X_test.append(scaled_data[-60:, 0])
            X_test = np.array(X_test)
            X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

            # 5. Make Prediction
            pred_scaled = model.predict(X_test, verbose=0) # Set verbose=0 to hide "1/1" log
            prediction = scaler.inverse_transform(pred_scaled)[0][0]

            # 6. Determine "Up" or "Down"
            if prediction > last_close:
                trend = "Up"
                confidence = min(98.0, 50.0 + (prediction - last_close) / last_close * 100 * 2) 
            else:
                trend = "Down"
                confidence = min(98.0, 50.0 + (last_close - prediction) / last_close * 100 * 2)

            # --- 7. Format Chart Data (300-day) ---
            chart_hist = hist.iloc[-300:]
            chart_ma_100 = ma_100_series.iloc[-300:]
            chart_ma_200 = ma_200_series.iloc[-300:]

            # Helper to convert np.nan to None (which becomes 'null' in JSON)
            def format_series_for_json(series, rate):
                 return [price * rate if not np.isnan(price) else None for price in series]

            chart_data = {
                "labels": [date.strftime('%Y-%m-%d') for date in chart_hist.index],
                "close_prices": format_series_for_json(chart_hist['Close'], exchange_rate),
                "ma_100": format_series_for_json(chart_ma_100, exchange_rate),
                "ma_200": format_series_for_json(chart_ma_200, exchange_rate),
            }

            # --- 8. Format Final Response (with Rupee conversion) ---
            response_data = {
                "ticker": ticker_symbol.upper(),
                
                "last_close_inr": f"{(last_close * exchange_rate):.2f}",
                "predicted_next_close_inr": f"{(prediction * exchange_rate):.2f}",
                "moving_average_100d_inr": f"{(ma_100 * exchange_rate):.2f}",
                "moving_average_200d_inr": f"{(ma_200 * exchange_rate):.2f}",

                "trend_prediction": trend,
                "confidence_percent": f"{confidence:.1f}",
                
                "chart_data": chart_data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Historical Chart View (10-Year) ---

class HistoricalChartView(APIView):
    """
    API view to fetch 10 years of historical data for long-term charts.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ticker_symbol = kwargs.get('ticker', None)
        if not ticker_symbol:
            return Response({"error": "No ticker symbol provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # --- Get Exchange Rate ---
            exchange_rate = 83.0 # Default fallback
            try:
                inr_ticker = yf.Ticker("INR=X")
                inr_data = inr_ticker.history(period="1d")
                if not inr_data.empty:
                    exchange_rate = inr_data['Close'].iloc[-1]
                else:
                    print("Warning: Could not fetch INR=X, using fallback rate.")
            except Exception as e:
                print(f"Warning: Could not fetch exchange rate. Defaulting to 83. Error: {e}")

            # 2. Fetch 10 YEARS of data
            stock = yf.Ticker(ticker_symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * 10) # 10 years
            hist = stock.history(start=start_date, end=end_date) 

            if hist.empty:
                return Response({"error": "Invalid ticker or no data found for 10-year period"}, status=status.HTTP_404_NOT_FOUND)

            # 3. Calculate 10-YEAR Moving Averages
            ma_100_series = hist['Close'].rolling(window=100).mean()
            ma_200_series = hist['Close'].rolling(window=200).mean()

            # --- 4. Format Chart Data ---
            # Helper to convert nan to None and apply exchange rate
            def format_series_for_json(series, rate):
                return [
                    price * rate if not np.isnan(price) else None 
                    for price in series
                ]

            chart_data = {
                "labels": [date.strftime('%Y-%m-%d') for date in hist.index],
                "ma_100": format_series_for_json(ma_100_series, exchange_rate),
                "ma_200": format_series_for_json(ma_200_series, exchange_rate),
            }
            
            return Response(chart_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

