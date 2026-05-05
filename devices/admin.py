from django.contrib import admin # django built-in admin module
from django.contrib.auth.admin import UserAdmin # django built-in user admin module
from .models import CustomUser, NetworkDevice, Metric

@admin.register(CustomUser)# Register the models with the admin site
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    search_fields = ['username', 'email']
    list_filter = ['role', 'is_staff', 'is_active']

admin.site.register(NetworkDevice)

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['device', 'metric', 'value', 'timestamp']
    list_filter = ['metric', 'timestamp']
    search_fields = ['device_id__name', 'metric_type']
    readonly_fields = ['timestamp']

