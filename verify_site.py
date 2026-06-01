import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_campus.settings')
django.setup()

from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model
from core.models import Student

User = get_user_model()

def run_checks():
    print("Starting site verification...")
    client = Client()

    # 1. Create/Get Test Student User
    username = 'test_student_verification'
    password = 'testpassword123'
    
    try:
        user = User.objects.get(username=username)
        print(f"User {username} exists.")
    except User.DoesNotExist:
        print(f"Creating user {username}...")
        user = User.objects.create_user(username=username, password=password, role='student')
        # Create associated Student profile
        Student.objects.create(
            user=user, 
            roll_no='TEST1001', 
            course='B.Tech', 
            department='CSE'
        )

    # 2. Login
    login_success = client.login(username=username, password=password)
    if not login_success:
        print("ERROR: Login failed!")
        return

    print("Login successful.")

    # 3. Define URLs to check
    urls_to_check = [
        '/student/dashboard/',
        '/attendance/view/',
        '/fees/',
        '/feedback/',
        '/complaint-list/',
        '/marks/view/',
        '/notice/view/',
        '/lost-and-found/',
    ]

    with open('verification_result.txt', 'w') as f:
        # 4. Check each URL
        all_passed = True
        for url in urls_to_check:
            try:
                print(f"Checking {url}...", end=' ')
                response = client.get(url, HTTP_HOST='127.0.0.1')
                if response.status_code == 200:
                    print("OK")
                    f.write(f"OK: {url}\n")
                elif response.status_code == 302:
                    print(f"REDIRECT (probably to login? Status: {response.status_code})")
                    f.write(f"REDIRECT: {url} (Status: {response.status_code})\n")
                else:
                    print(f"FAILED (Status: {response.status_code})")
                    f.write(f"FAILED: {url} (Status: {response.status_code})\n")
                    all_passed = False
            except Exception as e:
                print(f"EXCEPTION: {e}")
                f.write(f"EXCEPTION: {url} ({e})\n")
                all_passed = False

        if all_passed:
            f.write("SUCCESS: All modules checked and reachable.\n")
            print("SUCCESS")
        else:
            f.write("FAILURE: Some modules failed to load.\n")
            print("FAILURE")

run_checks()
