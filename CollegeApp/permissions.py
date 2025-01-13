from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied



class IsAdmin(BasePermission):
    """
    Allows access only to users with the admin role.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin



class IsAdminOrHOD(BasePermission):
    """
    Custom permission to allow only admins and HODs.
    """
    def has_permission(self, request, view):
        # Allow access if the user is authenticated and is either admin or HOD
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.role == 'hod'
        )

class CanUpdateProfile(BasePermission):
    """
    Custom permission to allow only specific users to update profiles based on role.
    """
    def has_object_permission(self, request, view, obj):
        # Allow Admin to update any profile
        if request.user.is_admin:
            return True

        # Allow HOD to update Faculty and HOD profiles
        if request.user.role == 'hod' and obj.role in ['faculty', 'hod']:
            return True

        # Allow Faculty to update Faculty and Student profiles
        if request.user.role == 'faculty' and obj.role in ['faculty', 'student']:
            return True

        # Block users from updating their own profiles
        if request.user == obj:
            return False

        # Otherwise, deny access
        return False

class IsHOD(BasePermission):
    """
    Custom permission to only allow HODs to perform CRUD operations on Faculty and Students
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and if the user has role 'hod'
        if request.user.is_authenticated and request.user.role == 'hod':
            return True
        return False


class IsFaculty(BasePermission):
    """
    Custom permission to only allow Faculty members to perform CRUD operations on Students
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated and if the user has role 'faculty'
        if request.user.is_authenticated and request.user.role == 'faculty':
            return True
        return False
    
class IsHODOrFaculty(BasePermission):
    """
    Allows access only to users with the role of HOD or Faculty.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['hod', 'faculty']

