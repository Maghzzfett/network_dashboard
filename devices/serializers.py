from rest_framework import serializers
from .models import CustomUser, NetworkDevice, Metric, Alert

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
        'id', 
        'username', 
        'email', 
        'role'
    ]

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
    class Meta:
        model = Metric
        fields = [
            'id',
            'device_id',
            'metric_type',
            'value',
            'units',
            'timestamp'
        ]

class AlertSerializer(serializers.ModelSerializer):
    device_id = NetworkDeviceSerializer(read_only=True)
    metric = MetricSerializer(read_only=True)
    class Meta:
        model = Alert
        fields = [
            'id',
            'device_id',
            'alert_type',
            'severity',
            'status',
            'metric',
            'message',
            'payload',
            'first_triggered_at',
            'last_triggered_at',
            'resolved_at'
        ]