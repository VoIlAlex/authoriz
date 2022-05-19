import importlib


def resolve_object(import_path):
    *module_path_parts, object_name = import_path.split('.')
    module_path = '.'.join(module_path_parts)
    module = importlib.import_module(module_path)
    return getattr(module, object_name)


__all__ = [
    'resolve_object',
]
