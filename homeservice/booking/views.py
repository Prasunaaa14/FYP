from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Service


# -------------------------------
# SERVICE LIST (Browse Services)
# -------------------------------
def service_list(request):
    services = Service.objects.all()
    return render(request, "booking/service_list.html", {
        "services": services
    })


# -------------------------------
# BOOK SERVICE (Single Service)
# -------------------------------
@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        # later you will save booking here
        return redirect("service_list")

    return render(request, "booking/book_service.html", {
        "service": service
    })
