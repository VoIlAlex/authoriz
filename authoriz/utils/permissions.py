class SkipPermission:
    """
    Return it with getter in permission class
    to skip permission check.
    """
    @staticmethod
    def check(obj):
        if isinstance(obj, SkipPermission):
            return True
        return False


class DenyPermission:
    """
    Return it with getter in permission class
    to deny access.
    """
    @staticmethod
    def check(obj):
        if isinstance(obj, DenyPermission):
            return True
        return False


__all__ = [
    'SkipPermission',
    'DenyPermission',
]
