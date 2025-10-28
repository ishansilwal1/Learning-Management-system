# Django LMS Deployment on Render

## Quick Deploy Steps

1. **Fork/Clone this repository**

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure Render Settings**
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn LMS.wsgi:application`
   - **Environment:** `Python 3`

4. **Set Environment Variables in Render**
   ```
   SECRET_KEY = [Generate new secret key]
   DEBUG = False
   SUPERUSER_USERNAME = admin
   SUPERUSER_EMAIL = admin@yourdomain.com
   SUPERUSER_PASSWORD = [Secure password]
   EMAIL_HOST_USER = your-email@gmail.com
   EMAIL_HOST_PASSWORD = your-app-password
   ```

5. **Add PostgreSQL Database (Optional)**
   - In Render dashboard: "New +" → "PostgreSQL"
   - Name: `lms-postgres`
   - Render will automatically set `DATABASE_URL`

## Generate Secret Key

Run this locally to generate a secure secret key:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## Local Development

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment:**
   ```bash
   cp .env.production .env
   # Edit .env with your local settings
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   python manage.py create_production_superuser
   ```

5. **Start development server:**
   ```bash
   python manage.py runserver
   ```

## Features

- User authentication and registration
- Class management for teachers
- Assignment creation and submission
- Grade management with ML analytics
- Calendar view for deadlines
- Real-time notifications
- Machine learning predictions for student performance

## Tech Stack

- **Backend:** Django 5.2.5, Python 3.13
- **Database:** PostgreSQL (production), SQLite (development)
- **ML:** scikit-learn, pandas, numpy
- **Frontend:** Bootstrap 5, JavaScript
- **Deployment:** Render, WhiteNoise for static files

## Production Features

- ✅ WhiteNoise for static file serving
- ✅ PostgreSQL database support
- ✅ Environment-based configuration
- ✅ Security headers and HTTPS
- ✅ Automated migrations and superuser creation
- ✅ ML model persistence with joblib