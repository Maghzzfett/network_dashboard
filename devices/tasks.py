# This file define the Celery task
from celery import shared_task # mark a function as a Celery task
from django.utils.timezone import now
from .poller import poll_device
from .models import NetworkDevice
from .utils.network_tools import ping_device
from django.utils import timezone

@shared_task
def poll_all_devices():
    """
      Celery pull the tasks periodically
    """
    devices = NetworkDevice.objects.all()
    for device in devices:
        poll_device(device) # calls the metrics and store them in db via the poll_device function

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
            device.status = "ONLINE" if reachable else "OFFLINE"
            device.last_checked = timezone.now()
            device.save()
            updated_count += 1
        except Exception as e:
            print(f"Error updating status for device {device.name}: {str(e)}")
            device.status = "UNKNOWN"
            device.last_checked = timezone.now()
            device.save()
    
    return f"Updated status for {updated_count} devices"