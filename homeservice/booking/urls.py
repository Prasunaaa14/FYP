from django.urls import path
from . import views

urlpatterns = [
    path("services/", views.service_list, name="service_list"),
    path("book/<int:service_id>/", views.book_service, name="book_service"),
]
