from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=255)
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.title)

    class Meta:
        ordering = ["title"]


class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="shows")
    screen_name = models.CharField()
    date_time = models.DateTimeField()
    total_seats = models.IntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.movie.title} - {self.screen_name} - {self.date_time}"

    class Meta:
        ordering = ["date_time"]
        unique_together = ["screen_name", "date_time"]


class Booking(models.Model):
    STATUS_CHOICES = [
        ("booked", "Booked"),
        ("cancelled", "Cancelled"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name="bookings")
    seat_number = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="booked")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.show} - Seat {self.seat_number}"

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["show", "seat_number", "status"]
        indexes = [
            models.Index(fields=["show", "seat_number", "status"]),
        ]
