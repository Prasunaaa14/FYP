from django.urls import path
from . import views

urlpatterns = [

    # =====================
    # CUSTOMER SIDE
    # =====================
    path("search/", views.search_services, name="search_services"),
    path("categories/", views.service_categories, name="service_categories"),
    path("category/<str:category>/", views.providers_by_category, name="providers_by_category"),
    path("book/<int:service_id>/", views.book_service, name="book_service"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),

    # =====================
    # DASHBOARDS
    # =====================
    path("customer/dashboard/", views.customer_dashboard, name="customer_dashboard"),
    path("provider/dashboard/", views.provider_dashboard, name="provider_dashboard"),

    # =====================
    # PROVIDER SERVICES
    # =====================
    path("provider/services/", views.provider_services, name="provider_services"),
    path("provider/services/add/", views.add_service, name="add_service"),
    path("provider/services/edit/<int:service_id>/", views.edit_service, name="edit_service"),
    path("provider/services/delete/<int:service_id>/", views.delete_service, name="delete_service"),

    # =====================
    # PROVIDER BOOKINGS
    # =====================
    path("booking/update/<int:booking_id>/", views.update_booking_status, name="update_booking_status"),
    path("provider/<int:provider_id>/", views.provider_profile, name="provider_profile"),

    # =====================
    # MESSAGING
    # =====================
    path("messages/", views.messages_inbox, name="messages_inbox"),
    path("messages/<int:booking_id>/", views.view_messages, name="view_messages"),

]
