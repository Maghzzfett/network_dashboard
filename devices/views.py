from rest_framework.response import Response 
from rest_framework.decorators import action # To add custom actions to viewsets
from rest_framework import generics
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied
from rest_framework import viewsets, permissions # Combines multiple views into one unit
from .permissions import DjangoGroupPermission
from .utils.network_tools import ping_device, traceroute_device
from .poller import snmp_get, poll_device
from django.utils import timezone
from django.utils.timezone import now

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

User = get_user_model() # Get the custom user model
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

    @action(detail=True, methods=["get"])
    def status(self, request,pk=None):
        device=self.get_object()
        reachable = ping_device(device.ip_address)
        device.status = "online" if reachable else "offline"
        device.last_checked = timezone.now()
        device.save()
        return Response(
            {
                "device": device.name,
                "ip_address": device.ip_address,
                "status": device.status,
                "last_checked": device.last_checked
            }
        )
    
    @action(detail=True, methods=["get"])
    def traceroute(self, requrest, pk=None):
        device=self.get_object()
        trace_output = traceroute_device(device.ip_address)
        return Response(
            {
                "device": device.name,
                "ip_address": device.ip_address,
                "traceroute": trace_output

            }
        )

class MetricViewSet(viewsets.ModelViewSet):
    queryset = Metric.objects.all()
    serializer_class = MetricSerializer
    permission_classes = [DjangoGroupPermission]

    @action(detail=True, methods=["get"])
    def poll_device(self, request, pk=None):
        """
        Custom endpoint: GET /metrics/{id}/poll/
        Runs the poller for the given device and stores metrics.
        """
        device = self.get_object()  # fetch the device instance

        # Retrieve previous counters if available
        prev_metric = (
            Metric.objects.filter(device=device, metric_type="bandwidth_in")
            .order_by("-created_at")
            .first()
        )
        prev_in, prev_out, prev_time = None, None, None
        if prev_metric:
            # You could store prev_in/out/time in a separate table or cache
            # For simplicity, assume you have them in Metric or another model
            prev_in = getattr(prev_metric, "prev_in", None)
            prev_out = getattr(prev_metric, "prev_out", None)
            prev_time = getattr(prev_metric, "prev_time", None)

        # Run the poller
        in_octets, out_octets, poll_time = poll_device(
            device, prev_in=prev_in, prev_out=prev_out, prev_time=prev_time
        )

        return Response({
            "device": device.id,
            "in_octets": in_octets,
            "out_octets": out_octets,
            "poll_time": poll_time,
        })



class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes= [DjangoGroupPermission]

