from typing import List

from django.conf import settings
from rest_framework.test import APIClient, APITestCase, override_settings
from authorization.namespaces.base import ActionEnumsService
from authorization.dataclasses import PermissionsRule, ParsedAction
from authorization.tests.parsing.utils import (
    TestPermissionsParser, get_rule_for_role, get_rule,
    ActionsLookup, TestActionsService,
)


@override_settings(ACTION_RULES_SERVICE={
    **settings.ACTION_RULES_SERVICE,
    "DISABLE_PARSING": True
})
class TestPermissionsParsingOverriding(APITestCase):
    # Broad override narrow rules.
    def test_permissions_parsing_parsed_rules_override_1(self):
        """
        Test target-object-wide rules overriding by target-wide rule.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='some-user-id'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                        params={
                            'project_id': 2
                        }
                    )
                ],
                target='some-user-id'
            ),
            PermissionsRule(
                name='Rule 3',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='some-user-id'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='some-user-id',
                effect='allow',
                params=['1']
            )
        )
        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='some-user-id',
                effect='allow',
                params=['2']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='some-user-id',
                effect='deny',
                params=['*']
            )
        )

    def test_permissions_parsing_parsed_rules_override_2(self):
        """
        Test target-wide rules overriding by object-wide rule.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='some-user-id'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='*'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        # It does not override because it
        # only deny one object or objects set.
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='some-user-id',
                effect='allow',
                params=['*']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='*',
                effect='deny',
                params=['1']
            )
        )

    def test_permissions_parsing_parsed_rules_override_3(self):
        """
        Test object-wide rules overriding by action-wide rule.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='*'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='*'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='*',
                effect='allow',
                params=['1']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='*',
                effect='deny',
                params=['*']
            )
        )

    def test_permissions_parsing_parsed_rules_override_4(self):
        """
        Test action-wide rules overriding by namespace-target-object-wide rule.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='*'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='some-user-id'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        # It does not override because it
        # only deny one object or objects set.
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='*',
                effect='allow',
                params=['*']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='some-user-id',
                effect='deny',
                params=['1']
            )
        )

    def test_permissions_parsing_parsed_rules_override_5(self):
        """
        Test namespace-target-object-wide rules overriding by namespace-target-wide rule.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='some-user-id'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                    )
                ],
                target='some-user-id'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='some-user-id',
                effect='deny',
                params=['1']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='some-user-id',
                effect='deny',
                params=['*']
            )
        )

    def test_permissions_parsing_parsed_rules_override_6(self):
        """
        Test namespace-target-wide rules overriding by namespace-object-wide rule.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                    )
                ],
                target='some-user-id'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='*'
            ),
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        # It does not override because it
        # only deny one object or objects set.
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='some-user-id',
                effect='allow',
                params=['*']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='*',
                effect='deny',
                params=['1']
            )
        )

    def test_permissions_parsing_parsed_rules_override_7(self):
        """
        Test namespace-object-wide rules overriding by namespace-wide rule.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='*'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                    )
                ],
                target='*'
            ),
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='*',
                effect='deny',
                params=['1']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='*',
                effect='deny',
                params=['*']
            )
        )

    def test_permissions_parsing_parsed_rules_override_8(self):
        """
        Test target-wide rules overriding by action-wide rule.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='some-user-id'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='*'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='some-user-id',
                effect='deny',
                params=['*']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='*',
                effect='deny',
                params=['*']
            )
        )

    def test_permissions_parsing_parsed_rules_override_9(self):
        """
        Test action-wide rules overriding by namespace-wide rule.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='*'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                    )
                ],
                target='*'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='*',
                effect='allow',
                params=['*']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='*',
                effect='deny',
                params=['*']
            )
        )

    # The same width
    def test_permissions_parsing_parsed_rules_override_same_1(self):
        """
        Test target-object-wide overriding.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='some-user-id'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='some-user-id'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='some-user-id',
                effect='allow',
                params=['1']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='some-user-id',
                effect='deny',
                params=['1']
            )
        )

    def test_permissions_parsing_parsed_rules_override_same_2(self):
        """
        Test target-wide overriding.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject'
                    )
                ],
                target='some-user-id'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject'
                    )
                ],
                target='some-user-id'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='some-user-id',
                effect='allow',
                params=['*']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='some-user-id',
                effect='deny',
                params=['*']
            )
        )

    def test_permissions_parsing_parsed_rules_override_same_3(self):
        """
        Test object-wide overriding.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='*'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='*'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='*',
                effect='allow',
                params=['1']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='*',
                effect='deny',
                params=['1']
            )
        )

    def test_permissions_parsing_parsed_rules_override_same_4(self):
        """
        Test action-wide overriding.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='*'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='*'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='*',
                effect='allow',
                params=['*']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='RetrieveProject',
                target='*',
                effect='deny',
                params=['*']
            )
        )

    def test_permissions_parsing_parsed_rules_override_same_5(self):
        """
        Test namespace-target-object-wide overriding.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='some-user-id'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='some-user-id'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='some-user-id',
                effect='allow',
                params=['1']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='some-user-id',
                effect='deny',
                params=['1']
            )
        )

    def test_permissions_parsing_parsed_rules_override_same_6(self):
        """
        Test namespace-target-wide overriding.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*'
                    )
                ],
                target='some-user-id'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*'
                    )
                ],
                target='some-user-id'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='some-user-id',
                effect='allow',
                params=['*']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='some-user-id',
                effect='deny',
                params=['*']
            )
        )

    def test_permissions_parsing_parsed_rules_override_same_7(self):
        """
        Test namespace-object-wide overriding.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='*'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='*'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='*',
                effect='allow',
                params=['1']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='*',
                effect='deny',
                params=['1']
            )
        )

    def test_permissions_parsing_parsed_rules_override_same_8(self):
        """
        Test namespace-object-wide overriding.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                    )
                ],
                target='*'
            ),
            PermissionsRule(
                name='Rule 2',
                effect='deny',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                    )
                ],
                target='*'
            )
        ]
        parser = TestPermissionsParser(rules)

        raw_rules_after_parsing, parsed_rules = parser.parse({})

        self.assertIsNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='*',
                effect='allow',
                params=['*']
            )
        )
        self.assertIsNotNone(
            get_rule(
                parsed_rules=parsed_rules,
                namespace='prj',
                action_name='*',
                target='*',
                effect='deny',
                params=['*']
            )
        )


@override_settings(ACTION_RULES_SERVICE={
    **settings.ACTION_RULES_SERVICE,
    "DISABLE_PARSING": True
})
class TestUserAllowedActions(APITestCase):
    fixtures = [
        'authorization/tests/parsing/data/user.json',
        'authorization/tests/parsing/data/entity.json',
        'authorization/tests/parsing/data/project.json',
    ]

    def test_user_allowed_actions_1(self):
        """
        Test namespace-wide rules.
        """

        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                    )
                ],
                target='*'
            )
        ]

        service = TestActionsService(
            test_case=self,
            rules=rules,
            actions=ActionEnumsService.actions_by_namespace('prj'),
            lookup=ActionsLookup(
                user_id='12c95beb-2e7a-490e-a653-34ae37e9ff14',
                user_roles=['sg_admin'],
                params={
                    'project_id': 1
                }
            ),
        )
        service.test(
            res_same=True,
            res_different_params=True,
            res_different_target=True,
            res_different_target_params=True,
            res_no_params=True,
            res_no_target=True,
            res_no_target_params=True
        )

    def test_user_allowed_actions_2(self):
        """
        Test namespace-object-wide rules.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='*'
            )
        ]

        service = TestActionsService(
            test_case=self,
            rules=rules,
            actions=ActionEnumsService.actions_by_namespace('prj'),
            lookup=ActionsLookup(
                user_id='12c95beb-2e7a-490e-a653-34ae37e9ff14',
                user_roles=['sg_admin'],
                params={
                    'project_id': 1
                }
            ),
        )
        service.test(
            res_same=True,
            res_different_params=False,
            res_different_target=True,
            res_different_target_params=False,
            res_no_params=False,
            res_no_target=True,
            res_no_target_params=False
        )

    def test_user_allowed_actions_3(self):
        """
        Test namespace-target-wide rules.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                    )
                ],
                target='12c95beb-2e7a-490e-a653-34ae37e9ff14'
            )
        ]

        service = TestActionsService(
            test_case=self,
            rules=rules,
            actions=ActionEnumsService.actions_by_namespace('prj'),
            lookup=ActionsLookup(
                user_id='12c95beb-2e7a-490e-a653-34ae37e9ff14',
                user_roles=['sg_admin'],
                params={
                    'project_id': 1
                }
            ),
        )
        service.test(
            res_same=True,
            res_different_params=True,
            res_different_target=False,
            res_different_target_params=False,
            res_no_params=True,
            res_no_target=False,
            res_no_target_params=False
        )

    def test_user_allowed_actions_4(self):
        """
        Test namespace-target-object-wide rules.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='*',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='12c95beb-2e7a-490e-a653-34ae37e9ff14'
            )
        ]

        service = TestActionsService(
            test_case=self,
            rules=rules,
            actions=ActionEnumsService.actions_by_namespace('prj'),
            lookup=ActionsLookup(
                user_id='12c95beb-2e7a-490e-a653-34ae37e9ff14',
                user_roles=['sg_admin'],
                params={
                    'project_id': 1
                }
            ),
        )
        service.test(
            res_same=True,
            res_different_params=False,
            res_different_target=False,
            res_different_target_params=False,
            res_no_params=False,
            res_no_target=False,
            res_no_target_params=False
        )

    def test_user_allowed_actions_5(self):
        """
        Test action-wide rules.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='*'
            )
        ]

        service = TestActionsService(
            test_case=self,
            rules=rules,
            actions=['prj:RetrieveProject'],
            lookup=ActionsLookup(
                user_id='12c95beb-2e7a-490e-a653-34ae37e9ff14',
                user_roles=['sg_admin'],
                params={
                    'project_id': 1
                }
            ),
        )
        service.test(
            res_same=True,
            res_different_params=True,
            res_different_target=True,
            res_different_target_params=True,
            res_no_params=True,
            res_no_target=True,
            res_no_target_params=True
        )

    def test_user_allowed_actions_6(self):
        """
        Test object-wide rules.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='*'
            )
        ]

        service = TestActionsService(
            test_case=self,
            rules=rules,
            actions=['prj:RetrieveProject'],
            lookup=ActionsLookup(
                user_id='12c95beb-2e7a-490e-a653-34ae37e9ff14',
                user_roles=['sg_admin'],
                params={
                    'project_id': 1
                }
            ),
        )
        service.test(
            res_same=True,
            res_different_params=False,
            res_different_target=True,
            res_different_target_params=False,
            res_no_params=False,
            res_no_target=True,
            res_no_target_params=False
        )

    def test_user_allowed_actions_7(self):
        """
        Test target-wide rules.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                    )
                ],
                target='12c95beb-2e7a-490e-a653-34ae37e9ff14'
            )
        ]

        service = TestActionsService(
            test_case=self,
            rules=rules,
            actions=['prj:RetrieveProject'],
            lookup=ActionsLookup(
                user_id='12c95beb-2e7a-490e-a653-34ae37e9ff14',
                user_roles=['sg_admin'],
                params={
                    'project_id': 1
                }
            ),
        )
        service.test(
            res_same=True,
            res_different_params=True,
            res_different_target=False,
            res_different_target_params=False,
            res_no_params=True,
            res_no_target=False,
            res_no_target_params=False
        )

    def test_user_allowed_actions_8(self):
        """
        Test target-object-wide rules.
        """
        rules = [
            PermissionsRule(
                name='Rule 1',
                effect='allow',
                actions=[
                    ParsedAction(
                        namespace='prj',
                        action_name='RetrieveProject',
                        params={
                            'project_id': 1
                        }
                    )
                ],
                target='12c95beb-2e7a-490e-a653-34ae37e9ff14'
            )
        ]

        service = TestActionsService(
            test_case=self,
            rules=rules,
            actions=['prj:RetrieveProject'],
            lookup=ActionsLookup(
                user_id='12c95beb-2e7a-490e-a653-34ae37e9ff14',
                user_roles=['sg_admin'],
                params={
                    'project_id': 1
                }
            ),
        )
        service.test(
            res_same=True,
            res_different_params=False,
            res_different_target=False,
            res_different_target_params=False,
            res_no_params=False,
            res_no_target=False,
            res_no_target_params=False
        )
