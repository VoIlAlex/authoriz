"""
Caching functionality for authorization module.
"""

import re
import json
from django.core.cache import caches
from django.conf import settings
from django.core.cache.backends import locmem
from django_redis.cache import RedisCache


class CacheManager:
    def __init__(self, client, cache_settings_key):
        self.client = client
        if isinstance(self.client, RedisCache):
            self.type = 'redis'
        else:
            self.type = 'mem'
        self.cache_settings_key = cache_settings_key

    def set(self, key, value, timeout=None):
        self.client.set(
            key=key,
            value=value,
            timeout=timeout
        )

    def get(self, key):
        return self.client.get(
            key=key,
            default=None
        )

    def keys(self, pattern):
        if self.type == 'redis':
            return self.client.keys(pattern)
        elif self.type == 'mem':
            location = settings.CACHES[self.cache_settings_key]['LOCATION']
            if location not in locmem._caches:
                return []
            local_caches = locmem._caches[location]
            keys = []
            r = re.compile(self.client.make_key(pattern))
            for k in local_caches:
                if r.match(k):
                    keys.append(k)
            return keys

    def delete(self, key):
        return self.client.delete(key)


cache = caches['default']
cache_settings_key = 'default'


cache_manager = CacheManager(
    client=cache,
    cache_settings_key=cache_settings_key
)


def build_key(namespace='actions', prefix=None, values=None, arrays=None, dicts=None):
    """
    Build redis key for specific params.
    """
    key = namespace
    if prefix:
        key += f'_{prefix}'
    arrays = arrays or []
    values = values or []
    dicts = dicts or {}
    if len(values) != 0:
        key += f'.{".".join(str(x) for x in values)}'
    for array in arrays:
        if len(array) != 0:
            key += f'.{",".join(str(x) for x in array)}'
    for d in dicts:
        if len(d) != 0:
            key += '.' + '&'.join([f"{str(key)}={str(value)}" for key, value in d.items()])
    return key


def save_user_allowed_actions_to_cache(user_id, user_roles, params, data, cache_prefix=None):
    key = build_key(
        prefix=cache_prefix,
        values=[user_id, 'uaa'],
        arrays=[
            user_roles
        ],
        dicts=[
            params
        ]
    )
    cache_manager.set(
        key=key,
        value=json.dumps(data)
    )


def get_user_allowed_actions_from_cache(user_id, user_roles, params, cache_prefix=None):
    key = build_key(
        prefix=cache_prefix,
        values=[user_id, 'uaa'],
        arrays=[
            user_roles
        ],
        dicts=[
            params
        ]
    )
    data = cache_manager.get(
        key=key
    )
    if data is None:
        return
    return json.loads(data)


def get_all_user_roles_from_cache(user_id, params, cache_prefix=None):
    key = build_key(
        prefix=cache_prefix,
        values=[
            user_id, 'aur'
        ],
        dicts=[
            params
        ]
    )
    data = cache_manager.get(
        key=key
    )
    if data is None:
        return
    return json.loads(data)


def save_all_user_roles_from_cache(user_id, params, data, cache_prefix=None):
    key = build_key(
        prefix=cache_prefix,
        values=[
            user_id, 'aur'
        ],
        dicts=[
            params
        ]
    )
    cache_manager.set(
        key=key,
        value=json.dumps(data),
    )


def clear_cache(namespace='actions', cache_prefix=None):
    """
    Clear all redis cache for namespace.
    """
    pattern = build_key(
        namespace=namespace,
        prefix=cache_prefix,
    )
    pattern += '.*'
    keys = cache_manager.keys(pattern)
    for key in keys:
        cache_manager.delete(key)


def clear_user_cache(user_id, namespace='actions', cache_prefix=None):
    """
    Clear specific user cache from redis.
    """
    key_pattern = namespace
    if cache_prefix:
        key_pattern += f'_{cache_prefix}'
    key_pattern += f'.{user_id}.*'
    keys = cache_manager.keys(key_pattern)
    for key in keys:
        if cache_manager.type == 'mem':
            first_part = key.split(namespace)[0]
            key = key[len(first_part):]
        cache_manager.delete(key)


__all__ = [
    'cache_manager',
    'build_key',
    'save_user_allowed_actions_to_cache',
    'get_user_allowed_actions_from_cache',
    'get_all_user_roles_from_cache',
    'save_all_user_roles_from_cache',
    'clear_cache',
    'clear_user_cache',
]
