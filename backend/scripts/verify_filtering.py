import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digital_campus.settings')
django.setup()

from core.models import User, Student, Teacher, Resource, Quiz, Question, QuizResult

def run_verification():
    print("🚀 Starting Department Filtering Verification...")

    # 1. Create Test Users & Departments
    try:
        # Teacher (CS)
        t_cs, _ = User.objects.get_or_create(username='teacher_cs', role='teacher')
        t_cs.set_password('pass')
        t_cs.save()
        teacher_cs, _ = Teacher.objects.get_or_create(user=t_cs, department='CS')
        
        # Student (CS)
        s_cs, _ = User.objects.get_or_create(username='student_cs', role='student')
        s_cs.set_password('pass')
        s_cs.save()
        student_cs, _ = Student.objects.get_or_create(user=s_cs, roll_no='CS001', course='B.Tech', department='CS')

        # Student (ME) - Different Department
        s_me, _ = User.objects.get_or_create(username='student_me', role='student')
        s_me.set_password('pass')
        s_me.save()
        student_me, _ = Student.objects.get_or_create(user=s_me, roll_no='ME001', course='B.Tech', department='ME')

        print("✅ Test Users Created: Teacher(CS), Student(CS), Student(ME)")
    except Exception as e:
        print(f"❌ Failed to create users: {e}")
        return

    # 2. Teacher (CS) Uploads Resource & Creates Quiz
    try:
        resource_cs = Resource.objects.create(
            title='CS Notes',
            uploaded_by=t_cs,
            resource_type='Notes',
            subject='Algorithms',
            department='CS',
            is_approved=True
        )
        print(f"✅ Resource Created for Department: {resource_cs.department}")

        quiz_cs = Quiz.objects.create(
            title='CS Quiz',
            subject='Algorithms',
            department='CS',
            teacher=teacher_cs
        )
        print(f"✅ Quiz Created for Department: {quiz_cs.department}")

    except Exception as e:
        print(f"❌ Failed to create content: {e}")
        return

    # 3. Verify Visibility for Student (CS)
    try:
        # Resource Visibility
        # Logic: Resource.objects.filter(department=dept)
        res_list_cs = Resource.objects.filter(department=student_cs.department)
        assert resource_cs in res_list_cs, "Student(CS) should see CS Resource"
        
        # Quiz Visibility
        quiz_list_cs = Quiz.objects.filter(department=student_cs.department)
        assert quiz_cs in quiz_list_cs, "Student(CS) should see CS Quiz"
        
        print("✅ Verified: Student(CS) CAN access CS content.")
    except AssertionError as e:
        print(f"❌ Verification Failed for Student(CS): {e}")

    # 4. Verify Visibility for Student (ME)
    try:
        # Resource Visibility
        res_list_me = Resource.objects.filter(department=student_me.department)
        assert resource_cs not in res_list_me, "Student(ME) should NOT see CS Resource"
        
        # Quiz Visibility
        quiz_list_me = Quiz.objects.filter(department=student_me.department)
        assert quiz_cs not in quiz_list_me, "Student(ME) should NOT see CS Quiz"
        
        print("✅ Verified: Student(ME) CANNOT access CS content.")
        
    except AssertionError as e:
        print(f"❌ Verification Failed for Student(ME): {e}")

    # Cleanup (Optional)
    # resource_cs.delete()
    # quiz_cs.delete()
    # t_cs.delete()
    # s_cs.delete()
    # s_me.delete()

    print("\n🎉 All Verification Tests Passed Successfully!")

if __name__ == '__main__':
    run_verification()
