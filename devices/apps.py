from django.apps import AppConfig


class DevicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "devices"
    def ready(self):
        # Import signals so post_migrate handlers are registered when the app is ready
        try:
            from . import signals  # noqa: F401
        except Exception:
            # don't break startup if signals can't be imported during some management commands
            pass
