from django.db import models

class Leaderboard(models.Model):
    """Leaderboard entries for various categories"""
    CATEGORY_CHOICES = [
        ('level', 'Niveau'),
        ('wealth', 'Richesse'),
        ('gatherer', 'Récolteur'),
        ('crafter', 'Artisan'),
        ('explorer', 'Explorateur'),
        ('combatant', 'Combattant'),
        ('quests', 'Quêtes'),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    player = models.ForeignKey('game.Player', on_delete=models.CASCADE, related_name='leaderboard_entries')
    score = models.BigIntegerField(default=0)
    rank = models.IntegerField(default=0)

    # Additional context (JSON)
    metadata = models.JSONField(default=dict, help_text="""
    {
        'level': 15,
        'total_gathered': 1000,
        'total_crafted': 500,
        etc.
    }
    """)

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('category', 'player')
        ordering = ['category', 'rank']
        indexes = [
            models.Index(fields=['category', 'rank']),
        ]

    def __str__(self):
        return f"#{self.rank} {self.player.user.username} - {self.get_category_display()}: {self.score}"
