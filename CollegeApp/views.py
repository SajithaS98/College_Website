from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import(
    HODSerializer,FacultySerializer,StudentSerializer,BaseUserSerializer,CourseSerializer,DepartmentSerializer,CustomUserSerializer
)
from .models import HOD,Faculty,Student,Course,Department,CustomUser
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
from rest_framework.generics import ListAPIView

from .permissions import IsAdminOrHOD,IsAdminOrSelf,IsHOD,IsFaculty




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


class HODListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            hods = HOD.objects.select_related('user', 'department').prefetch_related('courses', 'batches').all()
            serializer = HODSerializer(hods, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FacultyListCreateView(APIView):
    permission_classes = [IsHOD]  # Only allow HOD to access this view

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
    permission_classes = [IsHOD]  # Only allow HOD to access this view

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
        

class StudentListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            students = Student.objects.all()
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class StudentListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            students = Student.objects.all()
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CourseListView(APIView):
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
    permission_classes = [IsAdminOrHOD]

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
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get(self, request, pk=None):
        try:
            user = (
                CustomUser.objects.get(pk=pk) if pk else request.user
            )  # Admin/HOD can view by `pk`, others see their own profile
            serializer = CustomUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk=None):
        try:
            user = (
                CustomUser.objects.get(pk=pk) if pk else request.user
            )  # Admin/HOD can edit by `pk`, others edit their own profile

            serializer = CustomUserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)






    



        
