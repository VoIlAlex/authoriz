"""
Module specified dataclasses used by authorization module.
"""

from dataclasses import dataclass, field
from typing import List

from authorization.namespaces.base import ActionEnumsService

NEXT_RULE_ID = 1


def get_next_rule_id():
    global NEXT_RULE_ID
    id_ = NEXT_RULE_ID
    NEXT_RULE_ID += 1
    return id_


@dataclass
class ParsedAction:
    """
    Action data split into separate parts.
    """
    namespace: str
    action_name: str
    params: dict = field(default_factory=lambda: {})

    @property
    def full_name(self):
        return f'{self.namespace}:{self.action_name}'

    def __post_init__(self):
        assert isinstance(self.namespace, str)
        self.namespace = self.namespace
        namespace = ActionEnumsService.get_namespace(self.namespace)
        assert namespace is not None
        assert isinstance(self.action_name, str)
        assert self.action_name == '*' or self.action_name in ActionEnumsService.get_all_actions(with_namespace=False)

        # TODO: check how to deal with params of * actions.
        if self.params is None:
            self.params = {}
        assert isinstance(self.params, dict)
        if self.action_name != '*':
            namespace_params = [k for k in namespace.params[self.full_name]]
        else:
            namespace_params = []
            for k in namespace.params:
                namespace_params += [p for p in namespace.params[k]]
        for p in self.params:
            assert p in namespace_params
            p_value = self.params[p]
            if p_value and not isinstance(p_value, str):
                self.params[p] = str(p_value)


@dataclass
class PermissionsRule:
    """
    Permissions rule data split into separate parts.
    """
    name: str
    effect: str
    actions: List[ParsedAction]

    # <user-id> | role:<role-name>
    target: str
    id: int = field(default_factory=get_next_rule_id)

    def __post_init__(self):
        assert isinstance(self.name, str)
        assert isinstance(self.effect, str)
        self.effect = self.effect.lower()
        assert self.effect in ['allow', 'deny']
        assert isinstance(self.target, str)
        self.target = self.target.lower()


__all__ = [
    'ParsedAction',
    'PermissionsRule',
]
