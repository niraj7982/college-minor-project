import os
import django
import random
from datetime import date, timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_campus.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Student, Fee, Complaint, Notice, Marks, LostFoundItem, Teacher

User = get_user_model()

def populate():
    print("Populating sample data...")
    
    # 1. Get or Create Student
    username = 'test_student_verification'
    try:
        user = User.objects.get(username=username)
        student = user.student
        print(f"Using existing student: {username}")
    except User.DoesNotExist:
        print(f"User {username} not found. Please run verify_site.py first or create user manually.")
        return

    # 2. Add Fees
    if not Fee.objects.filter(student=student).exists():
        Fee.objects.create(student=student, amount=45000.00, due_date=date.today() + timedelta(days=30), semester='3rd Sem', status='Pending')
        Fee.objects.create(student=student, amount=2000.00, due_date=date.today() - timedelta(days=10), semester='Exam Fee', status='Paid')
        print("Added sample fees.")
    else:
        print("Fees already exist.")

    # 3. Add Complaints
    if not Complaint.objects.filter(student=student).exists():
        Complaint.objects.create(student=student, title="Water Cooler Not Working", description="The water cooler on the 2nd floor is broken.", status='Pending')
        Complaint.objects.create(student=student, title="Library Books", description="Need more copies of AI textbooks.", status='Resolved', admin_comment="Ordered 10 new copies.")
        print("Added sample complaints.")
    else:
        print("Complaints already exist.")

    # 4. Add Notices
    admin_user = User.objects.filter(role='admin').first()
    if not admin_user:
        # Create dummy admin if needed
        admin_user = User.objects.create_user('admin_demo', 'admin@test.com', 'admin123', role='admin')

    if not Notice.objects.exists():
        Notice.objects.create(title="Mid-Term Exams Schedule", content="Mid-term exams will start from next Monday.", category='Academic', posted_by=admin_user)
        Notice.objects.create(title="Annual Sports Day", content="Sports day is scheduled for 25th Feb. Register names with sports teacher.", category='Event', posted_by=admin_user)
        print("Added sample notices.")
    else:
        print("Notices already exist.")

    # 5. Add Marks
    if not Marks.objects.filter(student=student).exists():
        Marks.objects.create(student=student, subject="Data Structures", marks_obtained=85, total_marks=100, exam_type="Mid Term")
        Marks.objects.create(student=student, subject="Operating Systems", marks_obtained=78, total_marks=100, exam_type="Mid Term")
        print("Added sample marks.")
    else:
        print("Marks already exist.")

    # 6. Lost & Found
    if not LostFoundItem.objects.exists():
        LostFoundItem.objects.create(
            item_name="Blue Umbrella", 
            description="Found a blue umbrella near canteen.", 
            location="Canteen", 
            item_type="Found", 
            contact_info="Security Office", 
            posted_by=admin_user
        )
        print("Added sample Lost & Found item.")
    else:
        print("Lost & Found items already exist.")

    print("\nSUCCESS: Database populated with sample data!")

if __name__ == '__main__':
    populate()
