from django.urls import path
from .views import (
<<<<<<< HEAD
    UserRegistrationView,UserLoginView,ProfileView,VerifyOTPView,ResendOTPView,HODListView,FacultyListCreateView,FacultyUpdateDeleteView,
    StudentListView,CourseListView,DepartmentListView,DepartmentView
=======
    UserRegistrationView,UserLoginView,UserProfileView,UserDeleteView,VerifyOTPView,ResendOTPView,HODListView,FacultyListView,StudentListView
>>>>>>> master
    
)
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('resend_otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile-detail'),

    path('list-hods/', HODListView.as_view(), name='list-hods'),
<<<<<<< HEAD
    path('falist/', FacultyListCreateView.as_view(), name='falist'),
    path('falist/<int:pk>/', FacultyUpdateDeleteView.as_view(), name='faculty-update-delete'),
    path('stlist/', StudentListView.as_view(), name='stlist'),
    path('courses-list/', CourseListView.as_view(), name='course-list'),
    
    path('departments-list/', DepartmentListView.as_view(), name='department-list'),
    path('departments/', DepartmentView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentView.as_view(), name='department-detail'),
=======
    path('falist/', FacultyListView.as_view(), name='falist'),
    path('stlist/', StudentListView.as_view(), name='stlist'),
>>>>>>> master

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
