from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min
from .models import Student
from .forms import StudentForm
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from io import BytesIO
from django.contrib import messages
from .forms import MarkForm
from .models import Mark
from .forms import ClassroomForm
from .models import Student, Subject, Classroom, Mark, Teacher
from .forms import SubjectForm
from django.template.loader import get_template
# from xhtml2pdf import pisa
from django.contrib.auth import logout

def home (request):
    students = Student.objects.all()
    return render(request, 'home.html', {'students': students})

def logout_user(request):
    logout(request)
    return redirect('/login')

def calculate_grade(marks):
    if marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    else:
        return "F"

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        return redirect('/admin/')
    
    classroom_id = request.GET.get('classroom')

    if classroom_id and classroom_id != "ALL":
        mark_list = marks_list.filter(student__classroom_id=classroom_id)

    # Now filtering works
    students = Student.objects.filter(classroom__school=teacher.school)
    subjects = Subject.objects.filter(classroom__school=teacher.school)
    Classrooms = Classroom.objects.filter(school=teacher.school)
    marks_list = Mark.objects.filter(student__classroom__school=teacher.school) # Show all marks, not filtered by user
    print("MARKS COUNT:", marks_list.count())

    if classroom_id:
        marks_list = marks_list.filter(student__classroom_id=classroom_id)

    average_marks = marks_list.aggregate(Avg('marks'))['marks__avg']
    highest_marks = marks_list.aggregate(Max('marks'))['marks__max']
    lowest_marks = marks_list.aggregate(Min('marks'))['marks__min']

    pass_count = marks_list.filter(marks__gte=50).count()
    fail_count = marks_list.filter(marks__lt=50).count()

    # Chart data
    marks_qs = marks_list.values('student__name').annotate(avg_marks=Avg('marks'),
        highest=Max('marks'),
        lowest=Min('marks'))

    context = {
        'students': students,
        'subjects': subjects,
        'classrooms': Classrooms,
        'marks_list': marks_list,
        'marks_qs': marks_qs,
        'average_marks': average_marks,
        'highest_marks': highest_marks,
        'lowest_marks': lowest_marks,
        'pass_count': pass_count,
        'fail_count': fail_count, 
    }
        
    return render(request, 'users/dashboard.html', context)

def login_view(request):
    if request.method == "POST":
        # after successful login
        return redirect('dashboard')
    return render(request, 'login.html')

def pdf_report(request):
    return HttpResponse("PDF feature coming soon")
    teacher = Teacher.objects.filter(user=request.user).first()
    if not teacher:
        return redirect('/admin/')
    
    marks_list = Mark.objects.filter(student__school=teacher.school)

    # Summary calculations
    average_marks = marks_list.aggregate(Avg('marks'))['marks__avg']
    pass_count = marks_list.filter(marks__gte=50).count()
    fail_count = marks_list.filter(marks__lt=50).count()

    template_path = 'users/report_template.html'
    context = {
        'teacher': teacher,
        'marks_list': marks_list,
        'average_marks': average_marks,
        'pass_count': pass_count,
        'fail_count': fail_count,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="student_report.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF')
    
    return response

def add_classroom(request):
    try:
        # get the teacher limked to the to the logged-in user
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        # if no teacher exists, redirect to dashboard or show error
        return redirect('dashboard')
    
    if request.method == "POST":
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.school = teacher.school  # link to teacher's school
            classroom.save()
            return redirect('dashboard')
        else:
            # always define form here for GET requests
            Form = ClassroomForm()

        # At this point, form is always defined
        return render(request, 'users/add_classroom.html', {'form': form})

@login_required
def add_student(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return redirect('dashboard')

    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.school = teacher.school
            student.save()
            messages.success(request, "Student updated successfully.")
            return redirect('dashboard')
    else:
        form = StudentForm()
    return render(request, 'add_student.html', {'form': form})

def add_subject(request):
    try:
        teacher = Teacher.objects.get(user=request.user)
    except Teacher.DoesNotExist:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SubjectForm(request.POST)

        if form.is_valid():
            subject = form.save(commit=False)
            subject.teacher = teacher
            subject.classroom = form.cleaned_data['classroom'] # select classroom from form
            subject.save()
            return redirect('dashboard')
        else:
            form = SubjectForm()

        return render(request, 'users/add_subject.html', {'form': form})

def add_mark(request):
    if request.method == 'POST':
        form = MarkForm(request.POST)

        if form.is_valid():
            mark = form.save(commit=False)

            if mark.marks >= 80:
                mark.grade = "A"
            elif mark.marks >= 70:
                mark,grade = "B"
            elif mark.marks >= 60:
                mark.grade = "C"
            elif mark.marks >= 50:
                mark.grade = "D"
            else:
                mark.grade = "F"

            mark.status = "Pass" if mark.mark >= 50 else "Fail"

            mark.save()

            return redirect('dashboard')
        
    else:
        form = MarkForm()

    return render(request, 'users/add_mark.html', {'form': form})

def student_performance(request, student_id):
    student = Student.objects.get(id=student_id)

    marks = Mark.objects.filter(student=student)

    context = {
        'student': student,
        'marks': marks,
    }

    return render(request, 'users/student_performance.html', context)

@login_required
def edit_student(request, id):
    student = get_object_or_404(Student, id=id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = StudentForm(instance=student)

    return render(request, 'edit_student.html', {'form': form})

@login_required
def delete_student(request, id):
    student = get_object_or_404(Student, id=id)
    student.delete()
    return redirect('dashboard')




