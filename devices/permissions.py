# Global role-based permissions for device views
from rest_framework import permissions
from .utils.helpers import PermissionHelper


class DjangoGroupPermission(permissions.BasePermission):
    """Global permissions based on Django groups"""
    
    def has_permission(self, request, view):
        return PermissionHelper.can_read(request.user)
    
    def has_object_permission(self, request, view, obj):
        # Admins can access any object
        if PermissionHelper.is_admin(request.user):
            return True
        # Viewers can only read
        if PermissionHelper.is_viewer(request.user):
            return request.method in permissions.SAFE_METHODS
        return False
