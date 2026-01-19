from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
    )

    # One user = one profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=20,
    )
    verified_category = models.CharField(
        max_length=50,
        choices=[
            ("painting", "Painting"),
            ("plumbing", "Plumbing"),
            ("electrical", "Electrical"),
        ],
        null=True,
        blank=True
    )

    certificate = models.ImageField(upload_to="certificates/")

    # Location of user (city / area)
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Certificate ONLY for service provider
    certificate = models.ImageField(
        upload_to='certificates/',
        null=True,
        blank=True
    )

    # Admin verification ( for providers)
    is_verified = models.BooleanField(default=False)
    
    
    # ✅ EMAIL VERIFICATION TOKEN (NEW)
    email_token = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
