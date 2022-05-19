import os

from django.conf import settings
from rest_framework.test import APIClient, APITestCase, override_settings
from authorization.dataclasses import ParsedAction


@override_settings(ACTION_RULES_SERVICE={
    **settings.ACTION_RULES_SERVICE,
    "DISABLE_PARSING": True
})
class TestDataclasses(APITestCase):
    fixtures = [
        os.path.join(os.getcwd(), 'rest_api/tests/test_entities/data/user.json'),
        os.path.join(os.getcwd(), 'rest_api/tests/test_entities/data/entity.json')
    ]

    def test_parsed_action_1(self):
        action = ParsedAction(
            namespace='prj',
            action_name='RetrieveProject',
            params={
                'project_id': '1'
            }
        )

        self.assertEqual(action.namespace, 'prj')
        self.assertEqual(action.action_name, 'RetrieveProject')
        self.assertEqual(action.params, {
            'project_id': '1'
        })

    def test_parsed_action_2(self):
        action = ParsedAction(
            namespace='prj',
            action_name='RetrieveProject',
            params={
                'project_id': 1
            }
        )

        self.assertEqual(action.namespace, 'prj')
        self.assertEqual(action.action_name, 'RetrieveProject')
        self.assertEqual(action.params, {
            'project_id': '1'
        })

    def test_parsed_action_3(self):
        action = ParsedAction(
            namespace='prj',
            action_name='RetrieveProject'
        )

        self.assertEqual(action.namespace, 'prj')
        self.assertEqual(action.action_name, 'RetrieveProject')
        self.assertEqual(action.params, {})

    def test_parsed_action_exception_1(self):
        with self.assertRaises(Exception):
            _ = ParsedAction(
                namespace='prj',
                action_name='retrieveproject',
                params={
                    'project_id': 1
                }
            )

    def test_parsed_action_exception_2(self):
        with self.assertRaises(Exception):
            _ = ParsedAction(
                namespace='prj',
                action_name='SomeAction',
                params={
                    'project_id': 1
                }
            )

    def test_parsed_action_exception_3(self):
        with self.assertRaises(Exception):
            _ = ParsedAction(
                namespace='Prj',
                action_name='RetrieveProject',
                params={
                    'project_id': 1
                }
            )

    def test_parsed_action_exception_4(self):
        with self.assertRaises(Exception):
            _ = ParsedAction(
                namespace='Prj',
                action_name='RetrieveProject',
                params={
                    'project_id': 1,
                    'wrong_param': 1
                }
            )
