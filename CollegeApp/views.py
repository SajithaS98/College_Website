from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import(
    HODSerializer,FacultySerializer,StudentSerializer,BaseUserSerializer,CourseSerializer,DepartmentSerializer,CustomUserSerializer,
    AttendanceSerializer,FacultyAttendanceSerializer,StudentAttendanceReportSerializer,FacultyAttendanceReportSerializer,SubjectSerializer,
    BatchSerializer,AssignmentSerializer
)
from .models import (HOD,Faculty,Student,Course,Department,CustomUser,Attendance,StudentAttendance,FacultyAttendance,StudentAttendanceReport,
                     FacultyAttendanceReport,Subject,Batch,Assignment
)
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.tokens import RefreshToken

from django.core.mail import send_mail
from django.conf import settings
# from ..CollegeManagementProject.settings import EMAIL_HOST_USER

import random

from rest_framework.exceptions import PermissionDenied,NotFound

import datetime
from django.utils import timezone

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import ListAPIView,get_object_or_404

from .permissions import IsAdminOrHOD,IsHOD,IsFaculty,IsHODOrFaculty,IsAdmin,CanUpdateProfile,IsStudent




# Create your views here.

        
class UserRegistrationView(APIView):
    """
    API for registering HOD, Faculty, and Student by the superadmin.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Extract role from request data
            role = request.data.get('role')
            if not role:
                return Response({"error": "Role is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Select the appropriate serializer based on the role
            if role == 'hod':
                serializer = HODSerializer(data=request.data)
            elif role == 'faculty':
                serializer = FacultySerializer(data=request.data)
            elif role == 'student':
                serializer = StudentSerializer(data=request.data)
            else:
                return Response({"error": "Invalid role provided. Valid roles are 'admin', 'hod', 'faculty', 'student'."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Validate and save data
            if serializer.is_valid():
                role_object = serializer.save()

                # Access the related CustomUser object
                user = role_object.user

                # Generate OTP
                otp = random.randint(100000, 999999)
                otp_expiry = timezone.now() + datetime.timedelta(minutes=5)

                # Update user with OTP
                user.otp = otp
                user.otp_expiry = otp_expiry
                user.save()

                # Send OTP email
                try:
                    subject = 'Registration OTP'
                    message = f'Your OTP is {otp}. It is valid for 5 minutes.'
                    recipient_email = user.email
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email], fail_silently=False)

                    # Return success response after sending OTP
                    return Response(
                        {"user_id": user.id, "otp_sent": "OTP sent successfully."},
                        status=status.HTTP_200_OK,
                    )
                except Exception as email_error:
                    return Response(
                        {"error": f"Failed to send OTP email: {str(email_error)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')

            if not email:
                return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the user by email
            User = get_user_model()
            user = User.objects.filter(email=email).first()

            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check if the existing OTP is still valid
            if user.otp_expiry and timezone.now() < user.otp_expiry:
                return Response(
                    {"error": "Current OTP is still valid. Please use the existing OTP."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generate a new OTP
            otp = random.randint(100000, 999999)
            otp_expiry = timezone.now() + datetime.timedelta(minutes=5)

            # Update the OTP and expiry in the user model
            user.otp = otp
            user.otp_expiry = otp_expiry
            user.save()

            # Send the OTP via email
            try:
                subject = 'REGISTRATION OTP'
                message = f'Your new OTP is {otp}. Use this to complete your registration.'
                send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
            except Exception as e:
                return Response(
                    {"error": f"Failed to send OTP email: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"status": 1, "message": "OTP sent successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": 0, "message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


        
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Extract email and OTP from the request
            email = request.data.get('email')
            otp = request.data.get('otp')

            if not email or not otp:
                return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the user by email
            User = get_user_model()
            user = User.objects.filter(email=email).first()

            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check if OTP has expired
            if user.otp_expiry and timezone.now() > user.otp_expiry:
                return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

            # Verify OTP
            if user.otp == int(otp):
                user.verified = True  # Mark the user as verified
                user.otp = None       # Clear the OTP after successful verification
                user.otp_expiry = None
                user.save()
                return Response({"message": "Verification successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Extract email and password from the request
            email = request.data.get('email')
            password = request.data.get('password')

            # Check if email and password are provided
            if not email or not password:
                return Response(
                    {'error': 'Email and password are required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Authenticate the user
            user = authenticate(email=email, password=password)

            # If user is authenticated, generate tokens
            if user:
                # Generate tokens
                refresh = RefreshToken.for_user(user)

                # Common user data
                response_data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'email': user.email,
                    'role': user.role,
                    'id': user.id,
                    'full_name': user.full_name,
                    'phone': user.phone,
                    'dob': user.dob,
                    'gender': user.gender,
                    # 'photo':user.photo
                }

                # Add role-specific data
                if user.role == 'Faculty' or user.role == 'HOD':
                    response_data['department'] = user.department.name if user.department else None

                if user.role == 'Student':
                    response_data['department'] = user.department.name if user.department else None
                    response_data['course'] = user.course.name if user.course else None
                    response_data['batch'] = user.batch.name if user.batch else None

                return Response(response_data, status=status.HTTP_200_OK)

            # If authentication fails, return an error response
            return Response(
                {'error': 'Invalid credentials. Please try again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        except Exception as e:
            # Handle unexpected exceptions
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HODListCreateView(APIView):
    permission_classes = [IsAdmin] 

    def get(self, request):
        # List all faculties
        hodies = HOD.objects.all()
        serializer = HODSerializer(hodies, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Add a new faculty member
        serializer = HODSerializer(data=request.data)
        if serializer.is_valid():
            hod = serializer.save()
            return Response(HODSerializer(hod).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class HODUpdateDeleteView(APIView):
    permission_classes = [IsAdmin]  # Only allow HOD to access this view

    def get_object(self, pk):
        try:
            return HOD.objects.get(pk=pk)
        except HOD.DoesNotExist:
            return None

    def put(self, request, pk):
        # Update faculty details
        hod = self.get_object(pk)
        if hod is None:
            return Response({"error": "HOD not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = HODSerializer(hod, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Delete faculty record
        hod = self.get_object(pk)
        if hod is None:
            return Response({"error": "HOD not found."}, status=status.HTTP_404_NOT_FOUND)

        hod.delete()
        return Response({"message": "HOD deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



class FacultyListCreateView(APIView):
    permission_classes = [IsAdmin | IsHOD]  # Only allow HOD to access this view

    def get(self, request):
        # List all faculties
        faculties = Faculty.objects.all()
        serializer = FacultySerializer(faculties, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Add a new faculty member
        serializer = FacultySerializer(data=request.data)
        if serializer.is_valid():
            faculty = serializer.save()
            return Response(FacultySerializer(faculty).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacultyUpdateDeleteView(APIView):
    permission_classes = [IsAdmin | IsHOD]  # Only allow HOD to access this view

    def get_object(self, pk):
        try:
            return Faculty.objects.get(pk=pk)
        except Faculty.DoesNotExist:
            return None

    def put(self, request, pk):
        # Update faculty details
        faculty = self.get_object(pk)
        if faculty is None:
            return Response({"error": "Faculty not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FacultySerializer(faculty, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Delete faculty record
        faculty = self.get_object(pk)
        if faculty is None:
            return Response({"error": "Faculty not found."}, status=status.HTTP_404_NOT_FOUND)

        faculty.delete()
        return Response({"message": "Faculty deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        

class StudentListCreateView(APIView):
    # Allow both HOD and Faculty to access this view
    permission_classes = [IsAdmin | IsHOD | IsFaculty]  # HOD or Faculty can access

    def get(self, request):
        # List all students
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Add a new student
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            student = serializer.save()
            return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentUpdateDeleteView(APIView):
    # Allow both HOD and Faculty to access this view
    permission_classes = [IsAdmin | IsHOD | IsFaculty]  # HOD or Faculty can access

    def get_object(self, pk):
        try:
            return Student.objects.get(pk=pk)
        except Student.DoesNotExist:
            return None

    def put(self, request, pk):
        # Update student details
        student = self.get_object(pk)
        if student is None:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Delete student record
        student = self.get_object(pk)
        if student is None:
            return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)

        student.delete()
        return Response({"message": "Student deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    

class CourseListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            courses = Course.objects.all()

            if not courses:
                raise NotFound("No courses found.")

            serializer = CourseSerializer(courses, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            return Response(
                {"detail": "Courses not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        

class DepartmentListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        try:
            departments = Department.objects.all()

            if not departments:
                raise NotFound("No departments found.")

            serializer = DepartmentSerializer(departments, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Department.DoesNotExist:
            return Response(
                {"detail": "Departments not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        


class DepartmentView(APIView):
    permission_classes = [IsAdmin | IsHOD]

    def get(self, request, pk=None):
        """
        Retrieve a single department or list all departments.
        """
        try:
            if pk:
                department = Department.objects.get(pk=pk)
                serializer = DepartmentSerializer(department)
            else:
                departments = Department.objects.all()
                serializer = DepartmentSerializer(departments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Create a new department.
        """
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """
        Update an existing department.
        """
        try:
            department = Department.objects.get(pk=pk)
            serializer = DepartmentSerializer(department, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Department.DoesNotExist:
            return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        """
        Delete a department.
        """
        try:
            department = Department.objects.get(pk=pk)
            department.delete()
            return Response({"detail": "Department deleted successfully."}, status=status.HTTP_200_OK)
        except Department.DoesNotExist:
            return Response({"detail": "Department not found."}, status=status.HTTP_404_NOT_FOUND)
        


class ProfileView(APIView):
    permission_classes = [CanUpdateProfile]  # Use the custom permission class for update

    def get(self, request, pk=None):
        try:
            # Allow users to view their own profile
            if request.user.role == 'student':
                if pk != str(request.user.pk):
                    return Response({"detail": "Students can only view their own profiles."}, status=status.HTTP_403_FORBIDDEN)

            # Admin and HOD can view any profile, others can only view their own
            user = CustomUser.objects.get(pk=pk) if pk else request.user
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk=None):
        try:
            user = CustomUser.objects.get(pk=pk)

            # Block users from updating their own profiles
            if request.user == user:
                return Response({"detail": "You cannot update your own profile."}, status=status.HTTP_403_FORBIDDEN)

            # Admin, HOD, and Faculty can update profiles based on role restrictions
            if request.user.is_admin or (request.user.role == 'hod' and user.role in ['faculty', 'hod']) or (request.user.role == 'faculty' and user.role in ['faculty', 'student']):
                serializer = CustomUserSerializer(user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({"detail": "You do not have permission to update this profile."}, status=status.HTTP_403_FORBIDDEN)

        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
    

class FacultyAttendanceView(APIView):
    permission_classes = [IsHOD]  # Restrict to HOD users

    def post(self, request):
        serializer = FacultyAttendanceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        try:
            faculty_attendance = FacultyAttendance.objects.all()
            serializer = FacultyAttendanceSerializer(faculty_attendance, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            attendance = FacultyAttendance.objects.get(pk=pk)
        except FacultyAttendance.DoesNotExist:
            return Response({"error": "Faculty attendance record not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FacultyAttendanceSerializer(
            attendance, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class StudentAttendanceView(APIView):
    permission_classes = [IsHOD | IsFaculty]  # Restrict to HOD and Faculty

    def post(self, request):
        serializer = AttendanceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        if request.user.role == 'hod':
            attendance = Attendance.objects.all()
        else:
            attendance = Attendance.objects.filter(created_by=request.user)
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            attendance = Attendance.objects.get(pk=pk)
        except Attendance.DoesNotExist:
            return Response({"error": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AttendanceSerializer(attendance, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FacultyAttendanceReportView(APIView):
    permission_classes = [IsHOD | IsFaculty]  # You can use a specific permission class here

    def get(self, request):
        reports = FacultyAttendanceReport.objects.all()
        serializer = FacultyAttendanceReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FacultyAttendanceReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
    

class StudentAttendanceReportView(APIView):
    permission_classes = [IsHOD | IsFaculty]  # You can use a specific permission class here

    def get(self, request):
        reports = StudentAttendanceReport.objects.all()
        serializer = StudentAttendanceReportSerializer(reports, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StudentAttendanceReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class SubjectsListView(APIView):
    permission_classes = [IsHOD]

    def get(self, request, *args, **kwargs):
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubjectsDetailView(APIView):
    permission_classes = [IsHOD]

    def get_object(self, pk):
        try:
            return Subject.objects.get(pk=pk)
        except Subject.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        subject = self.get_object(pk)
        if subject is None:
            return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubjectSerializer(subject)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        subject = self.get_object(pk)
        if subject is None:
            return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubjectSerializer(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        subject = self.get_object(pk)
        if subject is None:
            return Response({"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)
        subject.delete()
        return Response({"message": "Subject deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



class BatchListView(APIView):
    permission_classes = [IsHOD]

    def get(self, request, *args, **kwargs):
        batches = Batch.objects.all()
        serializer = BatchSerializer(batches, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = BatchSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BatchDetailView(APIView):
    permission_classes = [IsHOD]

    def get(self, request, pk, *args, **kwargs):
        try:
            batch = Batch.objects.get(pk=pk)
        except Batch.DoesNotExist:
            return Response({"error": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BatchSerializer(batch)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        try:
            batch = Batch.objects.get(pk=pk)
        except Batch.DoesNotExist:
            return Response({"error": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BatchSerializer(batch, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            batch = Batch.objects.get(pk=pk)
        except Batch.DoesNotExist:
            return Response({"error": "Batch not found."}, status=status.HTTP_404_NOT_FOUND)

        batch.delete()
        return Response({"message": "Batch deleted successfully."}, status=status.HTTP_204_NO_CONTENT)



class AssignmentListView(APIView):
    permission_classes = [IsFaculty | IsHOD]  
    def get(self, request, *args, **kwargs):
        assignments = Assignment.objects.all()  
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignmentDetailView(APIView):
    permission_classes = [IsFaculty | IsHOD]

    def get(self, request, pk, *args, **kwargs):
        try:
            assignment = Assignment.objects.get(pk=pk)
        except Assignment.DoesNotExist:
            return Response({"error": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AssignmentSerializer(assignment)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        try:
            assignment = Assignment.objects.get(pk=pk)
        except Assignment.DoesNotExist:
            return Response({"error": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentSerializer(assignment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        try:
            assignment = Assignment.objects.get(pk=pk)
        except Assignment.DoesNotExist:
            return Response({"error": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        assignment.delete()
        return Response({"message": "Assignment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class StudentAssignmentListView(APIView):
    permission_classes = [IsStudent]

    def get(self, request, batch_id, *args, **kwargs):
        assignments = Assignment.objects.filter(batch_id=batch_id)
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data)




class HODDashboardView(APIView):
    permission_classes = [IsHOD]  # Ensure only HOD can access this view

    def get(self, request):
        # Get the HOD's department
        hod = request.user
        department = hod.department  # Assuming HOD has a department field

        # Get subjects, faculties, and students in the HOD's department
        subjects = Subject.objects.filter(department=department)
        faculties = Faculty.objects.filter(department=department)
        students = Student.objects.filter(department=department)

        # Serialize the data
        subject_serializer = SubjectSerializer(subjects, many=True)
        faculty_serializer = FacultySerializer(faculties, many=True)
        student_serializer = StudentSerializer(students, many=True)

        # Return the response
        return Response({
            "subjects": subject_serializer.data,
            "faculties": faculty_serializer.data,
            "students": student_serializer.data,
        }, status=status.HTTP_200_OK)


        
