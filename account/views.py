from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Profile
from booking.models import Booking


# ==========================
# CUSTOMER REGISTER
# ==========================
def register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")

        if not all([full_name, email, phone, password]):
            messages.error(request, "All fields are required")
            return redirect("register")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )

        Profile.objects.create(
            user=user,
            role="customer",
            is_verified=True
        )

        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "account/register.html")


# ==========================
# PROVIDER REGISTER
# ==========================
def provider_register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        service_category = request.POST.get("service_category")
        experience = request.POST.get("experience")
        certificate = request.FILES.get("certificate")

        if not all([
            full_name, email, phone, password,
            service_category, experience, certificate
        ]):
            messages.error(request, "All fields are required.")
            return redirect("provider_register")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("provider_register")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )

        verification_token = get_random_string(32)

        Profile.objects.create(
            user=user,
            role="provider",
            certificate=certificate,
            is_verified=False,
            email_token=verification_token
        )

        verification_link = f"http://127.0.0.1:8000/account/verify-email/{verification_token}/"

        send_mail(
            subject="Verify your HomeService Provider Account",
            message=f"""
Hi {full_name},

Please verify your email by clicking the link below:
{verification_link}

After verification, your account will be reviewed by admin.
""",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True
        )

        messages.success(
            request,
            "Provider account created successfully. Please verify your email."
        )
        return redirect("login")

    return render(request, "account/provider_register.html")


# ==========================
# LOGIN
# ==========================
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)

            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults={"role": "customer", "is_verified": True}
            )

            if profile.role == "provider":
                return redirect("provider_dashboard")

            return redirect("customer_dashboard")

        messages.error(request, "Invalid email or password")
        return redirect("login")

    return render(request, "account/login.html")


# ==========================
# LOGOUT
# ==========================
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("login")


# ==========================
# CUSTOMER DASHBOARD
# ==========================
@login_required
def customer_dashboard(request):
    bookings = Booking.objects.filter(
        customer=request.user
    ).order_by("-booking_date")

    return render(request, "account/customer_dashboard.html", {
        "bookings": bookings
    })


# ==========================
# PROVIDER DASHBOARD
# ==========================
@login_required
def provider_dashboard(request):
    bookings = Booking.objects.filter(
        service__provider__user=request.user
    ).order_by("-booking_date")

    return render(request, "account/provider_dashboard.html", {
        "bookings": bookings
    })


# ==========================
# PROFILE VIEW
# ==========================
@login_required
def profile_view(request):
    return render(request, "account/profile.html", {
        "profile": request.user.profile
    })


# ==========================
# BROWSE SERVICES (ACCOUNT SIDE)
# ==========================
@login_required
def browse_services(request):
    return render(request, "account/browse_services.html")


# ==========================
# SAVE LOCATION (AJAX)
# ==========================
@login_required
@require_POST
def save_location(request):
    lat = request.POST.get("lat")
    lng = request.POST.get("lng")
    address = request.POST.get("address", "")

    if not lat or not lng:
        return JsonResponse({"error": "Invalid location"}, status=400)

    profile = request.user.profile
    profile.latitude = lat
    profile.longitude = lng
    profile.location = address
    profile.save()

    return JsonResponse({"success": True})

@login_required
def edit_service(request, service_id):
    service = get_object_or_404(
        Service,
        id=service_id,
        provider=request.user.profile
    )

    if request.method == "POST":
        service.name = request.POST.get("name") or service.name
        service.description = request.POST.get("description") or service.description
        service.price = request.POST.get("price") or service.price
        service.location = request.POST.get("location") or service.location

        service.save()
        messages.success(request, "Service updated successfully.")
        return redirect("provider_services")

    return render(request, "booking/edit_service.html", {
        "service": service
    })
