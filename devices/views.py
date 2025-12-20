from rest_framework import generics
from rest_framework import viewsets # Combines multiple views into one unit
from .permissions import DjangoGroupPermission
from django.contrib.auth import get_user_model # Import the user model
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
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [DjangoGroupPermission]