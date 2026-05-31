from django.urls import path
from users import views
from . import views
from .views import dashboard_view
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('home/', views.dashboard_view, name='home'),
    path('add_student/', views.add_student, name='add_student'),
    path('edit/<int:id>/', views.edit_student, name='edit_student'),
    path('delete/<int:id>/', views.delete_student, name='delete_student'),
    
    # logout (simple redirect)
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('add-classroom/', views.add_classroom, name='add_classroom'),
    path('add-subject/', views.add_subject, name='add_subject'),
    path('add-mark/', views.add_mark, name='add_mark'),
    path('student/<int:student_id>/', views.student_performance_view, name='student_performance'),
    path('students/', views.student_view, name='students'),
    path('add-student/', views.add_student, name='add_student'),
    path('student-performance/<int:student_id>', views.student_performance_view, name='student_performance'),
    path('class-detail/', views.class_detail, name='class_detail'),
    path('class/<int:id>/', views.class_detail, name='class_detail'),
    path('student/<int:id>/', views.student_detail, name='student_detail'),
    path('signup/', views.signup_view, name='signup'),
    path('classes/', views.class_list, name='classes'),
    path('marks/', views.mark_list, name='marks'),
    path('class/<int:id>/report/', views.class_report_pdf, name='class_report_pdf'),
    path('settings/', views.settings_view, name='settings'),
    path('student/<int:id>/report/', views.student_report_pdf, name='student_report_pdf'),
    path('school/report/', views.school_report_pdf, name='school_report_pdf'),
    path('setup-school/', views.setup_school, name='setup_school'),
]