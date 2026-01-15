from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser # django built-in user model
from django.conf import settings # to reference the custom user model


class CustomUser(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        VIEWER = 'VIEWER', 'Viewer'

    role = models.CharField(
        max_length=10,
        choices=Roles.choices,
        default=Roles.ADMIN,
        verbose_name='User Role'
    )

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

class NetworkDevice(models.Model):
    class DeviceTypes(models.TextChoices):
        ROUTER = 'ROUTER', 'Router' # display format 'DATABASE', 'FIELD FORM WIDGET'
        SWITCH = 'SWITCH', 'Switch'
        FIREWALL = 'FIREWALL', 'Firewall'
        SERVER = 'SERVER', 'Server'

    class StatusTypes(models.TextChoices):
        ONLINE = 'ONLINE', 'Online'
        OFFLINE = 'OFFLINE', 'Offline'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    custom_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='devices',
        verbose_name='Owner',
        default=1,
        null=False,
        blank=False
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Device Name'# e.g., "Core Router"
    )
    ip_address = models.GenericIPAddressField(
        unique=True,
        verbose_name='IP Address'
    ) # IPv4 or IPv6 address
    device_type = models.CharField(
        max_length=20,
        choices= DeviceTypes.choices,
        verbose_name='Device Type'
    )

    location = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Location'
    )
    added_on = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Added On'
    )
    # online/offline/unknown
    status = models.CharField(
        max_length=20,
        choices=StatusTypes.choices,
        verbose_name='Status',
        default='UNKNOWN'
    )
    last_checked = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Last Checked At'
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(
                fields=['ip_address',]
            ),
            models.Index(
                fields=['device_type']
            )
        ]
        verbose_name = 'Network Device'

    def __str__(self):
        return f'{self.name} ({self.ip_address})'

class Metric(models.Model):
    device_id= models.ForeignKey(
        NetworkDevice, 
        on_delete=models.CASCADE,
        related_name='metric',
        verbose_name='Network Device'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Recorded At'
    )
    cpu_usage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        verbose_name='CPU Usage (%)'
    )
    memory_usage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        verbose_name='Memory Usage (%)'
    )
    bandwidth_in = models.BigIntegerField(
        null=True,
        verbose_name='Inbound Bandwidth (bytes)'
    )
    bandwidth_out = models.BigIntegerField(
        null=True,
        verbose_name='Outbound Bandwidth (bytes)'
    )
    class Meta:
        ordering = ['-timestamp'] # newest first
        indexes = [
            models.Index(
                fields=['device_id', 'timestamp']
            )
        ]
    def __str__ (self):
        return f'Metric for {self.device_id.name} at {self.timestamp}'

class Alert(models.Model):
    class AlertType(models.TextChoices):
        CPU = "CPU", "CPU"
        MEMORY = "MEM", "Memory"
        DISK = "DISK", "Disk"
        BANDWIDTH_IN = "BW_IN", "Bandwidth In"
        BANDWIDTH_OUT = "BW_OUT", "Bandwidth Out"
        CUSTOM = "CUSTOM", "Custom"

    class Severity(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARN", "Warning"
        CRITICAL = "CRIT", "Critical"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ACKED = "ACKED", "Acknowledged"
        RESOLVED = "RESOLVED", "Resolved"

    device_id = models.ForeignKey(
        "NetworkDevice",
        on_delete=models.CASCADE,
        verbose_name='Network Devide',
        related_name="alerts"
    )
    alert_type = models.CharField(
        max_length=32, 
        choices=AlertType.choices,
        verbose_name='Alert Type'
    )
    severity = models.CharField(
        max_length=8,
        choices=Severity.choices, 
        default=Severity.WARNING,
        verbose_name='Severity'
    )
    status = models.CharField(
        max_length=12, 
        choices=Status.choices, 
        default=Status.ACTIVE,
        verbose_name='Status',
    )

    # Optional link back to the metric row that caused this alert
    metric = models.ForeignKey(
        "Metric", 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='metrics_alerts',
        verbose_name='Related Metrix'
    )

    # Free-form human message and optional structured payload
    message = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name='Alert Message'
    )
    payload = models.JSONField(
        null=True, 
        blank=True, 
        help_text="Optional metric snapshot or context",
        verbose_name='Alert Payload'
    )

    first_triggered_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='First Triggered At'
    )
    last_triggered_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Last Triggered At'
    )
    resolved_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Resolved At'
    )

    class Meta:
        ordering = ["-last_triggered_at"] # newest first
        indexes = [
            models.Index(
                fields=["device_id", "status"]
            ),
            models.Index(
                fields=["alert_type", "status"]
            ),
            models.Index(
                fields=["last_triggered_at"]
            )
        ]

    def __str__(self):
        return f"{self.get_severity_display()} {self.get_alert_type_display()} on {self.device.name} ({self.status})"
    