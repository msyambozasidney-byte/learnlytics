from django.urls import path
from . import views
from .views import home_view
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_student/', views.add_student, name='add_student'),
    path('edit/<int:id>/', views.edit_student, name='edit_student'),
    path('delete/<int:id>/', views.delete_student, name='delete_student'),
    path('report/', views.pdf_report, name='pdf_report'),
    
    # logout (simple redirect)
    path('', home_view, name='home'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add-classroom/', views.add_classroom, name='add_classroom'),
    path('add-subject/', views.add_subject, name='add_subject'),
    path('add-mark/', views.add_mark, name='add_mark'),
    path('student/<int:student_id>/', views.student_performance, name='student_performance'),
    path('add-student/', views.add_student, name='add_student'),
    path('student-performance/<int:student_id>', views.student_performance, name='student_performance'),
    path('export-pdf/', views.pdf_report, name='export_pdf'),
]