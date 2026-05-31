from django.contrib import admin
from .models import Classroom, Student, Subject, Mark
from .models import School, UserProfile
from .models import Teacher

admin.site.register(Classroom)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Mark)
admin.site.register(School)
admin.site.register(UserProfile)
admin.site.register(Teacher)

list_display = ('name')