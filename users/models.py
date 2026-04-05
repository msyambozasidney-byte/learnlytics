from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return self.name

class Classroom(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

class Student(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE )
    name = models.CharField(max_length=250)
    school = models. ForeignKey('school', on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class Mark(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    score = models.IntegerField()
