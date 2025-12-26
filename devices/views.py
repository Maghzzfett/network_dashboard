from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, permissions # Combines multiple views into one unit
from .permissions import DjangoGroupPermission
from .serializers import (
    CustomUserSerializer,
    NetworkDeviceSerializer,
    MetricSerializer, 
    AlertSerializer
)
from .models import (
    CustomUser,
    NetworkDevice,
    Metric,
    Alert
)

User = get_user_model()
class CustomUserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [DjangoGroupPermission]

    def get_queryset(self):
        user = self.request.user
        # Admin can see all users
        if user.groups.filter(name='Admin').exists():
            return User.objects.all()
        # Viewers see themselves only
        return User.objects.filter(id=user.id)

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        # Admin can access any user
        if user.groups.filter(name='Admin').exists():
            return obj
        # Viewers can access only themselves
        elif obj.id != user.id:
            raise PermissionDenied("You can not access other users")
        return obj 
    
class NetworkDeviceViewSet(viewsets.ModelViewSet):
    queryset = NetworkDevice.objects.all()
    serializer_class = NetworkDeviceSerializer
    permission_classes = [DjangoGroupPermission]

class MetricViewSet(viewsets.ModelViewSet):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    permission_classes = [DjangoGroupPermission]

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes= [DjangoGroupPermission]

