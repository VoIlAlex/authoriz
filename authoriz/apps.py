from django.apps import AppConfig

from authoriz.cache import clear_cache
from authoriz.parsing.service import RulesParsingService


class AuthorizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authorization'

    def ready(self):
        RulesParsingService.initialize()
        clear_cache()
