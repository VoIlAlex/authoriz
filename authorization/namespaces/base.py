"""
Module with base functionality to work with actions namespaces.
"""

import enum
from functools import lru_cache
from typing import List, Optional

from django.db import models


class ActionEnumsService:
    """
    Service to work with action workspaces enums.
    """

    _ENUMS = []
    _NAMESPACE_DICT = {}

    @classmethod
    def register(cls, EnumCls):
        """
        Register enum class in service.
        """
        assert issubclass(ActionsNamespace, ActionsNamespace)
        ActionEnumsService._ENUMS.append(cls)
        ActionEnumsService._NAMESPACE_DICT[EnumCls.name] = EnumCls

    @classmethod
    @lru_cache
    def actions_by_namespace(cls, name, with_namespace=True):
        """
        Get all actions by namespace name.
        """
        ActionCls = ActionEnumsService._NAMESPACE_DICT.get(name, None)
        if ActionCls:
            if with_namespace:
                return [x for x in ActionCls.Actions.values]
            else:
                return [x.split(':')[1] for x in ActionCls.Actions.values]
        else:
            raise RuntimeError(f'Namespace {name} not found.')

    @classmethod
    def get_namespace(cls, name) -> Optional['ActionsNamespace']:
        """
        Get namespace enum class by namespace name.
        """
        return cls._NAMESPACE_DICT.get(name, None)

    @classmethod
    @lru_cache
    def get_namespaces(cls):
        """
        Get all namespaces enum classes.
        """
        return [x for x in cls._NAMESPACE_DICT]

    @classmethod
    def get_all_actions(cls, with_namespace=True):
        """
        Get all actions in registered namespace classes.
        """
        all_actions = []
        for namespace in ActionEnumsService._NAMESPACE_DICT:
            all_actions += ActionEnumsService.actions_by_namespace(namespace, with_namespace=with_namespace)
        return all_actions

    @classmethod
    def validate_action(cls, name: str):
        """
        Check if action is registered and allowed by system.
        """
        assert isinstance(name, str)
        name = name.strip()
        if name.endswith('*'):
            return name
        all_actions = ActionEnumsService.get_all_actions()
        parts = name.split('/')
        if len(parts) == 1:
            action_name = parts[0]
        elif len(parts) == 2:
            action_name, params = parts
        else:
            raise RuntimeError('Failed to parse action.')
        if action_name not in all_actions:
            raise RuntimeError(f'{action_name} is not allowed action name.')
        return action_name

    @classmethod
    def get_action_params(cls, action: str) -> List[str]:
        """
        Get params list by action name.
        """
        namespace_name, action_name = action.split(':')
        namespace = cls._NAMESPACE_DICT.get(namespace_name, None)
        if namespace:
            if action_name != '*':
                return namespace.params.get(action, [])
            else:
                params = []
                for k in namespace.params:
                    params += namespace.params[k]
                return params
        raise RuntimeError(f'Namespace for action {action} is not found.')


class ActionsNamespaceMetaClass(type):
    """
    Meta class to action namespaces. Registers namespace class and
    create some additional data.
    """
    def __init__(cls, *args, **kwargs):
        type.__init__(cls, *args, **kwargs)
        # TODO: put default meta on the stop of __Meta. And override it with Meta.
        meta = getattr(cls, f'_{cls.__name__}__Meta', None)
        if not meta:
            meta = getattr(cls, 'Meta', DefaultActionNamespaceMeta)
        if not getattr(meta, 'abstract', False):
            assert hasattr(cls, 'name')
            assert hasattr(cls, 'Actions')
            if not hasattr(cls, 'params'):
                cls.params = {}
            for p in cls.Actions.values:
                if p not in cls.params:
                    cls.params[p] = []
            actions_without_workspace = {}
            for enum_value_name in cls.Actions.names:
                actions_without_workspace[enum_value_name] = getattr(
                    cls.Actions,
                    enum_value_name
                ).split(':')[1]

            cls.PlainActions = enum.Enum('PlainActions', actions_without_workspace)
            ActionEnumsService.register(cls)


class DefaultActionNamespaceMeta:
    """
    Default namespace meta data.
    """
    abstract = False


class ActionsNamespace(metaclass=ActionsNamespaceMetaClass):
    """
       Base class for actions namespace.
    """
    name: str
    Actions: models.TextChoices
    params = {}

    class __Meta:
        abstract = True

    @classmethod
    def filter(cls, permissions_list):
        """
        Filter actions list and get only actions of this namespace.
        """
        return [
            permission for permission in permissions_list if permission.startswith(f'{cls.name}:')
        ]

    @classmethod
    def get_namespace_name(cls):
        return cls.name


__all__ = [
    'ActionEnumsService',
    'ActionsNamespaceMetaClass',
    'DefaultActionNamespaceMeta',
    'ActionsNamespace',
]
