"""
DRF mixins to support authorization module functionality.
"""

from collections import OrderedDict
from typing import Union
from abc import ABCMeta

from authoriz.permissions.base import BaseServicePermission


class APIViewPermissionsMixin(metaclass=ABCMeta):
    """
    Allows a ViewSet or APIView to define route required permissions.
    """

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        action = getattr(self, 'action', None)
        actions_permissions = self._get_actions_permissions()
        methods_permissions = self._get_methods_permissions()

        return [self._get_composed_permission(
            permission,
            actions_permissions=actions_permissions,
            action=action,
            methods_permissions=methods_permissions
        ) for permission in getattr(self, 'permission_classes', [])]

    @staticmethod
    def _validate_permissions(actions_permissions: Union[dict, OrderedDict]):
        if not isinstance(actions_permissions, (dict, OrderedDict)):
            return {}
        return actions_permissions

    def _get_actions_permissions(self):
        return self._validate_permissions(getattr(self, 'actions_permissions', {}))

    def _get_methods_permissions(self):
        return self._validate_permissions(getattr(self, 'methods_permissions', {}))

    @staticmethod
    def _get_composed_permission(
            permission_class,
            actions_permissions,
            action,
            methods_permissions
    ):
        """
        Get DRF permission class.
        """
        if issubclass(permission_class, BaseServicePermission):
            return permission_class(
                actions_permissions=actions_permissions,
                action=action,
                methods_permissions=methods_permissions
            )
        else:
            return permission_class()


__all__ = [
    'APIViewPermissionsMixin',
]
