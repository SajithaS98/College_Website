from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.utils import timezone

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user
    

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)

        return self.create_user(email, password, **extra_fields)
    


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=150,null=True,blank=True)  
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models. DateTimeField(auto_now_add=True,null=True)

    

    # def __str__(self):
    #     return self.course_name

    

class Department(models.Model):
    id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=150,null=True,blank=True) 
    description = models.TextField(blank=True, null=True)
    courses = models.ManyToManyField(Course,blank=True)
    photo = models.ImageField(upload_to="department_photos/", blank=True, null=True)
    hod = models.OneToOneField('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='department_hod')




    # def __str__(self):
    #     return self.department_name



class Batch(models.Model):
    batch_name = models.CharField(max_length=150,null=True,blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_date = models.IntegerField(blank=True, null=True)
    end_date = models.IntegerField(blank=True, null=True)

    # def __str__(self):
    #     return self.batch_name


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin','Admin'),
        ('hod','HOD'),
        ('faculty','Faculty'),
        ('student','Student'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.IntegerField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True,related_name='department_users')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(null=True, blank=True, default=False)
    otp = models.PositiveIntegerField(null=True, blank=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    # def __str__(self):
    #     return self.email

    def save(self, *args, **kwargs):
        # Ensure fields are reset for roles that don't need them
        if self.role not in ['hod', 'faculty', 'student']:
            self.department = None
        if self.role != 'student':
            self.course = None
            self.batch = None
        super().save(*args, **kwargs)


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    course = models.ForeignKey(Course, on_delete=models.CASCADE,related_name="primary_subjects")
    department = models.ForeignKey(Department, on_delete=models.CASCADE,null=True)
    Course_id= models.ForeignKey(Course,on_delete=models.CASCADE,related_name="secondary_subjects",null=True)
    staff_id = models.ForeignKey('Faculty',on_delete=models.CASCADE,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Faculty(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True,blank=True)
    address = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models. DateTimeField(auto_now_add=True,null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course,blank=True)
    batches = models.ManyToManyField(Batch,blank=True)
    photo = models.ImageField(upload_to='faculty_photos/', blank=True, null=True)
    subjects = models.ManyToManyField(Subject, related_name='faculties')


    # def __str__(self):
    #     return self.name 

class HOD(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True,blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,related_name='hod_department')
    courses = models.ManyToManyField(Course,blank=True)
    batches = models.ManyToManyField(Batch,blank=True)
    photo = models.ImageField(upload_to='hod_photos/', blank=True, null=True)
    faculty = models.ForeignKey(Faculty,on_delete=models.CASCADE,null=True)
    address = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models. DateTimeField(auto_now_add=True,null=True)



class Student(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True,blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch,on_delete=models.CASCADE,null=True)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)
    address = models.TextField(null=True)

class Assignment(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    description =models.TextField(max_length=300,null=True,blank=True)
    faculty = models.ForeignKey(Faculty,on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    deadline = models.DateTimeField(null=True,blank=True)

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment,on_delete=models.CASCADE)
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/',null=True,blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    message = models.TextField(max_length=300,null=True,blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    students = models.ManyToManyField(Student,blank=True)

class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2,null=True,blank=True)

class Note(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    file = models.FileField(upload_to='notes/',null=True,blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


class FacultyAttendance(models.Model):
    faculty = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    attendance_date = models.DateField()
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="recorded_faculty_attendance")

class Attendance(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.DO_NOTHING,null=True)
    subject = models.ForeignKey(Subject, on_delete=models.DO_NOTHING,null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_attendance",null=True)  # HOD or Faculty

class StudentAttendance(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='student_attendance')
    student = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, limit_choices_to={'role': 'student'})
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

class FacultyAttendanceReport(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StudentAttendanceReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    

