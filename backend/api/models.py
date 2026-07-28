import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    """
    Custom user model. Every account is either a RIDER or a DRIVER.
    We extend AbstractUser instead of the default User so we can add
    role + phone_number, which the whole app depends on.
    """

    class Role(models.TextChoices):
        RIDER = "RIDER", "Rider"
        DRIVER = "DRIVER", "Driver"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.RIDER)
    phone_number = models.CharField(max_length=15, unique=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    is_available = models.BooleanField(
        default=False,
        help_text="Only relevant for drivers — toggled on/off to accept rides.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Vehicle(models.Model):
    """A driver's registered vehicle. One driver -> one active vehicle."""

    class VehicleType(models.TextChoices):
        BODA = "BODA", "Boda Boda"
        SALOON = "SALOON", "Saloon"
        SUV = "SUV", "SUV"
        TUKTUK = "TUKTUK", "Tuktuk"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="vehicle",
        limit_choices_to={"role": User.Role.DRIVER},
    )
    vehicle_type = models.CharField(max_length=10, choices=VehicleType.choices, default=VehicleType.SALOON)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    plate_number = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plate_number} - {self.make} {self.model}"


class Ride(models.Model):
    """
    Core booking record. Created by a rider (status PENDING), picked up by a
    driver (ACCEPTED -> ONGOING), then finished (COMPLETED) or CANCELLED.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        ONGOING = "ONGOING", "Ongoing"
        COMPLETED = "COMPLETED", "Completed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="rides_taken",
        limit_choices_to={"role": User.Role.RIDER},
    )
    driver = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="rides_driven",
        limit_choices_to={"role": User.Role.DRIVER}, null=True, blank=True,
    )

    pickup_address = models.CharField(max_length=255)
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6)

    dropoff_address = models.CharField(max_length=255)
    dropoff_lat = models.DecimalField(max_digits=9, decimal_places=6)
    dropoff_lng = models.DecimalField(max_digits=9, decimal_places=6)

    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fare = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"Ride {self.id} - {self.status}"


class Payment(models.Model):
    """
    One payment per ride. M-Pesa fields are kept nullable since a cash ride
    won't populate them — mirrors the Daraja STK Push pattern used elsewhere.
    """

    class Method(models.TextChoices):
        MPESA = "MPESA", "M-Pesa"
        CASH = "CASH", "Cash"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ride = models.OneToOneField(Ride, on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=10, choices=Method.choices, default=Method.MPESA)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    # M-Pesa Daraja STK Push fields
    phone_number = models.CharField(max_length=15, blank=True)
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.id} - {self.status} (KES {self.amount})"