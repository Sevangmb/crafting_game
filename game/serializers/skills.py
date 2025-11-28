from rest_framework import serializers
from ..models import Skill, TalentNode

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'code', 'name', 'description']

class TalentNodeSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = TalentNode
        fields = ['id', 'skill', 'code', 'name', 'description', 'tier', 'xp_required', 'prereq_codes', 'effect_type', 'effect_value', 'params']
