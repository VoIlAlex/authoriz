from authoriz import config


def get_service_settings():
    return {
        'RULES_PARSERS': config.RULES_PARSERS,
        'DISABLE_PARSING': config.DISABLE_PARSING,
        'DISABLE_PERMISSIONS_CHECK': config.DISABLE_PERMISSIONS_CHECK
    }
