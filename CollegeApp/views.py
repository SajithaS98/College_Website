from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import(
    UserProfileSerializer,HODSerializer,
    FacultySerializer,StudentSerializer
)
from .models import HOD,Faculty,Student
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
                return Response({"error": "Invalid role provided. Valid roles are 'hod', 'faculty', 'student'."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Validate and save data
            if serializer.is_valid():
                user = serializer.save()

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
                        {"message": f"{role.capitalize()} registered successfully.", "user_id": user.id, "otp_sent": "OTP sent successfully."},
                        status=status.HTTP_201_CREATED,
                    )
                except Exception as email_error:
                    return Response(
                        {"error": f"Failed to send OTP email: {str(email_error)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'email': user.email,
                        'role':user.role,
                        'id':user.id
                    },
                    status=status.HTTP_200_OK
                )

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



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, user):
        """Helper function to get the user's profile based on their role."""
        try:
            if user.role == 'hod':
                return HOD.objects.get(user=user), HODSerializer
            elif user.role == 'faculty':
                return Faculty.objects.get(user=user), FacultySerializer
            elif user.role == 'student':
                return Student.objects.get(user=user), StudentSerializer
            else:
                return user, UserProfileSerializer
        except (HOD.DoesNotExist, Faculty.DoesNotExist, Student.DoesNotExist):
            raise NotFound("Profile not found for the user.")

    def get(self, request):
        try:
            user = request.user
            profile, serializer_class = self.get_profile(user)
            serializer = serializer_class(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



    

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            user = request.user
            # Perform user deletion
            user.delete()
            return Response(
                {'message': 'User deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return Response(
                {'error': f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        



    



