"""
Base functionality for permissions parsing.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

from authoriz.namespaces.base import ActionEnumsService
from authoriz.dataclasses import ParsedAction, PermissionsRule


class PermissionsParser(ABC):
    """
    A base class to all parsers that implement a functionality to
    parse all retrieved rules into a dict with overriding of each
    subsequent rule.
    """
    RULE_NEXT_ID = 1

    def parse(self, parsed_rules) -> Tuple[list, dict]:
        """
        Get raw rules and and parsed rules.
        """
        rules = self.get_rules()
        rules.sort(key=lambda r: r.id)
        for rule in rules:
            for action in rule.actions:
                self._apply_action(
                    parsed_rules=parsed_rules,
                    id_=rule.id,
                    action=action,
                    effect=rule.effect,
                    target=rule.target
                )
        return rules, parsed_rules

    @abstractmethod
    def get_rules(self) -> List[PermissionsRule]:
        """
        Abstract method to retrieve rules. It can be used
        to retrieve rules from any sources like files, database,
        API or anything else.
        """
        ...

    @staticmethod
    def _clean_dependant_rule(parsed_rules: dict,
                              action: ParsedAction,
                              target: str):
        """
        Clean rules that should be overridden by subsequent one.
        """
        params = ActionEnumsService.get_action_params(action.full_name)

        if action.action_name == '*':
            actions_to_override = ['*',
                                   *ActionEnumsService.actions_by_namespace(action.namespace, with_namespace=False)]
        else:
            actions_to_override = [action.action_name]

        for i, param in enumerate(params):
            if param in action.params:
                override_from_param = (i, param)
                break
        else:
            if len(params) != 0:
                override_from_param = (0, params[0])
            else:
                override_from_param = None

        override_for_role = None
        if target.startswith('role:'):
            override_for_role = target.split(':')[1]

        # Remove overridden rules
        if action.namespace in parsed_rules:
            namespace_dict = parsed_rules[action.namespace]

            for action_to_override in actions_to_override:
                if action_to_override in namespace_dict:
                    action_dict = namespace_dict[action_to_override]

                    if override_for_role:
                        if ':roles' in action_dict:
                            roles_dict = action_dict[':roles']
                        else:
                            continue

                        if override_for_role in roles_dict:
                            target_dict = roles_dict[override_for_role]
                        else:
                            continue
                    else:
                        target_dict = None

                    if override_from_param is None:
                        if target_dict:
                            target_dicts = [target_dict]
                        else:
                            target_dicts = []
                            if target == '*':
                                for target_key in action_dict:
                                    if target_key == ':roles':
                                        continue
                                    target_dicts.append(action_dict[target_key])
                            else:
                                if target in action_dict:
                                    target_dicts = [action_dict[target]]
                                else:
                                    target_dict = action_dict[target] = {}
                                    target_dicts.append(target_dict)

                        for target_dict in target_dicts:
                            target_dict.clear()

                    else:
                        if override_from_param[1] in action.params:
                            param_value = action.params[override_from_param[1]]
                        else:
                            param_value = '*'

                        if target_dict:
                            target_dicts = [target_dict]
                        else:
                            target_dicts = []
                            if target == '*':
                                for target_key in action_dict:
                                    if target_key == ':roles':
                                        continue
                                    target_dicts.append(action_dict[target_key])
                            else:
                                if target in action_dict:
                                    target_dicts = [action_dict[target]]
                                else:
                                    target_dict = action_dict[target] = {}
                                    target_dicts.append(target_dict)

                        for target_dict in target_dicts:
                            if len(target_dict) != 0:
                                for effect_key in ['allow', 'deny']:
                                    if effect_key in target_dict:
                                        effect_dict = target_dict[effect_key]
                                        param_parsed_dict = effect_dict
                                        to_continue = False
                                        for i, param_name in enumerate(params):
                                            if i == override_from_param[0]:
                                                break
                                            if '*' not in param_parsed_dict:
                                                to_continue = True
                                                break
                                            param_parsed_dict: dict = param_parsed_dict['*']
                                        if to_continue:
                                            continue

                                        if param_value == '*':
                                            param_parsed_dict.clear()
                                        else:
                                            if param_value in param_parsed_dict:
                                                del param_parsed_dict[param_value]

    @staticmethod
    def _apply_action(parsed_rules: dict,
                      id_: int,
                      action: ParsedAction,
                      effect: str,
                      target: str):
        """
        Apply to any parsed rule and "under"-rule. Apply order is:

            0. Roles-wide rules.

            1. Namespace-wide rules.
            np -> * -> * -> Allow -> *
            np -> * -> * -> Deny -> *

            2. Namespace-object-wide rules.
            np -> * -> * -> Allow -> project_id
            np -> * -> * -> Deny -> project_id
            ...

            3. Namespace-target-wide rules.
            np -> * -> user_id -> Allow -> *
            np -> * -> user_id -> Deny -> *

            4. Namespace-target-object-wide rules.
            np -> * -> user_id -> Allow -> project_id
            np -> * -> user_id -> Deny -> project_id
            ...

            5. Action-wide rules.
            np -> UpdateProject -> * -> Allow -> *
            np -> UpdateProject -> * -> Deny -> *

            6. Action-object-wide rules.
            np -> UpdateProject -> * -> Allow -> project_id
            np -> UpdateProject -> * -> Deny -> project_id
            ...

            7. Action-target-wide rules.
            np -> UpdateProject -> user_id -> Allow -> *
            np -> UpdateProject -> user_id -> Deny -> *

            8. Action-target-object-wide rules.
            np -> UpdateProject -> user_id -> Allow -> project_id
            np -> UpdateProject -> user_id -> Deny -> project_id
            ...
        """
        PermissionsParser._clean_dependant_rule(
            parsed_rules=parsed_rules,
            action=action,
            target=target
        )

        def get_or_create_value(d, key):
            if key in d:
                return d[key]
            else:
                d[key] = {}
                return d[key]

        namespace_dict = get_or_create_value(
            parsed_rules,
            action.namespace
        )
        action_dict = get_or_create_value(
            namespace_dict,
            action.action_name
        )
        if target.startswith('role:'):
            target = target.split(':')[1]
            action_dict = get_or_create_value(
                action_dict,
                ':roles'
            )

        target_dict = get_or_create_value(
            action_dict,
            target
        )
        params = ActionEnumsService.get_action_params(action.full_name)
        effect_dict = get_or_create_value(
            target_dict,
            effect
        )
        result_dict = effect_dict
        for param in params:
            param_value = action.params.get(param, '*')
            result_dict = get_or_create_value(
                result_dict,
                param_value
            )

        result_dict['rule'] = id_


__all__ = [
    'PermissionsParser',
]
