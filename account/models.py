from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('provider', 'Service Provider'),
    )

    CATEGORY_CHOICES = [
        ("painting", "Painting"),
        ("plumbing", "Plumbing"),
        ("electrical", "Electrical"),
        ("cleaning", "Cleaning"),
        ("carpentry", "Carpentry"),
        ("ac_repair", "AC Repair"),
    ]

    # One user = one profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=20,
    )
    
    # Phone number
    phone = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        unique=True,
        help_text="User's phone number"
    )
    
    # Multiple categories as comma-separated string or use separate model
    verified_categories = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Comma-separated list of verified categories"
    )

    # Location of user (city / area)
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Admin verification (for providers)
    is_verified = models.BooleanField(default=False)
    
    # ✅ EMAIL VERIFICATION TOKEN
    email_token = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username


# ==============================
# PROVIDER CATEGORY MODEL
# ==============================
class ProviderCategory(models.Model):
    CATEGORY_CHOICES = [
        ("painting", "Painting"),
        ("plumbing", "Plumbing"),
        ("electrical", "Electrical"),
        ("cleaning", "Cleaning"),
        ("carpentry", "Carpentry"),
        ("ac_repair", "AC Repair"),
    ]

    provider = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='service_categories'
    )

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('provider', 'category')

    def __str__(self):
        return f"{self.provider.user.username} - {self.get_category_display()}"


# ==============================
# PROVIDER CERTIFICATE MODEL
# ==============================
class ProviderCertificate(models.Model):
    provider = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='certificates'
    )

    certificate = models.ImageField(upload_to='certificates/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate - {self.provider.user.username}"

