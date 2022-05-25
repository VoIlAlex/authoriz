from authoriz.config import ROLE_CLASSES
from authoriz.utils.resolving import resolve_object


def get_all_roles():
    all_roles = []
    for role_class in ROLE_CLASSES:
        class_descriptor = role_class['class']
        if isinstance(class_descriptor, str):
            cls = resolve_object(class_descriptor)
        else:
            cls = class_descriptor
        all_roles += list(cls.values)
    return all_roles


def get_user_roles_by_param(user_id, param_name, param_value):
    roles = set()
    for role_class in ROLE_CLASSES:
        roles_by_class = set()
        for getter in [x for x in role_class['getters'] if x['key'] == param_name]:
            roles_by_getter = set(getter['getter'](user_id, param_value))
            if len(roles_by_class) == 0:
                roles_by_class = roles_by_getter
            else:
                roles_by_class &= roles_by_getter
        roles |= roles_by_class
    return roles


__all__ = [
    'get_all_roles',
]
