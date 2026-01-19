from django.contrib.auth.models import User

print("=== CURRENT USERS IN DATABASE ===")
for u in User.objects.all().order_by('id'):
    try:
        profile = u.profile
        role = profile.role
    except:
        role = "no profile"
    print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}, Role: {role}")

print(f"\nTotal users: {User.objects.count()}")
