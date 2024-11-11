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

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin','Admin'),
        ('hod','HOD'),
        ('faculty','Faculty'),
        ('student','Student'),
    ]


    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10,choices = ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['role']

    # def __str__(self):
    #     return self.email

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

class Course(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    description = models.TextField(max_length=300,null=True,blank=True)

class Batch(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

class HOD(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    faculty = models.ManyToManyField(Course)
    photo = models.ImageField(upload_to='hod_photos/', blank=True, null=True)

class Faculty(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    courses = models.ForeignKey(Course,on_delete=models.CASCADE)
    batches = models.ManyToManyField(Batch)
    photo = models.ImageField(upload_to='faculty_photos/', blank=True, null=True)

class Student(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch,on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)

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
    students = models.ManyToManyField(Student)

class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)

class Note(models.Model):
    title = models.CharField(max_length=100,null=True,blank=True)
    file = models.FileField(upload_to='notes/',null=True,blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)


    
