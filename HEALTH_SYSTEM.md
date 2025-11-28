# Système de Santé Avancé - Inspiré de SCUM

Ce document décrit le système de santé détaillé implémenté dans le jeu, inspiré du système réaliste de SCUM.

## Vue d'ensemble

Le système de santé suit individuellement chaque partie du corps, les blessures, les maladies, et les signes vitaux du joueur.

## Composants du Système

### 1. Parties du Corps (Body Parts)

Le joueur possède 10 parties du corps distinctes :

- **Tête** (critique x2.5) - Saignement élevé
- **Torse** (critique x2.0) - Très important
- **Bras gauche/droit** (x0.8)
- **Main gauche/droite** (x0.5)
- **Jambe gauche/droite** (x1.0)
- **Pied gauche/droit** (x0.6)

Chaque partie a :
- Santé (0-100%)
- État de saignement (avec sévérité)
- État de fracture
- Niveau d'infection
- Niveau de douleur

### 2. États de Santé

#### Saignement
- **Aucun / Mineur / Modéré / Sévère / Critique**
- Taux de saignement variable selon la partie du corps
- Peut être stoppé avec des bandages
- Réduit le volume sanguin

#### Fractures
- Possibles sur toutes les parties avec des os
- Nécessite une attelle pour guérir
- Cause de la douleur
- Réduit l'efficacité du joueur

#### Infections
- Se développent dans les blessures non traitées
- S'aggravent sans antibiotiques
- Peuvent mener à des maladies
- Niveau de 0-100%

#### Douleur
- Augmente avec les blessures
- Affecte les performances
- Réduite avec des antidouleurs
- Diminue naturellement pendant la guérison

### 3. Signes Vitaux

Le système suit :
- **Température corporelle** (30-43°C)
  - Normal : 37°C
  - < 34°C : Hypothermie
  - > 40°C : Hyperthermie

- **Volume sanguin** (0-100%)
  - < 40% : Hémorragie critique
  - < 70% : Perte de sang importante

- **Niveau d'oxygène** (0-100%)
  - < 70% : Hypoxie

- **Rythme cardiaque** (30-200 bpm)
  - Normal : 70 bpm

- **Stamina** (0-100%)

### 4. Maladies

7 maladies sont actuellement implémentées :

1. **Rhume commun**
   - Léger, se guérit naturellement
   - Cause fatigue et fièvre

2. **Grippe**
   - Plus sévère que le rhume
   - Forte fièvre, vomissements possibles

3. **Intoxication alimentaire**
   - De la nourriture avariée
   - Vomissements, douleurs

4. **Infection bactérienne**
   - Nécessite des antibiotiques
   - Progression rapide

5. **Mal des rayons**
   - Exposition aux radiations
   - Très dangereux, nécessite traitement

6. **Dysenterie**
   - Infection intestinale
   - Déshydratation rapide

7. **Choléra**
   - Très grave
   - Progression rapide, mortel sans traitement

Chaque maladie a :
- Sévérité actuelle (0-100%)
- Taux de progression
- Effets sur la santé
- Taux de guérison naturelle
- Possibilité de traitement

### 5. Soins Médicaux

Types d'objets médicaux disponibles :
- **Bandages** - Arrêter les saignements
- **Bandages avancés** - Plus efficaces
- **Attelles** - Traiter les fractures
- **Antidouleurs** - Réduire la douleur
- **Antibiotiques** - Combattre les infections
- **Antiviraux** - Traiter les virus
- **Anti-radiation** - Mal des rayons
- **Poches de sang** - Restaurer le volume sanguin
- **Solution saline** - Hydratation
- **Kits de chirurgie** - Extraire balles, chirurgie

## API Endpoints

### Statut de Santé

```http
GET /api/health/status/
```
Retourne le statut de santé complet du joueur.

### Parties du Corps

```http
GET /api/health/body-parts/
```
Liste toutes les parties du corps avec leur état.

### Maladies

```http
GET /api/health/diseases/
```
Liste les maladies actives du joueur.

```http
GET /api/health/diseases/all/
```
Liste toutes les maladies disponibles.

### Actions Médicales

**Appliquer un bandage**
```http
POST /api/health/bandage/
{
  "body_part_type": "head",
  "bandage_quality": 70
}
```

**Appliquer une attelle**
```http
POST /api/health/splint/
{
  "body_part_type": "left_leg"
}
```

**Soigner une partie**
```http
POST /api/health/heal/
{
  "body_part_type": "torso",
  "heal_amount": 20
}
```

**Infliger des dégâts (test/combat)**
```http
POST /api/health/damage/
{
  "body_part_type": "torso",
  "damage_amount": 25,
  "cause_bleeding": true,
  "bleeding_severity": "moderate",
  "can_fracture": true
}
```

**Contracter une maladie (test/événement)**
```http
POST /api/health/diseases/contract/
{
  "disease_name": "Grippe",
  "initial_severity": 20.0
}
```

## Services

### health_service.py

Fonctions principales :

- `initialize_player_health(player)` - Initialiser le système de santé pour un nouveau joueur
- `apply_damage_to_body_part(player, body_part_type, damage_amount, ...)` - Appliquer des dégâts
- `apply_bandage(player, body_part_type, bandage_quality)` - Bander une blessure
- `apply_splint(player, body_part_type)` - Poser une attelle
- `heal_body_part(player, body_part_type, heal_amount)` - Soigner
- `process_bleeding(player)` - Traiter le saignement (appel périodique)
- `process_infections(player)` - Traiter les infections (appel périodique)
- `process_diseases(player)` - Traiter les maladies (appel périodique)
- `natural_healing(player)` - Régénération naturelle (appel périodique)
- `contract_disease(player, disease_name, initial_severity)` - Contracter une maladie
- `get_player_health_summary(player)` - Obtenir résumé complet de santé

## Initialisation

Pour initialiser les parties du corps et les maladies dans la base de données :

```bash
python init_health_system.py
```

Ce script crée :
- 10 parties du corps avec leurs propriétés
- 7 maladies avec leurs caractéristiques

## Intégration avec d'autres Systèmes

### Nutrition
Le système de nutrition (déjà implémenté) affecte :
- Taux de régénération de santé
- Force du système immunitaire
- Résistance aux maladies

### Combat
Les blessures du combat devraient appliquer des dégâts aux parties du corps spécifiques.

### Environnement
- Température ambiante affecte la température corporelle
- Pluie/eau augmente le niveau d'humidité
- Zones radioactives causent le mal des rayons

## Processus Périodiques Recommandés

Pour un réalisme complet, ces fonctions devraient être appelées périodiquement :

1. **Chaque minute** :
   - `process_bleeding(player)` - Gérer la perte de sang

2. **Toutes les 10 minutes** :
   - `process_infections(player)` - Progression des infections

3. **Chaque heure** :
   - `process_diseases(player)` - Progression des maladies
   - `natural_healing(player)` - Régénération naturelle

Ces appels peuvent être gérés via Celery (tâches asynchrones) ou directement dans les endpoints selon l'architecture du jeu.

## État Critique

Le joueur est en état critique si :
- Volume sanguin < 40%
- Température corporelle < 34°C ou > 40°C
- Niveau d'oxygène < 60%

En état critique, le joueur devrait avoir des pénalités sévères et risque de mort.

## Exemples d'Utilisation

### Initialiser un nouveau joueur
```python
from game.services.health_service import initialize_player_health

initialize_player_health(player)
```

### Blessure de combat
```python
from game.services.health_service import apply_damage_to_body_part

result = apply_damage_to_body_part(
    player=player,
    body_part_type='torso',
    damage_amount=30,
    cause_bleeding=True,
    bleeding_severity='severe',
    can_fracture=True
)
```

### Soigner avec un bandage
```python
from game.services.health_service import apply_bandage

result = apply_bandage(
    player=player,
    body_part_type='head',
    bandage_quality=85
)
```

### Obtenir le statut complet
```python
from game.services.health_service import get_player_health_summary

summary = get_player_health_summary(player)
# summary contient toutes les infos de santé
```

## Améliorations Futures Possibles

1. **Chirurgie** - Extraire balles/éclats d'obus
2. **Amputation** - Dans les cas extrêmes
3. **Prothèses** - Remplacer membres perdus
4. **Cicatrices** - Blessures permanentes
5. **Immunité** - Résistance acquise aux maladies
6. **Groupe sanguin** - Pour les transfusions
7. **Allergies** - Réactions à certains médicaments
8. **Addiction** - Dépendance aux médicaments
9. **Effets secondaires** - Des médicaments
10. **Maladies chroniques** - Diabète, asthme, etc.

## Notes Techniques

- Tous les modèles utilisent FloatField pour les pourcentages (0-100)
- Les timestamps permettent de calculer la progression au fil du temps
- Les multiplicateurs critiques affectent l'impact des blessures sur la santé globale
- Le système est conçu pour être extensible

## Conclusion

Ce système de santé offre un niveau de profondeur et de réalisme comparable à SCUM, avec un suivi détaillé de chaque partie du corps, des blessures complexes, et un système de maladies complet. Il s'intègre naturellement avec le système de nutrition existant et peut être étendu pour plus de réalisme.
