from rest_framework import permissions



class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow access if user is the object owner (user id match) or admin.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            return True
        # obj can be User or Profile; try both
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
