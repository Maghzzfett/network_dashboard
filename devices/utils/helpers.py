"""
Helper utilities for common business logic operations.
Centralizes logic used across multiple modules to follow DRY principle.
"""

from django.utils import timezone
from rest_framework import permissions
from ..models import NetworkDevice, SeverityChoices
from .constants import ADMIN_GROUP, VIEWER_GROUP


class PermissionHelper:
    """Centralized permission checking logic"""
    
    @staticmethod
    def is_admin(user):
        """Check if user is in Admin group"""
        return user.groups.filter(name=ADMIN_GROUP).exists()
    
    @staticmethod
    def is_viewer(user):
        """Check if user is in Viewer group"""
        return user.groups.filter(name=VIEWER_GROUP).exists()
    
    @staticmethod
    def can_read(user):
        """User can read if authenticated and (Admin or Viewer)"""
        if not user.is_authenticated:
            return False
        return PermissionHelper.is_admin(user) or PermissionHelper.is_viewer(user)
    
    @staticmethod
    def can_write(user):
        """User can write only if Admin"""
        return PermissionHelper.is_admin(user)
    
    @staticmethod
    def can_modify_object(user, obj=None):
        """User can modify object only if Admin"""
        return PermissionHelper.is_admin(user)


class DeviceHelper:
    """Centralized device update and response logic"""
    
    @staticmethod 
    def update_device_status(device, reachable):
        """
        Update device status and last_checked timestamp.
        
        Args:
            device: NetworkDevice instance
            reachable (bool): Whether device is reachable
        """
        device.status = NetworkDevice.StatusTypes.ONLINE if reachable else NetworkDevice.StatusTypes.OFFLINE
        device.last_checked = timezone.now()
        device.save()
    
    @staticmethod
    def set_device_unknown(device):
        """Mark device as UNKNOWN status"""
        device.status = NetworkDevice.StatusTypes.UNKNOWN
        device.last_checked = timezone.now()
        device.save()
    
    @staticmethod
    def get_device_status_response(device):
        """
        Get standardized device status response for API endpoints.
        
        Returns:
            dict: Device status information
        """
        return {
            "id": device.id,
            "device": device.name,
            "ip_address": device.ip_address,
            "status": device.get_status_display(),
            "last_checked": device.last_checked
        }
    
    @staticmethod
    def get_device_detail_response(device):
        """Get detailed device information"""
        return {
            "id": device.id,
            "name": device.name,
            "ip_address": device.ip_address,
            "device_type": device.get_device_type_display(),
            "device_vendor": device.get_device_vendor_display() if device.device_vendor else None,
            "location": device.location,
            "status": device.get_status_display(),
            "last_checked": device.last_checked,
            "snmp_community": device.snmp_community,
            "added_on": device.added_on
        }
