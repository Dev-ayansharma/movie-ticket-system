from django.contrib.auth import authenticate
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from movies.models import Booking, Movie, Show
from movies.serializers import (
    BookingCreateSerializer,
    BookingSerializer,
    MovieSerializer,
    ShowSerializer,
    UserRegistrationSerializer,
)


# Create your views here.
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user",
        responses={
            201: openapi.Response(
                "User created successfully", UserRegistrationSerializer
            )
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": serializer.data,
                "message": "User registered successfully",
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Login and get JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response("Login successful"),
            401: "Invalid credentials",
        },
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "Login successful",
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                }
            )
        else:
            return Response(
                {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )


class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get list of all movies",
        responses={200: MovieSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class MovieShowsView(generics.ListAPIView):
    serializer_class = ShowSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Get all shows for a specific movie",
        responses={200: ShowSerializer(many=True)},
    )
    def get_queryset(self):
        movie_id = self.kwargs.get("movie_id")
        return Show.objects.filter(movie_id=movie_id)


class BookSeatView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Book a seat for a show",
        request_body=BookingCreateSerializer,
        responses={
            201: openapi.Response("Booking successful", BookingSerializer),
            400: "Bad request",
            404: "Show not found",
        },
    )
    def post(self, request, show_id):
        try:
            show = Show.objects.get(id=show_id)
        except Show.DoesNotExist:
            return Response(
                {"error": "Show not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookingCreateSerializer(
            data=request.data, context={"show_id": show_id}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        seat_number = serializer.validated_data["seat_number"]

        try:
            with transaction.atomic():
                # Check if seat is already booked
                existing_booking = (
                    Booking.objects.filter(
                        show=show, seat_number=seat_number, status="booked"
                    )
                    .select_for_update()
                    .exists()
                )

                if existing_booking:
                    return Response(
                        {"error": f"Seat {seat_number} is already booked"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Check total bookings don't exceed capacity
                total_booked = Booking.objects.filter(
                    show=show, status="booked"
                ).count()

                if total_booked >= show.total_seats:
                    return Response(
                        {"error": "Show is fully booked"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Create booking
                booking = Booking.objects.create(
                    user=request.user,
                    show=show,
                    seat_number=seat_number,
                    status="booked",
                )

                result_serializer = BookingSerializer(booking)
                return Response(
                    {
                        "message": "Booking successful",
                        "booking": result_serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response(
                {"error": f"Booking failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cancel a booking",
        responses={
            200: "Booking cancelled successfully",
            403: "Forbidden",
            404: "Booking not found",
        },
    )
    def post(self, request, booking_id):
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Security: Check if user owns the booking
        if booking.user != request.user:
            return Response(
                {"error": "You can only cancel your own bookings"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if booking.status == "cancelled":
            return Response(
                {"error": "Booking is already cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            booking.status = "cancelled"
            booking.save()

            serializer = BookingSerializer(booking)
            return Response(
                {
                    "message": "Booking cancelled successfully",
                    "booking": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Cancellation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MyBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all bookings for the logged-in user",
        responses={200: BookingSerializer(many=True)},
    )
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)
