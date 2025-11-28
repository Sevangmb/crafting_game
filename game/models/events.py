from django.db import models

class DynamicEvent(models.Model):
    """Random events that occur on the map"""
    EVENT_TYPES = [
        ('treasure', 'Trésor'),
        ('merchant', 'Marchand ambulant'),
        ('danger', 'Danger'),
        ('resource', 'Ressources abondantes'),
        ('weather', 'Météo'),
    ]

    # Event info
    name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='✨')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)

    # Location
    cell = models.ForeignKey('game.MapCell', on_delete=models.CASCADE, related_name='events')

    # Rewards/Effects (JSON)
    rewards = models.JSONField(default=dict, help_text="""
    {
        'xp': 50,
        'money': 100,
        'items': [{'material_id': 1, 'quantity': 5}],
        'gather_multiplier': 2.0
    }
    """)

    # Duration
    started_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    # Availability
    is_active = models.BooleanField(default=True)
    max_participants = models.IntegerField(default=-1, help_text="-1 = unlimited")
    participants = models.ManyToManyField('game.Player', related_name='participated_events', blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.icon} {self.name} at ({self.cell.grid_x}, {self.cell.grid_y})"

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def can_participate(self, player):
        if not self.is_active or self.is_expired():
            return False
        if self.max_participants > 0 and self.participants.count() >= self.max_participants:
            return False
        return player not in self.participants.all()
