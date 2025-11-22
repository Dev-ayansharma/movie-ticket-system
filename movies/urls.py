from django.urls import path

from .views import (
    BookSeatView,
    CancelBookingView,
    MovieListView,
    MovieShowsView,
    MyBookingsView,
    UserLoginView,
    UserRegistrationView,
)

urlpatterns = [
    # Authentication
    path("signup/", UserRegistrationView.as_view(), name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    # Movies & Shows
    path("movies/", MovieListView.as_view(), name="movie-list"),
    path("movies/<int:movie_id>/shows/", MovieShowsView.as_view(), name="movie-shows"),
    # Bookings
    path("shows/<int:show_id>/book/", BookSeatView.as_view(), name="book-seat"),
    path(
        "bookings/<int:booking_id>/cancel/",
        CancelBookingView.as_view(),
        name="cancel-booking",
    ),
    path("my-bookings/", MyBookingsView.as_view(), name="my-bookings"),
]
