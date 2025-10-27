import yfinance as yf
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

# --- Configuration ---
TRAIN_TICKER = 'SPY'       # Train on a broad market index for a more general model
LOOKBACK_DAYS = 60        # Use 60 days of history to predict the next day
DATA_START = '2010-01-01'
DATA_END = '2024-01-01'
MODEL_FILE = 'stock_predictor.keras'
SCALER_FILE = 'scaler.gz'

def create_dataset(dataset, look_back=LOOKBACK_DAYS):
    """Create sequences of data for LSTM."""
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back - 1):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)

print(f"Starting model training process for {TRAIN_TICKER}...")

# 1. Fetch Data
print(f"Downloading data from {DATA_START} to {DATA_END}...")
try:
    data = yf.download(TRAIN_TICKER, start=DATA_START, end=DATA_END)
    if data.empty:
        raise ValueError(f"No data downloaded for {TRAIN_TICKER}.")
    close_prices = data['Close'].values.reshape(-1, 1)
    print(f"Successfully downloaded {len(close_prices)} data points.")
except Exception as e:
    print(f"Error downloading data: {e}")
    exit()

# 2. Scale Data
print("Scaling data...")
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(close_prices)

# 3. Create Training Sequences
print(f"Creating sequences with {LOOKBACK_DAYS}-day lookback...")
train_size = int(len(scaled_data) * 0.8)
train_data = scaled_data[0:train_size]
test_data = scaled_data[train_size - LOOKBACK_DAYS:]

X_train, y_train = create_dataset(train_data)
X_test, y_test = create_dataset(test_data)

# Reshape input to be [samples, time steps, features]
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
print(f"Training data shape: {X_train.shape}")
print(f"Test data shape: {X_test.shape}")

# 4. Build LSTM Model
print("Building LSTM model...")
model = tf.keras.models.Sequential([
    tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(LOOKBACK_DAYS, 1)),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(50, return_sequences=False),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(25),
    tf.keras.layers.Dense(1)
])

model.compile(optimizer='adam', loss='mean_squared_error')
print(model.summary())

# 5. Train Model
print("Training model... (This may take a few minutes)")
model.fit(X_train, y_train, batch_size=32, epochs=20, validation_data=(X_test, y_test))

# 6. Save Model and Scaler
print(f"Saving model to {MODEL_FILE}...")
model.save(MODEL_FILE)

print(f"Saving scaler to {SCALER_FILE}...")
joblib.dump(scaler, SCALER_FILE)

print("\n--- Model training complete! ---")
print(f"Files '{MODEL_FILE}' and '{SCALER_FILE}' have been created.")
print("You can now run the Django server.")

