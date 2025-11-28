"""
Cache utilities for game data
"""
from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json


def get_cache_key(prefix, *args, **kwargs):
    """Generate a unique cache key from prefix and arguments"""
    key_parts = [prefix]
    for arg in args:
        key_parts.append(str(arg))
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    key_string = ":".join(key_parts)
    # Hash long keys to keep them short
    if len(key_string) > 200:
        key_string = hashlib.md5(key_string.encode()).hexdigest()
    return key_string


def cache_view_response(timeout_key, key_prefix):
    """
    Decorator to cache view responses
    Usage:
        @cache_view_response('materials', 'materials_list')
        def list(self, request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip caching for non-GET requests
            request = args[1] if len(args) > 1 else kwargs.get('request')
            if request and request.method != 'GET':
                return func(*args, **kwargs)

            # Generate cache key
            cache_key = get_cache_key(key_prefix, request.user.id if request and request.user.is_authenticated else 'anon')

            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response

            # Call the function
            response = func(*args, **kwargs)

            # Cache the response
            timeout = settings.CACHE_TTL.get(timeout_key, 300)
            cache.set(cache_key, response, timeout)

            return response
        return wrapper
    return decorator


def invalidate_cache(pattern):
    """Invalidate cache keys matching a pattern"""
    # Note: This is a simple implementation
    # For production, consider using Redis with pattern matching
    cache.delete_many([pattern])


def cache_queryset(timeout_key, key_prefix):
    """
    Decorator to cache queryset results
    Usage:
        @cache_queryset('materials', 'all_materials')
        def get_all_materials():
            return Material.objects.all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = get_cache_key(key_prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Call the function
            result = func(*args, **kwargs)

            # Cache the result
            timeout = settings.CACHE_TTL.get(timeout_key, 300)
            cache.set(cache_key, result, timeout)

            return result
        return wrapper
    return decorator


class CacheManager:
    """Manager class for cache operations"""

    @staticmethod
    def clear_player_cache(player_id):
        """Clear all cache for a specific player"""
        patterns = [
            f'player_data:{player_id}',
            f'inventory:{player_id}',
            f'skills:{player_id}',
            f'equipment:{player_id}',
        ]
        cache.delete_many(patterns)

    @staticmethod
    def clear_game_data_cache():
        """Clear all game data cache (materials, recipes, etc.)"""
        patterns = [
            'materials_list',
            'recipes_list',
            'workstations_list',
            'game_config',
        ]
        cache.delete_many(patterns)

    @staticmethod
    def clear_all():
        """Clear all cache"""
        cache.clear()
