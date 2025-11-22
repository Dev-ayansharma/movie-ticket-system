# 🎬 Movie Ticket Booking System

A robust REST API for movie ticket booking built with Django and Django REST Framework, featuring JWT authentication, comprehensive booking logic, and Swagger documentation.

## 📋 Features

- **User Authentication**: JWT-based signup and login
- **Movie Management**: Browse available movies
- **Show Management**: View shows for specific movies
- **Seat Booking**: Book seats with validation
- **Booking Management**: View and cancel bookings
- **Security**: Users can only cancel their own bookings
- **Swagger Documentation**: Interactive API documentation
- **Business Logic**:
  - Prevents double booking of seats
  - Prevents overbooking beyond capacity
  - Cancellation frees up seats
  - Seat number validation

## 🛠 Tech Stack

- Python 3.8+
- Django 4.2.7
- Django REST Framework 3.14.0
- djangorestframework-simplejwt 5.3.0
- drf-yasg 1.21.7 (Swagger)
- SQLite (default) / PostgreSQL

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd movie-booking-system
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Settings

Create a `.env` file in the project root (optional):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 7. Load Sample Data (Optional)

Create a `fixtures.json` file or use Django admin to add movies and shows.

### 8. Run the Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## 🚀 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/signup/` | Register a new user | No |
| POST | `/api/login/` | Login and get JWT tokens | No |

### Movies & Shows

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/movies/` | List all movies | No |
| GET | `/api/movies/<id>/shows/` | List shows for a movie | No |

### Bookings

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/shows/<id>/book/` | Book a seat | Yes |
| POST | `/api/bookings/<id>/cancel/` | Cancel a booking | Yes |
| GET | `/api/my-bookings/` | View user's bookings | Yes |

## 📖 API Usage Guide

### 1. Register a User

```bash
curl -X POST http://127.0.0.1:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Login

```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}
```

### 3. Get Movies (No Auth Required)

```bash
curl http://127.0.0.1:8000/api/movies/
```

### 4. Get Shows for a Movie

```bash
curl http://127.0.0.1:8000/api/movies/1/shows/
```

### 5. Book a Seat (Auth Required)

```bash
curl -X POST http://127.0.0.1:8000/api/shows/1/book/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "seat_number": 5
  }'
```

### 6. View My Bookings

```bash
curl http://127.0.0.1:8000/api/my-bookings/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Cancel a Booking

```bash
curl -X POST http://127.0.0.1:8000/api/bookings/1/cancel/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 📚 Swagger Documentation

Access the interactive API documentation at:

- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/

### Using JWT in Swagger

1. Navigate to http://127.0.0.1:8000/swagger/
2. Click the **Authorize** button (top right)
3. Enter: `Bearer YOUR_ACCESS_TOKEN`
4. Click **Authorize**
5. You can now test authenticated endpoints

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test

# Run with verbose output
python manage.py test --verbosity=2

# Run specific test class
python manage.py test movies.tests.BookingLogicTestCase
```

## 🏗 Project Structure

```
movie-booking-system/
├── manage.py
├── requirements.txt
├── README.md
├── project_name/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── movies/  # Your app name
    ├── __init__.py
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── tests.py
    └── migrations/
```

## 🔒 Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **User Authorization**: Users can only cancel their own bookings
3. **Input Validation**: Comprehensive validation for all inputs
4. **Database Transactions**: Atomic operations for booking to prevent race conditions
5. **Password Validation**: Django's built-in password validators

## ⚡ Business Logic Implementation

### Preventing Double Booking

The system uses database-level locking (`select_for_update()`) to prevent race conditions:

```python
existing_booking = Booking.objects.filter(
    show=show,
    seat_number=seat_number,
    status='booked'
).select_for_update().exists()
```

### Preventing Overbooking

Before creating a booking, the system checks total booked seats:

```python
total_booked = Booking.objects.filter(
    show=show,
    status='booked'
).count()

if total_booked >= show.total_seats:
    return error_response('Show is fully booked')
```

### Seat Validation

Validates seat numbers are within the allowed range:

```python
if seat_number > show.total_seats or seat_number < 1:
    return error_response('Invalid seat number')
```

## 🐛 Troubleshooting

### Issue: "No such table" error

**Solution**: Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: JWT token errors

**Solution**: Ensure you're using the format: `Bearer YOUR_ACCESS_TOKEN`

### Issue: Permission denied errors

**Solution**: Check that you're sending the JWT token in the Authorization header

## 📝 Sample Data

You can add sample data via Django admin or create a management command:

```python
# movies/management/commands/load_sample_data.py
from django.core.management.base import BaseCommand
from movies.models import Movie, Show
from datetime import datetime, timedelta

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        movie = Movie.objects.create(
            title="Inception",
            duration_minutes=148
        )
        
        Show.objects.create(
            movie=movie,
            screen_name="Screen 1",
            date_time=datetime.now() + timedelta(days=1),
            total_seats=50
        )
```

Run with: `python manage.py load_sample_data`

## 🎯 Future Enhancements

- [ ] Payment integration
- [ ] Email notifications
- [ ] Seat selection UI
- [ ] Multiple ticket booking
- [ ] Pricing tiers
- [ ] Show scheduling
- [ ] Theater chains support
- [ ] Real-time seat availability with WebSockets

## 📄 License

This project is created as an assignment and is free to use.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📧 Contact

For any queries, please open an issue on GitHub.

---

**Note**: This is a demonstration project for a backend developer intern assignment. Make sure to update security settings and use environment variables for production deployment.
