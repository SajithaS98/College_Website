from django.contrib import admin
from .models import Course,Batch,Student,HOD,Faculty,CustomUser,Department

# Register your models here.

admin.site.register(Course)
admin.site.register(Batch)
admin.site.register(Student)
admin.site.register(HOD)
admin.site.register(Department)
admin.site.register(Faculty)
admin.site.register(CustomUser)
