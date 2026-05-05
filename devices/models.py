from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser # django built-in user model
from django.conf import settings # to reference the custom user model


class SeverityChoices(models.TextChoices):
    INFO = "INFO", "Info"
    WARNING = "WARN", "Warning"
    CRITICAL = "CRIT", "Critical"


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

    class DeviceVendors(models.TextChoices):
        CISCO = 'CISCO', 'Cisco'
        JUNIPER = 'JUNIPER', 'Juniper'
        MIKROTIK = 'MIKROTIK', 'Mikrotik'

    class StatusTypes(models.TextChoices):
        ONLINE = 'ONLINE', 'Online'
        OFFLINE = 'OFFLINE', 'Offline'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    custom_id = models.ForeignKey(
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
    device_vendor = models.CharField(
        max_length=20,
        choices= DeviceVendors.choices,
        null=True,
        blank=True,
        verbose_name='Device Vendor'
    )

    location = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Location'
    )
    snmp_community = models.CharField(
        max_length=100,
        default='public',
        verbose_name='SNMP Community String',
        help_text='Community string for SNMP queries (default: public)'
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
        auto_now=True,
        null=True,
        blank= True,
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

class MetricType(models.Model):
    class MetricNames(models.TextChoices):
        CPU = "CPU", "cpu (%)"
        MEMORY = "Memory", "memory (GB)"
        BANDWIDTH_IN = "Bandwidth In", "bandwidth_in (bps)"
        BANDWIDTH_OUT = "Bandwidth Out", "bandwidth_out (bps)"
        UPTIME = "Uptime", "uptime (ticks)"
        CAPACITY = "Capacity", "capacity (bps)"

    class MetricUnits(models.TextChoices):
        PERCENT = "%", "Percent"
        GB = "GB", "Gigabytes"
        BPS = "bps", "Bits per second"
        TICKS = "ticks", "System ticks"

    name = models.CharField(
        max_length=32,
        choices=MetricNames.choices,
        unique=True,
        verbose_name='Metric Type Name'
    )
    unit = models.CharField(
        max_length=20,
        choices=MetricUnits.choices,
        verbose_name='Unit of Measurement',
    
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Metric Type'
        verbose_name_plural = 'Metric Types'

    def __str__(self):
        return f"{self.name} ({self.unit})"

class Metric(models.Model):
    device= models.ForeignKey(
        NetworkDevice, 
        on_delete=models.CASCADE,
        related_name='metric',
        verbose_name='Network Device'
    )
    metric= models.ForeignKey(
        MetricType,
        on_delete=models.PROTECT,
        verbose_name='Metric Type'
    )
    value = models.FloatField(
        null=True,
        blank=True,
        verbose_name='Metric Value'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Recorded At'
    )
  
    class Meta:
        ordering = ['-timestamp'] # newest first
        indexes = [
            models.Index(
                fields=['device', 'timestamp']
            )
        ]
    def __str__ (self):
        return f"{self.device.type} - {self.metric.name}: {self.value} at {self.timestamp}"

class AlertThreshold(models.Model):
    class Condition(models.TextChoices):
        GREATER_THAN = ">", "Greater than"
        LESS_THAN = "<", "Less than"
        GREATER_EQUAL = ">=", "Greater than or equal"
        LESS_EQUAL = "<=", "Less than or equal"
        EQUAL = "==", "Equal"

    device = models.ForeignKey(
        NetworkDevice,
        on_delete=models.CASCADE,
        related_name="alert_thresholds",
        verbose_name="Network Device"
    )
    
    metric_type = models.ForeignKey(
        MetricType,
        on_delete=models.PROTECT,
        verbose_name="Metric Type"
    )
    
    threshold_value = models.FloatField(
        verbose_name="Threshold Value",
        help_text="e.g., 80 for CPU percentage"
    )
    
    condition = models.CharField(
        max_length=2,
        choices=Condition.choices,
        default=">",
        verbose_name="Condition Operator"
    )
    
    duration_seconds = models.IntegerField(
        default=300,
        verbose_name="Duration (seconds)",
        help_text="Alert only fires if condition persists for this duration"
    )
    
    severity = models.CharField(
        max_length=8,
        choices=SeverityChoices.choices,
        default=SeverityChoices.WARNING,
        verbose_name="Alert Severity"
    )
    
    is_enabled = models.BooleanField(
        default=True,
        verbose_name="Enabled"
    )
    
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Description"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("device", "metric_type")
        indexes = [
            models.Index(fields=["device", "is_enabled"]),
            models.Index(fields=["metric_type"]),
        ]

    def __str__(self):
        return f"{self.device.name} - {self.metric_type.name} {self.condition} {self.threshold_value}"

class Alert(models.Model):
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
    threshold = models.ForeignKey(
        "AlertThreshold",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="triggered_alerts",
        verbose_name="Triggered By Threshold"
    )
    alert_type = models.ForeignKey(
        "MetricType",
        on_delete=models.PROTECT,
        verbose_name='Alert Type'
    )
    severity = models.CharField(
        max_length=8,
        choices=SeverityChoices.choices, 
        default=SeverityChoices.WARNING,
        verbose_name='Severity'
    )
    status = models.CharField(
        max_length=12, 
        choices=Status.choices, 
        default=Status.ACTIVE,
        verbose_name='Status',
    )

    # Track how many times this specific alert has recurred
    # Incremented when the same alert fires again (same device/alert_type)
    recurrence_count = models.IntegerField(
        default=1,
        verbose_name='Recurrence Count',
        help_text='Number of times this alert has been triggered'
    )

    # Optional link back to the metric row that caused this alert
    # Applies to: CPU, MEMORY, BANDWIDTH_IN, BANDWIDTH_OUT
    # Can be null for alerts triggered by device status changes (e.g., device offline)
    metric = models.ForeignKey(
        "Metric", 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='metrics_alerts',
        verbose_name='Related Metric'
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
        return f"{self.get_severity_display()} {self.alert_type.name} on {self.device.name} ({self.status})"
    