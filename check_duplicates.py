from django.contrib.auth.models import User
from account.models import Profile
from collections import Counter

# Get all users
users = User.objects.all()
print(f"Total users: {users.count()}")

# Check for duplicate usernames
usernames = [u.username for u in users]
username_counts = Counter(usernames)
duplicate_usernames = {username: count for username, count in username_counts.items() if count > 1}

# Check for duplicate emails
emails = [u.email for u in users]
email_counts = Counter(emails)
duplicate_emails = {email: count for email, count in email_counts.items() if count > 1}

print(f"\nDuplicate usernames: {duplicate_usernames}")
print(f"Duplicate emails: {duplicate_emails}")

# Show all users
print("\n=== ALL USERS ===")
for u in users:
    try:
        profile = u.profile
        role = profile.role
    except:
        role = "no profile"
    print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}, Role: {role}")

# Clean duplicates - keep the oldest user for each duplicate
if duplicate_usernames:
    print("\n=== REMOVING DUPLICATE USERNAMES ===")
    for username in duplicate_usernames.keys():
        duplicate_users = User.objects.filter(username=username).order_by('id')
        print(f"\nFound {duplicate_users.count()} users with username '{username}'")
        
        # Keep the first one, delete the rest
        users_to_delete = duplicate_users[1:]
        for user in users_to_delete:
            print(f"  Deleting user ID {user.id} (username: {user.username})")
            user.delete()

print("\n=== CLEANUP COMPLETE ===")
print(f"Remaining users: {User.objects.count()}")
