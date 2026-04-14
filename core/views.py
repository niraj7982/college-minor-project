from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
import random
import csv
import io
from datetime import date

from .forms import LoginForm, SignupForm, ComplaintForm, FeedbackForm, LostFoundForm, ForgotPasswordForm, VerifyOTPForm, NewPasswordForm, ChatbotTrainingForm, AssignmentForm, SubmissionForm, ResourceForm, QuizForm, QuestionForm, BusForm, FeeForm
from .models import User, Student, Teacher, Driver, Bus, Attendance, Marks, Notice, Complaint, Feedback, Fee, LostFoundItem, PasswordResetOTP, ChatbotTrainingData, Assignment, Submission, Resource, Quiz, Question, QuizResult, AttendanceUpload

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
def attendance_method_select(request):
    """Show the two-option attendance method chooser page."""
    if not request.user.is_teacher():
        return redirect('login')
    return render(request, 'core/take_attendance_select.html')

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
    
    return render(request, 'core/manual_attendance_form.html')

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
        course = request.POST.get('course')
        subject = request.POST.get('subject')
        total_marks = request.POST.get('total_marks')
        exam_type = request.POST.get('exam_type')
        
        students = Student.objects.filter(course__iexact=course)
        
        context = {
            'students': students,
            'course': course,
            'subject': subject,
            'total_marks': total_marks,
            'exam_type': exam_type,
        }
        return render(request, 'core/add_marks_grid.html', context)
        
    return render(request, 'core/add_marks.html')

@login_required
def save_marks(request):
    if not request.user.is_teacher():
        return redirect('login')
        
    if request.method == 'POST':
        course = request.POST.get('course')
        subject = request.POST.get('subject')
        total_marks = request.POST.get('total_marks')
        exam_type = request.POST.get('exam_type')
        all_student_ids = request.POST.getlist('all_student_ids')
        
        for s_id in all_student_ids:
            marks_val = request.POST.get(f'marks_{s_id}')
            if marks_val and marks_val.strip() != '':
                try:
                    student = Student.objects.get(user__id=s_id)
                    # Create or update the marks entry
                    Marks.objects.update_or_create(
                        student=student,
                        subject=subject,
                        exam_type=exam_type,
                        defaults={
                            'marks_obtained': int(marks_val),
                            'total_marks': int(total_marks)
                        }
                    )
                except Student.DoesNotExist:
                    continue
        
        from django.contrib import messages
        messages.success(request, f'Marks successfully saved for Course: {course}, Subject: {subject}.')
        return redirect('teacher_dashboard')
        
    return redirect('add_marks')

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
        notice_file = request.FILES.get('file')
        
        if not title or not content:
             return render(request, 'core/create_notice.html', {'error': 'Title and Content are required.'})

        Notice.objects.create(
            title=title,
            content=content,
            category=category,
            file=notice_file,
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
    import google.generativeai as genai
    from django.conf import settings as django_settings
    from django.db.models import Q

    # --- Session-based chat history ---
    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    chat_history = request.session['chat_history']
    response_text = ""
    user_query = ""

    if request.method == 'POST':
        # Handle clear history
        if request.POST.get('clear_history'):
            request.session['chat_history'] = []
            return redirect('chatbot')

        user_query = request.POST.get('query', '').strip()
        if not user_query:
            return render(request, 'core/chatbot.html', {'chat_history': chat_history})

        query_lower = user_query.lower()

        # --- Priority 1: Custom Knowledge Base (DB) ---
        custom_knowledge = ChatbotTrainingData.objects.filter(
            Q(question__icontains=query_lower) | Q(keywords__icontains=query_lower)
        ).first()

        if custom_knowledge:
            response_text = custom_knowledge.answer

        # --- Priority 2: Campus-specific live data rules ---
        elif 'teacher' in query_lower or 'faculty' in query_lower:
            teachers = Teacher.objects.all()
            if teachers:
                t_list = ", ".join([f"{t.user.username} ({t.department})" for t in teachers])
                response_text = f"Here are our teachers: {t_list}."
            else:
                response_text = "No teachers found in the directory."

        elif 'fee' in query_lower or 'due' in query_lower:
            if request.user.is_student():
                pending_fees = Fee.objects.filter(student=request.user.student, status='Pending')
                if pending_fees.exists():
                    total = sum(f.amount for f in pending_fees)
                    response_text = f"You have pending fees of Rs. {total}. Please check the 'Fees' section for details."
                else:
                    response_text = "You have no pending fees. Great job!"
            else:
                response_text = "Fee information is only available for students."

        elif 'syllabus' in query_lower or 'course' in query_lower:
            if request.user.is_student():
                response_text = f"You are enrolled in {request.user.student.course}. Please visit the department office for the detailed syllabus."
            else:
                response_text = "Syllabus information varies by course."

        elif 'attendance' in query_lower:
            response_text = "You can view your attendance in the Student Dashboard. Teachers can mark attendance from their dashboard."

        elif 'marks' in query_lower or 'result' in query_lower:
            response_text = "Marks can be viewed in the 'Marks' section of your dashboard once uploaded by your teacher."

        elif 'exam' in query_lower:
            response_text = "For exam schedules, please check the 'Notices' section or contact the administration."

        # --- Priority 3: Gemini AI fallback ---
        else:
            api_key = django_settings.GEMINI_API_KEY
            if api_key:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(
                        model_name='gemini-2.0-flash',
                        system_instruction=(
                            "You are a helpful Campus Assistant for a Digital Campus platform used by "
                            "students, teachers, and administrators. "
                            "Your role is to answer academic, campus-related, and general educational questions clearly and helpfully. "
                            "Keep responses concise and friendly. "
                            "If asked something unrelated to academics or campus life, gently steer the conversation back."
                        )
                    )
                    # Build history for multi-turn context
                    gemini_history = []
                    for msg in chat_history[-10:]:   # last 10 turns for context
                        gemini_history.append({'role': 'user', 'parts': [msg['user']]})
                        gemini_history.append({'role': 'model', 'parts': [msg['bot']]})

                    chat_session = model.start_chat(history=gemini_history)
                    gemini_response = chat_session.send_message(user_query)
                    response_text = gemini_response.text
                except Exception as e:
                    response_text = f"Sorry, I couldn't reach the AI service right now. Please try again shortly. (Error: {e})"
            else:
                response_text = (
                    "I'm not sure about that. Try asking about teachers, fees, attendance, marks, or exams. "
                    "(Gemini AI key not configured.)"
                )

        # --- Save to session history ---
        # Keep only last 5 exchanges to stay within signed-cookie size limits on Vercel
        chat_history.append({'user': user_query, 'bot': response_text})
        if len(chat_history) > 5:
            chat_history = chat_history[-5:]
        request.session['chat_history'] = chat_history
        request.session.modified = True

    return render(request, 'core/chatbot.html', {
        'chat_history': chat_history,
        'last_query': user_query,
    })

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
def edit_assignment(request, assignment_id):
    if not request.user.is_teacher():
        return redirect('home')
        
    assignment = get_object_or_404(Assignment, id=assignment_id, teacher=request.user.teacher)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully!')
            return redirect('teacher_assignments')
    else:
        form = AssignmentForm(instance=assignment)
        
    return render(request, 'core/edit_assignment.html', {'form': form, 'assignment': assignment})

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
        from datetime import date
        if date.today() > assignment.due_date and not assignment.accept_late_submissions:
            messages.error(request, 'The due date for this assignment has passed. Late submissions are not accepted.')
            return redirect('student_assignments')

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
                from django.utils import timezone
                existing_submission.submitted_at = timezone.now() # Update time correctly
                existing_submission.save()
                messages.success(request, 'Assignment submission updated.')
            else:
                submission.save()
                messages.success(request, 'Assignment submitted successfully.')
                
            return redirect('student_assignments')
    else:
        form = SubmissionForm(instance=existing_submission) if existing_submission else SubmissionForm()
        
    from datetime import date
    is_closed = (date.today() > assignment.due_date and not assignment.accept_late_submissions)
        
    return render(request, 'core/submit_assignment.html', {'form': form, 'assignment': assignment, 'is_closed': is_closed, 'existing_submission': existing_submission})

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
    from django.db.models import Q
    if request.user.is_admin():
        # Admin sees all
        resources = Resource.objects.filter(is_approved=True).order_by('-date_uploaded')
    else:
        # Show resources for this department, General, empty, or uploaded by user
        dept_q = Q(department__iexact='General') | Q(department__iexact='')
        if dept:
            dept_q |= Q(department__iexact=dept)
            
        resources = Resource.objects.filter(
            Q(is_approved=True) & (dept_q | Q(uploaded_by=request.user))
        ).distinct().order_by('-date_uploaded')
    
    pending_resources = None
    if request.user.is_teacher():
        # Teachers see all pending resources, so that mistyped departments aren't stuck hidden forever.
        pending_resources = Resource.objects.filter(
            is_approved=False
        ).order_by('-date_uploaded')
        
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

@login_required
def user_profile(request):
    from .forms import UserProfileForm
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            from django.contrib import messages
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'core/profile.html', {'form': form})

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


# ============================================================
# --- Attendance File Upload Views ---
# ============================================================

ALLOWED_ATTENDANCE_EXTENSIONS = {'xlsx', 'csv'}

def _get_file_extension(filename):
    return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

@login_required
def upload_attendance(request):
    """Allow teacher to upload an Excel or CSV file to bulk-import attendance."""
    if not request.user.is_teacher():
        return redirect('home')

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        course = request.POST.get('course', '').strip()
        attendance_date_str = request.POST.get('attendance_date', '').strip()
        uploaded_file = request.FILES.get('attendance_file')

        # --- Validation ---
        if not subject or not course or not attendance_date_str or not uploaded_file:
            messages.error(request, 'All fields are required — Subject, Course, Date, and File.')
            return render(request, 'core/upload_attendance.html')

        ext = _get_file_extension(uploaded_file.name)
        if ext not in ALLOWED_ATTENDANCE_EXTENSIONS:
            messages.error(request, 'Only .xlsx (Excel) and .csv files are supported.')
            return render(request, 'core/upload_attendance.html')

        try:
            from datetime import datetime
            attendance_date = datetime.strptime(attendance_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return render(request, 'core/upload_attendance.html')

        # --- Parse Rows ---
        rows = []   # list of (roll_no, status)
        parse_error = None

        if ext == 'xlsx':
            try:
                import openpyxl
                wb = openpyxl.load_workbook(uploaded_file, read_only=True, data_only=True)
                ws = wb.active
                headers = [str(cell.value).strip().lower() if cell.value else '' for cell in next(ws.iter_rows(min_row=1, max_row=1))]
                if 'roll_no' not in headers or 'status' not in headers:
                    parse_error = 'Excel file must have columns: roll_no, status'
                else:
                    roll_idx = headers.index('roll_no')
                    status_idx = headers.index('status')
                    for row in ws.iter_rows(min_row=2, values_only=True):
                        roll = str(row[roll_idx]).strip() if row[roll_idx] is not None else ''
                        status_val = str(row[status_idx]).strip().capitalize() if row[status_idx] is not None else ''
                        if roll:
                            rows.append((roll, status_val))
                wb.close()
            except Exception as e:
                parse_error = f'Failed to read Excel file: {e}'

        elif ext == 'csv':
            try:
                file_data = uploaded_file.read().decode('utf-8-sig')
                reader = csv.DictReader(io.StringIO(file_data))
                # Normalise header names
                fieldnames = [f.strip().lower() for f in (reader.fieldnames or [])]
                if 'roll_no' not in fieldnames or 'status' not in fieldnames:
                    parse_error = 'CSV file must have columns: roll_no, status'
                else:
                    for raw_row in reader:
                        norm = {k.strip().lower(): v for k, v in raw_row.items()}
                        roll = norm.get('roll_no', '').strip()
                        status_val = norm.get('status', '').strip().capitalize()
                        if roll:
                            rows.append((roll, status_val))
            except Exception as e:
                parse_error = f'Failed to read CSV file: {e}'

        if parse_error:
            messages.error(request, parse_error)
            return render(request, 'core/upload_attendance.html')

        if not rows:
            messages.error(request, 'The file has no data rows. Please check the file content.')
            return render(request, 'core/upload_attendance.html')

        # --- Import into DB ---
        imported = 0
        skipped = 0
        error_lines = []

        for roll_no, status_val in rows:
            if status_val not in ('Present', 'Absent'):
                skipped += 1
                error_lines.append(f"Roll {roll_no}: invalid status '{status_val}' (must be Present or Absent)")
                continue
            try:
                student = Student.objects.get(roll_no=roll_no)
                Attendance.objects.create(
                    student=student,
                    subject=subject,
                    status=status_val,
                    date=attendance_date,
                )
                imported += 1
            except Student.DoesNotExist:
                skipped += 1
                error_lines.append(f"Roll {roll_no}: student not found in system")

        # --- Save upload record ---
        # Re-open file for saving (it was consumed during parse)
        uploaded_file.seek(0)
        upload_record = AttendanceUpload.objects.create(
            teacher=request.user.teacher,
            subject=subject,
            course=course,
            attendance_date=attendance_date,
            file=uploaded_file,
            records_imported=imported,
            records_skipped=skipped,
            error_log='\n'.join(error_lines),
        )

        return redirect('attendance_upload_success', upload_id=upload_record.id)

    return render(request, 'core/upload_attendance.html')


@login_required
def attendance_upload_success(request, upload_id):
    """Show summary of a completed attendance upload."""
    if not request.user.is_teacher():
        return redirect('home')
    upload = get_object_or_404(AttendanceUpload, id=upload_id, teacher=request.user.teacher)
    error_lines = [line for line in upload.error_log.splitlines() if line.strip()]
    return render(request, 'core/attendance_upload_success.html', {
        'upload': upload,
        'error_lines': error_lines,
    })


@login_required
def attendance_upload_history(request):
    """List all attendance files uploaded by this teacher."""
    if not request.user.is_teacher():
        return redirect('home')
    uploads = AttendanceUpload.objects.filter(teacher=request.user.teacher).order_by('-uploaded_at')
    return render(request, 'core/attendance_upload_history.html', {'uploads': uploads})


@login_required
def download_attendance_template(request):
    """Generate and return a sample Excel attendance template for teachers."""
    if not request.user.is_teacher():
        return redirect('home')
    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Attendance'

        # Header row styling
        header_fill = PatternFill('solid', fgColor='4F46E5')
        header_font = Font(bold=True, color='FFFFFF', size=12)

        headers = ['roll_no', 'status']
        for col_idx, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')

        # Column widths
        ws.column_dimensions['A'].width = 18
        ws.column_dimensions['B'].width = 18

        # Example rows
        sample_rows = [
            ('101', 'Present'),
            ('102', 'Absent'),
            ('103', 'Present'),
        ]
        for row_idx, (roll, status) in enumerate(sample_rows, start=2):
            ws.cell(row=row_idx, column=1, value=roll)
            ws.cell(row=row_idx, column=2, value=status)

        # Add instructions on sheet 2
        ws2 = wb.create_sheet('Instructions')
        ws2['A1'] = 'HOW TO FILL ATTENDANCE TEMPLATE'
        ws2['A1'].font = Font(bold=True, size=14)
        instructions = [
            '',
            'COLUMNS:',
            '  roll_no  — The student roll number (must match exactly as registered in system)',
            '  status   — Must be exactly: Present  OR  Absent  (case-insensitive)',
            '',
            'RULES:',
            '  • Do not rename or delete the header row',
            '  • One student per row',
            '  • Rows with unknown roll numbers will be skipped and logged',
            '  • Delete example rows (101, 102, 103) before uploading',
        ]
        for i, line in enumerate(instructions, start=2):
            ws2.cell(row=i, column=1, value=line)
        ws2.column_dimensions['A'].width = 70

        # Return as HTTP response
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="attendance_template.xlsx"'
        return response

    except ImportError:
        messages.error(request, 'openpyxl is not installed. Please contact the administrator.')
        return redirect('upload_attendance')

# --- Admin Fees Module ---

@login_required
def admin_fee_list(request):
    if not request.user.is_admin():
        return redirect('home')
    fees = Fee.objects.all().order_by('-due_date')
    return render(request, 'core/admin_fee_list.html', {'fees': fees})

@login_required
def admin_add_fee(request):
    if not request.user.is_admin():
        return redirect('home')
        
    if request.method == 'POST':
        form = FeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee added successfully!')
            return redirect('admin_fee_list')
    else:
        form = FeeForm()
        
    return render(request, 'core/admin_add_fee.html', {'form': form})

@login_required
def pay_fee(request, fee_id):
    if not request.user.is_student():
        return redirect('home')
        
    fee = get_object_or_404(Fee, id=fee_id, student=request.user.student)
    
    if fee.status == 'Paid':
        messages.info(request, 'This fee is already paid.')
        return redirect('fee_status')
        
    if request.method == 'POST':
        # Simulate payment processing
        fee.status = 'Paid'
        fee.save()
        messages.success(request, 'Payment successful! Fee marked as Paid.')
        return redirect('fee_status')
        
    return render(request, 'core/pay_fee.html', {'fee': fee})


