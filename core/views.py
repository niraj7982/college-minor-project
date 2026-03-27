from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
import random

from .forms import LoginForm, SignupForm, ComplaintForm, FeedbackForm, LostFoundForm, ForgotPasswordForm, VerifyOTPForm, NewPasswordForm, ChatbotTrainingForm, AssignmentForm, SubmissionForm, ResourceForm, QuizForm, QuestionForm, BusForm
from .models import User, Student, Teacher, Driver, Bus, Attendance, Marks, Notice, Complaint, Feedback, Fee, LostFoundItem, PasswordResetOTP, ChatbotTrainingData, Assignment, Submission, Resource, Quiz, Question, QuizResult

def index(request):
    return render(request, 'core/index.html')

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_student():
                return redirect('student_dashboard')
            elif user.is_teacher():
                return redirect('teacher_dashboard')
            elif user.is_admin():
                return redirect('admin_dashboard')
            elif user.is_driver():
                return redirect('driver_dashboard')
            else:
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.email = form.cleaned_data['email']  # Explicitly save email
            user.role = form.cleaned_data['role']
            user.is_active = False #  # Deactivate account until admin approval
            user.save()
            
            # Create Profile
            if user.role == 'student':
                Student.objects.create(
                    user=user,
                    roll_no=form.cleaned_data['roll_no'],
                    course=form.cleaned_data['course'],
                    department=form.cleaned_data['department']
                )
            elif user.role == 'teacher':
                Teacher.objects.create(
                    user=user,
                    department=form.cleaned_data['department']
                )
            elif user.role == 'driver':
                Driver.objects.create(
                    user=user,
                    phone_number=form.cleaned_data['phone_number'],
                    license_number=form.cleaned_data['license_number']
                )
                
            messages.info(request, 'Your account has been created and is pending approval by the admin. Please wait for verification.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@login_required
def student_dashboard(request):
    if not request.user.is_student():
        return redirect('home')
        
    try:
        student = request.user.student
        attendance_records = Attendance.objects.filter(student=student)
        
        # Global Attendance
        total_classes = attendance_records.count()
        attended_classes = attendance_records.filter(status='Present').count()
        attendance_percentage = (attended_classes / total_classes * 100) if total_classes > 0 else 0
        
        # Subject-wise Attendance for Alerts
        subjects = attendance_records.values_list('subject', flat=True).distinct()
        low_attendance_subjects = []
        
        for sub in subjects:
            sub_total = attendance_records.filter(subject=sub).count()
            sub_present = attendance_records.filter(subject=sub, status='Present').count()
            if sub_total > 0:
                sub_percentage = (sub_present / sub_total) * 100
                if sub_percentage < 75:
                    low_attendance_subjects.append({
                        'name': sub,
                        'percentage': round(sub_percentage, 1)
                    })

        context = {
            'attendance_percentage': round(attendance_percentage, 2),
            'low_attendance_subjects': low_attendance_subjects,
            'show_attendance_alert': len(low_attendance_subjects) > 0
        }
    except Student.DoesNotExist:
        context = {
            'attendance_percentage': 0,
            'low_attendance_subjects': [],
            'show_attendance_alert': False,
            'error': 'Student profile not found. Please contact admin.'
        }
    return render(request, 'core/student_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    return render(request, 'core/teacher_dashboard.html')

@login_required
def admin_dashboard(request):
    return render(request, 'core/admin_dashboard.html')

@login_required
def take_attendance(request):
    if not request.user.is_teacher():
        return redirect('login')
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        course = request.POST.get('course')
        # Debug print
        print(f"Taking attendance for Course: {course}, Subject: {subject}")
        
        students = Student.objects.filter(course=course)
        context = {
            'students': students, 
            'subject': subject, 
            'course': course
        }
        return render(request, 'core/mark_attendance.html', context)
    
    return render(request, 'core/take_attendance_select.html')

@login_required
def save_attendance(request):
    if not request.user.is_teacher():
        return redirect('login')
        
    if request.method == 'POST':
        subject = request.POST.get('subject')
        all_student_ids = request.POST.getlist('all_student_ids')
        
        print(f"Saving attendance. Subject: {subject}, Students: {len(all_student_ids)}")
        
        for s_id in all_student_ids:
            try:
                student = Student.objects.get(user__id=s_id)
                status = 'Present' if request.POST.get(f'status_{s_id}') == 'on' else 'Absent'
                Attendance.objects.create(
                    student=student,
                    subject=subject,
                    status=status
                )
            except Student.DoesNotExist:
                print(f"Student with ID {s_id} not found!")
                continue
            
        return redirect('teacher_dashboard')

@login_required
def view_attendance(request):
    if request.user.is_student():
        student = request.user.student
        attendance_records = Attendance.objects.filter(student=student).order_by('-date')
        student_name = "My"
    elif request.user.is_admin():
        roll_no = request.GET.get('roll_no')
        if not roll_no:
            return render(request, 'core/admin_search_student.html', {'title': 'View Attendance'})
        
        try:
            student = Student.objects.get(roll_no=roll_no)
            attendance_records = Attendance.objects.filter(student=student).order_by('-date')
            student_name = f"{student.user.username}'s"
        except Student.DoesNotExist:
            return render(request, 'core/admin_search_student.html', {
                'title': 'View Attendance', 
                'error': f'Student with Roll No {roll_no} not found.'
            })
    else:
        return redirect('login')

    # Calculate stats for the chart
    total_days = attendance_records.count()
    days_present = attendance_records.filter(status='Present').count()
    days_absent = attendance_records.filter(status='Absent').count()
    
    # Subject-wise breakdown for multiple charts
    subjects = attendance_records.values_list('subject', flat=True).distinct()
    subject_charts_data = []
    colors = ['bg-primary', 'bg-success', 'bg-info', 'bg-warning', 'bg-danger', 'bg-secondary', 'bg-dark']
    # Force reload
    
    for i, sub in enumerate(subjects):
        sub_records = attendance_records.filter(subject=sub)
        present = sub_records.filter(status='Present').count()
        absent = sub_records.filter(status='Absent').count()
        subject_charts_data.append({
            'name': sub,
            'present': present,
            'absent': absent,
            'total': present + absent,
            'color': colors[i % len(colors)]
        })
    
    context = {
        'attendance_records': attendance_records,
        'total_days': total_days,
        'days_present': days_present,
        'days_absent': days_absent,
        'subject_charts_data': subject_charts_data,
        'student_name': student_name,
        'is_admin': request.user.is_admin()
    }
    return render(request, 'core/view_attendance_student.html', context)

@login_required
def add_marks(request):
    if not request.user.is_teacher():
        return redirect('login')
    
    if request.method == 'POST':
        roll_no = request.POST.get('roll_no')
        subject = request.POST.get('subject')
        marks_obtained = request.POST.get('marks_obtained')
        total_marks = request.POST.get('total_marks')
        exam_type = request.POST.get('exam_type')
        
        try:
            student = Student.objects.get(roll_no=roll_no)
            Marks.objects.create(
                student=student,
                subject=subject,
                marks_obtained=marks_obtained,
                total_marks=total_marks,
                exam_type=exam_type
            )
            return redirect('teacher_dashboard')
        except Student.DoesNotExist:
            print(f"Failed to add marks. Student {roll_no} not found.")
            return render(request, 'core/add_marks.html', {'error': f'Student with Roll No {roll_no} not found.'})
            
    return render(request, 'core/add_marks.html')

@login_required
def view_marks(request):
    if request.user.is_student():
        marks = Marks.objects.filter(student=request.user.student)
        heading = "My Marks"
    elif request.user.is_admin():
        roll_no = request.GET.get('roll_no')
        if not roll_no:
            return render(request, 'core/admin_search_student.html', {'title': 'View Marks'})
        
        try:
            student = Student.objects.get(roll_no=roll_no)
            marks = Marks.objects.filter(student=student)
            heading = f"Marks for {student.user.username} ({roll_no})"
        except Student.DoesNotExist:
             return render(request, 'core/admin_search_student.html', {
                'title': 'View Marks', 
                'error': f'Student with Roll No {roll_no} not found.'
            })
    else:
        return redirect('login')
        
    return render(request, 'core/view_marks.html', {'marks': marks, 'heading': heading, 'is_admin': request.user.is_admin()})

@login_required
def create_notice(request):
    # Fix permission check logic if ambiguous
    if not (request.user.is_teacher() or request.user.is_admin()):
        return redirect('login')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category = request.POST.get('category', 'General')
        
        if not title or not content:
             return render(request, 'core/create_notice.html', {'error': 'Title and Content are required.'})

        Notice.objects.create(
            title=title,
            content=content,
            category=category,
            posted_by=request.user
        )
        if request.user.is_teacher():
            return redirect('teacher_dashboard')
        else:
            return redirect('admin_dashboard')
            
    return render(request, 'core/create_notice.html')

@login_required
def admin_complaint_list(request):
    if not request.user.is_admin():
        return redirect('home')
        
    complaints = Complaint.objects.all().order_by('-date_posted')
    return render(request, 'core/admin_complaint_list.html', {'complaints': complaints})

@login_required
def resolve_complaint(request, complaint_id):
    if not request.user.is_admin():
        return redirect('home')
        
    complaint = get_object_or_404(Complaint, id=complaint_id)
    
    if request.method == 'POST':
        admin_comment = request.POST.get('admin_comment')
        complaint.admin_comment = admin_comment
        complaint.status = 'Solution Provided'
        complaint.save()
        messages.success(request, 'Solution provided successfully.')
        
    return redirect('admin_complaint_list')

@login_required
def admin_verify_users(request):
    if not request.user.is_admin():
        return redirect('home')
        
    pending_users = User.objects.filter(is_active=False).order_by('-date_joined')
    return render(request, 'core/admin_verify_users.html', {'pending_users': pending_users})

@login_required
def approve_user(request, user_id):
    if not request.user.is_admin():
        return redirect('home')
        
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f'User {user.username} has been approved.')
    return redirect('admin_verify_users')

@login_required
def reject_user(request, user_id):
    if not request.user.is_admin():
        return redirect('home')
        
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, f'User {user.username} has been rejected and removed.')
    return redirect('admin_verify_users')

# --- Student Module Views ---

@login_required
def complaint_list(request):
    if not request.user.is_student():
        return redirect('home')
    
    if request.method == 'POST':
        if 'mark_solved' in request.POST:
            complaint_id = request.POST.get('complaint_id')
            complaint = get_object_or_404(Complaint, id=complaint_id, student=request.user.student)
            complaint.status = 'Resolved'
            complaint.save()
            messages.success(request, 'Complaint marked as resolved.')
            return redirect('complaint_list')
        else:
            form = ComplaintForm(request.POST)
            if form.is_valid():
                complaint = form.save(commit=False)
                complaint.student = request.user.student
                complaint.save()
                messages.success(request, 'Complaint lodged successfully.')
                return redirect('complaint_list')
    else:
        form = ComplaintForm()
        
    complaints = Complaint.objects.filter(student=request.user.student).order_by('-date_posted')
    return render(request, 'core/complaint_list.html', {'complaints': complaints, 'form': form})

@login_required
def feedback_submit(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            return redirect('home') # Improve redirect later
    else:
        form = FeedbackForm()
    return render(request, 'core/feedback_form.html', {'form': form})

@login_required
def fee_status(request):
    if not request.user.is_student():
        return redirect('home')
        
    fees = Fee.objects.filter(student=request.user.student).order_by('-due_date')
    return render(request, 'core/fee_status.html', {'fees': fees})

@login_required
def lost_found_list(request):
    items = LostFoundItem.objects.all().order_by('-date_posted')
    
    if request.method == 'POST':
        form = LostFoundForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.posted_by = request.user
            item.save()
            return redirect('lost_found_list')
    else:
        form = LostFoundForm()
        
    return render(request, 'core/lost_found_list.html', {'items': items, 'form': form})

@login_required
def view_notices(request):
    notices = Notice.objects.all().order_by('-date_posted')
    return render(request, 'core/view_notices.html', {'notices': notices})

@login_required
def chatbot(request):
    response_text = ""
    if request.method == 'POST':
        query = request.POST.get('query', '').lower()
        
        # Simple Rule-based Logic with Dynamic Data

        # 0. Check Training Data (Custom Knowledge Base)
        from django.db.models import Q
        custom_knowledge = ChatbotTrainingData.objects.filter(
            Q(question__icontains=query) | Q(keywords__icontains=query)
        ).first()

        if custom_knowledge:
             response_text = custom_knowledge.answer
        
        # 1. Teachers
        elif 'teacher' in query or 'faculty' in query:
            teachers = Teacher.objects.all()
            if teachers:
                t_list = ", ".join([f"{t.user.username} ({t.department})" for t in teachers])
                response_text = f"Here are our teachers: {t_list}."
            else:
                response_text = "No teachers found in the directory."
                
        # 2. Fees (Student Only)
        elif 'fee' in query or 'due' in query:
            if request.user.is_student():
                pending_fees = Fee.objects.filter(student=request.user.student, status='Pending')
                if pending_fees.exists():
                    total = sum(f.amount for f in pending_fees)
                    response_text = f"You have pending fees of Rs. {total}. Please check the 'Fees' section for details."
                else:
                    response_text = "You have no pending fees. Great job!"
            else:
                response_text = "Fee information is only available for students."

        # 3. Academic / Syllabus
        elif 'syllabus' in query or 'course' in query:
             if request.user.is_student():
                 response_text = f"You are enrolled in {request.user.student.course}. Please visit the department office for the detailed syllabus."
             else:
                 response_text = "Syllabus information varies by course."

        # Existing Rules
        elif 'attendance' in query:
            response_text = "You can view your attendance in the Student Dashboard. Teachers can mark attendance from their dashboard."
        elif 'marks' in query or 'result' in query:
            response_text = "Marks can be viewed in the 'Marks' section of your dashboard once uploaded by your teacher."
        elif 'exam' in query:
            response_text = "For exam schedules, please check the 'Notices' section or contact the administration."
        elif 'contact' in query or 'help' in query:
            response_text = "You can contact the admin at admin@college.edu."
        elif 'hello' in query or 'hi' in query:
            response_text = "Hello! I am your campus assistant. How can I help you today?"
        else:
            response_text = "I'm sorry, I didn't understand that. Try asking about teachers, fees, attendance, or marks."
            
    return render(request, 'core/chatbot.html', {'response': response_text})

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                # Generate OTP
                otp = str(random.randint(100000, 999999))
                # Save OTP
                PasswordResetOTP.objects.create(user=user, otp=otp)
                
                # Send Email (Console)
                subject = 'Password Reset OTP'
                message = f'Your verification code is: {otp}'
                email_from = settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@digitalcampus.com'
                recipient_list = [email]
                
                send_mail(subject, message, email_from, recipient_list)
                
                # Store email in session
                request.session['reset_email'] = email
                
                msg = f'OTP has been sent to {email}'
                if settings.DEBUG:
                     msg += f' (Dev Mode: Your Code is {otp})'
                messages.success(request, msg)
                
                print(f"DEBUG: OTP for {email} is {otp}") # Helper for console
                return redirect('verify_otp')
                
            except User.DoesNotExist:
                messages.error(request, 'Email not found!')
    else:
        form = ForgotPasswordForm()
    return render(request, 'core/forgot_password.html', {'form': form})

def verify_otp(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')
        
    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp']
            try:
                user = User.objects.get(email=email)
                # Check if valid OTP exists (most recent)
                otp_record = PasswordResetOTP.objects.filter(user=user, otp=otp_input).last()
                
                if otp_record:
                    # Valid OTP
                    request.session['reset_verified'] = True
                    return redirect('reset_password')
                else:
                    messages.error(request, 'Invalid OTP!')
            except User.DoesNotExist:
                return redirect('forgot_password')
    else:
        form = VerifyOTPForm()
    return render(request, 'core/verify_otp.html', {'form': form})

def reset_password(request):
    email = request.session.get('reset_email')
    verified = request.session.get('reset_verified')
    
    if not email or not verified:
        return redirect('forgot_password')
        
    if request.method == 'POST':
        form = NewPasswordForm(request.POST)
        if form.is_valid():
            new_pass = form.cleaned_data['new_password']
            try:
                user = User.objects.get(email=email)
                user.set_password(new_pass)
                user.save()
                
                # Cleanup session
                del request.session['reset_email']
                del request.session['reset_verified']
                
                messages.success(request, 'Password reset successful! Please login.')
                return redirect('login')
            except User.DoesNotExist:
                return redirect('forgot_password')
    else:
        form = NewPasswordForm()
    return render(request, 'core/reset_password.html', {'form': form})

@login_required
def delete_lost_found_item(request, item_id):
    item = get_object_or_404(LostFoundItem, id=item_id)
    
    # Check permission: Only owner or admin can delete
    if request.user == item.posted_by or request.user.is_admin():
        item.delete()
        messages.success(request, 'Item post deleted successfully.')
    else:
        messages.error(request, 'You are not authorized to delete this item.')
    
    return redirect('lost_found_list')

@login_required
def train_chatbot(request):
    if not request.user.is_admin():
        return redirect('home')
        
    if request.method == 'POST':
        form = ChatbotTrainingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New training data added successfully!')
            return redirect('train_chatbot')
    else:
        form = ChatbotTrainingForm()
        
    training_data = ChatbotTrainingData.objects.all().order_by('-created_at')
    return render(request, 'core/train_chatbot.html', {'form': form, 'training_data': training_data})

# --- Assignment Module Views ---

@login_required
def create_assignment(request):
    if not request.user.is_teacher():
        return redirect('home')
        
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = request.user.teacher
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('teacher_assignments')
    else:
        form = AssignmentForm()
    return render(request, 'core/create_assignment.html', {'form': form})

@login_required
def teacher_assignments(request):
    if not request.user.is_teacher():
        return redirect('home')
    
    assignments = Assignment.objects.filter(teacher=request.user.teacher).order_by('-created_at')
    return render(request, 'core/teacher_assignments.html', {'assignments': assignments})

@login_required
def view_submissions(request, assignment_id):
    if not request.user.is_teacher():
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, id=assignment_id, teacher=request.user.teacher)
    submissions = Submission.objects.filter(assignment=assignment).order_by('-submitted_at')
    
    return render(request, 'core/view_submissions.html', {'assignment': assignment, 'submissions': submissions})

@login_required
def student_assignments(request):
    if not request.user.is_student():
        return redirect('home')
        
    student_course = request.user.student.course
    # Simple matching by course name
    assignments = Assignment.objects.filter(course__iexact=student_course).order_by('-due_date')
    
    return render(request, 'core/student_assignments.html', {'assignments': assignments})

@login_required
def submit_assignment(request, assignment_id):
    if not request.user.is_student():
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if already submitted
    existing_submission = Submission.objects.filter(assignment=assignment, student=request.user.student).first()
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user.student
            
            if existing_submission:
                # Update existing submission
                existing_submission.content = submission.content
                if submission.file:
                    existing_submission.file = submission.file
                existing_submission.submitted_at = submission.submitted_at # Update time
                existing_submission.save()
                messages.success(request, 'Assignment submission updated.')
            else:
                submission.save()
                messages.success(request, 'Assignment submitted successfully.')
                
            return redirect('student_assignments')
    else:
        form = SubmissionForm(instance=existing_submission) if existing_submission else SubmissionForm()
        
    return render(request, 'core/submit_assignment.html', {'form': form, 'assignment': assignment})

# --- Resource Hub Views ---

@login_required
def resource_list(request):
    dept = None
    if request.user.is_student():
        try:
            dept = request.user.student.department
        except Student.DoesNotExist:
            dept = None
    elif request.user.is_teacher():
        try:
            dept = request.user.teacher.department
        except Teacher.DoesNotExist:
            dept = None
            
    # Filter resources
    if dept:
        # Show resources for this department (case-insensitive)
        resources = Resource.objects.filter(is_approved=True, department__iexact=dept).order_by('-date_uploaded')
    elif request.user.is_admin():
        # Admin sees all
        resources = Resource.objects.filter(is_approved=True).order_by('-date_uploaded')
    else:
        # Fallback
        resources = Resource.objects.none()
    
    pending_resources = None
    if request.user.is_teacher():
        if dept:
            pending_resources = Resource.objects.filter(is_approved=False, department__iexact=dept).order_by('-date_uploaded')
        else:
            pending_resources = Resource.objects.none()
        
    return render(request, 'core/resource_list.html', {
        'resources': resources,
        'pending_resources': pending_resources,
        'is_teacher': request.user.is_teacher(),
        'user_department': dept
    })

@login_required
def upload_resource(request):
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = request.user
            
            if request.user.is_teacher():
                resource.is_approved = True
                messages.success(request, 'Resource uploaded successfully!')
            else:
                resource.is_approved = False
                messages.info(request, 'Resource uploaded and sent for approval.')
                
            resource.save()
            return redirect('resource_list')
    else:
        form = ResourceForm()
    return render(request, 'core/upload_resource.html', {'form': form})

@login_required
def approve_resource(request, resource_id):
    if not request.user.is_teacher():
        return redirect('resource_list')
        
    resource = get_object_or_404(Resource, id=resource_id)
    resource.is_approved = True
    resource.save()
    messages.success(request, 'Resource approved.')
    return redirect('resource_list')

@login_required
def delete_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    
    if request.user.is_teacher() or resource.uploaded_by == request.user:
        resource.delete()
        messages.success(request, 'Resource deleted.')
    else:
        messages.error(request, 'You do not have permission to delete this resource.')
        
    return redirect('resource_list')

# --- Online Quiz Views ---

@login_required
def quiz_list(request):
    dept = None
    if request.user.is_student():
        try:
            dept = request.user.student.department
        except Student.DoesNotExist:
            dept = None
    elif request.user.is_teacher():
        try:
            dept = request.user.teacher.department
        except Teacher.DoesNotExist:
            dept = None
            
    if dept:
        quizzes = Quiz.objects.filter(department__iexact=dept).order_by('-created_at')
    elif request.user.is_admin():
        quizzes = Quiz.objects.all().order_by('-created_at')
    else:
        quizzes = Quiz.objects.none()

    return render(request, 'core/quiz_list.html', {
        'quizzes': quizzes, 
        'is_teacher': request.user.is_teacher(),
        'user_department': dept
    })

@login_required
def create_quiz(request):
    if not request.user.is_teacher():
        return redirect('quiz_list')
        
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.teacher = request.user.teacher
            quiz.save()
            messages.success(request, 'Quiz created! Now add questions.')
            return redirect('add_question', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'core/create_quiz.html', {'form': form})

# --- Live Bus Tracking ---

@login_required
def driver_dashboard(request):
    if not request.user.is_driver():
        return redirect('home')
    
    # Check if driver has a bus assigned
    try:
        bus = Bus.objects.get(driver=request.user.driver)
    except Bus.DoesNotExist:
        bus = None
        
    return render(request, 'core/driver_dashboard.html', {'bus': bus})

@login_required
def admin_bus_list(request):
    if not request.user.is_admin():
        return redirect('home')
        
    buses = Bus.objects.all().order_by('bus_number')
    return render(request, 'core/admin_bus_list.html', {'buses': buses})

@login_required
def admin_add_bus(request):
    if not request.user.is_admin():
        return redirect('home')
        
    if request.method == 'POST':
        form = BusForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus added successfully!')
            return redirect('admin_bus_list')
    else:
        form = BusForm()
    return render(request, 'core/admin_add_bus.html', {'form': form, 'title': 'Add New Bus'})

@login_required
def admin_edit_bus(request, bus_id):
    if not request.user.is_admin():
        return redirect('home')
        
    bus = get_object_or_404(Bus, id=bus_id)
    if request.method == 'POST':
        form = BusForm(request.POST, instance=bus)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bus updated successfully!')
            return redirect('admin_bus_list')
    else:
        form = BusForm(instance=bus)
    return render(request, 'core/admin_add_bus.html', {'form': form, 'title': 'Edit Bus'})

@login_required
def admin_delete_bus(request, bus_id):
    if not request.user.is_admin():
        return redirect('home')
        
    bus = get_object_or_404(Bus, id=bus_id)
    bus.delete()
    messages.success(request, 'Bus deleted successfully!')
    return redirect('admin_bus_list')

from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def update_location(request):
    if request.method == 'POST' and request.user.is_driver():
        try:
            data = json.loads(request.body)
            lat = data.get('latitude')
            lng = data.get('longitude')
            is_active = data.get('is_active', True)
            
            driver = request.user.driver
            bus = Bus.objects.get(driver=driver)
            
            bus.latitude = lat
            bus.longitude = lng
            bus.is_active = is_active
            bus.save()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'forbidden'}, status=403)

@login_required
def track_bus(request):
    return render(request, 'core/track_bus.html')

def get_bus_locations(request):
    # Public or protected? Protected for safety
    if not request.user.is_authenticated:
        return JsonResponse({'buses': []})
        
    active_buses = Bus.objects.filter(is_active=True)
    data = []
    for bus in active_buses:
        if bus.latitude and bus.longitude:
            data.append({
                'id': bus.id,
                'bus_number': bus.bus_number,
                'route': bus.route_name,
                'lat': bus.latitude,
                'lng': bus.longitude,
                'driver_name': bus.driver.user.username if bus.driver else 'Unknown'
            })
            
    return JsonResponse({'buses': data})

@login_required
def add_question(request, quiz_id):
    if not request.user.is_teacher():
        return redirect('quiz_list')
        
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added.')
            if 'add_another' in request.POST:
                return redirect('add_question', quiz_id=quiz.id)
            else:
                return redirect('quiz_list')
    else:
        form = QuestionForm()
        
    questions = quiz.questions.all()
    return render(request, 'core/add_question.html', {'form': form, 'quiz': quiz, 'questions': questions})

@login_required
def take_quiz(request, quiz_id):
    if not request.user.is_student():
        return redirect('quiz_list')
        
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    
    # Check if already attempted
    existing_result = QuizResult.objects.filter(student=request.user.student, quiz=quiz).first()
    if existing_result:
        return render(request, 'core/quiz_result.html', {'result': existing_result, 'quiz': quiz})
    
    if request.method == 'POST':
        score = 0
        total = questions.count()
        
        for q in questions:
            selected_option = request.POST.get(f'question_{q.id}')
            if selected_option and int(selected_option) == q.correct_option:
                score += 1
                
        # Save Result
        result = QuizResult.objects.create(
            student=request.user.student,
            quiz=quiz,
            score=score,
            total_questions=total
        )
        return render(request, 'core/quiz_result.html', {'result': result, 'quiz': quiz})
        
    return render(request, 'core/take_quiz.html', {'quiz': quiz, 'questions': questions})
