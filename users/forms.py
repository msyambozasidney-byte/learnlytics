from django import forms
from .models import Student
from .models import Mark
from .models import Classroom, Student, Subject
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    school_name = forms.CharField(max_length=200)

    class Meta:

        model = User

        fields = (
            'username',
            'email',
            'school_name',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control rounded-3 py-2',
            'placeholder': 'Enter username'
        })

        self.fields['email'].widget.attrs.update({
            'class': 'form-control rounded-3 py-2',
            'placeholder': 'Enter email'
        })

        self.fields['school_name'].widget.attrs.update({
            'class': 'form-control rounded-3 py-2',
            'placeholder': 'Enter school name'
        })

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control rounded-3 py-2',
            'placeholder': 'Enter password'
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control rounded-3 py-2',
            'placeholder': 'Confirm password'
        })

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

def __ini__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for field in self.fields.values():
        field.widget.attrs.update({
            'class': 'form-control rounded-3 py-2'
        })

