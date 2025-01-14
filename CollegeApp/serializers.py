from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (CustomUser,HOD,Faculty,Student,Course,Batch,Department,Attendance,StudentAttendance,FacultyAttendance,FacultyAttendanceReport,
                     StudentAttendanceReport,Subject,Assignment,Submission,Notification,ExamResult,Note
)
from rest_framework.exceptions import ValidationError




CustomUser = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email","password","role","full_name","phone","dob","gender",]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class HODSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    password = serializers.CharField(source="user.password", write_only=True)
    role = serializers.CharField(source="user.role", read_only=True, default="faculty")
    full_name = serializers.CharField(source="user.full_name")
    phone = serializers.CharField(source="user.phone")
    dob = serializers.DateField(source="user.dob")
    gender = serializers.CharField(source="user.gender")
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    photo = serializers.ImageField(required=False)

    class Meta:
        model = HOD
        fields = ["id", "email", "password", "full_name", "phone", "dob", "gender", "department","photo", "role"]

    def create(self, validated_data):
        # Extract user data
        user_data = validated_data.pop("user")
        department = validated_data.pop("department")

        # Check if the email already exists
        if CustomUser.objects.filter(email=user_data["email"]).exists():
            raise ValidationError({"email": "This email is already registered."})

        # Create user instance
        user = CustomUser.objects.create_user(**user_data)
        user.role = "hod"
        user.save()

        # Create faculty instance
        hod = HOD.objects.create(user=user, department=department, **validated_data)
        return hod

    def update(self, instance, validated_data):
        # Handle user data
        user_data = validated_data.pop('user', {})
        user_instance = instance.user

        # Check if the email is being updated and if it already exists in another user
        if 'email' in user_data and user_data['email'] != user_instance.email:
            if CustomUser.objects.filter(email=user_data['email']).exists():
                raise ValidationError({"email": "This email is already registered."})

        # Update the user fields
        for attr, value in user_data.items():
            setattr(user_instance, attr, value)

        if 'password' in user_data:
            user_instance.set_password(user_data['password'])  # Ensure password is hashed

        user_instance.save()

        # Update hod fields
        if 'department' in validated_data:
            instance.department = validated_data['department']
        if 'hod' in validated_data:
            instance.hod = validated_data['hod']
        if 'courses' in validated_data:
            instance.courses.set(validated_data['courses'])
        if 'batches' in validated_data:
            instance.batches.set(validated_data['batches'])
        if 'photo' in validated_data:
            instance.photo = validated_data['photo']

        instance.save()
        return instance


class FacultySerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    password = serializers.CharField(source="user.password", write_only=True)
    role = serializers.CharField(source="user.role", read_only=True, default="faculty")
    full_name = serializers.CharField(source="user.full_name")
    phone = serializers.CharField(source="user.phone")
    dob = serializers.DateField(source="user.dob")
    gender = serializers.CharField(source="user.gender")
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Faculty
        fields = ["id", "email", "password", "full_name", "phone", "dob", "gender", "department","photo", "role"]

    def create(self, validated_data):
        # Extract user data
        user_data = validated_data.pop("user")
        department = validated_data.pop("department")

        # Check if the email already exists
        if CustomUser.objects.filter(email=user_data["email"]).exists():
            raise ValidationError({"email": "This email is already registered."})

        # Create user instance
        user = CustomUser.objects.create_user(**user_data)
        user.role = "faculty"
        user.save()

        # Create faculty instance
        faculty = Faculty.objects.create(user=user, department=department, **validated_data)
        return faculty

    def update(self, instance, validated_data):
        # Handle user data
        user_data = validated_data.pop('user', {})
        user_instance = instance.user

        # Check if the email is being updated and if it already exists in another user
        if 'email' in user_data and user_data['email'] != user_instance.email:
            if CustomUser.objects.filter(email=user_data['email']).exists():
                raise ValidationError({"email": "This email is already registered."})

        # Update the user fields
        for attr, value in user_data.items():
            setattr(user_instance, attr, value)

        if 'password' in user_data:
            user_instance.set_password(user_data['password'])  # Ensure password is hashed

        user_instance.save()

        # Update faculty fields
        if 'department' in validated_data:
            instance.department = validated_data['department']
        if 'hod' in validated_data:
            instance.hod = validated_data['hod']
        if 'courses' in validated_data:
            instance.courses.set(validated_data['courses'])
        if 'batches' in validated_data:
            instance.batches.set(validated_data['batches'])
        if 'photo' in validated_data:
            instance.photo = validated_data['photo']

        instance.save()
        return instance
    

class StudentSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    password = serializers.CharField(source="user.password", write_only=True)
    role = serializers.CharField(source="user.role", read_only=True, default="student")
    full_name = serializers.CharField(source="user.full_name")
    phone = serializers.CharField(source="user.phone")
    dob = serializers.DateField(source="user.dob")
    gender = serializers.CharField(source="user.gender")
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    batch = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all(), required=False)
    
    class Meta:
        model = Student
        fields = ["email", "password", "full_name", "phone", "dob", "gender", "department", "course", "batch", "role"]

    def create(self, validated_data):
        user_data = validated_data.pop("user")
        department = validated_data.pop("department")
        course = validated_data.pop("course")
        batch = validated_data.pop("batch", None)

        # Check if the email already exists
        if CustomUser.objects.filter(email=user_data["email"]).exists():
            raise ValidationError({"email": "This email is already registered."})

        # Create user instance
        user = CustomUser.objects.create_user(**user_data)
        user.role = "student"
        user.save()

        # Create student instance
        student = Student.objects.create(user=user, department=department, course=course, batch=batch, **validated_data)
        return student

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        user_instance = instance.user

        # Handle email uniqueness check
        if 'email' in user_data and user_data['email'] != user_instance.email:
            if CustomUser.objects.filter(email=user_data['email']).exists():
                raise ValidationError({"email": "This email is already registered."})

        # Update the user fields
        for attr, value in user_data.items():
            setattr(user_instance, attr, value)

        if 'password' in user_data:
            user_instance.set_password(user_data['password'])  # Ensure password is hashed

        user_instance.save()

        # Update student fields
        if 'department' in validated_data:
            instance.department = validated_data['department']
        if 'course' in validated_data:
            instance.course = validated_data['course']
        if 'batch' in validated_data:
            instance.batch = validated_data['batch']
        if 'photo' in validated_data:
            instance.photo = validated_data['photo']
        if 'address' in validated_data:
            instance.address = validated_data['address']

        instance.save()
        return instance

            


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'course_name', 'description', 'created_at', 'updated_at']


class DepartmentSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Department
        fields = ['id', 'department_name', 'description', 'courses','photo']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure the photo URL is correctly included
        if instance.photo:
            data['photo'] = instance.photo.url
        return data

    

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'full_name', 'phone', 'dob', 'gender',
            'department', 'course', 'batch', 'photo', 'role'
        ]  

    def to_representation(self, instance):
        """Customize representation based on the role."""
        data = super().to_representation(instance)

        # Remove fields irrelevant to non-student roles
        if instance.role != 'student':
            data.pop('course', None)
            data.pop('batch', None)

        return data
    

class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendance
        fields = ['id', 'student', 'status']

class AttendanceSerializer(serializers.ModelSerializer):
    student_attendance = StudentAttendanceSerializer(many=True, write_only=True)
    student_attendance_read = StudentAttendanceSerializer(many=True, read_only=True, source='student_attendance')

    class Meta:
        model = Attendance
        fields = ['id', 'batch', 'subject', 'date', 'created_at', 'updated_at', 'created_by', 'student_attendance', 'student_attendance_read']
        read_only_fields = ['created_by']

    def create(self, validated_data):
        student_attendance_data = validated_data.pop('student_attendance')
        request_user = self.context['request'].user
        attendance = Attendance.objects.create(**validated_data, created_by=request_user)

        for student_data in student_attendance_data:
            StudentAttendance.objects.create(attendance=attendance, **student_data)

        return attendance

    def update(self, instance, validated_data):
        # Update the main Attendance fields
        instance.batch = validated_data.get('batch', instance.batch)
        instance.subject = validated_data.get('subject', instance.subject)
        instance.date = validated_data.get('date', instance.date)
        instance.save()

        # Update or create student attendance records
        student_attendance_data = validated_data.pop('student_attendance', [])
        if student_attendance_data:
            for student_data in student_attendance_data:
                student_id = student_data.get('student')
                status = student_data.get('status')

                # Find the student attendance record or create a new one
                student_attendance = StudentAttendance.objects.filter(
                    attendance=instance,
                    student_id=student_id
                ).first()

                # If a student attendance record exists, update the status
                if student_attendance:
                    student_attendance.status = status
                    student_attendance.save()
                else:
                    # Create a new record if one does not exist
                    StudentAttendance.objects.create(attendance=instance, student_id=student_id, status=status)

        return instance

class FacultyAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyAttendance
        fields = ['id', 'faculty', 'attendance_date', 'status', 'recorded_by']
        read_only_fields = ['recorded_by']

    def create(self, validated_data):
        request_user = self.context['request'].user  # Get the logged-in user
        validated_data['recorded_by'] = request_user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Use .get() to safely extract values from validated_data
        faculty = validated_data.get('faculty', instance.faculty)
        attendance_date = validated_data.get('attendance_date', instance.attendance_date)
        status = validated_data.get('status', instance.status)
        
        # Update fields
        instance.faculty = faculty
        instance.attendance_date = attendance_date
        instance.status = status
        
        # Save the instance
        instance.save()
        return instance
    
class FacultyAttendanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyAttendanceReport
        fields = ['id', 'faculty', 'attendance', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class StudentAttendanceReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendanceReport
        fields = ['id', 'student', 'attendance', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'batch_name', 'course', 'start_year', 'end_year']

    def validate(self, data):
        """
        Ensure that start year is before end year
        """
        if data['start_year'] > data['end_year']:
            raise serializers.ValidationError("Start year cannot be after end year.")
        return data
    

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'student', 'file', 'submitted_at']