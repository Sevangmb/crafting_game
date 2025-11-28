"""
Time service for managing real-time game clock
Uses actual real-world time (1:1 ratio)
"""
from django.utils import timezone
from datetime import datetime


class TimeService:
    """Service for managing real-time game clock"""
    
    # Day/night cycle times (in hours, 24-hour format)
    SUNRISE = 6
    MORNING_END = 12
    AFTERNOON_END = 18
    SUNSET = 20
    NIGHT_END = 6  # Next day
    
    @staticmethod
    def get_current_game_time(player=None):
        """
        Get current real-time
        Returns current datetime (no acceleration)
        """
        return timezone.now()
    
    @staticmethod
    def get_day_number(player=None):
        """Get the current day of month"""
        game_time = TimeService.get_current_game_time(player)
        return game_time.day
    
    @staticmethod
    def get_time_of_day(player=None):
        """
        Get current time of day period
        Returns: 'morning', 'afternoon', 'evening', 'night'
        """
        game_time = TimeService.get_current_game_time(player)
        hour = game_time.hour
        
        if TimeService.SUNRISE <= hour < TimeService.MORNING_END:
            return 'morning'
        elif TimeService.MORNING_END <= hour < TimeService.AFTERNOON_END:
            return 'afternoon'
        elif TimeService.AFTERNOON_END <= hour < TimeService.SUNSET:
            return 'evening'
        else:
            return 'night'
    
    @staticmethod
    def is_daytime(player=None):
        """Check if it's currently daytime"""
        game_time = TimeService.get_current_game_time(player)
        hour = game_time.hour
        return TimeService.SUNRISE <= hour < TimeService.SUNSET
    
    @staticmethod
    def get_time_info(player=None):
        """
        Get comprehensive time information
        Returns dict with all time-related data
        """
        game_time = TimeService.get_current_game_time(player)
        time_of_day = TimeService.get_time_of_day(player)
        is_day = TimeService.is_daytime(player)
        day_number = TimeService.get_day_number(player)
        
        # Calculate sunrise/sunset times for today
        sunrise_time = game_time.replace(hour=TimeService.SUNRISE, minute=0, second=0)
        sunset_time = game_time.replace(hour=TimeService.SUNSET, minute=0, second=0)
        
        # Time of day icon
        time_icons = {
            'morning': '🌅',
            'afternoon': '☀️',
            'evening': '🌆',
            'night': '🌙'
        }
        
        # Time of day label (French)
        time_labels = {
            'morning': 'Matin',
            'afternoon': 'Après-midi',
            'evening': 'Soirée',
            'night': 'Nuit'
        }
        
        # Get date info
        month_names = [
            'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
            'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
        ]
        
        return {
            'current_time': game_time.strftime('%H:%M'),
            'current_time_full': game_time.strftime('%H:%M:%S'),
            'date': game_time.strftime('%d/%m/%Y'),
            'day_number': day_number,
            'month': game_time.month,
            'month_name': month_names[game_time.month - 1],
            'year': game_time.year,
            'time_of_day': time_of_day,
            'time_of_day_label': time_labels[time_of_day],
            'time_of_day_icon': time_icons[time_of_day],
            'is_daytime': is_day,
            'sunrise': sunrise_time.strftime('%H:%M'),
            'sunset': sunset_time.strftime('%H:%M'),
            'hour': game_time.hour,
            'minute': game_time.minute,
            'timestamp': game_time.isoformat()
        }
    
    @staticmethod
    def apply_time_effects(player):
        """
        Apply time-based effects to player
        (e.g., energy drain at night, bonuses during day)
        """
        time_of_day = TimeService.get_time_of_day(player)
        
        effects = {
            'energy_regen_mult': 1.0,
            'visibility_mult': 1.0,
            'spawn_rate_mult': 1.0
        }
        
        if time_of_day == 'night':
            # Night penalties/changes
            effects['visibility_mult'] = 0.7  # Reduced visibility
            effects['spawn_rate_mult'] = 1.5  # More dangerous at night
        elif time_of_day == 'morning':
            # Morning bonus
            effects['energy_regen_mult'] = 1.1  # Slight energy regen boost
        
        return effects
