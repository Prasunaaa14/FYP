from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if not hasattr(request.user, "profile") or request.user.profile.role != "admin":
            messages.error(request, "You are not authorized to access admin panel.")
            return redirect("login")

        return view_func(request, *args, **kwargs)

    return _wrapped_view

# Alias for backwards compatibility
admin_only = admin_required
