from django.conf import settings


"""
List of the role enum classes. With configuration.

Example:
[
    {
        "enum": "path.to.RoleClass",
        "user_relation_class": "path.to.UserRelationClass",
        "getters": [
            {
                "key": None,
                "getter": func(user_id)
            },
            {
                "key": "project_id",
                "getter": func(user_id, project_id)
            }
        ]
    }
]
"""
ROLE_CLASSES = getattr(settings, 'AUTHORIZ_ALL_ROLE_CLASSES', [])

"""
List of the rules parsers in the correct order.

Example:
[
    {
        'parser': 'authoriz.parsing.parsers.RolesRulesFilesParser',
        'args': [None],
        'kwargs': {
            'rules_dir': os.path.join(
                BASE_DIR,
                'rules'
            )
        },
    }
]
"""
RULES_PARSERS = getattr(settings, 'AUTHORIZ_RULES_PARSERS', [])

# Disables / enables parsing in the project.
DISABLE_PARSING = getattr(settings, 'AUTHORIZ_DISABLE_PARSING', False)

# Disables / enables permissions check in the views.
DISABLE_PERMISSIONS_CHECK = getattr(settings, 'AUTHORIZ_DISABLE_PERMISSIONS_CHECK', True)
