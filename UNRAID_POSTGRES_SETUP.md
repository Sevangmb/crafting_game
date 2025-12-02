# Configuration PostgreSQL Docker sur Unraid

## Serveur Unraid: 82.65.121.46
## Container PostgreSQL

---

## Méthode 1: Configurer le port mapping du container Docker

### Dans l'interface Unraid :

1. **Aller dans Docker** → Trouver votre container PostgreSQL
2. **Cliquer sur l'icône** du container → **Edit**
3. **Vérifier/Ajouter le port mapping** :
   - Container Port: `5432`
   - Host Port: `5432`
   - Protocol: `TCP`
   - Host Path Type: `Port`

4. **Appliquer les changements** et redémarrer le container

5. **Vérifier que le port est bien ouvert** :
   ```bash
   # Sur Unraid (en SSH ou via terminal)
   docker ps | grep postgres
   netstat -tulpn | grep 5432
   ```

---

## Méthode 2: Utiliser l'IP du container Docker directement

### Trouver l'IP du container :

```bash
# SSH sur Unraid
ssh root@82.65.121.46

# Trouver l'IP du container PostgreSQL
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <nom_du_container>
```

Ensuite, modifier `backend/settings.py` avec l'IP du container au lieu de 82.65.121.46

---

## Méthode 3: Accès via réseau Docker (recommandé si Django aussi sur Docker)

Si vous comptez mettre Django aussi sur Docker, créer un réseau Docker commun :

```bash
# Créer un réseau
docker network create crafting_network

# Connecter PostgreSQL au réseau
docker network connect crafting_network <postgres_container>

# Dans Django settings, utiliser:
# HOST: nom_du_container_postgres (résolution DNS Docker)
```

---

## Configuration du container PostgreSQL

### Créer la base de données dans le container :

```bash
# Se connecter au container
docker exec -it <nom_du_container_postgres> bash

# Ou directement exécuter psql
docker exec -it <nom_du_container_postgres> psql -U postgres

# Dans psql:
CREATE USER sevans WITH PASSWORD 'Oketos2727!';
CREATE DATABASE crafting_game OWNER sevans;
GRANT ALL PRIVILEGES ON DATABASE crafting_game TO sevans;
\c crafting_game
GRANT ALL PRIVILEGES ON SCHEMA public TO sevans;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO sevans;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO sevans;
\q
```

### Variables d'environnement (si vous recréez le container) :

Dans Unraid, vous pouvez ajouter ces variables :
- `POSTGRES_USER=sevans`
- `POSTGRES_PASSWORD=Oketos2727!`
- `POSTGRES_DB=crafting_game`

---

## Pare-feu Unraid

Vérifier que le port 5432 n'est pas bloqué :

```bash
# Sur Unraid
iptables -L -n | grep 5432

# Si bloqué, ajouter règle :
iptables -A INPUT -p tcp --dport 5432 -j ACCEPT
```

---

## Test de connexion

### Depuis Unraid lui-même :

```bash
# Test local
docker exec -it <postgres_container> psql -U sevans -d crafting_game -c "SELECT version();"
```

### Depuis Windows :

```bash
python test_db.py
```

---

## Solutions selon votre configuration

### Option A: Vous voulez accéder depuis Windows à PostgreSQL sur Unraid

**Configuration nécessaire :**
1. Port mapping Docker : 5432:5432
2. Pare-feu Unraid ouvert sur 5432
3. Router/box : port forwarding si nécessaire (peu probable en local)

### Option B: Vous voulez mettre Django aussi sur Docker Unraid

**Meilleure option pour la production !**

Créer un docker-compose ou template Unraid pour Django :
- Django container et PostgreSQL sur le même réseau Docker
- Communication interne via nom de container
- Pas besoin d'exposer PostgreSQL à l'extérieur

---

## Template Docker Compose (pour référence)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: crafting_game_db
    environment:
      POSTGRES_USER: sevans
      POSTGRES_PASSWORD: Oketos2727!
      POSTGRES_DB: crafting_game
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - crafting_network
    ports:
      - "5432:5432"

  django:
    build: .
    container_name: crafting_game_backend
    environment:
      DATABASE_HOST: postgres  # Nom du service
      DATABASE_PORT: 5432
      DATABASE_NAME: crafting_game
      DATABASE_USER: sevans
      DATABASE_PASSWORD: Oketos2727!
    depends_on:
      - postgres
    networks:
      - crafting_network
    ports:
      - "8000:8000"

volumes:
  postgres_data:

networks:
  crafting_network:
    driver: bridge
```

---

## Quelle option choisissez-vous ?

1. **Développement local** : PostgreSQL sur Unraid, Django sur Windows
   → Configurer port mapping + pare-feu

2. **Production** : Tout sur Docker Unraid
   → Créer container Django + réseau Docker commun

3. **Hybride** : PostgreSQL local sur Windows, Django sur Windows
   → Installer PostgreSQL sur Windows

---

## Commandes utiles Unraid/Docker

```bash
# Lister les containers
docker ps -a

# Voir les logs
docker logs <container_name>

# Port mapping actuel
docker port <container_name>

# IP du container
docker inspect <container_name> | grep IPAddress

# Accéder au shell du container
docker exec -it <container_name> bash

# Redémarrer le container
docker restart <container_name>
```

---

## Prochaines étapes

**Dites-moi :**
1. Quel est le nom de votre container PostgreSQL sur Unraid ?
2. Voulez-vous garder Django sur Windows ou le mettre aussi sur Docker ?
3. Avez-vous accès SSH à Unraid ?

Je vous aiderai avec la configuration exacte !
