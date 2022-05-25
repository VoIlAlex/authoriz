"""
Base functionality for DRF permissions classes to work with permissions parsing service.
"""
from django.conf import settings
from rest_framework.permissions import BasePermission

from authoriz.service import PermissionsService
from authoriz.utils.permissions import SkipPermission


class BaseServicePermission(BasePermission):
    """
    Base class that should be inherited by
    all permissions classes that are based
    on permissions parsing service.

    Inherited classes should only specify
    parameters getters.
    """
    def __init__(
            self,
            actions_permissions=None,
            action=None,
            methods_permissions=None,
    ):
        self.actions_permissions = actions_permissions or {}
        self.methods_permissions = methods_permissions or {}
        self.action = action

    def has_permission(self, request, view):
        """
        DRF permissions check implementation to check permissions by permissions service.
        """
        service_settings = getattr(settings, 'ACTION_RULES_SERVICE', {})
        if service_settings.get("DISABLE_PERMISSIONS_CHECK", False):
            return True
        params = {}
        params_attrs = [x for x in dir(self) if x.startswith('get_')]
        for param_attr in params_attrs:
            value = getattr(self, param_attr)(request, view)
            if SkipPermission.check(value):
                return True
            params[param_attr[4:]] = value

        user = request.user
        required_actions = PermissionsService._get_composed_view_actions(
            view,
            self.actions_permissions.get(self.action, []),
            self.methods_permissions.get(request.method, [])
        )
        return PermissionsService.is_user_allowed(user.id, required_actions, params)


__all__ = [
    'BaseServicePermission',
]
