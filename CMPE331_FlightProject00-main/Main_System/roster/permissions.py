from rest_framework import permissions

class IsStandardUser(permissions.BasePermission):
    """
    Allows access only to users who are NOT in the 'ViewOnly' group.
    """

    def has_permission(self, request, view):
        # If user is not authenticated, let IsAuthenticated handle it (or return False)
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is in 'ViewOnly' group
        if request.user.groups.filter(name='ViewOnly').exists():
            return False
            
        return True