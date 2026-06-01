import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_campus.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.cookie import CookieStorage
from core.views import signup_view, approve_user
from core.models import Student, SiteSettings
from core.forms import SignupForm

User = get_user_model()

def test_user_verification():
    print("Starting User Verification Test...")
    
    # Save original settings
    site_settings = SiteSettings.get_settings()
    original_require_approval = site_settings.require_approval
    site_settings.require_approval = True
    site_settings.save()
    
    username = 'test_verify_student'
    email = 'test_verify@example.com'
    roll_no = 'TEST_VERIFY_001'
    
    try:
        # 1. Cleanup previous test data
        User.objects.filter(username=username).delete()
        User.objects.filter(email=email).delete()
        Student.objects.filter(roll_no=roll_no).delete()
        print("Cleaned up previous test data.")

        # 2. Test Form Validity First
        data = {
            'username': username,
            'email': email,
            'password': 'password123',
            'confirm_password': 'password123',
            'role': 'student',
            'roll_no': roll_no,
            'course': 'B.Tech',
            'department': 'CS',
            'semester': '1st Semester'
        }
        
        form = SignupForm(data)
        if not form.is_valid():
            print("Form invalid!")
            print(form.errors)
            return
        else:
            print("Form is valid.")

        # 3. Simulate Signup View
        factory = RequestFactory()
        request = factory.post('/signup/', data)
        
        # Add session support
        try:
            from django.contrib.sessions.middleware import SessionMiddleware
            middleware = SessionMiddleware(lambda x: None)
            middleware.process_request(request)
            request.session.save()
        except Exception as e:
            print(f"Session setup warning: {e}")

        messages = CookieStorage(request)
        setattr(request, '_messages', messages)

        print("Submitting signup form to view...")
        try:
            response = signup_view(request)
            print(f"Signup View Response Code: {response.status_code}")
            if response.status_code == 302:
                print(f"Redirect URL: {response.url}")
        except Exception as e:
            print(f"Error in signup view: {e}")

        # 4. Verify User Created but Inactive
        try:
            new_user = User.objects.get(username=username)
            print(f"User created: {new_user.username}")
            
            if new_user.is_active:
                 print("FAILURE: User should be inactive initially.")
            else:
                 print("SUCCESS: User is inactive as expected.")
                 
        except User.DoesNotExist:
            print("FAILURE: User was not created.")
            return

        # 5. Simulate Admin Approval
        # Create a mock admin user
        try:
            admin_user = User.objects.filter(role='admin').first()
            if not admin_user:
                admin_user = User.objects.create_superuser('admin_test', 'admin@example.com', 'adminpass')
                admin_user.role = 'admin'
                admin_user.save()
                print("Created admin user.")
        except Exception as e:
            print(f"Error getting/creating admin: {e}")
            return
        
        request_approve = factory.get(f'/manage-users/approve/{new_user.id}/')
        request_approve.user = admin_user
        
        setattr(request_approve, '_messages', CookieStorage(request_approve))
        
        print(f"Approving user {new_user.username}...")
        approve_user(request_approve, new_user.id)
        
        # 6. Verify User Activated
        new_user.refresh_from_db()
        if new_user.is_active:
            print("SUCCESS: User is now active.")
        else:
            print("FAILURE: User is still inactive.")

        # Cleanup
        new_user.delete()
        print("Test Complete. Cleanup done.")
        
    finally:
        # Restore settings
        site_settings.require_approval = original_require_approval
        site_settings.save()

if __name__ == '__main__':
    test_user_verification()
