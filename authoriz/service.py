"""
Module with permissions service functionality.
"""

from functools import wraps
from typing import List, Optional
from uuid import UUID
from .cache import get_all_user_roles_from_cache, save_all_user_roles_from_cache
from .parsing.service import RulesParsingService
from .utils.roles import get_user_roles_by_param


class ActionsManager:
    """
    Actions manager is put into route decorated with @PermissionsService.required_actions(...)
    """
    def __init__(self, actions):
        self.actions = actions

    def has_permission(self, user_id: UUID, params):
        return PermissionsService.is_user_allowed(user_id, self.actions, params)


class PermissionsService:
    """
    Service to work with permissions.
    """
    _VIEWS_ROLES = {}

    @classmethod
    def is_user_allowed(cls, user_id, actions, params):
        """
        Check if user with has access to actions with specified params.
        """
        user_roles = cls._get_all_user_roles(user_id, **params)
        allowed_actions = RulesParsingService.get_user_allowed_actions(user_id, user_roles, params)
        return len(set(actions) - set(allowed_actions)) == 0

    @classmethod
    def required_actions(cls, actions: Optional[List[str]] = None):
        """
        Decorator to specified view function required actions.
        """
        def decorator(func):
            nonlocal cls, actions
            if '_p_actions' in dir(func):
                raise RuntimeError('Actions already specified.')
            func._p_actions = actions or []
            actions_manager = ActionsManager(
                actions=actions
            )

            @wraps(func)
            def _func(*args, **kwargs):
                nonlocal actions_manager
                return func(*args, actions_manager=actions_manager, **kwargs)

            cls._VIEWS_ROLES[cls._get_view_unique_identifier(_func)] = {
                'actions': actions,
                'view': _func
            }
            return _func

        return decorator

    @classmethod
    def _get_view_unique_identifier(cls, view):
        """
        Get view function/method unique identifier
        to store it in PermissionsService._VIEWS_ROLES dict.
        """
        module_name = view.__module__
        view_name = view.__qualname__
        return f'{module_name}.{view_name}'

    @classmethod
    def _get_all_user_roles(cls, user_id, use_cache=True, **kwargs):
        """
        Get user roles with specified params.
        """
        roles = None
        if use_cache:
            roles = get_all_user_roles_from_cache(
                user_id=user_id,
                params=kwargs
            )
        if not use_cache or roles is None:
            all_user_roles = []
            for kwargs_name, kwargs_value in kwargs.items():
                all_user_roles += get_user_roles_by_param(user_id, kwargs_name, kwargs_value)

            roles = list(set(all_user_roles))

            save_all_user_roles_from_cache(
                user_id=user_id,
                params=kwargs,
                data=roles
            )
        return roles

    @staticmethod
    def _get_composed_view_actions(view, *actions_list):
        """
        Get all actions required by view.
        """
        actions = []
        if hasattr(view, '_p_actions'):
            actions += view._p_actions
        for action_list in actions_list:
            actions += action_list
        return actions


__all__ = [
    'ActionsManager',
    'PermissionsService',
]
