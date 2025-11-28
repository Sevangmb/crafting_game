from django.db import models

class Skill(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name

class TalentNode(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='talents')
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    tier = models.IntegerField(default=1)
    xp_required = models.IntegerField(default=0)  # total_xp required to auto-unlock
    prereq_codes = models.JSONField(default=list, blank=True)
    effect_type = models.CharField(max_length=100)  # e.g., material_cost_reduction, bonus_output_chance
    effect_value = models.IntegerField(default=0)  # percent or flat depending on effect
    params = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = ('skill', 'code')

    def __str__(self):
        return f"{self.skill.code}:{self.code}"
