"""
Custom throttling classes for game actions
"""
from rest_framework.throttling import UserRateThrottle


class GameActionThrottle(UserRateThrottle):
    """
    Throttle for game actions like move, gather, craft
    Rate: 120 requests per minute
    """
    scope = 'game_action'


class LoginThrottle(UserRateThrottle):
    """
    Throttle for login attempts
    Rate: 10 requests per hour
    """
    scope = 'login'

    def allow_request(self, request, view):
        # Only apply to login endpoint
        if request.path.endswith('/auth/login/'):
            return super().allow_request(request, view)
        return True
