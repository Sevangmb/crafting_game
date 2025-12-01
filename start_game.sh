#!/bin/bash

echo "========================================"
echo "  Démarrage du jeu Crafting Game"
echo "========================================"
echo ""

# Vérifier si le venv existe
if [ ! -d "venv" ]; then
    echo "ERREUR: Environnement virtuel non trouvé!"
    echo "Veuillez créer le venv d'abord avec: python -m venv venv"
    exit 1
fi

# Activer l'environnement virtuel
echo "[1/4] Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier si les migrations sont à jour
echo "[2/4] Vérification des migrations..."
python manage.py migrate --check > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Migrations nécessaires détectées, application..."
    python manage.py migrate
fi

# Démarrer le backend Django en arrière-plan
echo "[3/4] Démarrage du backend Django..."
python manage.py runserver > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend démarré (PID: $BACKEND_PID)"

# Attendre que le backend démarre
echo "Attente du démarrage du backend..."
sleep 3

# Démarrer le frontend React en arrière-plan
echo "[4/4] Démarrage du frontend React..."
cd frontend
npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "Frontend démarré (PID: $FRONTEND_PID)"

echo ""
echo "========================================"
echo "  Jeu démarré avec succès!"
echo "========================================"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "PIDs des processus:"
echo "  Backend: $BACKEND_PID"
echo "  Frontend: $FRONTEND_PID"
echo ""
echo "Pour arrêter les serveurs:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "Logs disponibles dans:"
echo "  Backend: logs/backend.log"
echo "  Frontend: logs/frontend.log"
echo ""

# Garder le script actif et afficher les logs
echo "Appuyez sur Ctrl+C pour arrêter les serveurs..."
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# Attendre que l'utilisateur arrête
wait
