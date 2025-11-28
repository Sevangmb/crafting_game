from django.db import models

class Quest(models.Model):
    """Quests/missions that players can complete"""
    QUEST_TYPES = [
        ('gather', 'Récolter'),
        ('craft', 'Fabriquer'),
        ('explore', 'Explorer'),
        ('combat', 'Combat'),
        ('delivery', 'Livraison'),
        ('talk', 'Parler'),
    ]

    QUEST_DIFFICULTIES = [
        ('easy', 'Facile'),
        ('medium', 'Moyen'),
        ('hard', 'Difficile'),
        ('epic', 'Épique'),
    ]

    # Basic info
    name = models.CharField(max_length=200)
    description = models.TextField()
    story_text = models.TextField(blank=True, help_text="Narration / contexte de la quête")
    icon = models.CharField(max_length=50, default='📜')

    # Quest properties
    quest_type = models.CharField(max_length=20, choices=QUEST_TYPES)
    difficulty = models.CharField(max_length=20, choices=QUEST_DIFFICULTIES, default='easy')
    required_level = models.IntegerField(default=1, help_text="Niveau minimum requis")

    # Requirements (stored as JSON for flexibility)
    requirements = models.JSONField(default=dict, help_text="""
    Format: {
        'gather': [{'material_id': 1, 'quantity': 10}],
        'craft': [{'recipe_id': 5, 'quantity': 3}],
        'visit': [{'grid_x': 5, 'grid_y': 10}],
        'defeat': [{'mob_id': 2, 'quantity': 5}]
    }
    """)

    # Rewards
    reward_xp = models.IntegerField(default=0)
    reward_money = models.IntegerField(default=0)
    reward_items = models.JSONField(default=list, help_text="[{'material_id': 1, 'quantity': 5}]")

    # Quest chain
    chain_id = models.CharField(max_length=50, blank=True, null=True, help_text="Identifiant de la chaîne de quêtes")
    chain_order = models.IntegerField(default=0, help_text="Position dans la chaîne (0 = quête indépendante)")
    prerequisite_quest = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='next_quests')
    is_repeatable = models.BooleanField(default=False)
    is_daily = models.BooleanField(default=False, help_text="Quête quotidienne qui se reset automatiquement")
    cooldown_hours = models.IntegerField(default=24, help_text="Hours before quest can be repeated")

    # Availability
    is_active = models.BooleanField(default=True)
    start_npc = models.CharField(max_length=100, blank=True, help_text="PNJ qui donne la quête")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['required_level', 'name']

    def __str__(self):
        return f"{self.icon} {self.name} ({self.get_difficulty_display()})"


class PlayerQuest(models.Model):
    """Tracks player progress on quests"""
    QUEST_STATUS = [
        ('available', 'Disponible'),
        ('active', 'En cours'),
        ('completed', 'Terminée'),
        ('failed', 'Échouée'),
        ('abandoned', 'Abandonnée'),
    ]

    player = models.ForeignKey('game.Player', on_delete=models.CASCADE, related_name='quests')
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name='player_quests')
    status = models.CharField(max_length=20, choices=QUEST_STATUS, default='available')

    # Progress tracking (stored as JSON)
    progress = models.JSONField(default=dict, help_text="""
    Format: {
        'gather': {'material_1': 5, 'material_2': 10},
        'craft': {'recipe_5': 2},
        'visit': {'5,10': True},
        'defeat': {'mob_2': 3}
    }
    """)

    # Timestamps
    accepted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    can_repeat_at = models.DateTimeField(null=True, blank=True, help_text="When quest can be repeated")

    # Stats
    times_completed = models.IntegerField(default=0)

    class Meta:
        unique_together = ('player', 'quest')
        ordering = ['-accepted_at']

    def __str__(self):
        return f"{self.player.user.username} - {self.quest.name} ({self.get_status_display()})"

    def progress_percentage(self):
        """Calculate completion percentage"""
        if not self.quest.requirements:
            return 0

        total_tasks = 0
        completed_tasks = 0

        for task_type, tasks in self.quest.requirements.items():
            for task in tasks:
                total_tasks += 1
                # Check if this task is completed in progress
                if task_type in self.progress:
                    task_key = str(task.get('material_id') or task.get('recipe_id') or task.get('mob_id') or f"{task.get('grid_x')},{task.get('grid_y')}")
                    if task_key in self.progress[task_type]:
                        required = task.get('quantity', 1)
                        current = self.progress[task_type][task_key]
                        if current >= required:
                            completed_tasks += 1

        return int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
