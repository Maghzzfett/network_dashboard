from rest_framework import serializers
from .models import CustomUser, NetworkDevice, Metric, Alert, MetricType, AlertThreshold

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
        'id', 
        'username', 
        'email', 
        'role'
    ]

class MetricTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricType
        fields = ['id', 'name', 'unit', 'description', 'created_at']

class NetworkDeviceSerializer(serializers.ModelSerializer):
    custome_user = CustomUserSerializer(read_only=True)
    class Meta:
        model = NetworkDevice
        fields = [
        'id',
        'custome_user', 
        'name',
        'ip_address',
        'status', 
        'device_type', 
        'device_vendor',
        'location',
        'snmp_community',
        'last_checked'
    ]

class MetricSerializer(serializers.ModelSerializer):
    device_id = NetworkDeviceSerializer(read_only=True)
    metric_type_name = serializers.CharField(source='metric_type.name', read_only=True)
    metric_type_unit = serializers.CharField(source='metric_type.unit', read_only=True)
    
    class Meta:
        model = Metric
        fields = [
            'id',
            'device_id',
            'metric_type',
            'metric_type_name',
            'metric_type_unit',
            'value',
            'units',
            'timestamp'
        ]

class AlertThresholdSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source='device.name', read_only=True)
    metric_type_name = serializers.CharField(source='metric_type.name', read_only=True)
    severity_display = serializers.SerializerMethodField()
    
    def get_severity_display(self, obj):
        return obj.get_severity_display()
    
    class Meta:
        model = AlertThreshold
        fields = [
            'id',
            'device',
            'device_name',
            'metric_type',
            'metric_type_name',
            'threshold_value',
            'condition',
            'duration_seconds',
            'severity',
            'severity_display',
            'is_enabled',
            'description',
            'created_at',
            'updated_at'
        ]

class AlertSerializer(serializers.ModelSerializer):
    # Use IDs for foreign keys (performance optimization - no nested fetching)
    device_id = serializers.PrimaryKeyRelatedField(
        queryset=NetworkDevice.objects.all()
    )
    metric_id = serializers.PrimaryKeyRelatedField(
        source='metric',
        queryset=Metric.objects.all(),
        allow_null=True,
        required=False
    )
    threshold_id = serializers.PrimaryKeyRelatedField(
        source='threshold',
        queryset=AlertThreshold.objects.all(),
        allow_null=True,
        required=False
    )
    
    # Alert type is now FK to MetricType
    alert_type_name = serializers.CharField(
        source='alert_type.name',
        read_only=True
    )
    alert_type_unit = serializers.CharField(
        source='alert_type.unit',
        read_only=True
    )
    
    # Severity and status display (from choices)
    severity_display = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    # Device info for list/detail views (minimal)
    device_name = serializers.CharField(
        source='device_id.name',
        read_only=True
    )
    device_ip = serializers.CharField(
        source='device_id.ip_address',
        read_only=True
    )
    
    def get_severity_display(self, obj):
        return obj.get_severity_display()
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    class Meta:
        model = Alert
        fields = [
            'id',
            'device_id',
            'device_name',
            'device_ip',
            'alert_type',
            'alert_type_name',
            'alert_type_unit',
            'severity',
            'severity_display',
            'status',
            'status_display',
            'threshold_id',
            'metric_id',
            'message',
            'payload',
            'recurrence_count',
            'first_triggered_at',
            'last_triggered_at',
            'resolved_at'
        ]
        read_only_fields = [
            'first_triggered_at',
            'last_triggered_at',
            'device_name',
            'device_ip',
            'recurrence_count'
        ]