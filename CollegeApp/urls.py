from django.urls import path
from .views import (
    UserRegistrationView,UserLoginView,ProfileView,VerifyOTPView,ResendOTPView,HODListView,FacultyListCreateView,FacultyUpdateDeleteView,
    StudentListView,CourseListView,DepartmentListView,DepartmentView,StudentAttendanceView,FacultyAttendanceView,StudentAttendanceReportView,
    FacultyAttendanceReportView
    
)
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('resend_otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile-detail'),

    path('list-hods/', HODListView.as_view(), name='list-hods'),
    path('falist/', FacultyListCreateView.as_view(), name='falist'),
    path('falist/<int:pk>/', FacultyUpdateDeleteView.as_view(), name='faculty-update-delete'),
    path('stlist/', StudentListView.as_view(), name='stlist'),
    path('courses-list/', CourseListView.as_view(), name='course-list'),
    
    path('departments-list/', DepartmentListView.as_view(), name='department-list'),
    path('departments/', DepartmentView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentView.as_view(), name='department-detail'),

    path('student_attendance/', StudentAttendanceView.as_view(), name='student-attendance-list-create'),
    path('student_attendance/<int:pk>/', StudentAttendanceView.as_view(), name='student-attendance-detail'),

    path('faculty-attendance-reports/', FacultyAttendanceReportView.as_view(), name='faculty-attendance-report-list'),
    path('student-attendance-reports/', StudentAttendanceReportView.as_view(), name='student-attendance-report-list'),

    path('faculty-attendance/', FacultyAttendanceView.as_view(), name='faculty-attendance-list-create'),
    path('faculty-attendance/<int:pk>/', FacultyAttendanceView.as_view(), name='faculty-attendance-detail-update'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
