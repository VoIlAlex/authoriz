from django.apps import AppConfig

from authorization.cache import clear_cache
from authorization.parsing.service import RulesParsingService


class AuthorizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authorization'

    def ready(self):
        RulesParsingService.initialize()
        clear_cache()
