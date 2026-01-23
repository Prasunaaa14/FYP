from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile



# CUSTOMER REGISTER
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



# PROVIDER REGISTER

def provider_register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        service_category = request.POST.get("service_category")
        experience = request.POST.get("experience")
        certificate = request.FILES.get("certificate")

        #VALIDATION (location REMOVED)
        if not all([
            full_name, email, phone, password,
            service_category, experience, certificate
        ]):
            messages.error(request, "All fields are required.")
            return redirect("provider_register")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("provider_register")

        #CREATE USER
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )

        #CREATE PROFILE (location REMOVED)
        Profile.objects.create(
            user=user,
            role="provider",
            certificate=certificate,
            is_verified=False
        )

        messages.success(request, "Provider account created successfully. Please log in.")
        return redirect("login")

    return render(request, "account/provider_register.html")

# LOGIN View

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


# LOGOUT
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("login")



# DASHBOARDS

@login_required
def customer_dashboard(request):
    return render(request, "account/customer_dashboard.html")


@login_required
def provider_dashboard(request):
    return render(request, "account/provider_dashboard.html")
@login_required
def profile_view(request):
    return render(request, "account/profile.html")

#browse Services
@login_required
def browse_services(request):
    return render(request, "account/browse_services.html")

@login_required
def profile_view(request):
    return render(request, "account/profile.html", {
        "profile": request.user.profile
    })

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Profile

#save location
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
