
from functools import wraps


def init_required(check_func):
    """
    Decorator to specify condition
    to call a function.
    """
    def decorator(func):
        @wraps(func)
        def _func(*args, **kwargs):
            assert check_func()
            return func(*args, **kwargs)
        return _func
    return decorator


__all__ = [
    'init_required',
]
