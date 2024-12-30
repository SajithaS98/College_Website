from django.urls import path
from .views import (
    UserRegistrationView,UserLoginView,UserProfileView,UserDeleteView,VerifyOTPView,ResendOTPView,HODListView,FacultyListView,StudentListView
    
)
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('resend_otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('delete_profile/', UserDeleteView.as_view(), name='user-delete'),

    path('list-hods/', HODListView.as_view(), name='list-hods'),
    path('falist/', FacultyListView.as_view(), name='falist'),
    path('stlist/', StudentListView.as_view(), name='stlist'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
