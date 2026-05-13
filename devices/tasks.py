# This file define the Celery task
from celery import shared_task # mark a function as a Celery task
from django.utils.timezone import now
from .poller import poll_device
from .models import NetworkDevice
from .utils.network_tools import ping_device
from .utils.helpers import DeviceHelper
import logging

logger = logging.getLogger(__name__)
from django.utils import timezone

@shared_task # This celery decorater enables a function to be shared across the project, can be called from anywhere.
def poll_all_devices():
    """
    Celery task: Poll all devices for metrics periodically
    """
    devices = NetworkDevice.objects.all()
    for device in devices:
        try:
            poll_device(device)
        except Exception as e:
            logger.error(f"Error polling device {device.name}: {str(e)}")

@shared_task
def update_device_status():
    """
    Periodic task to automatically update network device status.
    Runs on schedule without manual operation.
    """
    devices = NetworkDevice.objects.all()
    updated_count = 0
    
    for device in devices:
        try:
            reachable = ping_device(device.ip_address)
            DeviceHelper.update_device_status(device, reachable)
            updated_count += 1
        except Exception as e:
            logger.error(f"Error updating status for device {device.name}: {str(e)}")
            DeviceHelper.set_device_unknown(device)
    
    return f"Updated status for {updated_count} devices"