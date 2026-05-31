from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.db.models import Avg, Max, Min, Count
from .models import Student
from .forms import StudentForm
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from django.http import HttpResponse
from io import BytesIO
from django.contrib import messages
from .forms import MarkForm
from .models import Mark
from .forms import ClassroomForm
from .models import Student, Subject, Classroom, Mark, Teacher, School, UserProfile
from .forms import SubjectForm
from django.template.loader import get_template
# from xhtml2pdf import pisa
from django.contrib.auth import logout
from django.contrib.auth.models import User
from users.models import School, Student, Teacher, Classroom, Subject, Mark
from django.db.models import Prefetch
from collections import defaultdict
from django.contrib.auth import login
from .forms import SignUpForm

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    return render(request, 'users/landing.html')



@login_required
def settings_view(request):
    school = get_user_school(request)

    if request.method == 'POST':
        school.name = request.POST.get('school_name')

        school.save()

        return redirect('settings')

    return render(request, 'users/settings.html', {
        'school': school
    })

@login_required
def setup_school(request):

    school = get_user_school(request)

    return render(request, 'users/setup_school.html',{
        'school': school
    })

def get_user_school(request):
    profile = getattr(request.user, 'userprofile', None)

    if profile is not None:
        return profile.school
    
    return None

def signup_view(request):
    print("SIGNUP VIEW RUNNING")

    if request.method == 'POST':
        print("POST REQUEST RECEIVED")

        form = SignUpForm(request.POST)

        if form.is_valid():
            print("FORM IS VALID")

            user = form.save()

            school_name = form.cleaned_data['school_name']

            school = School.objects.create(name=school_name)

            UserProfile.objects.create(
                user=user,
                school=school
            )

            login(request, user)

            print("USER CREATED SUCCESSFULLY")

            return redirect('dashboard')
        
        else:

            print(form.errors)

    else:

        form = SignUpForm()
        
    return render(request, 'registration/signup.html', {
        'form': form
    })

def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')
    
    error = None
    
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        
        else:

            error = "Invalid username or password"
   
    return render(request, 'registration/login.html', {
        'error': error
    })

@login_required
def dashboard_view(request):

    school = get_user_school(request)

    classrooms = Classroom.objects.filter(school=school)
    students = Student.objects.filter(classroom__school=school)
    subjects = Subject.objects.filter(mark__student__classroom__school=school).distinct()
    marks = Mark.objects.filter(student__classroom__school=school)
    selected_class = request.GET.get('class')

    if selected_class:
        filtered_students = Student.objects.filter(classroom_id=selected_class)
    else:
        filtered_students = Student.objects.all()
    
    schools_count = School.objects.count()
    classes_count = Classroom.objects.count()
    students_count = Student.objects.count()
    teachers_count = Teacher.objects.count()
    subjects_count = Subject.objects.count()

    marks = Mark.objects.filter(student__classroom__school=school)

    total_students = students.count()
    total_classes = classrooms.count()
    total_subjects = Subject.objects.filter(school=school).count()
    overall_average = Mark.objects.filter(school=school).aggregate(avg=Avg('score'))['avg']
    
    if overall_average is None:
        overall_average = 0

    chart_labels = []
    chart_data = []

    classrooms = Classroom.objects.filter(school=school)

    for classroom in classrooms:
        avg_score = Mark.objects.filter(student__classroom=classroom).aggregate(avg=Avg('score'))['avg']

        chart_labels.append(classroom.name)
        chart_data.append(avg_score if avg_score else 0)

    top_students = Student.objects.filter(classroom__school=school).annotate(avg_score=Avg('mark__score')
).order_by('-avg_score')[:5]

    students_at_risk = Student.objects.filter(classroom__school=school).annotate(avg_score=Avg('mark__score')
).filter(avg_score__lt=50).order_by('avg_score')

    recent_marks = Mark.objects.filter(student__classroom__school=school).order_by('-id')[:5]

    recent_students = students.order_by('-id')[:5]

    weak_subjects = Subject.objects.filter(school=school).annotate(avg_score=Avg('mark__score')
).order_by('-avg_score')[:5]
    
    classes = Classroom.objects.filter(school=school)

    class_names = []
    class_averages = []

    for classroom in classes:
        avg = Mark.objects.filter(student__classroom=classroom).aggregate(avg=Avg('score'))['avg']

        class_names.append(classroom.name)
        class_averages.append(round(avg, 2) if avg else 0)

    return render(request, 'home.html', {
        'school': school,
        'classrooms': classrooms,
        'students': students,
        'recent_students': recent_students,
        'filtered_students': filtered_students,
        'marks': marks,
        'weak_subjects': weak_subjects,
        'recent_marks': recent_marks,
        'students_at_risk': students_at_risk,
        'top_students': top_students,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'subjects': subjects,
        'class_names': class_names,
        'class_averages': class_averages,
        'total_students': total_students,
        'total_classes': total_classes,
        'total_subjects': total_subjects,
        'overall_average': round(overall_average, 1),
    })

def student_detail(request, id):
    school = get_user_school(request)
    if school is None:
        return redirect('login')
    
    student = get_object_or_404(
        Student,
        id=id,
        classroom__school=school # This is the key
    )

    return render(request, 'student_detail.html', {
        'student': student
    })

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

def login_view(request):
    if request.method == "POST":
        # after successful login
        return redirect('dashboard')
    return render(request, 'registration/login.html')


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
    school = get_user_school(request)
    if school is None:
        return render(request, 'users/add_student.html')
    
    classrooms = Classroom.objects.filter(school=school)

    if request.method == 'POST':
        name = request.POST.get('name')
        classroom_id = request.POST.get('classroom')

        # Ensure classroom belongs to this school
        classroom = Classroom.objects.get(
            id=classroom_id,
            school=school
        )

        Student.objects.create(
            name=name,
            classroom=classroom
        )

        return redirect('students')

    return render(request, 'users/add_student.html', {
        'classrooms': classrooms
    })

def get_user_school(request):
    profile = getattr(request.user, 'userprofile', None)

    if profile:
        return profile.school
    
    return None

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
    
    school = get_user_school(request)

    students = Student.objects.filter(classroom__school=school)

    subjects = Subject.objects.filter(school=school)

    if request.method == 'POST':

        student_id = request.POST.get('student')
        subject_id = request.POST.get('subject')
        score = request.POST.get('score')

        student = Student.objects.get(id=student_id)
        subject = Subject.objects.get(id=subject_id)

        Mark.objects.create(
            student=student,
            subject=subject,
            score=score,
            school=school
        )

        return redirect('marks')
    
    return render(request, 'users/add_mark.html', {
        'students': students,
        'subjects': subjects
    })

@login_required
def student_performance_view(request, student_id):
    school = get_user_school(request)
    
    student = get_object_or_404(
        Student,
        id=student_id,
        classroom__school=school
    )

    marks = Mark.objects.filter(student=student, school=school).select_related('subject')

    subject_names = []
    subject_scores = []

    for mark in marks:
        subject_names.append(mark.subject.name)
        subject_scores.append(mark.score)

    average_score = marks.aggregate(avg=Avg('score'))['avg']

    if average_score is None:
        average_score = 0


    context = {
        'student': student,
        'marks': marks,
        'subject_names': json.dumps(subject_names),
        'subject_scores': json.dumps(subject_scores),
        'average_score': round(average_score, 1),
    }

    return render(request, 'users/student_performance.html', context)

@login_required
def edit_student(request, id):
    school = get_user_school(request)
    if school is None:
        return redirect('login')
    
    student = get_object_or_404(
        Student,
        id=id,
        classroom__school=school
    )

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
    school = get_user_school(request)
    if school is None:
        return redirect('login')
    
    student = get_object_or_404(
        Student,
        id=id,
        classroom__school=school
    )

    student.delete()
    return redirect('students')

@login_required
def student_view(request):

    school = get_user_school(request)

    students = Student.objects.filter(classroom__school=school).select_related('classroom')

    return render(request, 'users/students.html', {
        'students': students,
        'school': school
    })
def class_list(request):
    school = get_user_school(request)
    if school is None:
        return render(request, 'users/classes.html', {
            'classroms': []
        })
    
    classrooms = Classroom.objects.filter(school=school)

    return render(request, 'users/classes.html', {
        'classrooms': classrooms
    })

def mark_list(request):
    school = get_user_school(request)
    if school is None:
        return render(request, 'users/marks.html', {
            'marks': []
        })
    
    marks = Mark.objects.filter(student__classroom__school=school)

    return render(request, 'users/marks.html', {
        'marks': marks
    })

@login_required
def class_detail(request, id):
    school = get_user_school(request)
    if school is None:
        return redirect('classes.html', {
            'classes': []
        })
    
    # Secure classroom
    classroom = get_object_or_404(
        Classroom,
        id=id,
        school=school
    )

    # Sidebar classes
    classes = Classroom.objects.filter(school=school)

    # Students in class
    students = Student.objects.filter(classroom=classroom, classroom__school=school)

    student_names = []
    student_averages = []

    # Marks in this class
    marks = Mark.objects.filter(
        student__classroom=classroom,
        student__classroom__school=school
    )

    # Class average
    class_avg = marks.aggregate(avg=Avg('score'))['avg']

    # Top student
    top_student = students.annotate(avg_score=Avg('mark__score')).order_by('-avg_score').first()

    # Student averages (Chart 1)
    student_data = []

    for student in students:
        avg = Mark.objects.filter(student=student).aggregate(avg=Avg('score'))['avg']

        student_data.append({
            'name': student.name,
            'avg': float(avg or 0)
        })

        student_names = [s['name'] for s in student_data]
        student_averages = [s['avg'] for s in student_data]

    student_data.sort(key=lambda x: x['avg'], reverse=True)
    student_data = student_data[:10]

    student_names = json.dumps(student_names)
    student_averages = json.dumps(student_averages)

    # Subject averages (Chart 2)
    subject_data = marks.values('subject__name').annotate(avg_score=Avg('score'))

    subject_names = []
    subject_averages = []

    for item in subject_data:
        subject_names.append(item['subject__name'])
        subject_averages.append(float(item['avg_score'] or 0))

    subject_names = json.dumps(subject_names)
    subject_averages = json.dumps(subject_averages)

    context = {
        'student_names': json.dumps(student_names),
        'student_averages': json.dumps(student_averages),
        'subject_names': json.dumps(subject_names),
        'subject_averages': json.dumps(subject_averages),
    }

    return render(request, 'users/class_detail.html', {
        'classroom': classroom,
        'classes': classes,
        'students': students,
        'class_avg': class_avg,
        'top_student': top_student,
        
        # Charts
        'student_names': student_names,
        'student_averages': student_averages,
        'subject_names': subject_names,
        'subject_averages': subject_averages,
    })

def class_report_pdf(request, id):
    # Get school safely
    school = get_user_school(request)

    classroom = get_object_or_404(
        Classroom,
        id=id,
        school=school
    )

    students = Student.objects.filter(classroom=classroom)

    response = HttpResponse(content_type='application/pdf')
    response['Content-disposition'] = (f'attachment; filename="{classroom.name}_report.pdf"')

    # Bettere page sizing and margins
    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topmargin=40,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    elements = []

    # Main title
    title = Paragraph(f"<font size=20><b>Learnlytics Class Report</b></font>", styles['Title'])

    elements.append(title)
    elements.append(Spacer(1, 20))

    # Class name
    class_name = Paragraph(f"<font size=14><b>Class:</b> {classroom.name}</font>", styles['Normal'])

    elements.append(class_name)
    elements.append(Spacer(1, 20))

    # Table data
    table_data = [
        ["Student Name", "Average"]
    ]

    for student in students:
        avg = Mark.objects.filter(student=student).aggregate(avg=Avg('score'))['avg']
        avg_display = round(avg, 2) if avg else 0

        table_data.append([
            student.name,
            str(avg_display)
        ])
    
    # Wider clearner table
    table = Table(
        table_data,
        colWidths=[300, 120]
    )

    # Beautiful styling
    table.setStyle(TableStyle([

        # Header background
        ('BACKGROUNG', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),

        #Header text color
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        # Font sizes
        ('FONTSIZE', (0, 0), (-1, -1), 11),

        # Header font
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        # Body font
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),

        # Padding
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        ('TOPPADDING', (0, 0), (-1, -1), 8),

        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),

        # Alternate row colors
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    elements.append(table)

    # Build PDF
    doc.build(elements)

    return response

def student_report_pdf(request, id):
    school = get_user_school(request)
    student = get_object_or_404(
        Student,
        id=id,
        classroom__school=school
    )

    marks = Mark.objects.filter(student=student)

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = (f'attachment; filename="{student.name}_report.pdf"')

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    elements = []

    # Title
    title = Paragraph(f"<font size=20><b>Student Report</b></font>", styles['Title'])

    elements.append(title)
    elements.append(Spacer(1, 20))

    # Student Info
    info = Paragraph(f"<b>Name:</b> {student.name}<br/>"
                     f"<b>Class:</b> {student.classroom.name}", styles['Normal'])
    
    elements.append(info)
    elements.append(Spacer(1, 20))

    # Table Data 
    table_data = [
        ["Subject", "Score"]
    ]

    for mark in marks:

        table_data.append([
            mark.subject.name,
            str(mark.score)
        ])

    # Table
    table = Table(
        table_data,
        colWidths=[250, 120]
    )

    table.setStyle(TableStyle([

        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 1, colors.grey),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),

    ]))

    elements.append(table)

    doc.build(elements)

    return response

def school_report_pdf(request):
    school = get_user_school(request)
    students = Student.objects.filter(classroom__school=school)

    response = HttpResponse(content_type='appliction/pdf')
    response['Content-Disposition'] = (f'attachment; filename"{school.name}_report.pdf"')

    doc = SimpleDocTemplate(
        response,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()

    elements = []

    # Title
    title = Paragraph(f"<font size=20><b>{school.name} Report</b></font>", styles['Title'])

    elements.append(title)
    elements.append(Spacer(1, 20))

    # Stats
    total_students = students.count()

    total_classes = Classroom.objects.filter(school=school).count()

    stats = Paragraph(f"<b>Total Students:</b>{total_students}<br/>"
                      f"<b>Total Classes:</b>{total_classes}", styles['Normal'])
    
    elements.append(stats)
    elements.append(Spacer(1, 20))

    # Table data
    table_data = [
        ["Student Name", "Class"]
    ]

    for student in students:

        table_data.append([
            student.name,
            student.classroom.name
        ])

    # Table
    table = Table(
        table_data,
        colWidths=[250, 180]
    )

    table.setStyle(TableStyle([

        ('BACKGROUNG', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),

        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),

        ('GRID', (0, 0), (-1, -1), 1, colors.grey),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

        ('BACKGROUND', (0, 1), (-1, -1), colors.beige)
    ]))

    elements.append(table)

    doc.build(elements)

    return response

@login_required
def add_classroom(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        school = get_user_school(request)
        Classroom.objects.create(
            name=name,
            school=school
        )

        return redirect('classes')
    
    return render(request, 'users/add_classroom.html')

@login_required
def add_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        school =get_user_school(request)
        Subject.objects.create(
            name=name,
            school=school
        )

        return redirect('setup_school')
    
    return render(request, 'users/add_subject.html')



    

    