from django.db import models
from django.contrib.auth.models import User
from account.models import Profile


# ==============================
# SERVICE MODEL
# ==============================

CATEGORY_CHOICES = [
    ("plumbing", "Plumbing"),
    ("electrical", "Electrical"),
    ("cleaning", "Cleaning"),
    ("carpentry", "Carpentry"),
    ("painting", "Painting"),
    ("ac_repair", "AC Repair"),
]


class Service(models.Model):
    provider = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="services"
    )

    name = models.CharField(max_length=100)
    description = models.TextField()

    # Category stored as key (painting, plumbing, etc.)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    location = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.provider.user.username})"


# ==============================
# BOOKING MODEL
# ==============================

class Booking(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    booking_date = models.DateTimeField(auto_now_add=True)

    booking_time = models.TimeField(
        null=True,
        blank=True
    )

    # Customer job location
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} → {self.service.name} ({self.status})"


# ==============================
# MESSAGE MODEL
# ==============================

class Message(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    content = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
