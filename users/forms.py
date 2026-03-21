from django import forms
from .models import Student
from .models import Mark
from .models import Classroom, Student, Subject

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name']

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'classroom']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'classroom']

class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['student', 'subject', 'marks','grade', 'status']

