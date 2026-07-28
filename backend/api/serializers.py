from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Payment, Ride, User, Vehicle


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "phone_number", "role",
            "profile_picture", "is_available", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "phone_number", "role",
            "password", "password2",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class VehicleSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source="driver.username", read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id", "driver", "driver_name", "vehicle_type",
            "make", "model", "color", "plate_number", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class DriverSummarySerializer(serializers.ModelSerializer):
    """Lightweight driver info nested inside ride responses — no PII overload."""
    vehicle = VehicleSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "phone_number", "vehicle"]


class RideSerializer(serializers.ModelSerializer):
    """Full ride detail — used for retrieve/list, includes nested driver+rider."""
    rider = UserSerializer(read_only=True)
    driver = DriverSummarySerializer(read_only=True)

    class Meta:
        model = Ride
        fields = [
            "id", "rider", "driver",
            "pickup_address", "pickup_lat", "pickup_lng",
            "dropoff_address", "dropoff_lat", "dropoff_lng",
            "distance_km", "fare", "status",
            "requested_at", "accepted_at", "completed_at",
        ]
        read_only_fields = ["id", "requested_at", "accepted_at", "completed_at"]


class RideCreateSerializer(serializers.ModelSerializer):
    """Used when a rider books a ride — rider is set from request.user in the view."""

    class Meta:
        model = Ride
        fields = [
            "id", "pickup_address", "pickup_lat", "pickup_lng",
            "dropoff_address", "dropoff_lat", "dropoff_lng",
            "distance_km", "fare",
        ]
        read_only_fields = ["id"]


class RideStatusUpdateSerializer(serializers.ModelSerializer):
    """Used by a driver to accept/start/complete a ride, or a rider to cancel."""

    class Meta:
        model = Ride
        fields = ["status"]


class PaymentSerializer(serializers.ModelSerializer):
    ride_id = serializers.UUIDField(source="ride.id", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "ride", "ride_id", "method", "status", "amount",
            "phone_number", "mpesa_checkout_request_id", "mpesa_receipt_number",
            "created_at", "paid_at",
        ]
        read_only_fields = [
            "id", "status", "mpesa_checkout_request_id",
            "mpesa_receipt_number", "created_at", "paid_at",
        ]


class InitiateMpesaPaymentSerializer(serializers.Serializer):
    """Input-only serializer for triggering an STK Push on a given ride."""
    ride_id = serializers.UUIDField()
    phone_number = serializers.CharField(max_length=15)