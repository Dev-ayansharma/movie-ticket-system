from django.contrib import admin

from .models import Booking, Movie, Show


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "duration_minutes", "created_at"]
    search_fields = ["title"]
    list_filter = ["created_at"]


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "movie",
        "screen_name",
        "date_time",
        "total_seats",
        "available_seats",
    ]
    list_filter = ["screen_name", "date_time", "movie"]
    search_fields = ["movie__title", "screen_name"]
    date_hierarchy = "date_time"

    def available_seats(self, obj):
        booked = Booking.objects.filter(show=obj, status="booked").count()
        return obj.total_seats - booked

    available_seats.short_description = "Available Seats"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "show", "seat_number", "status", "created_at"]
    list_filter = ["status", "created_at", "show__screen_name"]
    search_fields = ["user__username", "show__movie__title"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
