import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_campus.settings')
django.setup()

from core.models import User, Teacher, Student, Assignment, Submission

def test_assignment_flow():
    print("Starting Assignment Module Verification...")
    
    # 1. Create Test Users
    try:
        # Teacher
        t_user, _ = User.objects.get_or_create(username='test_teacher', role='teacher')
        t_user.set_password('pass')
        t_user.save()
        teacher, _ = Teacher.objects.get_or_create(user=t_user, department='CS')
        print("✅ Test Teacher Created/Found")

        # Student
        s_user, _ = User.objects.get_or_create(username='test_student', role='student')
        s_user.set_password('pass')
        s_user.save()
        student, _ = Student.objects.get_or_create(user=s_user, roll_no='TEST001', course='CS101', department='CS')
        print("✅ Test Student Created/Found")
        
    except Exception as e:
        print(f"❌ Failed to create users: {e}")
        return

    # 2. Create Assignment
    try:
        assignment = Assignment.objects.create(
            teacher=teacher,
            subject='CS101',
            course='CS101', # Matching student course
            title='Test Assignment 1',
            description='This is a test assignment',
            due_date=date.today()
        )
        print(f"✅ Assignment '{assignment.title}' Created")
    except Exception as e:
        print(f"❌ Failed to create assignment: {e}")
        return

    # 3. Student Submit Assignment
    try:
        submission = Submission.objects.create(
            assignment=assignment,
            student=student,
            content='This is a test submission.'
        )
        print(f"✅ Submission for '{assignment.title}' Created")
    except Exception as e:
        print(f"❌ Failed to create submission: {e}")
        return

    # 4. Verify Linkage
    try:
        assert submission.assignment == assignment
        assert submission.student == student
        assert assignment.teacher == teacher
        print("✅ Data Integrity Verified")
    except AssertionError as e:
        print(f"❌ Data Integrity Failed: {e}")
        return
        
    # Cleanup (Optional, commented out to inspect DB if needed)
    # assignment.delete()
    # t_user.delete()
    # s_user.delete()
    # print("✅ Test Data Cleaned Up")

    print("\n🎉 Verification Successful! The backend logic for Assignments is working.")

if __name__ == '__main__':
    test_assignment_flow()
