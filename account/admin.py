from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group

from .models import Profile


# Profile Admin

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'verified_status')
    list_filter = ('role', 'is_verified')
    search_fields = ('user__username',)

    def verified_status(self, obj):
        """
        Show verification only for providers
        """
        if obj.role == 'provider':
            return obj.is_verified
        return None

    verified_status.boolean = True
    verified_status.short_description = 'Verified'

    def get_fields(self, request, obj=None):
        """
        Control fields shown in admin based on role
        """
        if obj and obj.role == 'customer':
            return ('user', 'role')
        return ('user', 'role', 'certificate', 'is_verified')

    def save_model(self, request, obj, form, change):
        """
        Enforce business rules
        """
        if obj.role == 'customer':
            obj.is_verified = False
            obj.certificate = None
        super().save_model(request, obj, form, change)



# Profile Inline in User Admin

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

    def get_fields(self, request, obj=None):
        if obj and hasattr(obj, 'profile') and obj.profile.role == 'customer':
            return ('role',)
        return ('role', 'certificate', 'is_verified')



# Custom User Admin
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_role', 'provider_verified')

    def user_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.role
        return '-'

    user_role.short_description = 'User Role'

    def provider_verified(self, obj):
        if hasattr(obj, 'profile') and obj.profile.role == 'provider':
            return obj.profile.is_verified
        return None
    provider_verified.boolean = True
    provider_verified.short_description = 'Verified'

# Re-register User model
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
