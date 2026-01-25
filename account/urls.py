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
    
    # SERVICESpath("services/", views.browse_services, name="browse_services"),
    
    # PROFILE
    path("profile/", views.profile_view, name="profile"),
    path("save-location/", views.save_location, name="save_location"),
    path("verify-email/", views.verify_email, name="verify_email"),

    # CUSTOM ADMIN DASHBOARD 
   # ADMIN
path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
path("admin/users/", views.admin_users, name="admin_users"),
path("admin/providers/", views.admin_providers, name="admin_providers"),
path("admin/provider/<int:provider_id>/", views.admin_provider_detail, name="admin_provider_detail"),
path("admin/provider/<int:provider_id>/approve/", views.admin_approve_provider, name="admin_approve_provider"),
path("admin/provider/<int:provider_id>/reject/", views.admin_reject_provider, name="admin_reject_provider"),
path("admin/services/", views.admin_services, name="admin_services"),

]

