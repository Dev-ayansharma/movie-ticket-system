from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from movies.models import Booking, Movie, Show


class UserRegistrationSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    passoword2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
        )
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "email": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "duration_minutes", "created_at"]
        read_only_fields = ["id", "created_at"]


class ShowSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="movie.title", read_only=True)
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Show
        fields = [
            "id",
            "movie",
            "movie_title",
            "screen_name",
            "date_time",
            "total_seats",
            "available_seats",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_available_seats(self, obj):
        booked_count = Booking.objects.filter(show=obj, status="booked").count()
        return obj.total_seats - booked_count


class BookingCreateSerializer(serializers.Serializer):
    seat_number = serializers.IntegerField(min_value=1)

    def validate_seat_number(self, value):
        show_id = self.context.get("show_id")
        try:
            show = Show.objects.get(id=show_id)
            if value > show.total_seats:
                raise serializers.ValidationError(
                    f"Seat number must be between 1 and {show.total_seats}"
                )
        except Show.DoesNotExist:
            raise serializers.ValidationError("Invalid show")
        return value


class BookingSerializer(serializers.Serializer):
    show_details = ShowSerializer(source="show", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "user",
            "username",
            "show",
            "show_details",
            "seat_number",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "status", "created_at", "updated_at"]
