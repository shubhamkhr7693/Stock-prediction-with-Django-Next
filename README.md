# 📈 Intelligent Stock Prediction Portal

A full-stack web application that leverages Deep Learning (LSTM) to predict next-day stock prices with technical analysis insights and interactive visualizations.

## 🎯 Project Overview

**StockPredict** is an AI-powered financial analysis tool that democratizes access to institutional-grade stock market predictions. The system accepts a stock ticker symbol and predicts the next day's closing price along with trend direction, confidence score, and comprehensive technical analysis.

### Key Features

- 🤖 **Multivariate LSTM Model** trained on 10 years of S&P 500 data
- 📊 **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- 🔐 **Secure Authentication** using JWT tokens
- 💹 **Real-time Data** fetched from Yahoo Finance
- 📈 **Interactive Charts**: 300-day recent trends and 10-year historical analysis
- 💱 **Currency Conversion**: Automatic USD to INR conversion
- ⚡ **Optimized Performance** with in-memory model caching

---

## 🏗️ System Architecture

```
┌─────────────────┐
│   Client Side   │
│  (Next.js App)  │
└────────┬────────┘
         │ HTTP Request (JWT)
         ▼
┌─────────────────┐
│  Django Backend │
│   (REST API)    │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┐
    ▼          ▼          ▼
┌───────┐  ┌───────┐  ┌────────┐
│ Auth  │  │ Cache │  │ Yahoo  │
│ (JWT) │  │(LSTM) │  │Finance │
└───────┘  └───┬───┘  └────────┘
               │
               ▼
        ┌──────────────┐
        │ LSTM Model   │
        │  Prediction  │
        └──────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (React)
- **Styling**: Tailwind CSS
- **Charts**: Chart.js, react-chartjs-2
- **Animations**: Framer Motion
- **Icons**: Lucide React

### Backend
- **Framework**: Django 5.0
- **API**: Django REST Framework
- **Authentication**: djangorestframework-simplejwt
- **CORS**: django-cors-headers

### Machine Learning
- **Deep Learning**: TensorFlow 2.x, Keras
- **Data Processing**: Pandas, NumPy
- **Technical Analysis**: pandas-ta
- **Scaling**: scikit-learn (MinMaxScaler)
- **Market Data**: yfinance

### Database
- **Development**: SQLite3
- **Production**: PostgreSQL (recommended)

---

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/shubhamkhr7693/stock-prediction-portal.git
cd stock-prediction-portal
```

### 2. Backend Setup (Django)

```bash
# Navigate to backend directory
cd prediction_portal

# Create virtual environment
python -m venv env

# Activate virtual environment
# Windows:
env\Scripts\activate
# Mac/Linux:
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional technical analysis library
pip install pandas-ta
```

#### Backend Dependencies (requirements.txt)
```
Django==5.0
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
tensorflow==2.15.0
pandas==2.1.4
numpy==1.24.3
scikit-learn==1.3.2
yfinance==0.2.33
pandas-ta==0.3.14b0
joblib==1.3.2
```

### 3. Train the LSTM Model

```bash
# Run the model training script
python model_builder.py
```

This will:
- Download 10 years of SPY (S&P 500) data
- Calculate technical indicators (RSI, MACD, Bollinger Bands)
- Train the LSTM neural network
- Save `stock_predictor.keras` and `scaler.gz` files

**⏰ Note**: Training takes approximately 15-30 minutes depending on your hardware.

### 4. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

### 5. Start Backend Server

```bash
python manage.py runserver
```

Backend will run at: `http://127.0.0.1:8000/`

### 6. Frontend Setup (Next.js)

Open a **new terminal** window:

```bash
# Navigate to frontend directory
cd stock-frontend

# Install dependencies
npm install

# Install additional libraries
npm install framer-motion
npm install lucide-react
npm install chart.js react-chartjs-2
```

### 7. Start Frontend Server

```bash
npm run dev
```

Frontend will run at: `http://localhost:3000/`

---

## 📁 Project Structure

```
stock-prediction-portal/
│
├── prediction_portal/          # Django Backend
│   ├── prediction_portal/      # Main project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── predictor/              # Prediction app
│   │   ├── views.py           # API logic
│   │   ├── urls.py            # API routes
│   │   └── models.py
│   │
│   ├── model_builder.py       # LSTM training script
│   ├── stock_predictor.keras  # Trained model
│   ├── scaler.gz              # Data scaler
│   ├── manage.py
│   └── requirements.txt
│
└── stock-frontend/             # Next.js Frontend
    ├── app/
    │   ├── page.jsx           # Main application UI
    │   ├── layout.jsx
    │   └── globals.css
    │
    ├── public/
    ├── package.json
    └── next.config.js
```

---

## 🔌 API Endpoints

### Authentication

#### Register User
```http
POST /api/register/
Content-Type: application/json

{
  "username": "testuser",
  "password": "securepassword123"
}
```

#### Login (Get JWT Token)
```http
POST /api/token/
Content-Type: application/json

{
  "username": "testuser",
  "password": "securepassword123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Predictions

#### Get Stock Prediction
```http
GET /api/predict/{TICKER}/
Authorization: Bearer <access_token>

Example: GET /api/predict/AAPL/

Response:
{
  "ticker": "AAPL",
  "last_close_inr": "18500.50",
  "predicted_next_close_inr": "18720.30",
  "moving_average_100d_inr": "18200.00",
  "moving_average_200d_inr": "17800.00",
  "trend_prediction": "Up",
  "confidence_percent": "77.8",
  "chart_data": {
    "labels": ["2024-01-01", "2024-01-02", ...],
    "close_prices": [18400.50, 18450.20, ...],
    "ma_100": [18200.00, 18205.50, ...],
    "ma_200": [17800.00, 17805.00, ...]
  }
}
```

#### Get 10-Year Historical Analysis
```http
GET /api/historical-chart/{TICKER}/
Authorization: Bearer <access_token>

Example: GET /api/historical-chart/AAPL/

Response:
{
  "labels": ["2015-01-01", "2015-01-02", ...],
  "ma_100": [5000.00, 5010.50, ...],
  "ma_200": [4800.00, 4805.00, ...]
}
```

---

## 🎨 User Interface

### Login Page
- Secure JWT-based authentication
- Sign up for new users
- Modal-based design with blur effect

### Dashboard
- **Search Bar**: Enter stock ticker (e.g., AAPL, MSFT, GOOG)
- **Stat Cards**: Display current price, prediction, trend, and confidence
- **300-Day Chart**: Recent price action with moving averages
- **10-Year Analysis**: Long-term trend visualization (load on demand)

---

## 🧠 Model Details

### Architecture
```python
Sequential([
    LSTM(50, return_sequences=True, input_shape=(60, 1)),
    Dropout(0.2),
    LSTM(50, return_sequences=False),
    Dropout(0.2),
    Dense(25),
    Dense(1)  # Price prediction
])
```

### Training Details
- **Dataset**: 10 years of S&P 500 (SPY) daily data
- **Window Size**: 60 days
- **Features**: Close price, RSI, MACD, Bollinger Bands
- **Optimization**: Adam optimizer
- **Loss Function**: Mean Squared Error
- **Validation Split**: 80/20 train-test

### Confidence Score Calculation
The system calculates a UX-friendly confidence score (70-90%) based on prediction magnitude:

```
percent_change = abs((prediction - last_close) / last_close * 100)
normalized_change = min(percent_change, 3.0) / 3.0
confidence = 70.0 + (normalized_change * 20.0)
```

- **0% change** → 70% confidence (weak signal)
- **3%+ change** → 90% confidence (strong signal)

---

## 🔐 Security Features

- **JWT Authentication**: Secure token-based auth with access/refresh tokens
- **Permission Classes**: API endpoints protected by `IsAuthenticated`
- **CORS Configuration**: Restricted to frontend origin only
- **Input Validation**: Backend validates all ticker inputs
- **Error Handling**: Graceful error responses for invalid requests

---

## 🚀 Deployment

### Backend Deployment (Render/Heroku)

1. Update `settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
```

2. Add `gunicorn` to requirements.txt:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

3. Create `Procfile`:
```
web: gunicorn prediction_portal.wsgi
```

### Frontend Deployment (Vercel)

1. Update API URL in `page.jsx`:
```javascript
const API_URL = 'https://your-backend.render.com';
```

2. Deploy to Vercel:
```bash
vercel deploy --prod
```

---

## 🧪 Testing

### Test Cases

| Test Case | Input | Expected Output | Status |
|-----------|-------|-----------------|--------|
| Valid Ticker | AAPL | Prediction + Charts | ✅ Pass |
| Invalid Ticker | XYZ | 404 Error Message | ✅ Pass |
| No Authentication | Any | 401 Unauthorized | ✅ Pass |
| Registration | New User | Auto-login Success | ✅ Pass |

### Manual Testing
```bash
# Test backend health
curl http://127.0.0.1:8000/api/predict/AAPL/ \
  -H "Authorization: Bearer <your_token>"

# Test frontend
# Open http://localhost:3000 and search for AAPL
```

---

## ⚡ Performance Optimization

### Model Caching
The system loads the Keras model into RAM once on startup:
- **Cold Start**: ~3.5 seconds
- **Warm Cache**: ~0.6 seconds

### Data Caching (Future Enhancement)
Recommended: Add Redis layer to cache Yahoo Finance data for 5 minutes.

---

## 🐛 Troubleshooting

### "Model file not found"
```bash
# Make sure you ran the training script
cd prediction_portal
python model_builder.py
```

### "Permission denied" (Mac/Linux)
```bash
# Use sudo for npm global installs
sudo npm install -g npm@latest
```

### "CORS Error"
Ensure `CORS_ALLOWED_ORIGINS` in `settings.py` includes your frontend URL:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

### Exchange Rate Error
If `INR=X` fetch fails, system uses fallback rate of 83.0. This is expected behavior.

---

## 📚 Future Enhancements

- [ ] **Sentiment Analysis**: Integrate NewsAPI/Twitter for market sentiment
- [ ] **Portfolio Management**: User watchlists and portfolio tracking
- [ ] **Automated Retraining**: Weekly model updates on cloud (AWS Lambda)
- [ ] **Mobile App**: React Native port for iOS/Android
- [ ] **Advanced Charts**: Candlestick charts, volume analysis
- [ ] **Alerts System**: Email/SMS notifications for price targets

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Sumit Kumar Barnwal**
- Roll No: 23223087
- Program: MCA V Semester (2023-2026)
- Institution: National Institute of Technology Raipur
- Supervisor: Dr. Dibakar Saha

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Django REST Framework team for excellent API framework
- Next.js/Vercel for modern web development tools
- TensorFlow team for powerful ML libraries
- Yahoo Finance for providing free market data API

---

## ⚠️ Disclaimer

**This tool is for educational and research purposes only.** Stock market predictions are inherently uncertain. This system should NOT be used as the sole basis for investment decisions. Always consult with a qualified financial advisor before making investment choices.

**Past performance does not guarantee future results.**

---

Made with ❤️ and ☕ by Sumit Kumar Barnwal
