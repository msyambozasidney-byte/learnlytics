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
        fields = ['name']

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name']

SUBJECT_CHOICES = [
    ('Math', 'Math'),
    ('Science', 'Science'),
    ('English', 'English'),
]

class MarkForm(forms.ModelForm):
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)

    class Meta:
        model = Mark
        fields = ['student', 'subject', 'score']

