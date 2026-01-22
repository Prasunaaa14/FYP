from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django import forms

from .models import Profile
from booking.models import Booking, Service
from .forms import (
    CustomerRegistrationForm,
    ProviderRegistrationForm,
    ProviderCertificateUploadForm,
    LoginForm
)


# ==========================
# CUSTOMER REGISTER
# ==========================
def register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        
        if form.is_valid():
            # Extract validated data
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            
            # Create user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name
            )
            
            # Create customer profile
            Profile.objects.create(
                user=user,
                role="customer",
                is_verified=True
            )

            # Auto-login and go to dashboard
            login(request, user, backend='account.backends.EmailBackend')
            messages.success(request, "Account created successfully.")
            return redirect("customer_dashboard")
        else:
            # Display all form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = CustomerRegistrationForm()
    
    return render(request, "account/register.html", {'form': form})


# ==========================
# PROVIDER REGISTER
# ==========================
def provider_register(request):
    if request.method == "POST":
        form = ProviderRegistrationForm(request.POST)
        certificates = request.FILES.getlist("certificates")
        
        # Validate form
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return render(request, "account/provider_register.html", {'form': form})
        
        # Get number of selected categories
        service_categories = form.cleaned_data['service_categories']
        num_categories = len(service_categories)
        
        # Validate certificates count matches categories count
        if not certificates:
            messages.error(request, "At least one certificate is required")
            return render(request, "account/provider_register.html", {'form': form})
        
        num_certificates = len(certificates)
        
        if num_certificates != num_categories:
            messages.error(
                request, 
                f"🔴 Number of certificates must match number of categories selected. "
                f"You selected {num_categories} category/categories but uploaded {num_certificates} certificate(s). "
                f"Please upload exactly {num_categories} certificate(s) - one for each category."
            )
            return render(request, "account/provider_register.html", {'form': form})
        
        # Validate each certificate file
        certificate_form = ProviderCertificateUploadForm()
        for cert in certificates:
            certificate_form.cleaned_data = {'certificates': cert}
            try:
                certificate_form.clean_certificates()
            except forms.ValidationError as e:
                messages.error(request, f"Certificate validation error: {e.message}")
                return render(request, "account/provider_register.html", {'form': form})
        
        # Extract validated data
        full_name = form.cleaned_data['full_name']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        password = form.cleaned_data['password']
        experience = form.cleaned_data['experience']
        service_categories = form.cleaned_data['service_categories']
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )
        
        verification_token = get_random_string(32)
        
        # Create profile
        profile = Profile.objects.create(
            user=user,
            role="provider",
            is_verified=False,
            email_token=verification_token
        )
        
        # Add selected categories
        from account.models import ProviderCategory
        for category in service_categories:
            ProviderCategory.objects.create(
                provider=profile,
                category=category,
                is_verified=False
            )
        
        # Add certificates
        from account.models import ProviderCertificate
        for certificate in certificates:
            ProviderCertificate.objects.create(
                provider=profile,
                certificate=certificate
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
        
        # Auto-login and go to provider dashboard (still pending verification)
        login(request, user, backend='account.backends.EmailBackend')
        messages.success(
            request,
            "Provider account created successfully. Please verify your email."
        )
        return redirect("provider_dashboard")
    else:
        form = ProviderRegistrationForm()
    
    return render(request, "account/provider_register.html", {'form': form})


# ==========================
# LOGIN
# ==========================
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Authenticate user
            user = authenticate(request, username=email, password=password)
            
            if user:
                # Check if user account is active
                if not user.is_active:
                    messages.error(request, "Your account has been deactivated. Please contact support.")
                    return render(request, "account/login.html", {'form': form})
                
                # Login user
                login(request, user)
                
                # Get or create profile
                profile, _ = Profile.objects.get_or_create(
                    user=user,
                    defaults={"role": "customer", "is_verified": True}
                )
                
                # Redirect based on role
                if profile.role == "provider":
                    messages.success(request, f"Welcome back, {user.first_name}!")
                    return redirect("provider_dashboard")
                
                messages.success(request, f"Welcome back, {user.first_name}!")
                return redirect("customer_dashboard")
            else:
                messages.error(request, "Invalid email or password. Please try again.")
        else:
            # Display form validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = LoginForm()
    
    return render(request, "account/login.html", {'form': form})


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
