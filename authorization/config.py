from django.conf import settings


"""
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
ROLE_CLASSES = getattr(settings, 'AUTHORIZATION_ALL_ROLE_CLASSES', [])
