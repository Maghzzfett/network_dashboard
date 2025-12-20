"""Main use of signals is to automate group and permission 
assignment when a user is created."""

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission


@receiver(post_migrate)
def seed_roles_and_permissions(sender, **kwargs):
    """Create 'Viewer' and 'Admin' groups and assign sensible permissions.

    - Viewer: gets `view_` permissions for app models (read-only).
    - Admin: gets all model permissions for app models (add/change/delete/view).

    This function is idempotent and safe to run multiple times.
    """
    # Only act for this app label (or for project-wide post_migrate passes)
    app_label = getattr(sender, 'name', None) or getattr(sender, 'label', None) or None
    # Proceed if sender is None (project-wide) or sender is this app
    if app_label not in (None, 'devices', 'devices.apps.DevicesConfig'):
        return

    # Lazy import models to avoid import-time side effects
    try:
        from .models import NetworkDevice, Metric, Alert
    except Exception:
        # models may not be available in some manage.py commands; skip gracefully
        return

    model_list = [NetworkDevice, Metric, Alert]

    viewer_group, _ = Group.objects.get_or_create(name='Viewer')
    admin_group, _ = Group.objects.get_or_create(name='Admin')

    for model in model_list:
        # use get_for_model for the content type
        from django.contrib.contenttypes.models import ContentType

        ct = ContentType.objects.get_for_model(model)

        # Give Viewer the view permission (if it exists)
        try:
            view_perm = Permission.objects.get(content_type=ct, codename=f'view_{model._meta.model_name}')
            if not viewer_group.permissions.filter(pk=view_perm.pk).exists():
                viewer_group.permissions.add(view_perm)
        except Permission.DoesNotExist:
            # older Django or custom models may not have view perms; ignore
            pass

        # Give Admin all model permissions
        perms = Permission.objects.filter(content_type=ct)
        if perms.exists():
            # Use set to ensure idempotent replacement of perms for admin group
            admin_group.permissions.add(*[p for p in perms if not admin_group.permissions.filter(pk=p.pk).exists()])
