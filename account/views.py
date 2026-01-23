import random

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.conf import settings
from django import forms

from .models import Profile, ProviderCategory, ProviderCertificate
from booking.models import Booking, Service
from .forms import (
    CustomerRegistrationForm,
    ProviderRegistrationForm,
    ProviderCertificateUploadForm,
    LoginForm
)

# ==========================
# CUSTOMER REGISTER (EMAIL VERIFICATION REQUIRED)
# ==========================
def register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name
            )

            code = f"{random.randint(100000, 999999)}"

            Profile.objects.create(
                user=user,
                role="customer",
                is_verified=False,
                phone=phone,
                email_token=code,
            )

            # store pending email in session for OTP verification
            request.session['pending_email'] = email

            try:
                send_mail(
                    subject="Your HomeService verification code",
                    message=f"""
Hello {full_name},

Your one-time verification code is: {code}

Enter this code on the verification page to activate your account.

If you did not sign up, you can ignore this email.

Thanks,
HomeService Team
""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                messages.success(request, "Account created. Enter the code sent to your email.")
            except Exception as e:
                messages.warning(request, f"Account created. Email may have failed. Code: {code}")
                print(f"Email send error: {str(e)}")
            
            return redirect("verify_email")

        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
    else:
        form = CustomerRegistrationForm()

    return render(request, "account/register.html", {'form': form})


# ==========================
# PROVIDER REGISTER (EMAIL + ADMIN VERIFICATION)
# ==========================
def provider_register(request):
    if request.method == "POST":
        form = ProviderRegistrationForm(request.POST)
        certificates = request.FILES.getlist("certificates")

        if not form.is_valid():
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, error)
            return render(request, "account/provider_register.html", {'form': form})

        service_categories = form.cleaned_data['service_categories']

        if not certificates or len(certificates) != len(service_categories):
            messages.error(
                request,
                "Number of certificates must match number of selected categories."
            )
            return render(request, "account/provider_register.html", {'form': form})

        certificate_form = ProviderCertificateUploadForm()
        for cert in certificates:
            certificate_form.cleaned_data = {'certificates': cert}
            try:
                certificate_form.clean_certificates()
            except forms.ValidationError as e:
                messages.error(request, e.message)
                return render(request, "account/provider_register.html", {'form': form})

        full_name = form.cleaned_data['full_name']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        password = form.cleaned_data['password']

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )

        code = f"{random.randint(100000, 999999)}"

        profile = Profile.objects.create(
            user=user,
            role="provider",
            is_verified=False,
            phone=phone,
            email_token=code,
        )

        for category in service_categories:
            ProviderCategory.objects.create(
                provider=profile,
                category=category,
                is_verified=False
            )

        for certificate in certificates:
            ProviderCertificate.objects.create(
                provider=profile,
                certificate=certificate
            )

        # store pending email in session for OTP verification
        request.session['pending_email'] = email

        try:
            send_mail(
                subject="Your HomeService provider verification code",
                message=f"""
Hello {full_name},

Your one-time verification code is: {code}

Enter this code on the verification page to activate your provider account.
After email verification, your account will be reviewed by admin.

If you did not sign up, you can ignore this email.

Thanks,
HomeService Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, "Provider account created. Enter the code sent to your email.")
        except Exception as e:
            messages.warning(request, f"Provider account created. Email may have failed. Code: {code}")
            print(f"Email send error: {str(e)}")
        
        return redirect("verify_email")

    else:
        form = ProviderRegistrationForm()

    return render(request, "account/provider_register.html", {'form': form})


def verify_email(request):
    pending_email = request.session.get('pending_email')

    if not pending_email:
        messages.info(request, "No verification in progress. Please log in or register.")
        return redirect("login")

    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        profile = get_object_or_404(Profile, user__username=pending_email)

        if code == profile.email_token:
            profile.is_verified = True
            profile.email_token = None
            profile.save()
            messages.success(request, "Email verified successfully. You can now log in.")
            request.session.pop('pending_email', None)
            return redirect("login")
        else:
            messages.error(request, "Invalid code. Please try again.")

    return render(request, "account/email_verification.html")


# ==========================
# LOGIN
# ==========================
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user:
                profile = user.profile

                if not profile.is_verified:
                    request.session['pending_email'] = user.username
                    messages.error(request, "Please enter the verification code sent to your email.")
                    return redirect("verify_email")

                login(request, user)

                if profile.role == "provider":
                    return redirect("provider_dashboard")

                return redirect("customer_dashboard")

            messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()

    return render(request, "account/login.html", {'form': form})


# ==========================
# LOGOUT
# ==========================
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


# ==========================
# CUSTOMER DASHBOARD
# ==========================
@login_required
def customer_dashboard(request):
    bookings = Booking.objects.filter(customer=request.user).order_by("-booking_date")
    return render(request, "account/customer_dashboard.html", {"bookings": bookings})


# ==========================
# PROVIDER DASHBOARD
# ==========================
@login_required
def provider_dashboard(request):
    bookings = Booking.objects.filter(
        service__provider__user=request.user
    ).order_by("-booking_date")

    return render(request, "account/provider_dashboard.html", {"bookings": bookings})


# ==========================
# PROFILE
# ==========================
@login_required
def profile_view(request):
    return render(request, "account/profile.html", {"profile": request.user.profile})


# ==========================
# SAVE LOCATION (AJAX)
# ==========================
@login_required
@require_POST
def save_location(request):
    profile = request.user.profile
    profile.latitude = request.POST.get("lat")
    profile.longitude = request.POST.get("lng")
    profile.location = request.POST.get("address", "")
    profile.save()
    return JsonResponse({"success": True})
