# Système de Véhicules Avancé

Documentation complète du système de véhicules amélioré.

## Vue d'ensemble

Le système de véhicules offre une gestion réaliste et détaillée des véhicules incluant :
- Gestion du carburant
- Système de durabilité et réparations
- Entretien et maintenance
- Améliorations et upgrades
- Stations-service et garages
- Pièces détachées

## Types de Véhicules

### Catégories Disponibles

1. **Vélo (Bicycle)** 🚲
   - Pas de carburant nécessaire
   - Faible capacité de chargement
   - Bonne maniabilité
   - Exemples : Vélo de ville, VTT

2. **Moto (Motorcycle)** 🏍️
   - Carburant : Essence
   - Rapide et maniable
   - Capacité limitée
   - Exemple : Moto 125cc

3. **Voiture (Car)** 🚗
   - Carburant : Essence ou Diesel
   - Équilibre vitesse/capacité
   - Protection contre les intempéries
   - Exemples : Berline, SUV 4x4

4. **Camionnette (Van)** 🚐
   - Grande capacité de chargement
   - Diesel généralement
   - Idéal pour le transport

5. **Camion (Truck)** 🚚
   - Très grande capacité
   - Consommation élevée
   - Transport de marchandises lourdes

6. **Quad/ATV** 🏎️
   - Tout-terrain
   - Essence
   - Bon compromis vitesse/terrain

7. **Bateau (Boat)** 🚤
   - Navigation sur l'eau uniquement
   - Essence
   - Capacité moyenne

## Caractéristiques des Véhicules

### Performance

- **Vitesse maximale** (max_speed) : km/h
- **Accélération** (acceleration) : 0-10
- **Maniabilité** (handling) : 0-10
- **Capacité passagers** (passenger_capacity)
- **Capacité de chargement** (carry_capacity) : en kg

### Carburant

- **Type de carburant** :
  - `none` : Pas de carburant (vélos)
  - `petrol` : Essence
  - `diesel` : Diesel
  - `electric` : Électrique
  - `hybrid` : Hybride

- **Taille du réservoir** (fuel_tank_size) : litres
- **Consommation** (fuel_consumption) : L/100km

### Durabilité

- **Durabilité maximale** (max_durability)
- **Intervalle d'entretien** (maintenance_interval) : km

### Capacités Terrain

- **Tout-terrain** (can_offroad) : Peut rouler hors route
- **Navigation** (can_water) : Peut naviguer sur l'eau
- **Nécessite route** (requires_road) : Doit rester sur route

### Autres Attributs

- **Niveau de bruit** (noise_level) : 0-100 (affecte la discrétion)
- **Protection météo** (weather_protection) : 0-100 (protection pluie/froid)
- **Rareté** : common, uncommon, rare, epic, legendary
- **Valeur de base** : prix en argent

## PlayerVehicle - Véhicules du Joueur

Chaque véhicule possédé par un joueur a :

### État

- **Durabilité globale** (overall_durability)
- **Carburant actuel** (current_fuel)
- **Kilométrage total** (total_distance_km)
- **Distance depuis entretien** (distance_since_maintenance)
- **État** : cassé (is_broken), équipé (is_equipped), verrouillé (is_locked)

### Maintenance

- **Besoin d'entretien** (needs_maintenance)
- **Dernier entretien** (last_maintenance)

### Améliorations

- **Amélioration vitesse** (speed_upgrade) : % d'augmentation
- **Amélioration efficacité** (fuel_efficiency_upgrade) : % de réduction
- **Amélioration capacité** (capacity_upgrade) : kg supplémentaires
- **Équipements** :
  - Turbo (has_turbo)
  - Blindage (has_armor, armor_value)

### Emplacement

- **Position garée** (parked_x, parked_y)
- **Nom personnalisé** (custom_name)

### Propriétés Calculées

Le véhicule calcule automatiquement :

- **Pourcentage de carburant** : `fuel_percentage`
- **Pourcentage de durabilité** : `durability_percentage`
- **Vitesse effective** : `effective_speed` (avec upgrades et dégâts)
- **Consommation effective** : `effective_fuel_consumption`
- **Capacité effective** : `effective_carry_capacity`
- **Peut rouler** : `can_drive`

## Système de Carburant

### Types de Carburant

1. **Essence (Petrol)**
   - Voitures légères, motos
   - Prix moyen : ~1.75€/L

2. **Diesel**
   - SUV, camions, camionnettes
   - Prix moyen : ~1.65€/L

3. **Électrique**
   - Bornes de recharge
   - Prix : ~0.30€/kWh

### Stations-Service (FuelStation)

Attributs :
- Nom et position (latitude, longitude)
- Disponibilité par type de carburant
- Prix par litre/kWh
- Stock disponible (optionnel)
- État opérationnel

### Ravitaillement

```python
from game.services.advanced_vehicle_service import refuel_vehicle

result = refuel_vehicle(
    player=player,
    vehicle_id=vehicle.id,
    fuel_amount=30.0,  # 30 litres
    fuel_cost=52.50    # Coût total
)
```

### Consommation de Carburant

Le carburant est consommé automatiquement lors des déplacements :

```python
from game.services.advanced_vehicle_service import consume_fuel

result = consume_fuel(
    vehicle=player_vehicle,
    distance_km=50.0  # 50 km parcourus
)
# Consomme environ 4L pour une voiture à 8L/100km
```

## Système de Réparations

### Dégâts

Les véhicules perdent de la durabilité avec :
- L'utilisation normale
- Les accidents/collisions
- Le manque d'entretien

```python
from game.services.advanced_vehicle_service import apply_vehicle_damage

result = apply_vehicle_damage(
    vehicle=player_vehicle,
    damage_amount=150  # Points de durabilité perdus
)
```

### Réparations

Les véhicules peuvent être réparés dans les garages :

```python
from game.services.advanced_vehicle_service import repair_vehicle

result = repair_vehicle(
    player=player,
    vehicle_id=vehicle.id,
    repair_points=200,  # Durabilité à restaurer
    repair_cost=400     # Coût en argent
)
```

### Garages (Garage)

Attributs :
- Nom et position
- Services disponibles :
  - Réparation (can_repair)
  - Améliorations (can_upgrade)
  - Peinture (can_paint)
  - Installation pièces (can_install_parts)
- Niveau du mécanicien (mechanic_skill_level)
- Tarifs (repair_cost_per_point, upgrade_cost_multiplier)
- Inventaire de pièces

## Système d'Entretien

### Maintenance Régulière

Les véhicules nécessitent un entretien périodique :

```python
from game.services.advanced_vehicle_service import perform_maintenance

result = perform_maintenance(
    player=player,
    vehicle_id=vehicle.id
)
```

L'entretien :
- Réinitialise le compteur de distance
- Restaure un peu de durabilité
- Coûte de l'argent
- Améliore les performances

### Journal d'Entretien

Chaque opération est enregistrée dans `VehicleMaintenanceLog` :

- Type d'opération (réparation, entretien, ravitaillement, upgrade)
- Description
- Coût
- Durabilité restaurée
- Carburant ajouté
- Date
- Effectué par (joueur)

## Pièces Détachées

### Types de Pièces (VehiclePart)

- **Moteur** (engine) : Affecte vitesse et consommation
- **Transmission** : Performance générale
- **Roues** (wheels) : Maniabilité
- **Batterie** (battery) : Démarrage
- **Réservoir** (fuel_tank) : Capacité carburant
- **Radiateur** (radiator) : Refroidissement
- **Freins** (brakes) : Sécurité
- **Suspension** : Confort et maniabilité
- **Carrosserie** (body) : Protection
- **Pare-brise** (windshield)
- **Feux** (lights) : Visibilité
- **Système électrique** (electrical)
- **Échappement** (exhaust)

### Attributs des Pièces

- Durabilité maximale
- Poids
- Modificateurs de performance :
  - Vitesse
  - Efficacité carburant
  - Maniabilité
- Compatibilité avec types de véhicules
- Rareté et valeur

### Pièces Installées (PlayerVehiclePart)

Chaque pièce installée sur un véhicule :
- A sa propre durabilité
- Peut être endommagée ou cassée
- Affecte les performances du véhicule

## Améliorations (Upgrades)

### Types d'Améliorations

1. **Vitesse** (speed)
   - +10% de vitesse max par niveau
   - Coût croissant

2. **Efficacité carburant** (fuel_efficiency)
   - -10% de consommation par niveau
   - Économise du carburant

3. **Capacité** (capacity)
   - +20kg par niveau
   - Augmente le chargement possible

```python
from game.services.advanced_vehicle_service import purchase_upgrade

result = purchase_upgrade(
    player=player,
    vehicle_id=vehicle.id,
    upgrade_type='speed',  # ou 'fuel_efficiency' ou 'capacity'
    upgrade_cost=1000
)
```

## Services

### advanced_vehicle_service.py

Fonctions principales :

#### Gestion de Base
- `get_player_vehicles(player)` - Liste des véhicules
- `get_equipped_vehicle(player)` - Véhicule équipé
- `equip_vehicle(player, vehicle_id)` - Équiper
- `unequip_vehicle(player)` - Déséquiper

#### Carburant
- `refuel_vehicle(player, vehicle_id, fuel_amount, fuel_cost)` - Ravitailler
- `calculate_fuel_needed(vehicle, distance_km)` - Calculer carburant nécessaire
- `consume_fuel(vehicle, distance_km)` - Consommer carburant

#### Réparations et Entretien
- `apply_vehicle_damage(vehicle, damage_amount)` - Appliquer dégâts
- `repair_vehicle(player, vehicle_id, repair_points, repair_cost)` - Réparer
- `perform_maintenance(player, vehicle_id)` - Entretien

#### Localisation
- `find_nearby_fuel_stations(x, y, max_distance_km)` - Stations proches
- `find_nearby_garages(x, y, max_distance_km)` - Garages proches

#### Améliorations
- `purchase_upgrade(player, vehicle_id, upgrade_type, upgrade_cost)` - Acheter upgrade

#### Informations
- `get_vehicle_status(vehicle)` - Statut complet
- `get_maintenance_history(vehicle, limit)` - Historique

## Initialisation

Pour initialiser le système de véhicules :

```bash
python init_vehicles.py
```

Ce script crée :
- 9 types de véhicules
- 4 stations-service à Valence
- 3 garages
- 6 pièces détachées de base

## Intégration avec le Jeu

### Déplacement

Quand un joueur se déplace avec un véhicule :
1. Vérifier si le véhicule peut rouler (`can_drive`)
2. Calculer le carburant nécessaire
3. Consommer le carburant
4. Appliquer usure (distance)
5. Réduire le coût en énergie du joueur

### Combat

Les véhicules peuvent :
- Subir des dégâts lors de combats
- Offrir une protection (blindage)
- Permettre la fuite rapide

### Économie

- Achat/Vente de véhicules
- Coût du carburant
- Réparations et entretien
- Pièces détachées
- Améliorations

## Mécaniques de Jeu Recommandées

### Gestion Réaliste

1. **Carburant**
   - Trouve des stations-service
   - Gère ton budget carburant
   - Transporte des bidons d'essence

2. **Entretien**
   - Entretien régulier nécessaire
   - Les véhicules mal entretenus tombent en panne
   - Pièces qui s'usent

3. **Réparations**
   - Dégâts visibles sur les performances
   - Garages requis pour grosses réparations
   - Possibilité de réparations de fortune

### Progression

1. **Débuter**
   - Vélo → Économique, pas de carburant
   - Faible capacité

2. **Milieu de jeu**
   - Moto/Voiture → Rapide mais carburant
   - Meilleure capacité

3. **Fin de jeu**
   - SUV/Camion → Grande capacité
   - Tout-terrain
   - Très amélioré

## Exemples d'Utilisation

### Acheter un véhicule

```python
# Via le système de craft
vehicle_type = VehicleType.objects.get(name="Berline Citadine")

player_vehicle = PlayerVehicle.objects.create(
    player=player,
    vehicle_type=vehicle_type,
    overall_durability=vehicle_type.max_durability,
    current_fuel=vehicle_type.fuel_tank_size * 0.5,  # 50% plein
)
```

### Faire le plein

```python
# Trouver stations proches
stations = find_nearby_fuel_stations(
    player.current_x,
    player.current_y,
    max_distance_km=5
)

# Ravitailler
if stations:
    station = stations[0]
    fuel_amount = 40.0  # 40 litres
    cost = fuel_amount * station['petrol_price']

    result = refuel_vehicle(
        player=player,
        vehicle_id=player.current_vehicle.id,
        fuel_amount=fuel_amount,
        fuel_cost=int(cost)
    )
```

### Voyager

```python
distance_km = 100.0

# Consommer carburant
result = consume_fuel(
    vehicle=player.current_vehicle,
    distance_km=distance_km
)

if result['success']:
    # Réduire énergie joueur (avec véhicule)
    energy_cost = 10 * vehicle.vehicle_type.energy_cost_multiplier
    player.energy -= int(energy_cost)
    player.save()
else:
    # Pas assez de carburant!
    print(f"Carburant insuffisant: {result['error']}")
```

### Réparer

```python
# Trouver garages proches
garages = find_nearby_garages(
    player.current_x,
    player.current_y,
    max_distance_km=5
)

if garages:
    garage = garages[0]

    # Durabilité à réparer
    to_repair = 300
    cost = int(to_repair * garage['repair_cost_per_point'])

    result = repair_vehicle(
        player=player,
        vehicle_id=player.current_vehicle.id,
        repair_points=to_repair,
        repair_cost=cost
    )
```

## Améliorations Futures Possibles

1. **Customisation visuelle**
   - Peinture
   - Autocollants
   - Néons

2. **Mods avancés**
   - Nitro
   - Blindage renforcé
   - Systèmes audio

3. **Assurance**
   - Couvre les dégâts
   - Coût mensuel

4. **Vol de véhicules**
   - Système de verrouillage
   - Alarmes
   - Trackers GPS

5. **Courses**
   - Compétitions
   - Paris
   - Classements

6. **Convois**
   - Voyager en groupe
   - Protection mutuelle

7. **Météo et conditions**
   - Routes glissantes
   - Usure accélérée
   - Performances réduites

8. **Permis de conduire**
   - Requis pour certains véhicules
   - Niveaux de compétence

## Conclusion

Le système de véhicules offre une expérience de gestion réaliste et profonde, avec de nombreuses possibilités de gameplay. Il encourage :
- La planification (carburant, entretien)
- L'économie (coûts de possession)
- La progression (amélioration des véhicules)
- L'exploration (trouver stations et garages)

Le système est extensible et peut être enrichi avec de nombreuses fonctionnalités additionnelles.
