from django.contrib import admin
from .models import (Course,Batch,Student,HOD,Faculty,CustomUser,Department,Attendance,Subject,FacultyAttendance,StudentAttendance,
                     FacultyAttendanceReport,StudentAttendanceReport,Assignment,Submission
)
    
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.








admin.site.register(Course)
admin.site.register(Batch)
admin.site.register(Student)
admin.site.register(HOD)
admin.site.register(Department)
admin.site.register(Faculty)
admin.site.register(Attendance)
admin.site.register(FacultyAttendance)
admin.site.register(StudentAttendance)
admin.site.register(StudentAttendanceReport)
admin.site.register(FacultyAttendanceReport)
admin.site.register(Subject)
admin.site.register(Assignment)

admin.site.register(CustomUser)
