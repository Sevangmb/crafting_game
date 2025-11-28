"""
Serializers for the health system
"""
from rest_framework import serializers
from ..models import (
    BodyPart, PlayerBodyPart, PlayerHealthStatus,
    Disease, PlayerDisease, MedicalItem
)


class BodyPartSerializer(serializers.ModelSerializer):
    """Serializer for BodyPart model"""
    display_name = serializers.CharField(source='get_body_part_type_display', read_only=True)

    class Meta:
        model = BodyPart
        fields = [
            'id',
            'name',
            'body_part_type',
            'display_name',
            'critical_multiplier',
            'base_bleeding_rate',
            'can_fracture',
        ]
        read_only_fields = fields


class PlayerBodyPartSerializer(serializers.ModelSerializer):
    """Serializer for PlayerBodyPart model"""
    body_part_name = serializers.CharField(source='body_part.name', read_only=True)
    body_part_type = serializers.CharField(source='body_part.body_part_type', read_only=True)
    status = serializers.CharField(source='status_description', read_only=True)
    is_healthy = serializers.BooleanField(read_only=True)
    bleeding_severity_display = serializers.CharField(source='get_bleeding_severity_display', read_only=True)
    fracture_severity_display = serializers.CharField(source='get_fracture_severity_display', read_only=True)

    class Meta:
        model = PlayerBodyPart
        fields = [
            'id',
            'body_part_name',
            'body_part_type',
            'health',
            'is_bleeding',
            'bleeding_severity',
            'bleeding_severity_display',
            'bleeding_rate',
            'is_fractured',
            'fracture_severity',
            'fracture_severity_display',
            'is_infected',
            'infection_level',
            'pain_level',
            'is_bandaged',
            'bandage_quality',
            'is_splinted',
            'has_bullet',
            'status',
            'is_healthy',
        ]
        read_only_fields = [
            'body_part_name',
            'body_part_type',
            'status',
            'is_healthy',
            'bleeding_severity_display',
            'fracture_severity_display',
        ]


class PlayerHealthStatusSerializer(serializers.ModelSerializer):
    """Serializer for PlayerHealthStatus model"""
    is_critical = serializers.BooleanField(source='is_critical_condition', read_only=True)
    overall_health = serializers.FloatField(source='overall_health_percentage', read_only=True)
    status = serializers.CharField(source='status_summary', read_only=True)

    class Meta:
        model = PlayerHealthStatus
        fields = [
            'id',
            'body_temperature',
            'heart_rate',
            'blood_volume',
            'oxygen_level',
            'stamina',
            'is_wet',
            'wetness_level',
            'is_hypothermic',
            'is_hyperthermic',
            'exhaustion_level',
            'is_sick',
            'sickness_severity',
            'immune_strength',
            'health_regen_rate',
            'is_critical',
            'overall_health',
            'status',
        ]
        read_only_fields = [
            'is_critical',
            'overall_health',
            'status',
        ]


class DiseaseSerializer(serializers.ModelSerializer):
    """Serializer for Disease model"""
    disease_type_display = serializers.CharField(source='get_disease_type_display', read_only=True)

    class Meta:
        model = Disease
        fields = [
            'id',
            'name',
            'disease_type',
            'disease_type_display',
            'description',
            'base_severity',
            'progression_rate',
            'health_drain_rate',
            'stamina_penalty',
            'stat_penalty',
            'causes_fever',
            'causes_vomiting',
            'causes_fatigue',
            'causes_pain',
            'natural_recovery_rate',
            'requires_medicine',
            'is_contagious',
        ]
        read_only_fields = fields


class PlayerDiseaseSerializer(serializers.ModelSerializer):
    """Serializer for PlayerDisease model"""
    disease_name = serializers.CharField(source='disease.name', read_only=True)
    disease_type = serializers.CharField(source='disease.disease_type', read_only=True)
    disease_description = serializers.CharField(source='disease.description', read_only=True)
    stage = serializers.CharField(source='stage_description', read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = PlayerDisease
        fields = [
            'id',
            'disease_name',
            'disease_type',
            'disease_description',
            'current_severity',
            'stage',
            'is_active',
            'is_being_treated',
            'treatment_effectiveness',
            'contracted_at',
        ]
        read_only_fields = [
            'disease_name',
            'disease_type',
            'disease_description',
            'stage',
            'is_active',
            'contracted_at',
        ]


class MedicalItemSerializer(serializers.ModelSerializer):
    """Serializer for MedicalItem model"""
    item_name = serializers.CharField(source='material.name', read_only=True)
    medical_type_display = serializers.CharField(source='get_medical_type_display', read_only=True)

    class Meta:
        model = MedicalItem
        fields = [
            'id',
            'item_name',
            'medical_type',
            'medical_type_display',
            'heals_bleeding',
            'bleeding_stop_chance',
            'heals_fractures',
            'restores_health',
            'restores_blood',
            'cures_infection',
            'infection_cure_rate',
            'treats_disease',
            'disease_cure_rate',
            'reduces_pain',
            'pain_reduction',
            'pain_duration',
            'restores_stamina',
            'boosts_immune_system',
            'requires_skill',
            'required_skill_level',
            'use_time_seconds',
            'success_rate',
        ]
        read_only_fields = fields


class HealthSummarySerializer(serializers.Serializer):
    """
    Comprehensive health summary serializer
    Used for API responses
    """
    overall_health = serializers.IntegerField()
    blood_volume = serializers.FloatField()
    body_temperature = serializers.FloatField()
    stamina = serializers.FloatField()
    overall_pain = serializers.FloatField()
    is_critical = serializers.BooleanField()
    status_summary = serializers.CharField()

    injuries = serializers.DictField(child=serializers.IntegerField())
    diseases_count = serializers.IntegerField()
    body_parts = PlayerBodyPartSerializer(many=True)
    active_diseases = PlayerDiseaseSerializer(many=True)
