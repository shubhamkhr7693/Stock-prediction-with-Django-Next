from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import yfinance as yf
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import joblib
import os
from django.conf import settings

# --- Load Model and Scaler ---
# Build paths relative to the project's base directory
MODEL_PATH = os.path.join(settings.BASE_DIR, 'stock_predictor.keras')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'scaler.gz')

# Load the trained model and scaler
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except IOError:
    # This will be helpful for debugging if the files aren't found
    model = None
    scaler = None
except Exception as e:
    print(f"Error loading model or scaler: {e}")
    model = None
    scaler = None

class StockPredictionView(APIView):
    """
    API view to predict the next day's stock price for a given ticker.
    """
    def get(self, request, *args, **kwargs):
        # 1. Get Ticker from URL
        ticker = kwargs.get('ticker', None)
        if not ticker:
            return Response({"error": "No ticker symbol provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not model or not scaler:
             return Response({"error": "Model or scaler not loaded. Run model_builder.py"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # 2. Fetch data from Yahoo Finance
            stock = yf.Ticker(ticker)
            # We need at least 60 days to make one prediction, plus 200 days for the MA.
            hist = stock.history(period="300d") 

            # ---!!! THIS IS THE FIX !!!---
            # We must use .empty to check a pandas DataFrame, not 'if not hist:'
            if hist.empty:
                return Response({"error": "Invalid ticker or no data found"}, status=status.HTTP_404_NOT_FOUND)

            # 3. Calculate Moving Averages
            # Use .iloc[-1] to get the *most recent* day's value
            ma_100 = hist['Close'].rolling(window=100).mean().iloc[-1]
            ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
            last_close = hist['Close'].iloc[-1]

            # 4. Preprocess Data for Prediction
            data = hist['Close'].values
            
            # We need the last 60 days to predict the next one
            if len(data) < 60:
                return Response({"error": "Not enough historical data to make a prediction (need at least 60 days)."}, status=status.HTTP_400_BAD_REQUEST)

            # Scale *all* the data, then extract the last 60 days
            scaled_data = scaler.transform(data.reshape(-1, 1))
            
            # Get the last 60 days
            X_test = []
            X_test.append(scaled_data[-60:, 0])
            X_test = np.array(X_test)
            
            # Reshape for the LSTM model
            X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

            # 5. Make Prediction
            pred_scaled = model.predict(X_test)
            
            # Inverse the scaling to get the actual price
            prediction = scaler.inverse_transform(pred_scaled)[0][0]

            # 6. Determine "Up" or "Down"
            # Simple logic: is the prediction higher than the last close?
            if prediction > last_close:
                trend = "Up"
                # Simple "confidence" based on distance from last close
                confidence = min(98.0, 50.0 + (prediction - last_close) / last_close * 100 * 2) 
            else:
                trend = "Down"
                confidence = min(98.0, 50.0 + (last_close - prediction) / last_close * 100 * 2)

            # 7. Format and Return Response
            response_data = {
                "ticker": ticker.upper(),
                "last_close": f"{last_close:.2f}",
                "predicted_next_close": f"{prediction:.2f}",
                "trend_prediction": trend,
                "confidence_percent": f"{confidence:.1f}",
                "moving_average_100d": f"{ma_100:.2f}",
                "moving_average_200d": f"{ma_200:.2f}",
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Catch any other unforeseen errors
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

