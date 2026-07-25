from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Student, Teacher, Driver, Bus, Attendance, Marks, Notice, Complaint, Feedback, Fee, LostFoundItem, PasswordResetOTP, ChatbotTrainingData, Assignment, Submission, Resource, Quiz, Question, QuizResult

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'roll_no', 'course', 'department']
    search_fields = ['user__username', 'roll_no']

class TeacherAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']
    search_fields = ['user__username', 'department']

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status']
    list_filter = ['date', 'subject', 'status']

class MarksAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'exam_type', 'marks_obtained', 'total_marks']
    list_filter = ['subject', 'exam_type']

class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'posted_by', 'date_posted']
    search_fields = ['title', 'content']

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'course', 'subject', 'due_date']
    list_filter = ['course', 'subject', 'due_date']

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'submitted_at']
    list_filter = ['assignment', 'submitted_at']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Marks, MarksAdmin)
admin.site.register(Notice, NoticeAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Submission, SubmissionAdmin)
