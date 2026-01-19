from django.contrib.auth.models import User

# Find the duplicate users with the same email
duplicate_email = 'prasunashrestha3@gmail.com'
users_with_email = User.objects.filter(email=duplicate_email).order_by('id')

print(f"Found {users_with_email.count()} users with email '{duplicate_email}':")
for u in users_with_email:
    try:
        profile = u.profile
        print(f"  ID: {u.id}, Username: {u.username}, Role: {profile.role}, Created: {profile.created_at}")
    except:
        print(f"  ID: {u.id}, Username: {u.username}, Role: no profile")

if users_with_email.count() > 1:
    # Keep the first one (oldest), delete the rest
    users_to_delete = users_with_email[1:]
    for user in users_to_delete:
        print(f"\nDeleting duplicate user:")
        print(f"  ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        user.delete()
    print("\nDuplicates removed successfully!")
else:
    print("\nNo duplicates to remove.")

print(f"\nRemaining users with this email: {User.objects.filter(email=duplicate_email).count()}")
