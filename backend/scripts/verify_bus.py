import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_campus.settings')
django.setup()

from core.models import User, Driver, Bus

def verify_bus_management():
    print("Verifying Admin Bus Management...")

    # 1. Cleanup
    print("Cleaning up verification data...")
    User.objects.filter(username='verify_admin').delete()
    User.objects.filter(username='verify_driver').delete()
    
    # 2. Create Admin
    print("Creating Admin user...")
    admin_user = User.objects.create_superuser('verify_admin', 'admin@test.com', 'password123')
    
    # 3. Create Driver
    print("Creating Driver user...")
    driver_user = User.objects.create_user('verify_driver', 'driver@test.com', 'password123', role='driver')
    driver_profile = Driver.objects.create(user=driver_user, phone_number='9998887776', license_number='DL-PRO-999')
    
    # 4. Bus Creation (Admin Action)
    print("Admin creating bus...")
    bus = Bus.objects.create(
        bus_number='TEST-BUS-01',
        route_name='Test Route',
        driver=driver_profile
    )
    print(f"Bus created: {bus}")
    
    # 5. Verify Assignment
    print("Verifying assignment...")
    assigned_bus = Bus.objects.get(driver=driver_profile)
    
    if assigned_bus.bus_number == 'TEST-BUS-01':
        print("SUCCESS: Driver 'verify_driver' is correctly assigned to 'TEST-BUS-01'.")
    else:
        print("FAILURE: Driver assignment mismatch.")
        
    # 6. Verify Dashboard Logic
    print("Verifying dashboard access logic...")
    try:
        # This simulates the query in driver_dashboard view
        check_bus = Bus.objects.get(driver=driver_profile)
        print("SUCCESS: Driver dashboard query found the bus.")
    except Bus.DoesNotExist:
        print("FAILURE: Driver dashboard query failed.")

if __name__ == '__main__':
    try:
        verify_bus_management()
    except Exception as e:
        print(f"ERROR: {e}")
