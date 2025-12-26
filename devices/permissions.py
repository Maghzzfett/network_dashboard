# Global role-based permissions for device views
from rest_framework import permissions

class DjangoGroupPermission(permissions.BasePermission):
    # Global permissions for Authentication based on Django groups
    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user.is_authenticated:
            return False
        # Admins have full access
        if request.user.groups.filter(name='Admin').exists():
            return True
        # Viewers can only read
        elif request.user.groups.filter(name='Viewer').exists():
            return request.method in permissions.SAFE_METHODS
        
        return False # Default deny access
    
    # Object-level permissions
    def has_object_permission(self, request, view, obj):
        # Admins can access any object
        if request.user.groups.filter(name='Admin').exists():
            return True
        # Viewers can only read objects
        elif request.user.groups.filter(name='Viewer').exists():
            return request.method in permissions.SAFE_METHODS
    
        return False # Default deny access
