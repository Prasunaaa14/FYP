from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register, name="register"),
    path("provider-register/", views.provider_register, name="provider_register"),
    path("logout/", views.logout_view, name="logout"),

    # DASHBOARDS
    path("dashboard/customer/", views.customer_dashboard, name="customer_dashboard"),
    path("dashboard/provider/", views.provider_dashboard, name="provider_dashboard"),
    #services
    path("services/", views.browse_services, name="browse_services"),
    
    # PROFILE
    path("profile/", views.profile_view, name="profile"),
     path("save-location/", views.save_location, name="save_location"),
]
