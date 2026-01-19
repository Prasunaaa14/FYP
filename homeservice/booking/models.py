from django.db import models
from django.contrib.auth.models import User
from account.models import Profile

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    provider = models.ForeignKey(Profile, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('completed', 'Completed')
        ],
        default='pending'
    )

    def __str__(self):
        return f"{self.customer.username} - {self.service.name}"
