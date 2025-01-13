from rest_framework.permissions import BasePermission


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

class IsAdminOrSelf(BasePermission):
    """
    Custom permission to allow only admins, HODs, and the user themselves to view or update profiles.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Allow if the user is an admin or HOD
        if request.user.is_staff or request.user.role == 'hod':
            return True  # Admin or HOD can view or update all profiles

        # Allow if the user is viewing or updating their own profile
        user_id = view.kwargs.get('pk')  # Assuming 'pk' is passed in the URL
        if str(request.user.id) == str(user_id):  # Match user ID with the pk in the URL
            return True

        # Disallow access for other cases
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

