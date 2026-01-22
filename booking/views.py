from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import Service, Booking, Message
from account.models import Profile


# =====================================================
# PUBLIC: SERVICE CATEGORIES PAGE (No Login Required)
# =====================================================
def service_categories(request):
    """Public view - anyone can browse service categories"""
    categories = [
        ("painting", "Painting"),
        ("plumbing", "Plumbing"),
        ("electrical", "Electrical"),
        ("cleaning", "Cleaning"),
        ("carpentry", "Carpentry"),
        ("ac_repair", "AC Repair"),
    ]

    return render(request, "booking/service_categories.html", {
        "categories": categories
    })


# =====================================================
# PUBLIC: PROVIDERS BY CATEGORY (No Login Required)
# =====================================================
def providers_by_category(request, category):
    """Public view - anyone can view providers in a category"""
    from account.models import ProviderCategory
    
    # Get provider IDs that have THIS CATEGORY
    # Filter by both category and is_verified status
    provider_ids = ProviderCategory.objects.filter(
        category=category,
        is_verified=True  # Only get verified categories
    ).values_list('provider_id', flat=True)
    
    # Get VERIFIED providers with this verified category
    providers = Profile.objects.filter(
        id__in=provider_ids,
        role="provider",
        is_verified=True  # Only show verified providers
    ).distinct()

    return render(request, "booking/providers_by_category.html", {
        "providers": providers,
        "category": category.replace("_", " ").title(),
        "is_authenticated": request.user.is_authenticated
    })


# =====================================================
# CUSTOMER: BOOK A SERVICE
# =====================================================
@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, is_active=True)

    if request.method == "POST":
        Booking.objects.create(
            customer=request.user,
            service=service,
            booking_time=request.POST.get("service_time"),
            location=request.POST.get("location"),
            status="pending"
        )

        messages.success(request, "Service booked successfully.")
        return redirect("customer_dashboard")

    return render(request, "booking/book_service.html", {
        "service": service
    })


# =====================================================
# CUSTOMER DASHBOARD
# =====================================================
@login_required
def customer_dashboard(request):
    bookings = Booking.objects.filter(
        customer=request.user
    ).order_by("-booking_date")

    return render(request, "account/customer_dashboard.html", {
        "bookings": bookings
    })


# =====================================================
# PROVIDER DASHBOARD (FIXED + STATS)
# =====================================================
@login_required
def provider_dashboard(request):
    provider = request.user.profile

    bookings = Booking.objects.filter(
        service__provider=provider
    ).order_by("-booking_date")

    context = {
        "bookings": bookings,
        "pending_count": bookings.filter(status="pending").count(),
        "active_count": bookings.filter(status="approved").count(),
        "completed_count": bookings.filter(status="completed").count(),
    }

    return render(request, "account/provider_dashboard.html", context)


# =====================================================
# PROVIDER: APPROVE / REJECT BOOKING
# =====================================================
@login_required
@require_POST
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.service.provider.user != request.user:
        messages.error(request, "Unauthorized action.")
        return redirect("provider_dashboard")

    action = request.POST.get("action")

    if action == "approve":
        booking.status = "approved"
        messages.success(request, "Booking approved.")

    elif action == "reject":
        booking.status = "rejected"
        messages.success(request, "Booking rejected.")

    booking.save()
    return redirect("provider_dashboard")


# =====================================================
# CUSTOMER: CANCEL BOOKING
# =====================================================
@login_required
@require_POST
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        customer=request.user
    )

    if booking.status != "pending":
        messages.error(request, "You can only cancel pending bookings.")
        return redirect("customer_dashboard")

    booking.status = "cancelled"
    booking.save()

    messages.success(request, "Booking cancelled successfully.")
    return redirect("customer_dashboard")


# =====================================================
# PROVIDER: VIEW OWN SERVICES
# =====================================================
@login_required
def provider_services(request):
    services = Service.objects.filter(
        provider=request.user.profile
    )

    return render(request, "booking/provider_services.html", {
        "services": services
    })


# =====================================================
# PROVIDER: ADD SERVICE
# =====================================================
@login_required
def add_service(request):
    profile = request.user.profile

    # Block unverified providers from adding services
    if not profile.is_verified:
        messages.error(request, "Your account is not verified yet. Please wait for admin approval before adding services.")
        return redirect("provider_dashboard")

    if request.method == "POST":
        category = request.POST.get("category")

        Service.objects.create(
            provider=profile,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            category=category,
            price=request.POST.get("price"),
            location=request.POST.get("location"),
            is_active=True
        )

        messages.success(request, "Service added successfully.")
        return redirect("provider_services")

    return render(request, "booking/add_service.html")


# =====================================================
# PROVIDER: EDIT SERVICE
# =====================================================
@login_required
def edit_service(request, service_id):
    service = get_object_or_404(
        Service,
        id=service_id,
        provider=request.user.profile
    )

    if request.method == "POST":
        service.name = request.POST.get("name")
        service.description = request.POST.get("description")
        service.price = request.POST.get("price")
        service.location = request.POST.get("location")
        service.save()

        messages.success(request, "Service updated successfully.")
        return redirect("provider_services")

    return render(request, "booking/edit_service.html", {
        "service": service
    })


# =====================================================
# PROVIDER: DELETE SERVICE
# =====================================================
@login_required
def delete_service(request, service_id):
    service = get_object_or_404(
        Service,
        id=service_id,
        provider=request.user.profile
    )

    if request.method == "POST":
        service.delete()
        messages.success(request, "Service deleted successfully.")
        return redirect("provider_services")

    return render(request, "booking/delete_service.html", {
        "service": service
    })


# =====================================================
# PUBLIC: VIEW PROVIDER PROFILE (No Login Required)
# =====================================================
def provider_profile(request, provider_id):
    """Public view - anyone can view provider profile"""
    provider = get_object_or_404(
        Profile,
        id=provider_id,
        role="provider",
        is_verified=True
    )

    services = Service.objects.filter(
        provider=provider,
        is_active=True
    )

    return render(request, "booking/provider_profile.html", {
        "provider": provider,
        "services": services,
        "is_authenticated": request.user.is_authenticated
    })


# =====================================================
# MESSAGING: INBOX (ALL CONVERSATIONS)
# =====================================================
@login_required
def messages_inbox(request):
    # Get all bookings for the current user
    if hasattr(request.user, 'profile') and request.user.profile.role == 'provider':
        # Provider: show bookings where they are the service provider
        bookings = Booking.objects.filter(
            service__provider=request.user.profile
        ).order_by('-booking_date').distinct()
    else:
        # Customer: show their bookings
        bookings = Booking.objects.filter(
            customer=request.user
        ).order_by('-booking_date')
    
    # Add last message info to each booking
    conversations = []
    for booking in bookings:
        last_message = booking.messages.last()
        unread_count = booking.messages.filter(
            is_read=False
        ).exclude(sender=request.user).count()
        
        conversations.append({
            'booking': booking,
            'last_message': last_message,
            'unread_count': unread_count,
        })
    
    return render(request, "booking/messages_inbox.html", {
        "conversations": conversations,
    })


# =====================================================
# MESSAGING: VIEW CONVERSATION
# =====================================================
@login_required
def view_messages(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Security check: only customer or provider can view messages
    if request.user != booking.customer and request.user != booking.service.provider.user:
        messages.error(request, "Unauthorized access.")
        return redirect("customer_dashboard")
    
    # Get all messages for this booking
    conversation = Message.objects.filter(booking=booking)
    
    # Mark messages as read for the current user
    conversation.filter(~Q(sender=request.user), is_read=False).update(is_read=True)
    
    # Handle new message submission
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                booking=booking,
                sender=request.user,
                content=content
            )
            messages.success(request, "Message sent successfully.")
            return redirect("view_messages", booking_id=booking_id)
    
    context = {
        "booking": booking,
        "conversation": conversation,
        "is_customer": request.user == booking.customer,
    }
    
    return render(request, "booking/messages.html", context)
