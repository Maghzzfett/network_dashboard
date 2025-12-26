from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, NetworkDeviceViewSet, MetricViewSet, AlertViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'devices', NetworkDeviceViewSet, basename='device')
router.register(r'metrics', MetricViewSet, basename='metric')
router.register(r'alerts', AlertViewSet, basename='alert')

urlpatterns = router.urls