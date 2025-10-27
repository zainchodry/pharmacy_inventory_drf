from rest_framework import permissions




class IsPharmacistOrAdmin(permissions.BasePermission):
    """
    Allow access to authenticated users who are admin or pharmacist.
    Other roles (supplier/customer) are denied for write operations.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == "admin" or user.role == "pharmacist":
            return True
        # allow read-only for others
        if request.method in permissions.SAFE_METHODS:
            return True
        return False
