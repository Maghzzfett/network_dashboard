# This file define the Celery task
from celery import shared_task # mark a function as a Celery task
from django.utils.timezone import now
from .poller import poll_device
from .models import NetworkDevice

@shared_task
def poll_all_devices():
    """
      Celery pull the tasks periodically
    """
    devices = NetworkDevice.objects.all()
    for device in devices:
        poll_device(device) # calls the metrics and store them in db via the poll_device function