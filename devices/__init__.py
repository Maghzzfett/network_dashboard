# aim is to make celery app importable from network_dashboard package
# important for celery to work with django
from network_dashboard.celery import app as celery_app

__all__ = ('celery_app',)