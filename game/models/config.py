from django.db import models

class GameConfig(models.Model):
    """Global game configuration settings"""
    key = models.CharField(max_length=100, unique=True, help_text="Configuration key (unique identifier)")
    value = models.TextField(help_text="Configuration value (can be JSON for complex values)")
    description = models.TextField(blank=True, default='', help_text="Description of what this configuration does")
    last_modified = models.DateTimeField(auto_now=True, help_text="Last time this configuration was modified")

    class Meta:
        verbose_name = "Game Configuration"
        verbose_name_plural = "Game Configurations"
        ordering = ['key']

    def get_value(self):
        """Parse JSON value or return string"""
        import json
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value

    def set_value(self, value):
        """Store value as JSON string"""
        import json
        self.value = json.dumps(value)

    @classmethod
    def get_config(cls, key, default=None):
        """Get configuration value with default fallback"""
        try:
            config = cls.objects.get(key=key)
            return config.get_value()
        except cls.DoesNotExist:
            return default

    def save(self, *args, **kwargs):
        """Override save to clear configuration cache"""
        super().save(*args, **kwargs)
        # Clear the configuration cache when a config is updated
        from game.utils.config_helper import clear_config_cache
        clear_config_cache()

    def __str__(self):
        value_preview = str(self.value)[:30]
        if len(str(self.value)) > 30:
            value_preview += "..."
        return f"{self.key} = {value_preview}"
