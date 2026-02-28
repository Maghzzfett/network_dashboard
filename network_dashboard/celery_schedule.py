# This file is responsible for storing periodic task schedules for Celery beat 
# and pushes to the Redis broker to be picked up by Celery workers
from celery.schedules import crontab
from .tasks import poll_all_devices

# Register the periodi task with Celery beat
CELERY_BEAT_SCHEDULE = {
    'poll-devices-every-60-seconds': {
        'task' : 'network_dashboard.tasks.poll_all_devices',
        'schedule' : 60.0, # every 60 seconds
    }
}