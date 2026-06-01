from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Student, Teacher, Bus, Driver, Attendance, Marks, Notice, Complaint, Feedback, Fee, LostFoundItem, PasswordResetOTP, ChatbotTrainingData, Assignment, Submission, Resource, Quiz, Question, QuizResult

COURSE_CHOICES = [
    ('', 'Select Course'),
    ('btech', 'B.Tech'),
    ('bsc', 'B.Sc'),
    ('bca', 'BCA'),
    ('mtech', 'M.Tech'),
    ('mca', 'MCA'),
    ('mba', 'MBA'),
]

DEPARTMENT_CHOICES = [
    ('', 'Select Department/Branch'),
    ('cs', 'CS'),
    ('cse', 'C.SE / CSE'),
    ('ece', 'ECE'),
    ('ee', 'EE'),
    ('me', 'ME'),
    ('ce', 'CE'),
    ('it', 'IT'),
]

SEMESTER_CHOICES = [
    ('', 'Select Semester'),
    ('1st Semester', '1st Semester'),
    ('2nd Semester', '2nd Semester'),
    ('3rd Semester', '3rd Semester'),
    ('4th Semester', '4th Semester'),
    ('5th Semester', '5th Semester'),
    ('6th Semester', '6th Semester'),
    ('7th Semester', '7th Semester'),
    ('8th Semester', '8th Semester'),
]




class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    role = forms.ChoiceField(choices=[('student', 'Student'), ('teacher', 'Teacher'), ('driver', 'Driver')], widget=forms.Select(attrs={'class': 'form-control'}))
    
    # Extra fields for profiles
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    roll_no = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll No (Student Only)'}))
    course = forms.ChoiceField(choices=COURSE_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    
    # Driver fields
    phone_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (Driver Only)'}))
    license_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'License Number (Driver Only)'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name', 'required': 'true'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name', 'required': 'true'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        role = cleaned_data.get("role")
        roll_no = cleaned_data.get("roll_no")
        course = cleaned_data.get("course")
        department = cleaned_data.get("department")
        semester = cleaned_data.get("semester")
        phone_number = cleaned_data.get("phone_number")
        license_number = cleaned_data.get("license_number")
        email = cleaned_data.get("email")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
            
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', 'Email is already taken')

        if role == 'student':
            if not roll_no:
                self.add_error('roll_no', 'Roll No is required for Students')
            elif Student.objects.filter(roll_no=roll_no).exists():
                self.add_error('roll_no', 'Roll No is already registered')
                
            if not course:
                self.add_error('course', 'Course is required for Students')
            if not department:
                self.add_error('department', 'Department is required for Students')
            if not semester:
                self.add_error('semester', 'Semester is required for Students')
        
        elif role == 'teacher':
             if not department:
                self.add_error('department', 'Department is required for Teachers')
                
        elif role == 'driver':
             if not phone_number:
                 self.add_error('phone_number', 'Phone Number is required for Drivers')
             if not license_number:
                 self.add_error('license_number', 'License Number is required for Drivers')
                
        return cleaned_data

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complaint Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Describe your issue...', 'rows': 4}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your feedback matters...', 'rows': 4}),
        }

class LostFoundForm(forms.ModelForm):
    class Meta:
        model = LostFoundItem
        fields = ['item_name', 'item_type', 'description', 'location', 'contact_info', 'image']
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item Name'}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description...', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Where did you lose/find it?'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Info'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your registered email'}))

class VerifyOTPForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit OTP'}))

class NewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class ChatbotTrainingForm(forms.ModelForm):
    class Meta:
        model = ChatbotTrainingData
        fields = ['question', 'answer', 'keywords']
        widgets = {
            'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g. When does the library open?'}),
            'keywords': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'library, time, open'}),
        }

class AssignmentForm(forms.ModelForm):
    course = forms.ChoiceField(choices=COURSE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'course', 'semester', 'subject', 'due_date', 'file', 'accept_late_submissions']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Assignment Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Assignment Description'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'accept_late_submissions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['content', 'file']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Type your answer or comments here...'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

# --- New Modules: Resources & Quiz Forms ---

class ResourceForm(forms.ModelForm):
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Resource
        fields = ['title', 'resource_type', 'subject', 'department', 'semester', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resource Title'}),
            'resource_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class QuizForm(forms.ModelForm):
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Quiz
        fields = ['title', 'subject', 'department', 'semester', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quiz Title'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Quiz Description/Instructions'}),
        }

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option1', 'option2', 'option3', 'option4', 'correct_option']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Question Text'}),
            'option1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 1'}),
            'option2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 2'}),
            'option3': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 3'}),
            'option4': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option 4'}),
            'correct_option': forms.Select(attrs={'class': 'form-control'}),
        }

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['bus_number', 'route_name', 'driver']
        widgets = {
            'bus_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bus Number'}),
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Route Name'}),
            'driver': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(BusForm, self).__init__(*args, **kwargs)
        # Filter drivers who don't have a bus assigned yet (plus the current one if editing)
        # For simplicity, we just show all drivers or maybe those without a bus?
        # Let's show all drivers for now, generic implementation.
        self.fields['driver'].queryset = Driver.objects.all()
        self.fields['driver'].label_from_instance = lambda obj: f"{obj.user.username} (License: {obj.license_number})"

class FeeForm(forms.ModelForm):
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Fee
        fields = ['student', 'semester', 'amount', 'due_date', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(FeeForm, self).__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.all()
        self.fields['student'].label_from_instance = lambda obj: f"{obj.user.username} ({obj.roll_no})"

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'profile_pic': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
