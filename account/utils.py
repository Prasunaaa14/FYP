import random
from django.core.mail import send_mail
from django.conf import settings


def generate_otp():
    return str(random.randint(100000, 999999))


def send_verification_email(email, otp):
    subject = "HomeService Email Verification Code"
    message = f"""
Your HomeService verification code is:

{otp}

Do not share this code with anyone.
"""
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
    )
