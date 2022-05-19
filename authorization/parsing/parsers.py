"""
Specific permissions parsers.
"""

import os
import rapidjson
from typing import List

from authorization.namespaces.base import ActionEnumsService
from authorization.parsing.base import PermissionsRule, PermissionsParser
from authorization.utils.parsing import parse_action
from authorization.utils.roles import get_all_roles


class RolesRulesFilesParser(PermissionsParser):
    def __init__(self, role=None, rules_dir=None):
        self.role = role
        self.rules_dir = rules_dir or os.path.join(
            os.getcwd(),
            'rules'
        )

    def get_rules(self) -> List[PermissionsRule]:
        """
        Get rules from `rules` folder where filename is
        a name of user role.
        """
        rules_dir = self.rules_dir
        if self.role is None:
            all_roles = get_all_roles()
        else:
            all_roles = [self.role]
        rules = []
        for role in all_roles:
            role_file = os.path.join(rules_dir, f'{role}.json')
            if not os.path.exists(role_file):
                continue
            with open(role_file) as f:
                role_rules = rapidjson.load(f, parse_mode=rapidjson.PM_COMMENTS | rapidjson.PM_TRAILING_COMMAS)
            for rule in role_rules:
                rule = self._validate_rule(rule)
                rule = PermissionsRule(
                    name=rule['name'],
                    effect=rule['effect'],
                    actions=[parse_action(action) for action in rule['action']],
                    target=f'role:{role}'
                )
                rules.append(rule)
        return rules

    @staticmethod
    def _validate_rule(rule: dict):
        """
        Check if rule dict match structural requirements.
        """
        rule = {k.lower(): v for k, v in rule.items()}
        assert 'name' in rule
        assert 'effect' in rule
        assert 'action' in rule
        assert isinstance(rule['name'], str)
        assert isinstance(rule['effect'], str)
        assert isinstance(rule['action'], list)
        for action in rule['action']:
            ActionEnumsService.validate_action(action)
        return rule


__all__ = [
    'RolesRulesFilesParser',
]
