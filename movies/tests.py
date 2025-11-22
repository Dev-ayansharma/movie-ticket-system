from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Booking, Movie, Show


class BookingLogicTestCase(APITestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username="testuser1", email="test1@example.com", password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@example.com", password="testpass123"
        )

        # Create test movie
        self.movie = Movie.objects.create(title="Test Movie", duration_minutes=120)

        # Create test show
        self.show = Show.objects.create(
            movie=self.movie,
            screen_name="Screen 1",
            date_time=datetime.now() + timedelta(days=1),
            total_seats=10,
        )

        # Get JWT tokens
        self.client = APIClient()
        response = self.client.post(
            "/api/login/", {"username": "testuser1", "password": "testpass123"}
        )
        self.token1 = response.data["tokens"]["access"]

        response = self.client.post(
            "/api/login/", {"username": "testuser2", "password": "testpass123"}
        )
        self.token2 = response.data["tokens"]["access"]

    def test_successful_booking(self):
        """Test that a user can successfully book a seat"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1}")
        response = self.client.post(
            f"/api/shows/{self.show.id}/book/", {"seat_number": 1}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["booking"]["seat_number"], 1)
        self.assertEqual(response.data["booking"]["status"], "booked")

    def test_prevent_double_booking(self):
        """Test that a seat cannot be booked twice"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1}")

        # First booking
        response1 = self.client.post(
            f"/api/shows/{self.show.id}/book/", {"seat_number": 2}
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Second booking attempt (same seat, different user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token2}")
        response2 = self.client.post(
            f"/api/shows/{self.show.id}/book/", {"seat_number": 2}
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already booked", response2.data["error"])

    def test_prevent_overbooking(self):
        """Test that bookings cannot exceed show capacity"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1}")

        # Book all seats
        for i in range(1, 11):  # Show has 10 seats
            response = self.client.post(
                f"/api/shows/{self.show.id}/book/", {"seat_number": i}
            )
            if i <= 10:
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Try to book one more
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token2}")
        response = self.client.post(
            f"/api/shows/{self.show.id}/book/", {"seat_number": 11}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_booking_frees_seat(self):
        """Test that cancelling a booking makes the seat available again"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1}")

        # Book a seat
        response = self.client.post(
            f"/api/shows/{self.show.id}/book/", {"seat_number": 3}
        )
        booking_id = response.data["booking"]["id"]

        # Cancel the booking
        response = self.client.post(f"/api/bookings/{booking_id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["booking"]["status"], "cancelled")

        # Try to book the same seat again
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token2}")
        response = self.client.post(
            f"/api/shows/{self.show.id}/book/", {"seat_number": 3}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_cancel_others_booking(self):
        """Test security: users can only cancel their own bookings"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1}")

        # User1 books a seat
        response = self.client.post(
            f"/api/shows/{self.show.id}/book/", {"seat_number": 4}
        )
        booking_id = response.data["booking"]["id"]

        # User2 tries to cancel User1's booking
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token2}")
        response = self.client.post(f"/api/bookings/{booking_id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_seat_number(self):
        """Test that booking with invalid seat number fails"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1}")

        # Try to book seat number beyond capacity
        response = self.client.post(
            f"/api/shows/{self.show.id}/book/", {"seat_number": 999}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Try to book seat number 0
        response = self.client.post(
            f"/api/shows/{self.show.id}/book/", {"seat_number": 0}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthenticationTestCase(APITestCase):
    def test_signup(self):
        """Test user registration"""
        response = self.client.post(
            "/api/signup/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "password2": "SecurePass123!",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)

    def test_login(self):
        """Test user login"""
        # Create user
        User.objects.create_user(username="loginuser", password="testpass123")

        # Login
        response = self.client.post(
            "/api/login/", {"username": "loginuser", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
