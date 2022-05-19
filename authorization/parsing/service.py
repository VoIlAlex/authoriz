"""
Service functionality to deal with permissions parsing and
handling parsed rules.
"""

import importlib
from typing import List
from django.conf import settings

from authorization.namespaces.base import ActionEnumsService
from authorization.cache import get_user_allowed_actions_from_cache, save_user_allowed_actions_to_cache
from authorization.parsing.base import PermissionsParser
from authorization.utils.parsing import merge_raw_rules_lists


class RulesParsingService:
    # Initialization status data of service
    _initialized = False
    _init_statuses = {
        'setup_parsers': False,
        'parse_rules': False
    }

    # Parsers that is used for parsing
    _PARSERS: List[PermissionsParser] = []

    # Parsing results
    _RAW_RULES = []
    _PARSED_RULES = {}

    @classmethod
    def get_user_allowed_actions(cls, user_id, user_roles, params, use_cache=True, cache_prefix=None):
        """
        Get allowed actions for specified user with specified user roles
        from rules parsing data.
        """
        actions = None
        if use_cache:
            actions = get_user_allowed_actions_from_cache(
                user_id=user_id,
                user_roles=user_roles,
                params=params,
                cache_prefix=cache_prefix
            )
        if not use_cache or actions is None:
            params = {str(k): str(v) for k, v in params.items()}
            allowed_actions = {}
            for namespace in cls._PARSED_RULES:
                namespace_dict = cls._PARSED_RULES[namespace]
                for action in sorted(namespace_dict, key=lambda item: 1 if item == '*' else -1):
                    action_dict = namespace_dict[action]
                for target in ['*', *[f'role:{ur}' for ur in user_roles], str(user_id)]:
                    action_full_name = f'{namespace}:{action}'
                    action_params = ActionEnumsService.get_action_params(action_full_name)
                    if target.startswith('role:'):
                        if ':roles' not in action_dict:
                            continue
                        action_dict = action_dict[':roles']
                        target = target[5:]
                    if target not in action_dict:
                        continue
                    target_dict = action_dict[target]
                    for effect in target_dict:
                        effect_dict = target_dict[effect]
                        rule_dicts = []
                        param_dicts = [(0, effect_dict)]
                        while len(param_dicts):
                            i, param_dict = param_dicts.pop(0)
                            for param_value in ['*', params.get(action_params[i], None)]:
                                if param_value is None or param_value not in param_dict:
                                    continue

                                if i + 1 != len(action_params):
                                    param_dicts.append(
                                        (i + 1, param_dict[param_value])
                                    )
                                else:
                                    rule_dicts.append(
                                        param_dict[param_value]
                                    )

                        for rule_dict in rule_dicts:
                            if action_full_name in allowed_actions:
                                if allowed_actions[action_full_name]['rule'] > rule_dict['rule']:
                                    continue
                                else:
                                    allowed_actions[action_full_name] = {
                                        **rule_dict,
                                        'effect': effect
                                    }
                            else:
                                allowed_actions[action_full_name] = {
                                    **rule_dict,
                                    'effect': effect
                                }
            actions = cls._expand_actions(allowed_actions)
            save_user_allowed_actions_to_cache(
                user_id=user_id,
                user_roles=user_roles,
                params=params,
                data=actions,
                cache_prefix=cache_prefix
            )
        return actions

    @classmethod
    def initialize(cls, service_settings: dict = None):
        """
        Setup rules parsing service (parsers, rules).
        """
        service_settings = service_settings or getattr(settings, 'ACTION_RULES_SERVICE', {})
        if not service_settings.get('DISABLE_PARSING', False):
            cls._setup_parsers(service_settings)
            cls._parse_rules(service_settings)

    @classmethod
    def _setup_parsers(cls, service_settings: dict):
        """
        Get parser classes and initialize them.
        """
        cls._init_statuses['setup_parsers'] = False
        cls._PARSERS.clear()
        rules_parsers = service_settings.get('RULES_PARSERS', [])
        for parser_data in rules_parsers:
            parser_path = parser_data.get('parser')
            args = parser_data.get('args', tuple())
            kwargs = parser_data.get('kwargs', {})
            if hasattr(parser_path, '__call__'):
                parser = parser_path
            elif isinstance(parser_path, str):
                parser_package_name, parser_name = parser_path.rsplit('.', 1)
                parser_package = importlib.import_module(parser_package_name)
                parser = getattr(parser_package, parser_name)
            else:
                raise RuntimeError(f'Unexpected parser type {type(parser_path)}.')
            cls._PARSERS.append(parser(*args, **kwargs))
        cls._init_statuses['setup_parsers'] = True

    @classmethod
    def _parse_rules(cls, service_settings: dict):
        """
        Get and parse all the rules.
        """
        cls._init_statuses['parse_rules'] = False
        cls._RAW_RULES.clear()
        cls._PARSED_RULES.clear()
        assert cls._init_statuses['setup_parsers']
        raw_rules_lists = []
        parsed_rules = {}
        for parser in cls._PARSERS:
            raw_rules, parsed_rules = parser.parse(parsed_rules)
            raw_rules_lists.append(raw_rules)
        raw_rules = merge_raw_rules_lists(raw_rules_lists)
        cls._RAW_RULES = raw_rules
        cls._PARSED_RULES = parsed_rules
        cls._init_statuses['parse_rules'] = True

    @classmethod
    def _expand_actions(cls, actions: dict):
        """
        Get list of all actions without wildcards.
        """
        actions = {k: v for k, v in actions.items() if v['effect'] == 'allow'}
        final_actions = set()
        for action in actions:
            if action.endswith('*'):
                namespace, action_name = action.split(':')
                final_actions.update(ActionEnumsService.actions_by_namespace(namespace))
            else:
                final_actions.add(action)
        return list(final_actions)


__all__ = [
    'RulesParsingService',
]
