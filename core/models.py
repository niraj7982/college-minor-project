from django.db import models
from django.contrib.auth.models import AbstractUser

# User Roles
class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
        ('driver', 'Driver'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def is_student(self):
        return self.role == 'student'
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def is_admin(self):
        return self.role == 'admin'

    def is_driver(self):
        return self.role == 'driver'

    @property
    def display_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.username

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    roll_no = models.CharField(max_length=20, unique=True)
    course = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} ({self.roll_no})"

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(max_length=15)
    license_number = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username

class Bus(models.Model):
    bus_number = models.CharField(max_length=20, unique=True)
    driver = models.OneToOneField(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    route_name = models.CharField(max_length=100)
    # Live Location Data
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False) # Is the trip active?

    def __str__(self):
        return f"{self.bus_number} - {self.route_name}"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    date = models.DateField(default=None, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def save(self, *args, **kwargs):
        if self.date is None:
            from datetime import date as _date
            self.date = _date.today()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.username} - {self.subject} - {self.status}"


class Marks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    marks_obtained = models.IntegerField()
    total_marks = models.IntegerField()
    exam_type = models.CharField(max_length=50) # e.g. 'Mid Term', 'Final'

    def __str__(self):
        return f"{self.student.user.username} - {self.subject}: {self.marks_obtained}/{self.total_marks}"

class Notice(models.Model):
    CATEGORY_CHOICES = (
        ('General', 'General'),
        ('Academic', 'Academic'),
        ('Event', 'Event'),
    )
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='General')
    content = models.TextField()
    file = models.FileField(upload_to='notices/', blank=True, null=True)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Solution Provided', 'Solution Provided'),
        ('Resolved', 'Resolved'),
        ('Rejected', 'Rejected'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    admin_comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.student.user.username}"

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username}"

class Fee(models.Model):
    STATUS_CHOICES = (
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    semester = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.student.user.username} - {self.semester} ({self.status})"

class LostFoundItem(models.Model):
    TYPE_CHOICES = (
        ('Lost', 'Lost'),
        ('Found', 'Found'),
    )
    item_name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    item_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    contact_info = models.CharField(max_length=100)
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='lost_found_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.item_type}: {self.item_name}"

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.otp}"

class ChatbotTrainingData(models.Model):
    question = models.TextField(help_text="The question referencing the topic (e.g., 'When is the exam?')")
    answer = models.TextField(help_text="The answer the bot should give.")
    keywords = models.CharField(max_length=255, help_text="Comma-separated keywords for matching (e.g., 'exam, date, schedule')")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class Assignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    accept_late_submissions = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.subject})"

    @property
    def is_closed(self):
        from datetime import date
        return date.today() > self.due_date and not self.accept_late_submissions

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='submissions/', blank=True, null=True)

    def __str__(self):
        return f"Submission by {self.student.user.username} for {self.assignment.title}"

# --- New Modules: Resources & Quiz ---

class Resource(models.Model):
    TYPE_CHOICES = (
        ('Notes', 'Notes'),
        ('PYQ', 'Previous Year Question'),
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='resources/')
    resource_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=100)
    department = models.CharField(max_length=100, default='General')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.resource_type})"

class Quiz(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    department = models.CharField(max_length=100, default='General')
    description = models.TextField(blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.subject}"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    correct_option = models.IntegerField(choices=[(1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')])

    def __str__(self):
        return f"{self.quiz.title} - Q: {self.text[:30]}"

class QuizResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.quiz.title}: {self.score}/{self.total_questions}"

class AttendanceUpload(models.Model):
    """Stores metadata about attendance files uploaded by teachers."""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    attendance_date = models.DateField()
    file = models.FileField(upload_to='attendance_uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    records_imported = models.IntegerField(default=0)
    records_skipped = models.IntegerField(default=0)
    error_log = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.teacher.user.username} - {self.subject} ({self.attendance_date})"

