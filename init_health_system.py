"""
Initialize the health system with body parts and diseases
Run this script once to populate the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from game.models import BodyPart, Disease


def create_body_parts():
    """Create all body parts"""
    print("Creating body parts...")

    body_parts_data = [
        {
            'name': 'Tête',
            'body_part_type': 'head',
            'critical_multiplier': 2.5,  # Head injuries are critical
            'base_bleeding_rate': 3.0,  # Head bleeds heavily
            'can_fracture': True,
        },
        {
            'name': 'Torse',
            'body_part_type': 'torso',
            'critical_multiplier': 2.0,  # Torso is very important
            'base_bleeding_rate': 2.0,
            'can_fracture': True,
        },
        {
            'name': 'Bras gauche',
            'body_part_type': 'left_arm',
            'critical_multiplier': 0.8,
            'base_bleeding_rate': 1.5,
            'can_fracture': True,
        },
        {
            'name': 'Bras droit',
            'body_part_type': 'right_arm',
            'critical_multiplier': 0.8,
            'base_bleeding_rate': 1.5,
            'can_fracture': True,
        },
        {
            'name': 'Main gauche',
            'body_part_type': 'left_hand',
            'critical_multiplier': 0.5,
            'base_bleeding_rate': 1.0,
            'can_fracture': True,
        },
        {
            'name': 'Main droite',
            'body_part_type': 'right_hand',
            'critical_multiplier': 0.5,
            'base_bleeding_rate': 1.0,
            'can_fracture': True,
        },
        {
            'name': 'Jambe gauche',
            'body_part_type': 'left_leg',
            'critical_multiplier': 1.0,
            'base_bleeding_rate': 1.8,
            'can_fracture': True,
        },
        {
            'name': 'Jambe droite',
            'body_part_type': 'right_leg',
            'critical_multiplier': 1.0,
            'base_bleeding_rate': 1.8,
            'can_fracture': True,
        },
        {
            'name': 'Pied gauche',
            'body_part_type': 'left_foot',
            'critical_multiplier': 0.6,
            'base_bleeding_rate': 1.2,
            'can_fracture': True,
        },
        {
            'name': 'Pied droit',
            'body_part_type': 'right_foot',
            'critical_multiplier': 0.6,
            'base_bleeding_rate': 1.2,
            'can_fracture': True,
        },
    ]

    for data in body_parts_data:
        body_part, created = BodyPart.objects.get_or_create(
            body_part_type=data['body_part_type'],
            defaults=data
        )
        if created:
            print(f"  [OK] Created: {body_part.name}")
        else:
            print(f"  - Already exists: {body_part.name}")

    print(f"\nTotal body parts: {BodyPart.objects.count()}\n")


def create_diseases():
    """Create common diseases"""
    print("Creating diseases...")

    diseases_data = [
        {
            'name': 'Rhume commun',
            'disease_type': 'common_cold',
            'description': 'Une infection virale légère qui cause fatigue et inconfort.',
            'base_severity': 15.0,
            'progression_rate': 2.0,
            'health_drain_rate': 0.5,
            'stamina_penalty': 10.0,
            'stat_penalty': 5.0,
            'causes_fever': True,
            'causes_vomiting': False,
            'causes_fatigue': True,
            'causes_pain': False,
            'natural_recovery_rate': 5.0,
            'requires_medicine': False,
            'is_contagious': True,
        },
        {
            'name': 'Grippe',
            'disease_type': 'flu',
            'description': 'Infection virale sévère avec fièvre et faiblesse importante.',
            'base_severity': 30.0,
            'progression_rate': 3.0,
            'health_drain_rate': 1.5,
            'stamina_penalty': 30.0,
            'stat_penalty': 15.0,
            'causes_fever': True,
            'causes_vomiting': True,
            'causes_fatigue': True,
            'causes_pain': True,
            'natural_recovery_rate': 2.0,
            'requires_medicine': False,
            'is_contagious': True,
        },
        {
            'name': 'Intoxication alimentaire',
            'disease_type': 'food_poisoning',
            'description': 'Causée par de la nourriture contaminée ou avariée.',
            'base_severity': 25.0,
            'progression_rate': 5.0,
            'health_drain_rate': 2.0,
            'stamina_penalty': 40.0,
            'stat_penalty': 20.0,
            'causes_fever': False,
            'causes_vomiting': True,
            'causes_fatigue': True,
            'causes_pain': True,
            'natural_recovery_rate': 10.0,
            'requires_medicine': True,
            'is_contagious': False,
        },
        {
            'name': 'Infection bactérienne',
            'disease_type': 'bacterial',
            'description': 'Infection bactérienne nécessitant des antibiotiques.',
            'base_severity': 40.0,
            'progression_rate': 4.0,
            'health_drain_rate': 3.0,
            'stamina_penalty': 25.0,
            'stat_penalty': 15.0,
            'causes_fever': True,
            'causes_vomiting': False,
            'causes_fatigue': True,
            'causes_pain': True,
            'natural_recovery_rate': 1.0,
            'requires_medicine': True,
            'is_contagious': False,
        },
        {
            'name': 'Mal des rayons',
            'disease_type': 'radiation_sickness',
            'description': 'Maladie causée par exposition aux radiations.',
            'base_severity': 50.0,
            'progression_rate': 2.0,
            'health_drain_rate': 5.0,
            'stamina_penalty': 50.0,
            'stat_penalty': 30.0,
            'causes_fever': True,
            'causes_vomiting': True,
            'causes_fatigue': True,
            'causes_pain': True,
            'natural_recovery_rate': 0.5,
            'requires_medicine': True,
            'is_contagious': False,
        },
        {
            'name': 'Dysenterie',
            'disease_type': 'dysentery',
            'description': 'Infection intestinale grave causant déshydratation.',
            'base_severity': 35.0,
            'progression_rate': 6.0,
            'health_drain_rate': 2.5,
            'stamina_penalty': 45.0,
            'stat_penalty': 25.0,
            'causes_fever': True,
            'causes_vomiting': True,
            'causes_fatigue': True,
            'causes_pain': True,
            'natural_recovery_rate': 1.5,
            'requires_medicine': True,
            'is_contagious': True,
        },
        {
            'name': 'Cholera',
            'disease_type': 'cholera',
            'description': 'Maladie infectieuse grave causant déshydratation rapide.',
            'base_severity': 60.0,
            'progression_rate': 8.0,
            'health_drain_rate': 4.0,
            'stamina_penalty': 60.0,
            'stat_penalty': 40.0,
            'causes_fever': True,
            'causes_vomiting': True,
            'causes_fatigue': True,
            'causes_pain': True,
            'natural_recovery_rate': 0.5,
            'requires_medicine': True,
            'is_contagious': True,
        },
    ]

    for data in diseases_data:
        disease, created = Disease.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f"  [OK] Created: {disease.name}")
        else:
            print(f"  - Already exists: {disease.name}")

    print(f"\nTotal diseases: {Disease.objects.count()}\n")


def main():
    print("=" * 60)
    print("INITIALISATION DU SYSTEME DE SANTE")
    print("=" * 60)
    print()

    create_body_parts()
    create_diseases()

    print("=" * 60)
    print("[SUCCESS] Initialisation terminee avec succes!")
    print("=" * 60)


if __name__ == '__main__':
    main()
