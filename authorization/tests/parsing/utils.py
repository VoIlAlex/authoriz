from copy import deepcopy
from dataclasses import dataclass, field
from typing import List

from authorization.dataclasses import PermissionsRule
from authorization.parsing.base import PermissionsParser
from authorization.parsing.service import RulesParsingService


class TestPermissionsParser(PermissionsParser):
    def __init__(self, rules: List[PermissionsRule], *args, **kwargs):
        super(TestPermissionsParser, self).__init__(*args, **kwargs)
        self.rules = rules

    def get_rules(self) -> List[PermissionsRule]:
        return self.rules


def get_rule_for_role(parsed_rules: dict,
                      namespace: str,
                      action_name: str,
                      target_role: str,
                      params: List[str],
                      effect: str):
    effect_dict = parsed_rules.get(
        namespace,
        {}
    ).get(
        action_name,
        {}
    ).get(
        ':roles',
        {}
    ).get(
        target_role,
        {}
    ).get(
        effect,
        {}
    )

    if len(effect_dict) == 0:
        return None

    param_dict = effect_dict
    for param in params:
        param_dict = param_dict.get(param, {})

    return param_dict.get('rule', None)


def get_rule(parsed_rules: dict,
             namespace: str,
             action_name: str,
             target: str,
             params: List[str],
             effect: str):

    effect_dict = parsed_rules.get(
        namespace,
        {}
    ).get(
        action_name,
        {}
    ).get(
        target,
        {}
    ).get(
        effect,
        {}
    )

    if len(effect_dict) == 0:
        return None

    param_dict = effect_dict
    for param in params:
        param_dict = param_dict.get(param, {})

    return param_dict.get('rule', None)


def setup_test_parser(rules):
    RulesParsingService.initialize({
        'RULES_PARSERS': [
            {
                'parser': TestPermissionsParser,
                'args': [rules],
            }
        ]
    })


@dataclass
class ActionsLookup:
    user_id: str
    user_roles: List[str]
    params: dict = field(default_factory=lambda: {})

    def without_params(self):
        copy = deepcopy(self)
        copy.params = {}
        return copy

    def without_user_roles(self):
        copy = deepcopy(self)
        copy.user_roles = []
        return copy

    def without_user_id(self):
        copy = deepcopy(self)
        copy.user_id = '*'
        return copy

    def different_params(self):
        copy = deepcopy(self)
        for param in copy.params:
            copy.params[param] = int(copy.params[param]) + 1
        return copy

    def different_user_id(self):
        copy = deepcopy(self)
        if copy.user_id == '*':
            return copy
        else:
            copy.user_id = copy.user_id[:-1] + 'x'
        return copy


def test_actions(self, lookup: ActionsLookup, actions: List[str], reverse=False, exact=False):
    allowed_actions = RulesParsingService.get_user_allowed_actions(
        user_id=lookup.user_id,
        user_roles=lookup.user_roles,
        params=lookup.params,
        use_cache=False,
        cache_prefix='test'
    )
    if not reverse:
        assert_equal = self.assertEqual
        assert_true = self.assertTrue
    else:
        assert_equal = self.assertNotEqual
        assert_true = self.assertFalse

    if exact:
        assert_equal(len(allowed_actions), len(actions))
    for action in actions:
        assert_true(action in allowed_actions)


class TestActionsService:
    def __init__(self, test_case, rules, actions, lookup: ActionsLookup):
        self.test_case = test_case
        self.rules = rules
        self.actions = actions
        self.lookup = lookup

    def test(self,
             res_same=None,
             res_different_params=None,
             res_different_target=None,
             res_different_target_params=None,
             res_no_params=None,
             res_no_target=None,
             res_no_target_params=None):
        setup_test_parser(self.rules)

        if res_same is not None:
            test_actions(
                self.test_case,
                self.lookup,
                self.actions,
                exact=True,
                reverse=not res_same
            )

        if res_different_params is not None:
            test_actions(
                self.test_case,
                self.lookup.different_params(),
                self.actions,
                exact=True,
                reverse=not res_different_params
            )
        if res_different_target is not None:
            test_actions(
                self.test_case,
                self.lookup.different_user_id(),
                self.actions,
                exact=True,
                reverse=not res_different_target
            )
        if res_different_target_params:
            test_actions(
                self.test_case,
                self.lookup.different_user_id().different_params(),
                self.actions,
                exact=True,
                reverse=not res_different_target_params
            )
        if res_no_target:
            test_actions(
                self.test_case,
                self.lookup.without_user_id(),
                self.actions,
                exact=True,
                reverse=not res_no_target
            )
        if res_no_params:
            test_actions(
                self.test_case,
                self.lookup.without_params(),
                self.actions,
                exact=True,
                reverse=not res_no_params
            )
        if res_no_target_params:
            test_actions(
                self.test_case,
                self.lookup.without_user_id().without_params(),
                self.actions,
                exact=True,
                reverse=not res_no_target_params
            )
