import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_campus.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Student

User = get_user_model()

def test_user_verification_client():
    print("Starting User Verification Test (Client)...")
    
    username = 'verify_client_user'
    email = 'verify_client@example.com'
    password = 'password123'
    roll_no = 'CLIENT_001'
    
    # 1. Cleanup
    User.objects.filter(username=username).delete()
    User.objects.filter(email=email).delete()
    Student.objects.filter(roll_no=roll_no).delete()
    
    c = Client()
    
    # 2. Signup
    print("Submitting Signup Form...")
    response = c.post('/signup/', {
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': password,
        'role': 'student',
        'roll_no': roll_no,
        'course': 'B.Tech',
        'department': 'CS'
    }, follow=True)
    
    print(f"Signup Response Status: {response.status_code}")
    
    # Check messages
    messages = list(response.context['messages']) if response.context and 'messages' in response.context else []
    for m in messages:
        print(f"Message: {m}")
        if "pending approval" in str(m):
            print("SUCCESS: Found pending approval message.")

    # 3. Verify Inactive
    try:
        user = User.objects.get(username=username)
        if not user.is_active:
             print(f"SUCCESS: User {username} is inactive.")
        else:
             print(f"FAILURE: User {username} is active!")
    except User.DoesNotExist:
        print("FAILURE: User not created.")
        return

    # 4. Login Attempt (Should fail)
    login_logged_in = c.login(username=username, password=password)
    if not login_logged_in:
        print("SUCCESS: Login failed for inactive user.")
    else:
        print("FAILURE: Login succeeded for inactive user!")
        c.logout()

    # 5. Admin Approval
    # Create Admin
    admin_username = 'admin_verify_test'
    User.objects.filter(username=admin_username).delete()
    admin = User.objects.create_superuser(admin_username, 'admin@test.com', 'adminpass')
    
    c.force_login(admin)
    print("Logged in as Admin.")
    
    # Approve
    print(f"Approving user {user.id}...")
    response = c.get(f'/manage-users/approve/{user.id}/', follow=True)
    print(f"Approve Response Status: {response.status_code}")
    
    user.refresh_from_db()
    if user.is_active:
        print("SUCCESS: User is now active.")
    else:
        print("FAILURE: User is still inactive after approval!")

    # 6. Login Attempt (Should succeed)
    c.logout()
    login_success = c.login(username=username, password=password)
    if login_success:
        print("SUCCESS: Login succeeded for activated user.")
    else:
        print("FAILURE: Login failed for activated user!")

    # Cleanup
    user.delete()
    admin.delete()
    print("Test Complete.")

if __name__ == '__main__':
    test_user_verification_client()
