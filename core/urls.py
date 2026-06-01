from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='user_profile'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('attendance/take/', views.take_attendance, name='take_attendance'),
    path('attendance/select/', views.attendance_method_select, name='attendance_method_select'),
    path('attendance/save/', views.save_attendance, name='save_attendance'),
    path('attendance/view/', views.view_attendance, name='view_attendance'),
    path('attendance/upload/', views.upload_attendance, name='upload_attendance'),
    path('attendance/upload/success/<int:upload_id>/', views.attendance_upload_success, name='attendance_upload_success'),
    path('attendance/upload/history/', views.attendance_upload_history, name='attendance_upload_history'),
    path('attendance/download-template/', views.download_attendance_template, name='download_attendance_template'),
    path('marks/add/', views.add_marks, name='add_marks'),
    path('marks/save/', views.save_marks, name='save_marks'),
    path('marks/view/', views.view_marks, name='view_marks'),
    path('notice/create/', views.create_notice, name='create_notice'),
    path('notice/view/', views.view_notices, name='view_notices'),
    path('chatbot/', views.chatbot, name='chatbot'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup_view, name='signup'),
    path('', views.index, name='home'),
    path('lost-and-found/', views.lost_found_list, name='lost_found_list'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('lost-and-found/delete/<int:item_id>/', views.delete_lost_found_item, name='delete_lost_found_item'),
    path('train-chatbot/', views.train_chatbot, name='train_chatbot'),
    path('complaint-list/', views.complaint_list, name='complaint_list'),
    path('manage-complaints/', views.admin_complaint_list, name='admin_complaint_list'),
    path('manage-complaints/resolve/<int:complaint_id>/', views.resolve_complaint, name='resolve_complaint'),
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('fees/', views.fee_status, name='fee_status'),
    path('feedback/', views.feedback_submit, name='feedback_submit'),
    
    # Assignment Module
    path('assignment/create/', views.create_assignment, name='create_assignment'),
    path('assignment/edit/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
    path('assignment/teacher_list/', views.teacher_assignments, name='teacher_assignments'), # Changed name to avoid conflict if any, clearer
    path('assignment/submissions/<int:assignment_id>/', views.view_submissions, name='view_submissions'),
    path('assignment/student_list/', views.student_assignments, name='student_assignments'),
    path('assignment/submit/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    
    # Resource Hub
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/upload/', views.upload_resource, name='upload_resource'),
    path('resources/approve/<int:resource_id>/', views.approve_resource, name='approve_resource'),
    path('resources/delete/<int:resource_id>/', views.delete_resource, name='delete_resource'),

    # Online Quiz
    path('quiz/', views.quiz_list, name='quiz_list'),
    path('quiz/create/', views.create_quiz, name='create_quiz'),
    path('quiz/edit/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('quiz/add_question/<int:quiz_id>/', views.add_question, name='add_question'),
    path('quiz/take/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('quiz/results/<int:quiz_id>/', views.view_quiz_results, name='view_quiz_results'),
    # Bus Tracking & Management
    path('driver/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('bus/track/', views.track_bus, name='track_bus'),
    path('bus/locations/', views.get_bus_locations, name='get_bus_locations'),
    path('bus/update_location/', views.update_location, name='update_location'),
    
    # Admin Bus Management
    path('manage-buses/', views.admin_bus_list, name='admin_bus_list'),
    path('manage-buses/add/', views.admin_add_bus, name='admin_add_bus'),
    path('manage-buses/edit/<int:bus_id>/', views.admin_edit_bus, name='admin_edit_bus'),
    path('manage-buses/delete/<int:bus_id>/', views.admin_delete_bus, name='admin_delete_bus'),
    
    # User Verification
    path('manage-users/verify/', views.admin_verify_users, name='admin_verify_users'),
    path('manage-users/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('manage-users/reject/<int:user_id>/', views.reject_user, name='reject_user'),
    path('manage-users/toggle-approval/', views.toggle_approval_mode, name='toggle_approval_mode'),
    
    # Admin Fees
    path('manage-fees/', views.admin_fee_list, name='admin_fee_list'),
    path('manage-fees/add/', views.admin_add_fee, name='admin_add_fee'),
    
    # Student Fees Payment
    path('fees/pay/<int:fee_id>/', views.pay_fee, name='pay_fee'),
]
