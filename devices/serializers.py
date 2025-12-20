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
        'name',
        'ip_address', 
        'device_type', 
        'location'
    ]

class MetricSerializer(serializers.ModelSerializer):
    device_id = NetworkDeviceSerializer(read_only=True)
    class Meta:
        model = Metric
        fields = [
        'id',
        'timestamp', 
        'cpu_usage', 
        'memory_usage', 
        'disk_usage', 
        'bandwidth_in', 
        'bandwidth_out'
    ]

class AlertSerializer(serializers.ModelSerializer):
    device_id = NetworkDeviceSerializer(read_only=True)
    metric = MetricSerializer(read_only=True)
    class Meta:
        model = Alert
        fields = [
        'id',
        'alert_type',
        'severity',
        'message',
        'created_at',
        'status',
        'first_triggered',
        'last_triggered',
        'resolved_at',
        'payload'
    ]