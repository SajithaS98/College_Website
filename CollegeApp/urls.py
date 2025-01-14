from django.urls import path
from .views import (
    UserRegistrationView,UserLoginView,ProfileView,VerifyOTPView,ResendOTPView,FacultyListCreateView,FacultyUpdateDeleteView,
    StudentListCreateView,StudentUpdateDeleteView,CourseListView,DepartmentListView,DepartmentView,StudentAttendanceView,FacultyAttendanceView,
    StudentAttendanceReportView,FacultyAttendanceReportView,HODListCreateView,HODUpdateDeleteView,HODDashboardView,SubjectsListView,SubjectsDetailView,
    BatchListView,BatchDetailView,AssignmentListView,AssignmentDetailView,StudentAssignmentListView,SubmissionListCreateView,SubmissionDeleteView 
)
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('resend_otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('verify_otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', UserLoginView.as_view(), name='user-login'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('profile/<int:pk>/', ProfileView.as_view(), name='profile-detail'),

    path('hodlist/', HODListCreateView.as_view(), name='hodlist'),
    path('hodlist/<int:pk>/', HODUpdateDeleteView.as_view(), name='hod-update-delete'),

    path('falist/', FacultyListCreateView.as_view(), name='falist'),
    path('falist/<int:pk>/', FacultyUpdateDeleteView.as_view(), name='faculty-update-delete'),

    path('stlist/', StudentListCreateView.as_view(), name='stlist'),
    path('stlist/<int:pk>/', StudentUpdateDeleteView.as_view(), name='student-update-delete'),

    path('courses-list/', CourseListView.as_view(), name='course-list'),
    
    path('departments-list/', DepartmentListView.as_view(), name='department-list'),
    path('departments/', DepartmentView.as_view(), name='department-list-create'),
    path('departments/<int:pk>/', DepartmentView.as_view(), name='department-detail'),

    path('student_attendance/', StudentAttendanceView.as_view(), name='student-attendance-list-create'),
    path('student_attendance/<int:pk>/', StudentAttendanceView.as_view(), name='student-attendance-detail'),

    path('faculty-attendance/', FacultyAttendanceView.as_view(), name='faculty-attendance-list-create'),
    path('faculty-attendance/<int:pk>/', FacultyAttendanceView.as_view(), name='faculty-attendance-detail-update'),

    path('faculty-attendance-reports/', FacultyAttendanceReportView.as_view(), name='faculty-attendance-report-list'),
    path('student-attendance-reports/', StudentAttendanceReportView.as_view(), name='student-attendance-report-list'),

    path('subjects/', SubjectsListView.as_view(), name='subjects-list'),
    path('subjects/<int:pk>/', SubjectsDetailView.as_view(), name='subjects-detail'),

    path('batches/', BatchListView.as_view(), name='batch-list'),
    path('batches/<int:pk>/', BatchDetailView.as_view(), name='batch-detail'),

    path('assignments/', AssignmentListView.as_view(), name='assignment-list'),  # HOD and Faculty can access this
    path('assignments/<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),  # HOD and Faculty can access this
    path('student/assignments/<int:batch_id>/', StudentAssignmentListView.as_view(), name='student-assignment-list'),

    path('assignments/<int:assignment_id>/submissions/', SubmissionListCreateView.as_view(), name='submission-list-create'),
    path('assignments/<int:assignment_id>/submissions/<int:submission_id>/', SubmissionDeleteView.as_view(), name='submission-delete'),

    path('hod-dashboard/', HODDashboardView.as_view(), name='hod-dashboard'),

]
